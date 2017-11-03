import pycronofy
import pytz
import os
import datetime as dt

from pyappointment.settings import CRONOFY_ACCESS_TOKEN, CAL_NAMES, CAL_CREATE_BOOKING

def utc_range(today, delta):
    # Get current day for timezone.
    mon = today
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

def filter_ids(cal_ids):
    # Figure out which calendar IDs we need to check.
    return [
        c['calendar_id'] for c in cal_ids if
        c['calendar_name'].lower() in map(str.lower, CAL_NAMES)
    ]

def get_events(date, delta, handle=None, cal_ids=None):
    # Create Cronofy client object.
    if handle is None:
        handle = connect_calendar()
    if cal_ids is None:
        cal_ids = filter_ids(handle.list_calendars())

    # Look up items in delta's events
    start, finish = utc_range(date, dt.timedelta(delta))
    return handle.read_events(
        calendar_ids=cal_ids, from_date=start, to_date=finish).all()
