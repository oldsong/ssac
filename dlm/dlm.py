from skyfield.api import Loader, Topos
from skyfield import almanac  # 用来计算日出日落，月出月落
import datetime
import pytz

# 先生成一个加载数据用的 loader，使用当前目录下已经下载的数据文件，
# 而且不考虑文件可能太老的问题，所以可以离线情况下用
# 正常情况不带 expire=False 时，加载时判断本地数据太老会去自动下载
load = Loader('.', expire=False)

# 加载时间数据，包括闰秒之类比较麻烦的东西
# 这里也指定一下 builtin=True，直接用本地数据，不要试图从网上下
# 不知道它跟前面 load 实例化时指定的 expire=False 是不是重了
ts = load.timescale(builtin=True)

# 加载行星数据
planets = load('de421.bsp')

# 用 pytz 整出个时区来
tz_ucsb = pytz.timezone('America/Los_Angeles')

# 先生成 2 个不带时区信息的日期时间，所谓 naive 的 datetime
# 用来计算这两个时间之内的所有日出日落，比如下面就会算出 9 次日出 9 次日落
d0_naive = datetime.datetime(2020, 3, 10)
d1_naive = datetime.datetime(2020, 3, 19)

# 把它们带上时区信息，这里用 pytz 里的 localize() 方法，因为直接用 datetime.datetime(2020, 3, 10, tzinfo=tz_ucsb) 是不行的
d0 = tz_ucsb.localize(d0_naive)
d1 = tz_ucsb.localize(d1_naive)

# 还得转成 Skyfield 用的时间（内部可能是 Julian date）
t0 = ts.utc(d0)
t1 = ts.utc(d1)

# 观察点，UCSB 的经纬度
ucsb = Topos(34.4, -119.8)

# 算日出日落
f = almanac.sunrise_sunset(planets, ucsb)  # f 应该是一个函数对象
t, y = almanac.find_discrete(t0, t1, f)

# y 是一个 numpy ndarray，跟 t 一样多元素，取值 True 时表示 t 里面对应日出时间，否则对应日落时间

t_ucsb = t.astimezone(tz_ucsb)     # 转回 ucsb 本地时区，结果 t_ucsb 是一个 numpy 的 ndarray
print("========= Sun rising and setting ", d0.strftime('%c %Z'), " - ", d1.strftime('%c %Z'))
for i in range(t_ucsb.size):
    if y[i]:
        print("Sunrise at: ", t_ucsb[i].strftime('%c %Z'))
    else:
        print("Sunset at: ", t_ucsb[i].strftime('%c %Z'))

# 算月出月落
moon = planets['Moon']
f = almanac.risings_and_settings(planets, moon, ucsb)  # f 应该是一个函数对象
t, y = almanac.find_discrete(t0, t1, f)

# y 是一个 numpy ndarray，跟 t 一样多元素，取值 True 时表示 t 里面对应日出时间，否则对应日落时间

t_ucsb = t.astimezone(tz_ucsb)  # 转回 ucsb 本地时区，结果 t_ucsb 是一个 numpy 的 ndarray
print("========= Moon rising and setting ", d0.strftime('%c %Z'), " - ", d1.strftime('%c %Z'))
for i in range(t_ucsb.size):
    if y[i]:
        print("Moonrise at: ", t_ucsb[i].strftime('%c %Z'))
    else:
        print("Moonset at: ", t_ucsb[i].strftime('%c %Z'))

# 算日出的另方法，这个方法肯定是没考虑到太阳是一个有大小的盘，当星星一样处理了
sun = planets['Sun']
f = almanac.risings_and_settings(planets, sun, ucsb)  # f 应该是一个函数对象
t, y = almanac.find_discrete(t0, t1, f)

# y 是一个 numpy ndarray，跟 t 一样多元素，取值 True 时表示 t 里面对应日出时间，否则对应日落时间

t_ucsb = t.astimezone(tz_ucsb)  # 转回 ucsb 本地时区，结果 t_ucsb 是一个 numpy 的 ndarray
print("********** Sun rising and setting ", d0.strftime('%c %Z'), " - ", d1.strftime('%c %Z'))
for i in range(t_ucsb.size):
    if y[i]:
        print("Moonrise at: ", t_ucsb[i].strftime('%c %Z'))
    else:
        print("Moonset at: ", t_ucsb[i].strftime('%c %Z'))

########### 以上计算日出日落的方法见：
########### https://rhodesmill.org/skyfield/almanac.html

########## 下面是计算视位置：方位角和高度角，见
########## https://rhodesmill.org/skyfield/positions.html

earth = planets['Earth']
ucsb_earth = earth + ucsb   # 必须转成明确在地球上，可能是换坐标系了吧
apparent_t0_sun = ucsb_earth.at(t0).observe(sun).apparent()
apparent_t0_moon = ucsb_earth.at(t0).observe(moon).apparent()

# 算太阳的
alt, az, distance = apparent_t0_sun.altaz()    # 求方位角等
print("Sun at %s, altitude=%s, azimuth=%s" % (d0.strftime('%c %Z'), alt.dstr(), az.dstr())) # 角度用字符串表示
print("Sun at %s, altitude=%f, azimuth=%f" % (d0.strftime('%c %Z'), alt.degrees, az.degrees))  # 角度用浮点数表示

# 算地球的
alt, az, distance = apparent_t0_moon.altaz()    # 求方位角等
print("Moon at %s, altitude=%s, azimuth=%s" % (d0.strftime('%c %Z'), alt.dstr(), az.dstr()))


