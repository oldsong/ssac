import time
import julian
import pytz
from datetime import timedelta
import datetime
from sunclock import sun_rise_set, equ2hor
from timezonefinder import TimezoneFinder

# Calculate:
#   solar transit time, in Julian day with fraction
#   sunset hour angle, in fraction of Julian day
#   declination of the Sun at the date, in radians
# Input:
#   n: number of days since Jan 1st, 2000 12:00
#   lo: longitude of the observer on the Earth, west is negative, in degree
#   la: latitude of the observer on the Earth, north is positive, in degree
#def sun_rise_set(n, lo, la):

# Convert Equatorial coordinate to horizontal
#   ha: hour angle, in fraction of a Julian day
#   dec: declination, in radians
#   la: latitude of the observer on the Earth, in degree
# Return a tuple with 2 elements:
#   0: azimuth, measured from the north, positive to east, in degree
#   1: altitude, in degree
# def equ2hor(ha, dec, la):

# Calculate timezone from longitude, return a timezone.timezone object
def get_timezone(lon):
    hours = lon // 15
    if ((lon % 15) > 7.5): hours = hours + 1
    return datetime.timezone(timedelta(hours=hours))  # 标准时区

year, month, day = 2020, 3, 9
lat, lon = 51, 0.1   # London
lat, lon = 39, 170    # 
lat, lon = 39, 179    # 
lat, lon = 39, 116    # Beijing
lat, lon = 34, -118   # Los Angles

# first try to find the timezone from observer longtitude
tf = TimezoneFinder()
tz_str = tf.timezone_at(lat=lat, lng=lon)
if (tz_str == None):  # 很不幸没找到, 也许是在公海上?
    tz = get_timezone(lon)  # 用标准算法算一个标准时区
    d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
else:
    tz = pytz.timezone(tz_str)  # 用找到的名字到 pytz 里找对应的时区
    if (tz == None):  # 很不幸没找到, 这应该不会发生的, 但还是防止一下吧
        tz = get_timezone(lon)  # 只能还是用标准算法算一个标准时区
        d_local = datetime.datetime(year, month, day, hour=12, tzinfo=tz)
    else:  # 找到了 pytz 里的时区, 但这个时区不能直接用在 datetime.datetime 的构造函数里, 得用其 localize 方法
        d_local = tz.localize(datetime.datetime(year, month, day, hour=12))

d_utc = d_local.astimezone(tz=datetime.timezone.utc)  # 转换成 UTC 时间
tz_h = d_local.tzinfo.utcoffset(d_local) / timedelta(hours=1)  # 与UTC差的小时数, 将用于显示本地时间

n = round(julian.to_jd(d_utc) - 2451545)  # number of days since Jan 1st, 2000 12:00
sun_rs = sun_rise_set(n, lon, lat)  # 计算当天的日出日落
sun_rs_next = sun_rise_set(n + 1, lon, lat)  # 计算次日j的日出日落

# 当天日出时间, Julian date, 加了一个时区修正, 因为 julian 库不认时区, 都当UTC处理了, 下面几个也一样
j_rise = sun_rs[0] - sun_rs[1] + tz_h/24

d_rise = julian.from_jd(j_rise)  # 当天日出时间, dateime date
print(d_rise.strftime("当日日出时间: %m/%d/%Y %H:%M:%S"))
j_rise_next = sun_rs_next[0] - sun_rs_next[1] + tz_h/24  # 次日日出时间, 时区修正Julian date
d_rise_next = julian.from_jd(j_rise_next)  # 次日日出时间, dateime date
print(d_rise_next.strftime("次日日出时间: %m/%d/%Y %H:%M:%S"))
j_set = sun_rs[0] + sun_rs[1] + tz_h/24

print('\033[?25l')  # hide the cursor

# 从日出前 4 小时到日落后 4 小时循环显示
#  当前时间: 2020/03/08 03:03:12
#  下次日出时间: 2020/03/08 07:03:12, 倒计时: 4 hours
# 每 0.04 秒显示一次，每次增加 1 分钟，这样大约是 1500 倍速模拟
j_start = j_rise - 4/24  # start time
j_stop = j_set + 4/24  # stop time
j_minute = 1/1440  # a minute in Julian day
i = 0
while True:
    try:
        j_now = j_start + i * j_minute
        if (j_now > j_stop):
            j_now = j_start
            i = 0
        i = i + 1
        if (j_now > j_rise):  # 已过当天日出时间, 我们显示次日的日出时间
            d_this_rise = d_rise_next
        else:
            d_this_rise = d_rise
        d_now = julian.from_jd(j_now)
        if (j_now < j_rise or j_now > j_set):   # 日出前或日落后没有特殊背景色
            print('\033[0m', end="", flush=True)  # clear graphic mode attribute
        else:
            #print('\033[41m', end="", flush=True)  # set background code to Red
            print('\033[7m', end="", flush=True)  # set reverse video
        print(d_now.strftime("      当前时间: %m/%d/%Y %H:%M:%S"), "   ")
        print(d_this_rise.strftime("  下次日出时间: %m/%d/%Y %H:%M:%S"), "   ")
        print("    日出倒计时:", (d_this_rise - d_now) // 1, "       ")
        print('\033[3A', end="", flush=True)  # move cursor up 3 rows
        time.sleep(0.04)
    except:  # 按了 Control-C 中断, 恢复屏幕
        print('\033[0m', end="", flush=True)  # clear graphic mode attribute
        print('\033[3B', end="", flush=True)  # move cursor down 3 rows
        print('\033[?25h')  # show the cursor
        exit(0)

