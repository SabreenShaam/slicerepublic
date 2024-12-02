from datetime import datetime
from pytz import timezone
import pytz
import time
import math


def utcnow():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def utcnow_plus(timedelta):
    return utcnow() + timedelta


def utc_today_midnight_plus(timedelta):
    dt = utcnow() + timedelta
    midnight = datetime(dt.year, dt.month, dt.day)
    return midnight


def make_utc(date):
    return date.replace(tzinfo=pytz.utc)


def utcnow_millis():
    return int(round(time.time() * 1000))


def get_local_datetime(utc_datetime, local_tz):
    tz = timezone(local_tz)
    local_datetime = tz.normalize(utc_datetime)
    return local_datetime


def time_diff(time_1, time_2):
    dt_1 = datetime(1970, 1, 1, time_1.hour, time_1.minute, time_2.second)
    dt_2 = datetime(1970, 1, 1, time_2.hour, time_2.minute, time_2.second)
    return dt_1 - dt_2


def get_local_diff_in_minute(date_1, date_2):
    # date_1 timezone not aware
    tz = timezone("Europe/London")
    local_date_1 = tz.localize(date_1)
    timestamp_1 = time.mktime(local_date_1.timetuple())

    # date_2 timezone aware
    local_date_2 = get_local_datetime(date_2, "Europe/London")
    timestamp_2 = time.mktime(local_date_2.timetuple())
    diff_minutes = math.ceil((timestamp_1 - timestamp_2) / 60)
    return diff_minutes


def is_within_date_range(from_date, to_date, date):
    if from_date <= date <= to_date:
        return True
    return False


def convert_time_to_twelve_hour_clock(hour, minute):
    d = datetime.strptime((hour + ":" + minute), "%H:%M")
    return d.strftime("%I:%M %p")


def localize(dt):
    local_dt = timezone("Europe/London").localize(dt)
    return local_dt
