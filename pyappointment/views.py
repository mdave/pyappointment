from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from django.contrib import messages

import datetime as dt
import dateutil.parser
import uuid
import pytz

from pyappointment import settings, calendar_link
from pyappointment.email import send_attendee_email, send_organizer_email
from pyappointment.availability import MEETING_AVAIL, Availability
from pyappointment.forms import BookingForm

LOCALTZ = pytz.timezone(settings.TIME_ZONE)

def convert_iso8601(iso_str, tz):
    """
    Converts a date in ISO 8601 format to a datetime object, given a timezone tz.
    """
    tmp = dateutil.parser.parse(iso_str)
    if tmp.tzinfo is None:
        # All-day event, so assume we're in the local timezone
        tmp = LOCALTZ.localize(tmp)
    return tmp.astimezone(tz)

def replace_time(date, time):
    """
    Replaces the time component of a date with values from a given dateutil.time
    object.
    """
    return date.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)

def get_monday(date):
    """
    Returns start of the week (defined as Monday) given a particular date.
    """
    return date - dt.timedelta(date.weekday())

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def check_available(booking_info, start, finish, events):
    # First, check this time isn't in the past.
    now = dt.datetime.now(LOCALTZ)
    if start < now:
        return False, "date in the past"

    # Now check if we have sufficient lead time for this booking type.
    lead_time = booking_info['lead_time']
    if start < now + dt.timedelta(hours=lead_time):
        return False, "not enough lead time: bookings must be at least {:d} {:s} in advance".format(
            lead_time, 'hour' if lead_time == 1 else 'hours')

    # Don't let anyone book later than an upper limit.
    upper_limit = booking_info['future_limit']
    if upper_limit != 0 and start > now + dt.timedelta(days=upper_limit):
        return False, "date too far in the future"

    # If this booking type defines a custom availability, check against this.
    if 'availability' in booking_info:
        # Determine if we've defined a specific date for this booking
        # type. Specific dates are defined in the form 'YYYY-MM-DD'. In this
        # case, we ignore _any_ other general dates given in the availability
        # list.
        specific_dates = False
        for key in booking_info['availability'].keys():
            if '-' in key:
                specific_dates = True
                break

        avail = False
        if specific_dates:
            for key, val in booking_info['availability'].items():
                if '-' not in key:
                    continue

                # Parse this date and check it matches our key.
                d_y, d_m, d_d = [ int(a) for a in key.split('-') ]
                if dt.date(d_y, d_m, d_d) != start.date():
                    continue

                # Construct availability
                avail = Availability.from_config(val).is_available(start.time(), finish.time())
                if avail:
                    break
        else:
            # Check against normal availability.
            dow = start.strftime('%a').upper()
            avail_val = booking_info['availability'].get(dow)
            if avail_val is not None:
                avail = Availability.from_config(avail_val).is_available(start.time(), finish.time())

        if not avail:
            return False, "non-available time"

    elif not MEETING_AVAIL[start.weekday()].is_available(start.time(), finish.time()):
        # Check hard-coded availability times.
        return False, "non-available time"

    # Finally, check against events.
    for e in events:
        e_start = convert_iso8601(e['start'], LOCALTZ)
        e_end   = convert_iso8601(e['end'], LOCALTZ)

        if start < e_end and finish > e_start:
            if settings.SHOW_CONFLICTING_EVENTS:
                return False, "conflicts with event: " + e['summary']
            else:
                return False, "conflicts with existing event"

    return True, "available"

def generate_week_times(booking_info, date):
    # Calculate minimum and maximum times for the week's availability.
    min_time, max_time = dt.time.max, dt.time.min

    # Holds the index of days we'll be displaying.
    display_days = []

    # Get monday before date.
    monday = get_monday(date)

    for i, avail in enumerate(MEETING_AVAIL):
        t_min, t_max = avail.day_range()
        if t_min is None:
            continue

        # Check for specific availability regions to override minimum and
        # maximum.
        if 'availability' in booking_info:
            date_i = monday + dt.timedelta(days=i)
            for key, val in booking_info['availability'].items():
                if '-' not in key:
                    continue

                d_y, d_m, d_d = [ int(a) for a in key.split('-') ]
                if dt.date(d_y, d_m, d_d) != date_i.date():
                    continue

                t_min, t_max = Availability.from_config(val).day_range()
                break

            if t_min is None:
                continue

        min_time, max_time = min(min_time, t_min), max(max_time, t_max)
        display_days.append(i)

    # Populate a list of times that we've available.
    times    = []
    monday   = replace_time(get_monday(date), min_time)
    duration = dt.timedelta(minutes=booking_info['duration'])
    delta    = dt.timedelta(minutes=booking_info['slots'])

    # Grab raw event data from calendar.
    events = calendar_link.get_events(monday, 7)

    # Track availability:
    #
    #   - one_availability is True if at least one slot in the week is free;
    #   - prev_gap is True if the previous timeslot was a gap (i.e. no time was
    #     available across all of the days);
    #   - avail_days[i] is True if at least one appointment slot is available
    #     for display_days[i].
    #
    # These are used to condense the week view to only a sensible range of
    # times.
    one_available = False
    prev_gap      = False
    avail_days    = [ False ] * len(display_days)

    for d in perdelta(monday, replace_time(monday, max_time), delta):
        tmp = []
        no_avail = True
        for n, i in enumerate(display_days):
            date = d + dt.timedelta(days=i)

            # First, check availability against specified limits.
            available, reason = check_available(booking_info, date, date + duration, events)
            if available:
                no_avail      = False
                one_available = True
                avail_days[n] = True

            tmp.append({
                'date': date,
                'available': available,
                'reason': reason
            })

        if not no_avail:
            times.append(tmp)
            prev_gap = False
        else:
            if not prev_gap:
                times.append('gap')
                prev_gap = True

    # Remove any days where we're not fully available, if this is configured for
    # this booking type.
    if 'collapse_days' in booking_info and booking_info['collapse_days']:
        times = [
            [ d for i, d in enumerate(t) if avail_days[i] ]
            if type(t) == list else t for t in times
        ]

    # Trim from start of array
    if len(times) > 0:
        if times[0] == 'gap':
            times.pop(0)

    # Trim from end of array
    if len(times) > 0:
        if times[-1] == 'gap':
            times.pop()

    return { 'times': times, 'one_available': one_available, 'monday': monday }

