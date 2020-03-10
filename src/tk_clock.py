from tkinter import *
from tkinter import ttk
import datetime
import julian
from sunclock import sun_rise_set, equ2hor
import pytz
from timezonefinder import TimezoneFinder

width = 600
height = 400

root = Tk()
root.title("Sunrise Simulator Alarm Clock")
#root.geometry("%dx%d+%d+%d" % (width, height, x, y))
#root.resizable(0, 0)
#root.config(bg="light blue")
#frame = ttk.Frame(content, borderwidth=5, relief="sunken", width=width, height=height)
#clock = Label(Mid, font=('times', 20 , 'bold'), fg="green", bg="light blue")

# Frame
content = ttk.Frame(root)
content.grid(column=0, row=0)

# =============== Row 0 ==============
# clock
clock_var = StringVar()
clock_lbl = ttk.Label(content, textvariable=clock_var)
clock_lbl.grid(column=0, row=0, columnspan=3)

# geolocation
location_var = StringVar()
location_lbl = ttk.Label(content, textvariable=location_var)
location_lbl.grid(column=3, row=0)

# show Day/Night indication
day_night_var = StringVar()
day_night_lbl = ttk.Label(content, textvariable=day_night_var)
day_night_lbl.grid(column=4, row=0)

# =============== Row 1 ==============
# "Next Sunrise: " label
next_rise_lbl = ttk.Label(content, text="Next Sunrise: ")
next_rise_lbl.grid(column=0, row=1)

# Today/Tomorrow indication
today_tomorrow_var = StringVar()
today_tomorrow_lbl = ttk.Label(content, textvariable=today_tomorrow_var)
today_tomorrow_lbl.grid(column=1, row=1)

# show next sunrise time
next_sunrise_var = StringVar()
next_sunrise_lbl = ttk.Label(content, textvariable=next_sunrise_var)
next_sunrise_lbl.grid(column=2, row=1)

# next sunrise "Countdown" label
countdown1_lbl = ttk.Label(content, text="Countdown: ")
countdown1_lbl.grid(column=3, row=1)

# next sunrise countdown
sunrise_countdown_var = StringVar()
sunrise_countdown_lbl = ttk.Label(content, textvariable=sunrise_countdown_var)
sunrise_countdown_lbl.grid(column=4, row=1)

# =============== Row 2 ==============
# "Next Sunset: " label
next_set_lbl = ttk.Label(content, text="Next Sunset: ")
next_set_lbl.grid(column=0, row=2)

# Today/Tomorrow indication
today_tomorrow_set_var = StringVar()
today_tomorrow_set_lbl = ttk.Label(content, textvariable=today_tomorrow_set_var)
today_tomorrow_set_lbl.grid(column=1, row=2)

# show next sunset time
next_sunset_var = StringVar()
next_sunset_lbl = ttk.Label(content, textvariable=next_sunset_var)
next_sunset_lbl.grid(column=2, row=2)

# next sunset "Countdown" label
countdown2_lbl = ttk.Label(content, text="Countdown: ")
countdown2_lbl.grid(column=3, row=2)

# next sunset countdown
sunset_countdown_var = StringVar()
sunset_countdown_lbl = ttk.Label(content, textvariable=sunset_countdown_var)
sunset_countdown_lbl.grid(column=4, row=2)

# =============== Row 3 ==============
canvas = Canvas(content)
canvas.grid(column=0, row=3)
canvas.create_line((0,0,100,100))

# ============== METHODS ==================

def tick():
    update()
    clock_lbl.after(simu_tick_ms, tick)

# Calculate standard timezone from longitude, return a timezone.timezone object
def get_std_timezone(lng):
    hours = lng // 15
    if ((lng % 15) > 7.5): hours = hours + 1
    return datetime.timezone(datetime.timedelta(hours=hours))

# Julian.to_jd() ignores timezone, this is for timezone aware datetime
def myjulian_to_jd(d_with_tz):
    return julian.to_jd(d_with_tz.astimezone(datetime.timezone.utc))

# Julian.from_jd() return naive UTC datetime
def myjulian_from_jd(j, tz):
    return julian.from_jd(j).replace(tzinfo=datetime.timezone.utc).astimezone(tz)

# time interval as string like 'HH:MM' between 2 Julian days
def myjulian_interval(j1, j2):
    d = julian.from_jd(j2) - julian.from_jd(j1)  # timedelta object
    h = d.total_seconds() // 3600
    m = (d.total_seconds() % 3600) / 60
    return "%d:%d" % (h, m)

# Get timezone, datetime objects of the noon of the specified local date
# in local timezone and in UTC
def get_noons(year, month, day, lat, lon):
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lng=lon, lat=lat)  # show the geolocation
    if (tz_str != None):   # find a location in TimezoneFinder's database
        tz = pytz.timezone(tz_str)
        if (tz != None):   # everything is OK
            # NOTE: pytz's tz cannot be used in datetime.datetime() constructor
            d_local = tz.localize(datetime.datetime(year, month, day, hour=12))
        else:  # somehow pytz does not has this location
            tz = get_std_timezone(lon)  # have to use standard time zone
            d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
    else:  # this geolocation is not in TimezoneFinder's database
        tz = get_std_timezone(lon)  # have to use a standard time zone
        d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
    d_utc = d_local.astimezone(tz=datetime.timezone.utc)  # 转换成 UTC 时间
    return {'tz': tz, 'd_local': d_local, 'd_utc': d_utc}

