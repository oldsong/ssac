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
#   the sunrise/sunset time, in Julian day with fraction
#   the sunrise/sunset azimuth, measured from the south, west is positive
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
    return jt - hour_angle_j, jt + hour_angle_j, degrees(A_rise), degrees(A_set)

# Print now in string and Julian day for city specified
def print_now(city):
    tz_city = pytz.timezone(city)
    d_city = datetime.now(tz_city)
    jd_city = julian.to_jd(d_city, fmt='jd')
    print(city, ": Julian day = ", jd_city, ", ", d_city)

print_now("Europe/London")
print_now("America/Los_Angeles")
print_now("Asia/Shanghai")

for i in range(60):
    #j = 2458913 - 2451545 + i
    j = math.floor(julian.to_jd(datetime(2020, 8, 15))) - 2451545 + i
    #sun_rs = sun_rise_set(j, 116+25.0/60, 39.0+55.0/60)  # location of Beijing
    sun_rs = sun_rise_set(j, 116, 39)  # location of Beijing
    #print(sun_rs)
    dt_rise = julian.from_jd(sun_rs[0] + 8.0/24)  # sunrise datetime
    dt_set = julian.from_jd(sun_rs[1] + 8.0/24)  # sunset datetime
    ratio_day = round((dt_set - dt_rise) / timedelta(1), 2)
    A_r = round(sun_rs[2] + 180, 2)
    A_s = round(sun_rs[3] + 180, 2)
    ratio_A = round((A_s - A_r) / 360, 2)
    print(dt_rise, ",", dt_set, ",", ratio_day, ",", A_r, ",", A_s, ",", ratio_A, A_r + A_s)