def view_week(request, booking_type, year, month, day):
    try:
        date = LOCALTZ.localize(dt.datetime(int(year), int(month), int(day), hour=9))
    except ValueError:
        raise Http404("Date does not exist")

    now       = dt.datetime.now(LOCALTZ)
    monday    = get_monday(date)
    prev_date = monday - dt.timedelta(days=7)
    next_date = monday + dt.timedelta(days=7)

    if prev_date < now - dt.timedelta(days=7):
        prev_date = None

    booking_info = settings.BOOKING_TYPES[booking_type]
    future_limit = booking_info['future_limit']
    if future_limit != 0 and next_date > now + dt.timedelta(days=future_limit):
        next_date = None

    return render(request, 'week_view.html', {
        'times': generate_week_times(booking_info, date),
        'booking_type': booking_type,
        'booking_info': booking_info,
        'organizer': settings.ORGANIZER_NAME,
        'prev_date': prev_date,
        'next_date': next_date,
        'show_reasons': settings.SHOW_REASONS
    })

def booking_form(request, booking_type, year, month, day, hour, minute):
    try:
        date = LOCALTZ.localize(dt.datetime(
            int(year), int(month), int(day), hour=int(hour), minute=int(minute)))
    except pytz.exceptions.AmbiguousTimeError:
        raise Http404("Time error")
    except ValueError:
        raise Http404("Date does not exist")

    # Validate availability.
    handle = calendar_link.connect_calendar()
    cal_ids = handle.list_calendars()
    events = calendar_link.get_events(
        date, 1, handle=handle, cal_ids=calendar_link.filter_ids(cal_ids))

    book_cal_id = [
        c['calendar_id'] for c in cal_ids if
        c['calendar_name'].lower() == settings.CAL_CREATE_BOOKING.lower()
    ][0]

    booking_info = settings.BOOKING_TYPES[booking_type]
    duration     = booking_info['duration']
    start        = date
    finish       = date + dt.timedelta(minutes=duration)

    if not check_available(booking_info, start, finish, events)[0]:
        return render(request, 'error.html', {
            'error_title': 'Booking error',
            'error_message': 'This slot is not available for bookings.',
            'redirect': '/' + booking_type + '/' + date.strftime('%Y-%m-%d'),
            'redirect_msg': '« Return to grid'
        })

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Error in your form. Please check below.")
        else:
            try:
                event = {
                    'event_id': 'book-%s' % uuid.uuid4(),
                    'summary': booking_info['description'] + ': ' + form.cleaned_data['name'],
                    'description': form.cleaned_data['notes'],
                    'start': start.astimezone(pytz.utc),
                    'end': finish.astimezone(pytz.utc),
                    'tzid': str(LOCALTZ)
                }

                handle.upsert_event(calendar_id=book_cal_id, event=event)
            except:
                return render(request, 'error.html', {
                    'error_title': 'Booking error',
                    'error_message': 'Something went wrong! Try again.',
                    'redirect': '/' + booking_type + '/' + date.strftime('%Y-%m-%d'),
                    'redirect_msg': '« Return to grid'
                })

            # Send reminder email.
            send_attendee_email(start, finish, form.cleaned_data['name'], booking_type,
                                form.cleaned_data['notes'], event['event_id'],
                                form.cleaned_data['email'])
            send_organizer_email(start, finish, form.cleaned_data['name'], booking_type,
                                 form.cleaned_data['notes'], event['event_id'])

            return render(request, 'book_success.html', {
                'date': start,
                'booking_type': booking_type,
                'booking_info': booking_info,
                'redirect': '/' + booking_type + '/' + date.strftime('%Y-%m-%d'),
                'redirect_msg': '« Return to grid'
            })

    else:
        form = BookingForm()

    return render(request, 'book.html', {
        'form': form,
        'date': date,
        'booking_type': booking_type,
        'booking_info': booking_info,
        'duration': 30
    })

def view_booking_type(request, booking_type):
    now = dt.datetime.now(LOCALTZ)
    return view_week(request, booking_type, now.year, now.month, now.day)

def index(request):
    now = dt.datetime.now(LOCALTZ)

    return render(request, 'index.html', {
        'organizer': settings.ORGANIZER_NAME,
        'booking_types': {
            k: v for k, v in settings.BOOKING_TYPES.items() if not v['hidden']
        }
    })
