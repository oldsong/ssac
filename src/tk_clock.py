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
today_tomorrow_var = StringVar()
today_tomorrow_lbl = ttk.Label(content, textvariable=today_tomorrow_var)
today_tomorrow_lbl.grid(column=1, row=2)

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
def tick(tz):
    now_str = datetime.datetime.now(tz).strftime('%c %Z')
    clock_var.set(datetime.datetime.now(tz).strftime('%c %Z'))
    clock_lbl.after(200, tick, tz)

# Calculate standard timezone from longitude, return a timezone.timezone object
def get_std_timezone(lng):
    hours = lng // 15
    if ((lng % 15) > 7.5): hours = hours + 1
    return datetime.timezone(datetime.timedelta(hours=hours))

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

# ============= main =============
 
if __name__ == '__main__':
    year, month, day = 2020, 3, 9  # simulation start date
    simulate_days = 3
    lat, lon = 51, 0.1   # London
    lat, lon = 39, 170    # 
    lat, lon = 39, 179    # 
    lat, lon = 39, 116    # Beijing
    lat, lon = 34, -118   # Los Angles

    noons = get_noons(year, month, day, lat, lon)  # noon of the simulation start day
    # calcuate number of days since Jan 1st, 2000 12:00 UTC
    n = round(julian.to_jd(noons['d_utc']) - julian.to_jd(datetime.datetime(year, month, day, hour=12)))
    sun = []
    for i in range(simulate_days + 1):
        sun.append(sun_rise_set(n + i, lon, lat))
    location_var.set("Lat: %s, Lon: %s" % (lat, lon))
    tick(noons['tz'])
    root.mainloop()
