# coding=utf-8
import argparse
from tkinter import *
from tkinter import ttk
import datetime
import julian
from sunclock import sun_rise_set, equ2hor
import pytz
from timezonefinder import TimezoneFinder

simu_pre_rise_hour = 1  # we simulate 1 hours before sunrise
simu_pre_rise_j = simu_pre_rise_hour / 24  # convert to Julian day
simu_aft_set_hour = 1  # simulate 1 hours after sunset, then jump to next day
simu_aft_set_j = simu_aft_set_hour / 24  # convert to Julian day
simu_tick_ms = 80  # microseconds of simulating tick
simu_tick_step_minutes = 15  # simulating minutes per tick
simu_tick_step_j = simu_tick_step_minutes / 1440  # Julian day per tick
simu_track_segments = 32  # segments of sun position curve, even number is better I guess
simu_sun_radius = 7 # radius of sun disc in the graph

# these 2 globals will be modified by tick
simu_curr_day = 0  # the day we are simulating
simu_curr_tick = 0 # the tick number at the day we are simulating

## ===== Canvas related sizes ======
width_canvas, height_canvas = 600, 320
pad_left, pad_right, pad_top, pad_bottom = 45, 20, 20, 35  # for X, Y labels and beauty
# should be OK for 30N < observer latitude < 50N
# NOTE: we set south azimuth is 0, positive to west, so we should -180 from equ2hor() result
azimuth_max, altitude_max = 135, 90
ratio_x = (width_canvas - pad_left - pad_right) / (azimuth_max * 2)
ratio_y = (height_canvas - pad_top - pad_bottom) / altitude_max

# ====== Masters =====
root = Tk()
root.title("Sunrise Simulator Alarm Clock")

# Frame
content = ttk.Frame(root)
content.grid(column=0, row=0)

# =============== Row 0: the big clock ==============
# clock
clock_var = StringVar()
clock_lbl = ttk.Label(content, relief="sunken", font=('times', 24, 'bold'),
        textvariable=clock_var, anchor="center")
clock_lbl.grid(column=0, row=0, columnspan=3, pady=8, padx=10, sticky=(W, E))

# =============== Row 1: sunrise, sunset and geolocation ==============
# sunrise time
sunrise_time_var = StringVar()
sunrise_time_lbl = ttk.Label(content, relief="sunken", font=('times', 16 , 'bold'),
        textvariable=sunrise_time_var, width=14, anchor="center")
sunrise_time_lbl.grid(column=0, row=1, sticky=W, padx=10)

# sunset time
sunset_time_var = StringVar()
sunset_time_lbl = ttk.Label(content, relief="sunken", font=('times', 16 , 'bold'),
        textvariable=sunset_time_var, width=14, anchor="center")
sunset_time_lbl.grid(column=1, row=1)

# geolocation
location_var = StringVar()
location_lbl = ttk.Label(content, relief="sunken", font=('times', 16 , 'bold'),
        textvariable=location_var, width=18, anchor="center")
location_lbl.grid(column=2, row=1, sticky=E, padx=10)

# ======= Row 2: the canvas ======
canvas = Canvas(content, borderwidth=1, relief="sunken", width=width_canvas, height=height_canvas)
canvas.grid(column=0, row=2, columnspan=3, padx=10, pady=8)

# ===== METHODS =====

# called every simu_tick_ms microseconds
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

# Julian.from_jd() return naive UTC datetime, this returns an aware datetime
def myjulian_from_jd(j, tz):
    return julian.from_jd(j).replace(tzinfo=datetime.timezone.utc).astimezone(tz)

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
    d_utc = d_local.astimezone(tz=datetime.timezone.utc)  # get an UTC one for the same datetime
    return {'tz': tz, 'd_local': d_local, 'd_utc': d_utc}

# map a horizontal (azimuthz, altitude) coordinates to our graph coordinates
def map_hor_to_rect(az, alt):
    x = (az + azimuth_max) * ratio_x + pad_left
    y = (90 - alt) * ratio_y +pad_top
    return (x, y)

# draw the sun position graph background
def graph_init():
    global id_sun

    # big box
    canvas.create_rectangle((pad_left, pad_top, width_canvas-pad_right, height_canvas-pad_bottom))

    # orientation labels along X
    c = map_hor_to_rect(0, 0)
    y = c[1] + 15  # move down a little bit
    canvas.create_text(c[0], y, text="S")  # South
    c = map_hor_to_rect(-90, 0)
    canvas.create_text(c[0], y, text="E")   # East
    c = map_hor_to_rect(90, 0)
    canvas.create_text(c[0], y, text="W")   # West

    # altitude labels along Y
    c = map_hor_to_rect(-azimuth_max, 0)
    x = c[0] - 15  # move left a little bit
    canvas.create_text(x, c[1], text="0")  # altitude 0 degree
    c = map_hor_to_rect(-azimuth_max, 45)
    canvas.create_text(x, c[1], text="45")  # altitude 45 degree
    c = map_hor_to_rect(-azimuth_max, 90)
    canvas.create_text(x, c[1], text="90")  # altitude 90 degree

    # draw sun tracks for every simulated days
    for i in range(simu_days):
        step = (sun[i]['j_set'] - sun[i]['j_rise']) / simu_track_segments
        track = []  # contains point coordinates like [x0, y0, x1, y1, x2, y2...]
        for j in range(simu_track_segments + 1):  # generate coordinates for every segment
            h = equ2hor(sun[i]['j_rise_ah'] + j*step, sun[i]['dec'], obsv_lat)
            c = map_hor_to_rect(h[0] - 180, h[1])
            track.append(c[0])
            track.append(c[1])
        canvas.create_line(track, smooth='true', dash=[2,4]) # make it smooth

    # draw the sun disc, since it is hidden we don't bother to calculate a position
    id_sun = canvas.create_oval(0, 0, 0, 0, fill='red', outline='yellow', state='hidden')

