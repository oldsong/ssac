## 核心算法

输入: 观测者所在的经度, 纬度, 日期, 时区

输出: 相应时区的本地时间表示的当天日出, 日落时间

### 参考书1:

Astronomical Algorithm, 2nd Edition, Willmann-Bell Inc. (1998) by Jean Meeus.

有一个根据该书中算法写的 Python 库:

https://github.com/architest/pymeeus

它的文档:

https://pymeeus.readthedocs.io/en/latest/

安装该库的方法:

pip3 install pymeeus

但要使用该库似乎还是要了解不少概念. 另外一个 GitHub 项目:

https://github.com/pavolgaj/AstroAlgorithms4Python

可能更容易用一些. 

### 参考网站1:

美国国家海洋与大气管理局地球系统研究实验室全球监测部的太阳计算器, 也是根据该书算法计算的:

https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html

它有 Excel 和 OpenOffice 表格可以用来验算, 其 JavaScript 代码应该也可以直接参考.

### 参考网站2:

计算月球和太阳即时赤道坐标系位置的 JavaScript: 

http://www.stargazing.net/kepler/jsmoon.html

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

我们会用到:

 - America/New\_York
 - America/Los\_Ageles

---
Python 的 Console UI 库 Urwid

http://urwid.org/

pip3 install urwid

---
另一个库, 优点是说做简单的事情非常快, 不像 urwid 是传统的事件驱动型

pip3 install npyscreen

文档在: 

https://npyscreen.readthedocs.io/index.html

---
最简单的显示数字钟, 完全是用 print 输出: 

https://stackoverflow.com/questions/37515587/run-a-basic-digital-clock-in-the-python-shell

---
用 tkinter 似乎也很简单: 

https://www.geeksforgeeks.org/python-create-a-digital-clock-using-tkinter/

下面这个好像稍装饰了一下: 

https://www.sourcecodester.com/tutorials/python/11402/python-simple-digital-clock.html

---
终端模式下, 可以用 ANSI Escape 字符来控制显示位置. 有个库: 

https://github.com/kodie/ansiescapes

pip3 install ansiescapes

下面这个获得当前终端的尺寸, 如果想居中显示之类的可以参考: 

https://stackoverflow.com/questions/40931467/how-can-i-manually-get-my-terminal-to-return-its-character-size

其中那个取光标位置没十分搞懂. 它其实是用了个 ANSI 转义码 6n, 把当前光标位置显示到某地方效果等同于
用键盘输入写进了东西, 所以接着就可以从标准输出读进来. 这个 6n 转议码在 Wikipedia 里有点说明, 但没
完全看明白. 而且对 sys.stdin 这个迭代器的 next 输出再 repr 下然后显示时好像还带有转义字符. 而且奇
怪的是程序不会退出继续跑. 哦, 明白了: 相当于键盘输入了序列 ESC[n;mR, 其中n是行数, m是列数, 另外迭
代器没返回是因为还没回车

但 Python 中有直接得到终端尺寸的函数在 shutil 模块中: 

https://docs.python.org/3/library/shutil.html#shutil.get\_terminal\size

一些 ANSI Escape Code 可以看: 

http://ascii-table.com/ansi-escape-sequences.php

在 Wikipedia 上的应该比较全: 

https://en.wikipedia.org/wiki/ANSI\_escape\_code

如果要显示颜色可以用下面这个库: 

https://github.com/skabbass1/escape

---
JPL 会发布轨道参数及算法: 

https://en.wikipedia.org/wiki/Jet\_Propulsion\_Laboratory\_Development\_Ephemeris

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

