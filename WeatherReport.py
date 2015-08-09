#coding=utf-8
"""
Created on Tue Aug 04 15:05:21 2015

@author: yesheng
天气预报主模块
"""
import wx
import cStringIO
import time
import smtplib
import email
import re
import ConfigParser
from email.Message import Message
from email.Header import Header
from urllib import urlopen
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from GetWeather import WeatherInfo
from CfgDlg import CfgDlg
from MySearcher import MySearcher


class MyApp(wx.App):
    '''应用程序类wx.App的子类'''
    def __init__(self):
        wx.App.__init__(self, redirect = False)
        frame = MyFrame()
        frame.Show(True)


class MyFrame(wx.Frame):
    '''主窗口界面类'''
    def __init__(self):
        wx.Frame.__init__(self, None, -1, style = wx.DEFAULT_FRAME_STYLE ^ \
        (wx.MAXIMIZE_BOX | wx.RESIZE_BORDER))
#属性设置 
        self.searcher = MySearcher()  # 数据库查询对象
        self._cityCode = self.searcher.getMainCityCode()  # 主界面城市查询
        url = 'http://m.weather.com.cn/mweather/%s.shtml' % self._cityCode
#        print url
        wInfo = WeatherInfo(url).wInfo  # 获取天气信息           
# wInfo = [标题，更新日期，今天天气信息，未来第1天天气信息，...,未来第6天天气信息]       
        self.SetTitle(wInfo[0])        
        self.panel = wx.Panel(self)
        self.stBar = self.CreateStatusBar()  # 创建状态栏
        self.stBar.SetFieldsCount(2) 
        self.stBar.SetStatusWidths([-4, -2])
        self.stBar.SetStatusText(wInfo[1], 0)  # 状态栏显示发布时间
        
        self.todayInfo = wInfo[2]    # 今日天气信息
        self.daysInfo = wInfo[3:]   # 未来6天天气信息
#布局设置
        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add(self._DoLayout(), 1)
        self.SetSizer(fsizer)
        fsizer.Fit(self)
#定时设置
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTime, self.timer)
#回调设置 
        self.Bind(wx.EVT_CLOSE,self.OnCloseWindow)
#==============================================================================
#布局函数
#==============================================================================
    
    def _DoLayout(self):       
#        上半区布局        
        hdLeft = self._LayoutHeadLeft(self.todayInfo)  # 今日天气部分
        hdRight = self._LayoutHeadRight()  # 个性化设置部分
        hbox = wx.BoxSizer(wx.HORIZONTAL)    #使用水平BoxSizer放置今日天气信息和3个按钮
        hbox.Add(hdLeft,  1, flag=wx.EXPAND)
        hbox.Add(hdRight, 0, flag=wx.EXPAND)
#       下半区布局
        days = self._LayoutDaysWeather(self.daysInfo)#未来天气部分
#       整体布局
        psizer = wx.BoxSizer(wx.VERTICAL)
        psizer.Add(hbox, 0, wx.EXPAND)
#        psizer.AddSpacer(10)
        psizer.Add(days, 0, wx.EXPAND)
#        psizer.AddSpacer(10)        
        self.panel.SetSizer(psizer)
        psizer.Fit(self)  
        
        return psizer
    
    def _LayoutHeadLeft(self, todayInfo):
        '''窗口上半部分左侧布局，主要是今日天气信息'''
