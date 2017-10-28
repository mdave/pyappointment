import pycronofy
import pytz
import os
import datetime as dt

CAL_NAMES = [
    "Dave", "Dave's Work", "Meetings"
]

CRONOFY_ACCESS_TOKEN = os.environ.get('CRONOFY_ACCESS_TOKEN')

def utc_range(today, delta):
    # Get current day for timezone.
    mon = today - dt.timedelta(today.weekday())
    sun = mon + delta
    tz = today.tzinfo

    # Get midnight in correct timezone
    midnight   = tz.localize(dt.datetime.combine(mon, dt.time(0, 0)),
                             is_dst=None)
    midnight_p = tz.localize(dt.datetime.combine(sun, dt.time(0, 0)),
                             is_dst=None)
    
    return midnight.astimezone(pytz.utc), midnight_p.astimezone(pytz.utc), 

def connect_calendar():
    return pycronofy.Client(access_token=CRONOFY_ACCESS_TOKEN)

def calendar_ids(cronofy):
    # Figure out which calendar IDs we need to check.
    return [
        c['calendar_id'] for c in cronofy.list_calendars() if
        c['calendar_name'].lower() in map(str.lower, CAL_NAMES)
    ]

def get_events(date, delta):
    # Create Cronofy client object.
    handle = connect_calendar()
    cal_ids = calendar_ids(handle)

    # Look up items in week's events
    start, finish = utc_range(date, dt.timedelta(delta))
    return handle.read_events(
        calendar_ids=cal_ids, from_date=start, to_date=finish).all()
