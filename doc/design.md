## 核心数学公式
输入：经度，纬度，格林尼冶时间

输出：太阳高度角

参考书：

Astronomical Algorithm

https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html
美国国家海洋与大气管理局地球系统研究实验室全球监测部的太阳计算器，是根据上一本书还加上大气折射修正

https://github.com/soniakeys/meeus
那本书的算法，但是用 go 语言的

http://www.stargazing.net/kepler/sunrise.html
有 Excel 和 QBASIC 算法代码

---
Wikipedia 上的日出/日落方程

它以2000年1月1日中午12点的轨道初始条件计算，大概前后1百年内误差不到百分之一。这个误差应该就是均时差，
equation of time，本身的误差。均时差最大约16分33秒，最小约14分6秒，所以误差最多不超过10秒。

其计算主要包括两个值：当天的均时差，当天的太阳赤纬。

---
其以2000年1月1日轨道初始条件计算均时差的近似公式可能就是这个两个sin函数相加：

http://www.sws.bom.gov.au/Category/Educational/The%20Sun%20and%20Solar%20Activity/General%20Info/EquationOfTime.pdf

这个近似公式的推导似乎是这个：
http://www58.homepage.villanova.edu/alan.whitman/eqoftime.pdf

---
更多的均时差计算近似公式，其中一些精度更高，可见：

https://equation-of-time.info/calculating-the-equation-of-time
