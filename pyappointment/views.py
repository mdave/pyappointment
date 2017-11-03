from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from django.contrib import messages

import datetime as dt
import dateutil.parser
import uuid
import pytz

from pyappointment import settings, calendar_link
from pyappointment.email import send_attendee_email, send_organizer_email
from pyappointment.availability import MEETING_AVAIL
from pyappointment.forms import BookingForm

LOCALTZ = pytz.timezone(settings.TIME_ZONE)

def convert_iso8601(iso_str, tz):
    """
    Converts a date in ISO 8601 format to a datetime object, given a timezone tz.
    """
    return dateutil.parser.parse(iso_str).astimezone(tz)

def replace_time(date, time):
    return date.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)

def get_monday(date):
    return date - dt.timedelta(date.weekday())

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def check_available(booking_type, start, finish, events):
    # First, check we're within 2 hours of right now.
    now = dt.datetime.now(LOCALTZ)
    if start < now + dt.timedelta(hours=2):
        return False, "date in the past"

    # Don't let anyone book later than an upper limit
    upper_limit = settings.BOOKING_TYPES[booking_type]['future_limit']
    if upper_limit != 0 and start > now + dt.timedelta(days=upper_limit):
        return False, "date too far in the future"

    # Now check hard-coded availability times
    if not MEETING_AVAIL[start.weekday()].is_available(start.time(), finish.time()):
        return False, "non-available time"

    # Finally, check against events.
    for e in events:
        e_start = convert_iso8601(e['start'], LOCALTZ)
        e_end   = convert_iso8601(e['end'], LOCALTZ)

        if start < e_end and finish > e_start:
            return False, "conflicts with event: " + e['summary']

    return True, "available"

def generate_week_times(booking_type, date):
    # Calculate minimum and maximum times for the week's availability.
    min_time, max_time = dt.time.max, dt.time.min

    for avail in MEETING_AVAIL:
        t_min, t_max = avail.day_range()
        if t_min is None:
            continue

        min_time, max_time = min(min_time, t_min), max(max_time, t_max)

    # Populate a list of times that we've available.
    booking_info = settings.BOOKING_TYPES[booking_type]
    times        = []
    monday       = replace_time(get_monday(date), min_time)
    duration     = dt.timedelta(minutes=booking_info['duration'])
    delta        = dt.timedelta(minutes=booking_info['slots'])

    # Grab raw event data from calendar.
    events = calendar_link.get_events(monday, 7)

    one_available = False

    for d in perdelta(monday, replace_time(monday, max_time), delta):
        tmp = []
        for i in range(0,7):
            date = d + dt.timedelta(days=i)

            # First, check availability against specified limits.
            available, reason = check_available(booking_type, date, date + duration, events)

            if available:
                one_available = True

            tmp.append({
                'date': date,
                'available': available,
                'reason': reason
            })
        times.append(tmp)

    return { 'times': times, 'one_available': one_available }

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

    future_limit = settings.BOOKING_TYPES[booking_type]['future_limit']
    if future_limit != 0 and next_date > now + dt.timedelta(days=future_limit):
        next_date = None

    return render(request, 'week_view.html', {
        'times': generate_week_times(booking_type, date),
        'booking_type': booking_type,
        'booking_info': settings.BOOKING_TYPES[booking_type],
        'organizer': settings.ORGANIZER_NAME,
        'prev_date': prev_date,
        'next_date': next_date
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

    if not check_available(booking_type, start, finish, events)[0]:
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

                #handle.upsert_event(calendar_id=book_cal_id, event=event)
            except:
                return render(request, 'error.html', {
                    'error_title': 'Booking error',
                    'error_message': 'Something went wrong! Try again.',
                    'redirect': '/' + booking_type + '/' + date.strftime('%Y-%m-%d'),
                    'redirect_msg': '« Return to grid'
                })

            # Send reminder email.
            #send_appointment_email(start, finish, form.cleaned_data['name'], booking_info,
            #                       form.cleaned_data['notes'], event['event_id'],
            #                       form.cleaned_data['email'])
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
        'booking_types': settings.BOOKING_TYPES
    })
