from math import sin, cos, tan, asin, acos, atan2, pi, radians, degrees
import math
import julian
from datetime import datetime, timedelta
import pytz

# Return approximation of local mean solar time noon, expressed as a J2000 Julian day
# (number of days since Jan 1st, 2000 12:00) with day fration, leap seconds considered
# https://en.wikipedia.org/wiki/Epoch_(astronomy)#Julian_Dates_and_J2000
#   n: number of days since Jan 1st, 2000 12:00
#   lo: longitude west (west is negative, east is positive) of the observer on the Earth, in degree
def local_mean_solar_noon(n, lo):
    return (n + 0.0008 - lo / 360.0)

# Return the Earth's solar oribit mean anomaly at time specified , in degree
# https://en.wikipedia.org/wiki/Mean_anomaly
#   j: time, J2000 Julian day with fraction
def solar_mean_anomaly(j):
    return (357.5291 + 0.98560028 * j) % 360

# Return the Earth's equation of the center from mean anomaly, truncated at 3rd term, in degree
# https://en.wikipedia.org/wiki/Equation_of_the_center
#   m: current solar mean anomaly of the Earth
def equation_of_the_center(m):
    m = radians(m)
    return (1.9148*sin(m) + 0.02*sin(2*m) + 0.0003*sin(3*m))

# Calculate solar ecliptic longitude from mean anomaly and eqution of the center, in degree
# https://en.wikipedia.org/wiki/Ecliptic_coordinate_system#Spherical_coordinates
#   m: current solar mean anomaly of the Earth
#   c: current equation of the center of the Earth
def solar_ecliptic_longitude(m, c):
    return (m + c + 180 + 102.9372) % 360

# Calculate the time of local true solar transit (solar noon) from mean solar noon, in Julian date
# Actually this is the equation of time correction
# https://en.wikipedia.org/wiki/Equation_of_time
# https://en.wikipedia.org/wiki/Solar_noon
#   j: time of mean solar noon, expressed as J2000 Julian day with day fration
#   m: earth solar mean anomaly at the mean solar noon specified as j, in degree
#   l: solar ecliptic longitude at the mean solar noon specified as j, in degree
def local_true_solar_transit(j, m, l):
    return (2451545.0 + j + 0.0053*sin(radians(m)) - 0.0069*sin(2*radians(l)))

# Calculate the declination of the Sun from its ecliptic longitude, return as sine of the declination
#   l: solar ecliptic longitude, in degree
def sin_declination_of_sun(l):
    return (sin(radians(l)) * sin(radians(23.44)))

# Calculate the hour angle of sunrise or sunset, select the positive value, in fraction of Julian day
# Atmospheric refraction and angle subtended by solar disc correction included
#   d: sine of the declination of the Sun
#   la: latitude of the observer on the Earth, north is positive, in degree
def julian_hour_angle(d, la):
    da = asin(d)  # declination in radians
    la_r = radians(la)  # observer latitude in radians
    # cosine of the hour angel of sunrise or sunset
    cha = (sin(radians(-0.83)) - sin(la_r) * d) / (cos(la_r) * cos(da))
    return abs(acos(cha) / (2*math.pi))

# Calculate:
#   solar transit time, in Julian day with fraction
#   sunset hour angle, in fraction of Julian day
#   declination of the Sun at the date, in radians
# Input:
#   n: number of days since Jan 1st, 2000 12:00
#   lo: longitude west (west is negative) of the observer on the Earth, in degree
#   la: latitude of the observer on the Earth, north is positive, in degree
def sun_rise_set(n, lo, la):
    j = local_mean_solar_noon(n, lo)  # local mean solar noon, in J2000 Julian day
    #print("local mean solar noon in J2000: ", j)
    m = solar_mean_anomaly(j)  # solar mean anomaly at local mean solar noon
    c = equation_of_the_center(m)  # equation of the center at the local mean solar noon
    l = solar_ecliptic_longitude(m, c)  # solar ecliptic longitude
    jt = local_true_solar_transit(j, m, l) # solar transit in Julian day
    d = sin_declination_of_sun(l)  # sine of the declination of the Sun
    hour_angle_j = julian_hour_angle(d, la)  # time interval of sun rise to transit
    ha_r = hour_angle_j * math.pi * 2  # hour angle of sunset in radians
    la_r = radians(la)  # observer latutude in radians
    dec = asin(d)  # Sun declination in radians
    A_rise = atan2(sin(-ha_r), cos(-ha_r) * sin(la_r) - tan(dec) * cos(la_r))
    A_set = atan2(sin(ha_r), cos(ha_r) * sin(la_r) - tan(dec) * cos(la_r))
    #return jt - hour_angle_j, jt + hour_angle_j, degrees(A_rise), degrees(A_set)
    return jt, hour_angle_j, dec

