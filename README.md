# Weather
wxPython编写界面的天气预报小程序
1、简介：
   基于“三思之旅”博客( http://think3t.iteye.com/)中“打造自己的天气预报”项目，利用wxPython实现GUI界面，Beautiful Soup 实现对中国天气（http://m.weather.com.cn/mweather/101280101.shtml）内容抓取，环境python2.7整体思路延续“三思之旅”的相关内容，部分内容进行了优化改动。

2、优化及改动部分：
（1）修改从网页获取天气图标，不需要本地存储
（2）修改wx.ListCtrl中获取item值的方式为self.list.GetItem(row, col).Text
（3）修改获取天气信息页面的urlopen语句段，原因是发现过于频繁的urlopen会被网站拒绝，故设置重试次数及等候时间
（4）修改主界面、设置界面的OnClose()回调函数，原因是在通过py2exe打包生成exe文件后发现存在关闭窗口后无法结束进程的问题
（5）修改设置界面中删除用户信息语句段，避免出现全部用户数据清空后异常

2、文件:
 （1）WeatherReport.py 天气预报主模块
 （2）MySearcher.py 数据库模块
 （3）GetWeather.py 天气信息获取模块
 （4）CfgDlg.py  设置窗口模块
 （5）Config.ini 定时设置文件
 （6）data    数据库文件
 （7）error   天气信息获取异常Log
 （8）mysetup.py py2exe打包设置脚本