#        todayInfo=[日期, 日间图片, 晚间图片, 天气气温]   
#        print todayInfo[3]
        #一个静态文本控件
        self.tLbl = wx.StaticText(self.panel, -1, label=todayInfo[3])
        todayImgs  = self._CreateImg(todayInfo[1:3], [70,65])#生成日间、夜间图片
        self.todaySbs = []        
        
        for item in todayImgs:
            self.todaySbs.append( wx.StaticBitmap(self.panel, -1, item))
            
        #使用GridBagSizer来放置两个图片和两个文本控件
        GBSizer = wx.GridBagSizer(vgap=5, hgap=5)   #Grid之间水平、竖直方向间距都是5个像素
        GBSizer.Add(self.todaySbs[0], pos=(0, 0), span=(1, 1), flag=0)   #天气图片1，放置在第1行第1列，占一行一列
        GBSizer.Add(self.todaySbs[1], pos=(0, 1), span=(1, 1), flag=0)   #天气图片2，放置在第1行第2列，占一行一列
        GBSizer.Add(self.tLbl, pos=(1, 0), span=(1, 2), flag= 0)  #天气文字信息，放置在第2行第1列，占一行两列
        #再使用Static Box Sizer来放置上面的GridBagSizer
        sbox = wx.StaticBox(self.panel, -1, todayInfo[0])        
        sbsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sbsizer.Add(GBSizer, 0, wx.ALL, 2)
        
        return sbsizer
    
    def _LayoutHeadRight(self):
        '''放置3个按钮'''
        self.updateBtn = wx.Button(self.panel, -1, label=u"更新")
        self.setupBtn = wx.Button(self.panel, -1, label=u"设置")
        self.sendBtn = wx.Button(self.panel, -1, label=u"发送")        

        self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.updateBtn)
        self.Bind(wx.EVT_BUTTON, self.OnConfig, self.setupBtn)
        self.Bind(wx.EVT_BUTTON, self.OnSend, self.sendBtn)      

        #使用Static Box Sizer来放置上面的GridBagSizer
        sbox = wx.StaticBox(self.panel, -1, u"个性化")        
        sbsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sbsizer.Add(self.updateBtn, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5)
        sbsizer.Add(self.setupBtn, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5)
        sbsizer.Add(self.sendBtn, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5)
                
        return sbsizer
     
    def _LayoutDayWeather(self, dayInfo):
        """放置未来每天的天气信息"""
        #两个静态文本控件
        self.futureDlbl.append(wx.StaticText(self.panel, -1, label=dayInfo[0]))
        self.futureTlbl.append(wx.StaticText(self.panel, -1, label=dayInfo[3]))

        imgs  = self._CreateImg(dayInfo[1:3], [20, 20])  # 日间、夜间图片    
        self.futureDsbs.append( wx.StaticBitmap(self.panel, -1, imgs[0]))
        self.futureNsbs.append(wx.StaticBitmap(self.panel, -1, imgs[1]))
        
        #使用GridBagSizer来放置两个图片和两个文本控件
        GBSizer = wx.GridBagSizer(vgap=5, hgap=5)
        GBSizer.Add(self.futureDlbl[-1], pos=(0, 0), flag = 0)#日期
        GBSizer.Add(self.futureDsbs[-1], pos=(1, 0), flag = wx.EXPAND)#日间图片
        GBSizer.Add((5, -1), (1, 1))
        GBSizer.Add(self.futureNsbs[-1], pos=(1, 2), flag = wx.EXPAND)#夜间图片
        GBSizer.Add((10, -1), (1, 3))
        GBSizer.Add(self.futureTlbl[-1], pos=(1, 4), flag = wx.ALIGN_CENTER | wx.EXPAND)#天气气温
        
        return GBSizer
    
    def _LayoutDaysWeather(self, daysInfo):
        """使用竖直方向的StaticBoxSizer放置未来6天的天气信息"""
        sbox = wx.StaticBox(self.panel, -1, u"未来6日天气")
        sbsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
#       未来6日的日间图标   
        self.futureDsbs = []
#       未来6日的夜间图标
        self.futureNsbs =[]
#        未来6日的日期
        self.futureDlbl = []
#        未来6日的气温天气
        self.futureTlbl = []
        
        for dayInfo in daysInfo:
            sbsizer.Add(self._LayoutDayWeather(dayInfo), flag=wx.EXPAND)
        
        return sbsizer
     
    def _CreateImg(self, urlList, size):
        '''从网站生成天气图标'''
        staImg =[]
        for url in urlList:
            if url:
                img = cStringIO.StringIO(urlopen(url).read())
                imgTemp = wx.ImageFromStream(img)
                imgTemp.Rescale(size[0], size[1])
                staImg.append(wx.BitmapFromImage(imgTemp))
            else:
#            如果已经是夜间，则填充一个空图片
                staImg.append(wx.EmptyBitmap(size[0], size[1], 100))
                
        return staImg
#==============================================================================
# Button回调函数
#==============================================================================

    def OnRefresh(self,event):
        '''更新回调函数'''
        self._cityCode = self.searcher.getMainCityCode()  # 主界面城市查询
        wInfo = WeatherInfo('http://m.weather.com.cn/mweather/%s.shtml' % self._cityCode).wInfo 
        todayInfo = wInfo[2]  
        daysInfo = wInfo[3:]  
#        更新标题栏、状态栏
        self.SetTitle(wInfo[0])          
        self.stBar.SetStatusText(wInfo[1], 0)  
#       更新今日天气气温
        self.tLbl.SetLabel(todayInfo[3])                 
#       更新今日天气图标
        todayImgs = self._CreateImg(todayInfo[1:3], [70, 65]) 
        self.todaySbs[0].SetBitmap(todayImgs[0])
        self.todaySbs[1].SetBitmap(todayImgs[1])
        