# Convert Equatorial coordinate to horizontal
#   ha: hour angle, in fraction of a Julian day
#   dec: declination, in radians
#   la: latitude of the observer on the Earth, in degree
# Return a tuple with 2 elements:
#   0: azimuth, measured from the north, positive to east, in degree
#   1: altitude, in degree
def equ2hor(ha, dec, la):
    ha_r = ha * math.pi * 2  # hour angle in radians
    la_r = radians(la) # observer latitude in radians
    A = atan2(sin(ha_r), cos(ha_r) * sin(la_r) - tan(dec) * cos(la_r))
    a = asin( sin(la_r) * sin(dec) + cos(la_r) * cos(dec) * cos(ha_r))
    return round(degrees(A)+180, 2), round(degrees(a), 2)

# Print now in string and Julian day for city specified
def print_now(city):
    tz_city = pytz.timezone(city)
    d_city = datetime.now(tz_city)
    jd_city = julian.to_jd(d_city, fmt='jd')
    print(city, ": Julian day = ", jd_city, ", ", d_city)

#print_now("Europe/London")
#print_now("America/Los_Angeles")
#print_now("Asia/Shanghai")

# print sunrise/sunset date time:
#   y, m, d: year, month (1-12), day(1-31) of the start day
#   days: number of days to print
#   la, lo: observer latitude/longitude
#   tz_h: timezone correction, in hours
def print_sunrise(y, m, d, days, la, lo, tz_h):
    for i in range(days):
        j = math.floor(julian.to_jd(datetime(y, m, d))) - 2451545 + i
        #sun_rs = sun_rise_set(j, 116+25.0/60, 39.0+55.0/60)  # location of Beijing
        #sun_rs = sun_rise_set(j, 116, 39)  # location of Beijing
        sun_rs = sun_rise_set(j, lo, la)
        dt_rise = julian.from_jd(sun_rs[0] + tz_h/24 - sun_rs[1])  # sunrise datetime
        dt_set = julian.from_jd(sun_rs[0] + tz_h/24 + sun_rs[1])  # sunset datetime
        h_r = equ2hor(-sun_rs[1], sun_rs[2], la) # sunrise horizontal coordinates
        h_s = equ2hor(sun_rs[1], sun_rs[2], la) # sunset horizontal coordinates
        print(dt_rise, ",", dt_set, ",", h_r, h_s)

#print_sunrise(2020, 8, 20, 60, 39, 116, 8)

# print horizontal coordinates of the Sun for a day from sunrise to sunset
#   y, m, d: year, month (1-12), day(1-31) of the start day
#   slices: how many points to print except the sunrise and sunset
#   la, lo: observer latitude/longitude
#   tz_h: timezone correction, in hours
def print_sun_coord(y, m, d, slices, la, lo, tz_h):
    n = math.floor(julian.to_jd(datetime(y, m, d))) - 2451545
    sun_rs = sun_rise_set(n, lo, la)
    dt_rise = julian.from_jd(sun_rs[0] + tz_h/24 - sun_rs[1])  # sunrise datetime
    dt_set = julian.from_jd(sun_rs[0] + tz_h/24 + sun_rs[1])  # sunset datetime
    slices = math.floor(slices)
    if (slices <= 0):
        slices = 1
    step = 2 * sun_rs[1] / (slices + 1)
    for i in range(slices + 2):
        j = sun_rs[0] + tz_h/24 - sun_rs[1] + i * step  # time as Julian day
        h = equ2hor(i * step - sun_rs[1], sun_rs[2], la)  # horizontal coordinates
        print(julian.from_jd(j), h)

# print the Sun positions observed from Beijing (39N, 116E) at Jun 22, 2020
# 242 time points (including sunrise and sunset)
#print_sun_coord(2020, 6, 22, 240, 39, 116, 8)

