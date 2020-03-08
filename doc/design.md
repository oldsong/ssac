## 核心算法

输入: 观测者所在的经度, 纬度, 日期, 时区

输出: 相应时区的本地时间表示的当天日出, 日落时间

### 参考书1:

Astronomical Algorithm, 2nd Edition, Willmann-Bell Inc. (1998) by Jean Meeus.

有一个根据该书中算法写的 Python 库:

[Meeus 天文算法的 Python 库](https://github.com/architest/pymeeus)

它的文档:

[PyMeeus 库文档](https://pymeeus.readthedocs.io/en/latest/)

安装该库的方法:

```shell
pip3 install pymeeus
```

但要使用该库似乎还是要了解不少概念. 另外一个 GitHub 项目:

https://github.com/pavolgaj/AstroAlgorithms4Python

可能更容易用一些, 但我看其中 moon 的部分, 没看懂, 也许是计算的某个具体时间点的实际例子.

### 参考网站1:

美国国家海洋与大气管理局地球系统研究实验室全球监测部的太阳计算器, 也是根据该书算法计算的:

https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html

它有 Excel 和 OpenOffice 表格可以用来验算, 其 JavaScript 代码应该也可以直接参考.

### 参考网站2:

计算月球和太阳即时赤道坐标系位置的 JavaScript: 

[JavaScript 计算月球太阳赤道坐标](http://www.stargazing.net/kepler/jsmoon.html)

从赤经赤纬计算出本地的地平坐标还要另外计算(见下).

### 参考书2:

Practical Astronomy with your Calculator or Spreadsheet, 4th Edition, Cambridge University Press. (2011) by Peter Duffett-Smith, Jonathan Zwart

该书中用到的 Excel 和 OpenOffice 文件可以用来验算, 下载地址:

https://www.cambridge.org/cn/academic/subjects/physics/amateur-and-popular-astronomy/practical-astronomy-your-calculator-or-spreadsheet-4th-edition?format=PB

### Wikipedia 上的日出/日落方程

[Sunrise equation - Wikipedia](https://en.wikipedia.org/wiki/Sunrise_equation)

其计算均时差(Equation of Time)的近似公式可能就是这个两个sin函数相加:

http://www.sws.bom.gov.au/Category/Educational/The%20Sun%20and%20Solar%20Activity/General%20Info/EquationOfTime.pdf

这个近似公式的推导似乎是这个:

http://www58.homepage.villanova.edu/alan.whitman/eqoftime.pdf

### 均时差近似公式

更多的均时差计算近似公式, 其中一些精度更高, 可见: 

https://equation-of-time.info/calculating-the-equation-of-time

### 计算 Julian 日期

有个 Python 库 julian 可以用来方便计算 Julian Date

https://github.com/dannyzed/julian

pip3 install julian

### 从赤道坐标系转到地平坐标系

转到地平坐标的目的是可以方便地用它来画图: 方位角和高度角.

[Ecliptic coordinate system - Widipedia](https://en.wikipedia.org/wiki/Ecliptic_coordinate_system)

[贴吧中一个例子](http://tieba.baidu.com/p/4201509958)

[用 PyMeeus 库](https://pymeeus.readthedocs.io/en/latest/Coordinates.html#pymeeus.Coordinates.equatorial2horizontal)

知道 Hour Angle 就可以很容易从赤道坐标转成地平坐标. 计算日出时已经算出了日出时的太阳 Hour Angle，所以很容易把当天的太阳地平坐标算出来. 当然近似了一下把当天的太阳赤道坐标当作常数了.

计算月球的地平坐标时, 是否可以根据当天的太阳与月球的赤经差直接得到月球的时角?

### Python 日期时间文档: 

https://docs.python.org/3/library/datetime.html

### 时区处理

有个 pytz 库

pip3 install pytz

列出所有其包含的时区名: 

https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones

例如:

 - America/New\_York
 - America/Los\_Ageles
 - Asia/Shanghai

## 用户界面 User Interface

### 字符界面

如果用普通的 print, 每秒钟显示一行，则会造成屏幕上大量的输出，很难看。

---
最简单的显示数字钟, 完全是用 print 输出, 但带 end, flush 等参数, 回车而不换行: 

[StackOverflow terminal digital clock](https://stackoverflow.com/questions/37515587/run-a-basic-digital-clock-in-the-python-shell)

但只能显示一行. 如果想要比较自由地控制在屏幕指定位置显示, 可以使用 ANSI Escape Code:

[ANSI escape code - Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)

这个 ANSI Escape Code 更简要一些，但没有 Wikipedia 上的全:

[常用 ANSI Escape Code](http://ascii-table.com/ansi-escape-sequences.php)

下面这个库应该更方便:

[Python ANSI Escape](https://github.com/kodie/ansiescapes)

它可以用 pip 安装:

pip3 install ansiescapes

如果要显示颜色用下面这个库更方便:

[Python escape 设置字符颜色及效果](https://github.com/skabbass1/escape)

Python 中有直接得到终端尺寸的函数在 shutil 模块中:

[Python shutil.get\_terminal\_size() 函数](https://docs.python.org/3/library/shutil.html#shutil.get_terminal_size)

取得终端尺寸之后就可以计算如何居中显示了.

---
有一些更强大的字符界面库, 可以做出类似 GUI 的效果, 但复杂不少。

Python 的 Console UI 库 Urwid

[Python Urwid](http://urwid.org/)

```shell
pip3 install urwid
```

另一个库 npyscreen, 优点是说做简单的事情非常快, 不像 urwid 是传统的事件驱动型

pip3 install npyscreen

文档在: 

[Python npyscreen doc](https://npyscreen.readthedocs.io/index.html)

### GUI 界面
用 Python 的 Tk 库 tkinter 似乎也不难, 比如下面这个数字时钟的例子: 

[simple Python tkinter digital clock](https://www.geeksforgeeks.org/python-create-a-digital-clock-using-tkinter/)

下面这个稍稍装饰了一下: 

[Python tkinter digital clock with little style](https://www.sourcecodester.com/tutorials/python/11402/python-simple-digital-clock.html)

在 Windows 中 tkinter 似乎是自带的, 在 Linux 中可能要安装一下:

```shell
sudo apt install python3-tk
```

***Modern Tkinter for Busy Python Developers*** 这本书不错, 其 PDF 版在本目录中可以找到.

tkinter 缺少一个自带的日期时间控件, 可能可以用这个:

[tkcalendar 的 DateEntry](https://tkcalendar.readthedocs.io/en/stable/DateEntry.html)

## 备忘
---
JPL 会发布轨道参数及算法: 

[JPL 星历](https://en.wikipedia.org/wiki/Jet_Propulsion_Laboratory_Development_Ephemeris)

https://naif.jpl.nasa.gov/naif/index.html

https://github.com/AndrewAnnex/SpiceyPy

精度很高, 但过于复杂了. 

---
这里有计算位置公式汇总, 包括月球位置计算

https://www.aa.quae.nl/en/reken/hemelpositie.html

日出/日落计算还有专门页: 

https://www.aa.quae.nl/en/reken/zonpositie.html

好像国际天文联合会有个专门的服务: 

International Astronomical Union's Standards of Fundamental Astronomy (SOFA) service

http://www.iausofa.org/

---
根据经纬度来找时区, 可以配合 pytz 来使用: 

https://github.com/MrMinimal64/timezonefinder

pip3 install timezonefinder

```python
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()
latitude, longitude = 52.5061, 13.358
tf.timezone_at(lng=longitude, lat=latitude) # returns 'Europe/Berlin'
```

这个库挺大的, 因为它实际上包含很多多边形数据用于判断时区. 问题在于它对于很多地方会返回空, 可能大部分是在公海, 所以如果返回空就按经度进行计算: 每 15 度是一个时区的中央经线, 中央经线左右各 7.5 度是同一个时区.
