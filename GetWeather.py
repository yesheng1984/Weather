# -*- coding: UTF-8 -*-
"""
Created on Tue Aug 04 15:05:21 2015

@author: yesheng
获取天气信息模块
"""
from BeautifulSoup import BeautifulSoup    # For processing HTML
import urllib 
import re
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')


class WeatherInfo(object):
    '''天气信息类'''
    def __init__(self, url, attempts = 100):
        self.url = url
# wInfo = [标题，更新日期，今天天气信息，未来第1天天气信息，...,未来第6天天气信息]             
        self.wInfo = []
        self.GetWeather(attempts)
    
    def GetWeather(self, attempts):
        '''获取天气信息'''
#        下载天气预报网页
        attempt = 0 #网页连接尝试次数
        while attempt < attempts:
            contents = urllib.urlopen(self.url).read()    #Get the source code of the site
            soup = BeautifulSoup(contents)    #Get the soup
            city_name = soup.title.contents[0].split()[0].encode('gbk')   #获取城市名称
            print city_name #测试
#       7天天气预报
       
            try:
                release_time = soup.find('div', attrs = {'class':'sk'}).h2.find(text = re.compile(u"([\u4e00-\u9fa5]+)")).encode('gbk')
            except AttributeError, e:
                attempt += 1
                print "Attempt No.%d, Error %s" % (attempt, e)
#                记录下被拒绝的网页内容
                with open('error.html', 'w+') as log:
                    log.write(contents)
                time.sleep(5) #如果连接不成功则休眠
                continue
            else:
                print release_time
                break
#        发布时间
        self.wInfo.append(city_name) 
        self.wInfo.append(release_time)
#        每日天气信息
#        todayIfo = [日期,图片1 Strem, 图片2 Strem,天气，气温 ]
        
        days = []
        days_weather = []
        days_temper = []
        b = soup.b
        for i in range(7):
            todayInfo = []
            days.append(b.string)
#            日期
            todayInfo.append(b.string)
            imgTag = b.findNext()
#            图片1 
#            print dict(imgTag.img.attrs)['src'] #测试
            todayInfo.append(dict(imgTag.img.attrs)['src'])

            if b.string != u"夜间":
                dayTime = dict(imgTag.img.attrs)['alt']
#            图片2 
                todayInfo.append(dict(imgTag.img.findNext('img').attrs)['src'])

#                print dict(imgTag.img.findNext('img').attrs)['src']
            
                nigTime = dict(imgTag.img.findNext('img').attrs)['alt']
#           天气            
                days_weather.append(dayTime + ' ' + nigTime)
                days_temper.append(b.findNext('span').string)
                todayInfo.append('日间 '+ dayTime + ',  夜间 ' + nigTime + ' ' + b.findNext('span').string)
            else:
                dayTime = ''
                todayInfo.append(0)
                nigTime = dict(imgTag.img.attrs)['alt']
                days_weather.append(nigTime)

#            气温
                days_temper.append(b.findNext('span').string)
                todayInfo.append('夜间 '+ nigTime + ' ' + b.findNext('span').string)
            
            b = b.findNext('b')
            
                
            self.wInfo.append(todayInfo)

if __name__ == '__main__':
    
    myWeather = WeatherInfo('http://m.weather.com.cn/mweather/101280102.shtml', 10)   

    for item in myWeather.wInfo:
        print item
        print '\n'

