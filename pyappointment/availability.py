import datetime as dt
import pytz

class Availability():
    """
    A class detailing availability times.
    """

    time_ranges = []

    def __init__(self, times):
        self.time_ranges = [ [ dt.datetime.combine(dt.date.today(), t) for t in tt ] for tt in times ] 

    def is_available(self, start_time, finish_time):
        # Convert to datetime so that we can use timedelta
        start = dt.datetime.combine(dt.date.today(), start_time)
        finish = dt.datetime.combine(dt.date.today(), finish_time)

        for rs, rf in self.time_ranges:
            if rs <= start and finish <= rf:
                return True
        return False

    def day_range(self):
        """
        Returns extremes of the availability ranges
        """
        if self.time_ranges == []:
            return None, None
        return min(self.time_ranges, key=lambda t: t[0])[0].time(), \
               max(self.time_ranges, key=lambda t: t[1])[1].time()

MEETING_AVAIL = [
    Availability([
        (dt.time(9, 30), dt.time(12, 30)),
        (dt.time(13, 30), dt.time(16, 30))
    ]),
    Availability([
        (dt.time(9, 30), dt.time(12, 30)),
        (dt.time(13, 30), dt.time(16, 30))
    ]),
    Availability([
        (dt.time(9, 30), dt.time(12, 30)),
        (dt.time(13, 30), dt.time(16, 30))
    ]),
    Availability([
        (dt.time(9, 30), dt.time(12, 30)),
        (dt.time(13, 30), dt.time(16, 30))
    ]),
    Availability([
        (dt.time(9, 30), dt.time(12, 30)),
        (dt.time(13, 30), dt.time(16, 30))
    ]),
    Availability([]),
    Availability([])
]