#       更新未来6日天气  
        i = 0  
        for dayInfo in daysInfo:
            self.futureDlbl[i].SetLabel(dayInfo[0])  # 未来日期
            self.futureTlbl[i].SetLabel(dayInfo[3])  # 未来气温天气
            futureImgs = self._CreateImg(dayInfo[1:3], [20, 20]) 
            self.futureDsbs[i].SetBitmap(futureImgs[0])  # 未来日间图片
            self.futureNsbs[i].SetBitmap(futureImgs[1])  # 未来夜间图片
            i += 1  

    def OnSend(self, event):
        '''发送回调函数'''
        self._SendToUsers()

    def _SendToUsers(self):
        '''给所有用户发邮件'''
        users = self.searcher.getUserInfo()  # 从数据库中获取用户信息
        for (mail, city, note) in users:
            wInfo = WeatherInfo('http://m.weather.com.cn/mweather/%s.shtml' %city).wInfo
#           生成邮件内容            
            mailContent = []
            for w in wInfo[2:]:
                mailContent.append("【" + w[0] + "】  " + w[3])
#            print mailContent
            mailContent = ";\r\n".join(mailContent)
            subj =  wInfo[0].decode('gbk')  # 邮件主题
            self._SendToUser(mail, subj, mailContent)
            self.stBar.SetStatusText(u'%s 发送完成!' % mail.split('@')[0], 0)
        self.stBar.SetStatusText(u'全部邮件发送完成!', 0)       
        time.sleep(15)  # 十秒后状态栏恢复原先内容
        self.stBar.SetStatusText(wInfo[1], 0)

    def _SendToUser(self, to, subj, content, \
    myemail = 'yesheng1984@139.com', mypass = 'gdsy2002sysu2006'):
        '''给单个用户发送邮件'''
        smtpport = '25'  # SMTP端口号
        smtpuser = re.match('^\w+', myemail).group()  # 根据Email地址获取用户名
        smtpserver = re.sub('^\w+@', 'smtp.', myemail)  # 根据Email地址获取SMTP服务器地址
        server = smtplib.SMTP(smtpserver, smtpport)  # 构造SMTP对象

        server.login(smtpuser, mypass)  # 验证用户名及密码
        msg = Message()  # 构造邮件信息
        msg['Mime-Version'] = '1.0'  # Mine的版本
        msg['From'] = '天气预报'  # 发送邮箱地址
        msg['To'] = to  # 接收邮箱地址
        msg['Subject'] = Header(subj,'utf-8')  # 邮件主题，注意此处使用了UTF-8编码，不然发送中文乱码
        msg['Date'] = email.Utils.formatdate()  # 发送时间
        msg.set_payload(content, 'UTF-8')    # 邮件正文，此处也使用了UTF-8编码

        try:
            server.sendmail(myemail, to, unicode(msg))   # may also raise exc
        except Exception, ex:
            print Exception, ex
            print 'Error - send failed'  # 捕获到异常说明发送失败
    
    def OnConfig(self, event):
        '''设置回调函数'''
        CfgDlg(self.searcher)
        myIni = ConfigParser.ConfigParser()
        myIni.read('Config.ini')  # 读取配置文件
        if int(myIni.get('Config', 'Timer')):
            print "Start Timer!\n"
            self.timer.Start(500)
        else:
            print "Stop Timer!\n"
            self.timer.Stop()

    def OnTime(self, event):
        '''定时回调函数'''
        t = time.localtime(time.time())
        st = time.strftime("%H:%M:%S", t)  # 将时间对象转换成HH:MM:SS格式(24小时)字符串
        self.stBar.SetStatusText(st, 1)  # 将时间字符串显示在状态栏上

        myIni = ConfigParser.ConfigParser()
        myIni.read('Config.ini')
        isTimerOn = myIni.get('Config', 'Timer')
        timer_hour = myIni.get('Config', 'Hour')
        timer_minute = myIni.get('Config', 'Minute')
        timer_second = myIni.get('Config', 'Second')

        if(isTimerOn):  # 如果定时发送复选框
            timer = timer_hour + ':' + timer_minute \
            + ':' + timer_second  # 获取定时时间
            print "timer: %s\n" % (timer)
            print "st: %s\n" % (st)
            if(not cmp(st, timer)):  # 当前时间等于定时时间时
                time.sleep(1)  # 因为定时器每500毫秒刷新一次，所以延时1秒钟，防止连续发送两次
                print "Ready to send!"
                self._SendToUsers()  # 给用户发送天气预报
    
    def OnCloseWindow(self,event):
        "退出回调函数"
#        print "OnCloseWindow tigger!"
#        self.Close(True)
        self.searcher.close()        
        self.Destroy()


if __name__ == "__main__":    
    app = MyApp()
    app.MainLoop()