# update all the widgets
def update():
    global simu_curr_tick, simu_curr_day
    if simu_tick_step_j*simu_curr_tick > sun[simu_curr_day]['j_total']:
        simu_curr_day += 1
        if simu_curr_day == simulate_days:
            simu_curr_day = 0
        simu_curr_tick = 0

    # current Julian day
    j = sun[simu_curr_day]['j_start'] + simu_curr_tick*simu_tick_step_j

    clock_var.set(myjulian_from_jd(j, noons['tz']).strftime('%c %Z'))
    if j < sun[simu_curr_day]['j_rise'] or j > sun[simu_curr_day]['j_set']:
        day_night_var.set('Night')
    else:
        day_night_var.set('Day')

    if j < sun[simu_curr_day]['j_rise']:  # before today's sunrise
        today_tomorrow_var.set('Today')
        next_sunrise_var.set(myjulian_from_jd(sun[simu_curr_day]['j_rise'], noons['tz']).
                strftime('%H:%M'))
        sunrise_countdown_var.set(myjulian_interval(j, sun[simu_curr_day]['j_rise']))
        today_tomorrow_set_var.set('Today')
        next_sunset_var.set(myjulian_from_jd(sun[simu_curr_day]['j_set'], noons['tz']).
                strftime('%H:%M'))
        sunset_countdown_var.set(myjulian_interval(j, sun[simu_curr_day]['j_set']))
    else:  # after today's sunrise
        today_tomorrow_var.set('Tomorrow')
        next_sunrise_var.set(myjulian_from_jd(sun[simu_curr_day + 1]['j_rise'], noons['tz']).
                strftime('%H:%M'))
        sunrise_countdown_var.set(myjulian_interval(j, sun[simu_curr_day + 1]['j_rise']))
        if j < sun[simu_curr_day]['j_set']:  # still before today's sunset
            today_tomorrow_set_var.set('Today')
            next_sunset_var.set(myjulian_from_jd(sun[simu_curr_day]['j_set'], noons['tz']).
                    strftime('%H:%M'))
            sunset_countdown_var.set(myjulian_interval(j, sun[simu_curr_day]['j_set']))
        else: # after today's sunset
            today_tomorrow_set_var.set('Tomorrow')
            next_sunset_var.set(myjulian_from_jd(sun[simu_curr_day + 1]['j_set'], noons['tz']).
                    strftime('%H:%M'))
            sunset_countdown_var.set(myjulian_interval(j, sun[simu_curr_day + 1]['j_set']))

    simu_curr_tick += 1

# XXX imported from sunclock.py, just for reference
# Calculate, result as a tuple:
#   solar transit time, in Julian day with fraction
#   sunset hour angle, in fraction of Julian day
#   declination of the Sun at the date, in radians
# Input:
#   n: number of days since Jan 1st, 2000 12:00
#   lo: longitude of the observer on the Earth, west is negative, in degree
#   la: latitude of the observer on the Earth, north is positive, in degree
#def sun_rise_set(n, lo, la):

# XXX imported from sunclock.py, just for reference
# Convert Equatorial coordinate to horizontal
#   ha: hour angle, in fraction of a Julian day
#   dec: declination, in radians
#   la: latitude of the observer on the Earth, in degree
# Return a tuple with 2 elements:
#   0: azimuth, measured from the north, positive to east, in degree
#   1: altitude, in degree
# def equ2hor(ha, dec, la):

# ============= main =============
 
simu_pre_rise_hour = 2  # we simulate 2 hours pre sunrise
simu_pre_rise_j = simu_pre_rise_hour / 24  # in Julian day
simu_aft_set_hour = 2  # simulate 2 hours after sunset, then jump to next sunrise - pre hour
simu_aft_set_j = simu_aft_set_hour / 24  # in Julian day
simu_tick_ms = 200  # microseconds of simulating tick
simu_tick_step_minutes = 5  # simulating minutes per tick
simu_tick_step_j = simu_tick_step_minutes / 1440  # Julian day per tick

simu_curr_day = 0  # the day we are simulating
simu_curr_tick = 0 # the tick number at the day we are simulating

year, month, day = 2020, 3, 9  # simulation start date
simulate_days = 3
lat, lon = 51, 0.1   # London
lat, lon = 39, 170    #
lat, lon = 39, 179    #
lat, lon = 39, 116    # Beijing
lat, lon = 34, -118   # Los Angles

if __name__ == '__main__':
    noons = get_noons(year, month, day, lat, lon)  # noon of the simulation start day
    print(noons)
    # calcuate number of days since Jan 1st, 2000 12:00 UTC
    n = round(julian.to_jd(noons['d_utc']) - julian.to_jd(datetime.datetime(2000, 1, 1, hour=12)))
    sun = []
    for i in range(simulate_days + 1):   # calculate sunrise/sunset data
        s = sun_rise_set(n + i, lon, lat)
        print("j_transit: ", s[0], myjulian_from_jd(s[0], noons['tz']).strftime('%c %Z'), flush=True)
        sun.append({
            'j_rise': s[0] - s[1],  # sunrise time in Julian day
            'j_set': s[0] + s[1],   # sunset time in Julian day
            'j_start': s[0] - s[1] - simu_pre_rise_j,  # simulate start time in Julian day
            'j_stop': s[0] + s[1] + simu_aft_set_j, # simulate stop time in Julian day
            'j_total': 2 * s[1] + simu_pre_rise_j + simu_aft_set_j  # time to simulate at this day
            })

    location_var.set("Lat: %s, Lon: %s" % (lat, lon))
    tick()
    root.mainloop()

