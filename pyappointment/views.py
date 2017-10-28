from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404

import datetime as dt
import dateutil.parser
import pytz

from pyappointment import calendar_link
from pyappointment.availability import MEETING_AVAIL

LOCALTZ = pytz.timezone('Europe/London')

def convert_iso8601(iso_str, tz):
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

def check_available(start, finish, events):
    # First, check we're within 2 hours of right now.
    now = dt.datetime.now(LOCALTZ)
    if finish < now - dt.timedelta(hours=2):
        return False, "earlier than threshold"

    # Don't let anyone book later than 3 weeks ahead
    if start > now + dt.timedelta(days=21):
        return False, "later than threshold"

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

def generate_week_times(date):
    # Calculate minimum and maximum times for the week's availability.
    min_time, max_time = dt.time.max, dt.time.min

    for avail in MEETING_AVAIL:
        t_min, t_max = avail.day_range()
        if t_min is None:
            continue

        min_time, max_time = min(min_time, t_min), max(max_time, t_max)

    # Populate a list of times that we've available.
    times  = []
    monday = replace_time(get_monday(date), min_time)
    delta  = dt.timedelta(minutes=30)

    # Grab raw event data from calendar.
    events = calendar_link.get_events(monday, 7)

    for d in perdelta(monday, replace_time(monday, max_time), dt.timedelta(minutes=30)):
        tmp = []
        for i in range(0,7):
            date = d + dt.timedelta(days=i)

            # First, check availability against specified limits.
            slot_begin = date
            slot_end = date + delta
            available, reason = check_available(date, date + delta, events)
            tmp.append({
                'date': date,
                'available': available,
                'reason': reason
            })
        times.append(tmp)

    return times

def view_week(request, year, month, day):
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
    if next_date > now + dt.timedelta(days=21):
        next_date = None

    return render(request, 'week_view.html', {
        'times': generate_week_times(date),
        'prev_date': prev_date,
        'next_date': next_date
    })

def booking_form(request, year, month, day, hour, minute):
    return "kek"

def index(request):
    now = dt.datetime.now(LOCALTZ)
    return view_week(request, now.year, now.month, now.day)