# update all the widgets, called by tick()
def update():
    global simu_curr_tick, simu_curr_day

    if simu_tick_step_j*simu_curr_tick > sun[simu_curr_day]['j_total']:  # this day is done
        simu_curr_day += 1
        if simu_curr_day == simu_days:  # last day is done, wrap to the first day
            simu_curr_day = 0
        simu_curr_tick = 0

    # current time in Julian day
    j = sun[simu_curr_day]['j_start'] + simu_curr_tick*simu_tick_step_j

    # update clock, sunrise and sunset time
    clock_var.set(myjulian_from_jd(j, noons['tz']).strftime('%c %Z'))
    if simu_curr_tick == 0:   # only need to be done at the beginning of the day
        sunrise_time_var.set(myjulian_from_jd(sun[simu_curr_day]['j_rise'], noons['tz'])
                .strftime('Sunrise: %H:%M'))
        sunset_time_var.set(myjulian_from_jd(sun[simu_curr_day]['j_set'], noons['tz'])
                .strftime('Sunset: %H:%M'))

    # update sun disc position
    ah = j - sun[simu_curr_day]['j_transit'] # current local Sun angle hour
    h = equ2hor(ah, sun[simu_curr_day]['dec'], obsv_lat)  # Sun horizontal coords
    if (h[1] < -0.83):  # hide the Sun if it is below the horizon
        canvas.itemconfigure(id_sun, state='hidden')
    else:
        c = map_hor_to_rect(h[0] - 180, h[1])  # we set south = 0
        x0, y0 = c[0] - simu_sun_radius, c[1] - simu_sun_radius
        x1, y1 = c[0] + simu_sun_radius, c[1] + simu_sun_radius
        canvas.coords(id_sun, x0, y0, x1, y1)  # move to the right position
        canvas.itemconfigure(id_sun, state='normal')  # show the Sun

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

# ====== main ======

simu_year, simu_month, simu_day = 2019, 12, 21  # simulation start date
simu_days = 7  # how many days to simulate
simu_day_interval = 30 # interval between each simulating day

obsv_lat, obsv_lon = 34.4, -119.8   # UCSB

if __name__ == '__main__':
    # get simulation parameters from command line arguments
    parser = argparse.ArgumentParser(description='Sunrise simulator alarm clock for latitude 24N - 55N.')
    parser.add_argument('-y', '--year', help='year of start date (1900-2100)', type=int, metavar='YEAR', choices=range(1900,2101), default=simu_year)
    parser.add_argument('-m', '--month', help='month of start date (1-12)', type=int, metavar='MONTH', choices=range(1, 13), default=simu_month)
    parser.add_argument('-d', '--day', help='day of start date (1-31)', type=int, metavar='DAY', choices=range(1, 32), default=simu_day)
    parser.add_argument('--days', help='number of days to simulate (1-365)', type=int, metavar='DAYS', choices=range(1, 366), default=simu_days)
    parser.add_argument('--int', help='number of days between each simulating days (1-365)', type=int, metavar='INT', choices=range(1, 366), default=simu_day_interval)
    parser.add_argument('--lat', help='observer latitude (24-55)', type=float, default=obsv_lat)
    parser.add_argument('--lon', help='observer longitude (-180.0-180.0)', type=float, default=obsv_lon)
    args = parser.parse_args()
    if args.lat < 24 or args.lat > 55:
        print("Sorry, we can only deal with observer latitude between 24N and 55N")
        exit(1)
    if args.lon < -180 or args.lon > 180:
        print("Sorry, observer longitude must be between -180 and 180")
        exit(1)
    simu_year, simu_month, simu_day = args.year, args.month, args.day
    simu_days, simu_day_interval = args.days, args.int
    obsv_lat, obsv_lon = args.lat, args.lon

    # get noon of the simulation start day and timezone
    noons = get_noons(simu_year, simu_month, simu_day, obsv_lat, obsv_lon)
    # calcuate number of days since Jan 1st, 2000 12:00 UTC
    n = round(julian.to_jd(noons['d_utc']) - julian.to_jd(datetime.datetime(2000, 1, 1, hour=12)))
    sun = []
    for i in range(simu_days):   # calculate sunrise/sunset data for each simulating day
        s = sun_rise_set(n + i*simu_day_interval, obsv_lon, obsv_lat)
        sun.append({
            'j_transit': s[0],  # Sun transit time in Julian day
            'j_rise': s[0] - s[1],  # sunrise time in Julian day
            'j_set': s[0] + s[1],   # sunset time in Julian day
            'j_start': s[0] - s[1] - simu_pre_rise_j,  # simulate start time in Julian day
            'j_stop': s[0] + s[1] + simu_aft_set_j, # simulate stop time in Julian day
            'j_total': 2 * s[1] + simu_pre_rise_j + simu_aft_set_j,  # time to simulate at this day
            'j_rise_ah': - s[1],  # local sunrise Angle Hour in fraction of a Julian day
            'dec': s[2],  # declination of the Sun
            })

    location_var.set("%s° N, %s° E" % (round(obsv_lat, 2), round(obsv_lon, 2)))
    graph_init()
    tick()
    root.mainloop()

