import argparse
import time
import julian
import pytz
from datetime import timedelta
import datetime
from sunclock import sun_rise_set, equ2hor
from timezonefinder import TimezoneFinder

year, month, day = 2020, 3, 9
lat, lon = 51, 0.1   # London
lat, lon = 39, 170    # 
lat, lon = 39, 179    # 
lat, lon = 34.4, -119.8   # UCSB

parser = argparse.ArgumentParser(description='Sunrise simulator alarm clock.')
parser.add_argument('-y', '--year', help='year of date', type=int, metavar='YEAR', choices=range(1900,2101), default=year)
parser.add_argument('-m', '--month', help='month of date (1-12)', type=int, metavar='MONTH', choices=range(1, 13), default=month)
parser.add_argument('-d', '--day', help='day of date (1-31)', type=int, metavar='DAY', choices=range(1, 32), default=day)
parser.add_argument('--lat', help='observer latitude (-65.7-65.7)', type=float, default=lat)
parser.add_argument('--lon', help='observer longitude (-180.0-180.0)', type=float, default=lon)
args = parser.parse_args()
if args.lat < -65.7 or args.lat > 65.7:
    print("Sorry, please chose latitude between -65.7 and 65.7.")
    exit(1)
if args.lon < -180 or args.lon > 180:
    print("Sorry, please chose longitude between -180 and 180.")
    exit(1)
year, month, day = args.year, args.month, args.day
lat, lon = args.lat, args.lon

# Calculate timezone from longitude, return a timezone.timezone object
def get_timezone(lon):
    hours = lon // 15
    if ((lon % 15) > 7.5): hours = hours + 1
    return datetime.timezone(timedelta(hours=hours))  # standard timezone

# first try to find the timezone from observer longtitude
tf = TimezoneFinder()
tz_str = tf.timezone_at(lat=lat, lng=lon)
if (tz_str == None):  # not found
    tz = get_timezone(lon)  # use standard timezone
    d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
else:  # found
    tz = pytz.timezone(tz_str)
    if (tz == None):  # but not in pytz
        tz = get_timezone(lon)   # use standard timezone
        d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
    else:  # remember normally pytz timezone cannot be used in datetime constructor
        d_local = tz.localize(datetime.datetime(year, month, day, hour=12))

# calculate offset of our timezone to UTC
d_utc = d_local.astimezone(tz=datetime.timezone.utc)
tz_h = d_local.tzinfo.utcoffset(d_local) / timedelta(hours=1)

n = round(julian.to_jd(d_utc) - 2451545)  # number of days since Jan 1st, 2000 12:00
sun_rs = sun_rise_set(n, lon, lat)  # do the math
sun_rs_next = sun_rise_set(n + 1, lon, lat)  # do the math for the next day

# sunrise time in Julian date, we add an timezone correction because julian.from_jd() ignores timezone
j_rise = sun_rs[0] - sun_rs[1] + tz_h/24

d_rise = julian.from_jd(j_rise)  # sunrise time in local dateime date (because we have added timezone correction)
print(d_rise.strftime("\n     Sunrise today: %m/%d/%Y %H:%M:%S"))
j_rise_next = sun_rs_next[0] - sun_rs_next[1] + tz_h/24  # next day sunrise in Julian date, with timezone correction
d_rise_next = julian.from_jd(j_rise_next)  # next day sunrise time in local date
print(d_rise_next.strftime("  Sunrise tomorrow: %m/%d/%Y %H:%M:%S"))
j_set = sun_rs[0] + sun_rs[1] + tz_h/24

print('\033[?25l')  # hide the cursor

# simulate a single day from 2 hours before sunrise to 2 hour after sunset
# tick every 0.04 seconds, and every tick is equivalent to 1 minutes
# so it is about 1500x fast-forward
# roll back when finished, until Control-C is pressed
j_start = j_rise - 2/24  # start time
j_stop = j_set + 2/24  # stop time
j_minute = 1/1440  # a minute in Julian day
tick_time = 0.04
i = 0
while True:
    try:
        j_now = j_start + i * j_minute
        if (j_now > j_stop):
            j_now = j_start
            i = 0
        i = i + 1
        if (j_now > j_rise):  # today's sunrise has passed, show next sunrise
            d_this_rise = d_rise_next
        else:
            d_this_rise = d_rise
        d_now = julian.from_jd(j_now)
        if (j_now < j_rise or j_now > j_set):   # no special graphic attribute in night
            print('\033[0m', end="", flush=True)  # clear graphic mode attribute
        else:
            print('\033[7m', end="", flush=True)  # set reverse video when sun is above horizon
        print(d_now.strftime("      Current time: %m/%d/%Y %H:%M:%S"), "   ")
        print(d_this_rise.strftime("      Next sunrise: %m/%d/%Y %H:%M:%S"), "   ")
        print(" Sunrise countdown:", (d_this_rise - d_now) // 1, "       ")
        print('\033[3A', end="", flush=True)  # move cursor up 3 rows
        time.sleep(tick_time)
    except:  # Control-C pressed, recover the display
        print('\033[0m', end="", flush=True)  # clear graphic mode attribute
        print('\033[3B', end="", flush=True)  # move cursor down 3 rows
        print('\033[?25h')  # show the cursor
        exit(0)

