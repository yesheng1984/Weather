#coding=utf-8
"""
Created on Tue Aug 04 15:05:21 2015

@author: yesheng
设置窗口模块
"""
import wx
import re
import ConfigParser
from MySearcher import MySearcher


class AddCfgFrame(wx.Frame):
    '''新增用户窗口类'''
    def __init__(self, Plist, Psearcher, Ptotaluser, Pmaincity):
#        super(AddCfgFrame, self).__init__(self, None, -1, u'增加用户')
        wx.Frame.__init__(self, None, -1, u'增加用户')
        self.panel = wx.Panel(self)
        self.stBar = self.CreateStatusBar()

#        窗口第一部分
        self.choLb =  wx.StaticText(self.panel, -1, u"选择城市")        
#       从父窗口得到数据库搜索对象
        self.searcher = Psearcher
        self.Plist = Plist
        self.Ptotaluser = Ptotaluser
        self.Pmaincity = Pmaincity
        
        # 从数据库中导出省、市、县信息并存在3个列表中
        provList = self.searcher.listProvs()
        cityList = self.searcher.listCityOfProv(u'北京')#默认省份
        zoonList = self.searcher.listZoonOfCity(u'北京', u'北京')#默认城市
        
# 创建省份下拉框，默认显示北京，绑定EVT_CHOICE事件处理器
        self.provCho = wx.Choice(self.panel, -1, choices=provList)
        self.provCho.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnProvSel, self.provCho)
        
# 创建市下拉框，默认显示北京，绑定EVT_CHOICE事件处理器
        self.cityCho = wx.Choice(self.panel, -1, choices=cityList)
        self.cityCho.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnCitySel, self.cityCho)
        
# 创建区/县下拉框，默认显示北京
        self.zoonCho = wx.Choice(self.panel, -1, choices=zoonList)
        self.zoonCho.SetSelection(0)
        
#       窗口第二部分
        self.mailLb = wx.StaticText(self.panel, -1, u"邮箱地址")
        self.mailTxt = wx.TextCtrl(self.panel, -1)
        self.mcityChk = wx.CheckBox(self.panel, -1, label=u'主城市')   
        
#       窗口第三部分
        self.OKBtn = wx.Button(self.panel, wx.ID_OK, label=u'确定')
        self.cancelBtn = wx.Button(self.panel, wx.ID_CANCEL, label=u'取消')

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.OKBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        
#        窗口布局
        fsizer = wx.BoxSizer(wx.VERTICAL)# frame sizer
        fsizer.Add(self._DoLayOut(), 1, wx.EXPAND)
        
        self.SetSizer(fsizer)
        fsizer.Fit(self)
#        self.SetInitialSize((310,165))
        
        self.Show()
#==============================================================================
#  布局函数       
#==============================================================================
    
    def _DoLayOut(self):
        '新增用户窗口布局管理'
        psizer = wx.GridBagSizer(vgap = 10, hgap = 10)
        psizer.Add(self.choLb, pos = (1, 1), span = (1, 1))
        psizer.Add(self.provCho, pos = (1, 2), span = (1, 1), flag = wx.EXPAND)
        psizer.Add(self.cityCho, pos = (1, 3), span = (1, 1), flag = wx.EXPAND)
        psizer.Add(self.zoonCho, pos = (1, 4), span = (1, 1), flag = wx.EXPAND)
        psizer.Add((10, 10), (1, 5))
        
        psizer.Add(self.mailLb, pos = (2, 1), span = (1, 1))
        psizer.Add(self.mailTxt, pos = (2, 2), span = (1, 2), flag = wx.EXPAND)
        psizer.Add(self.mcityChk, pos = (2, 4), span = (1, 1))
        
        psizer.Add(self.OKBtn, pos = (3, 2), span = (1, 1))
        psizer.Add(self.cancelBtn, pos = (3, 3), span = (1, 1))
        
        psizer.Fit(self)
        self.panel.SetSizer(psizer)

        return psizer
#==============================================================================
#回调函数      
#==============================================================================
    
    def OnOK(self, event):
        '''确定回调函数'''
        prov = self.provCho.GetStringSelection()  # 获取当前选中的省份名称
        city = self.cityCho.GetStringSelection()  # 获取当前市的名称
        zoon = self.zoonCho.GetStringSelection()  # 获取当前区/县的名称
        cityCode = self.searcher.getCityCode(prov, city, zoon)  # 从数据库中获取当前选中的城市代码
        mailAddr = self.mailTxt.GetValue()  # 获取邮箱地址
        
    # 判断邮箱地址格式是否合法
        if mailAddr == '':  # 如果邮箱为空，则状态栏提示'请输入邮箱地址！'
            self.stBar.SetStatusText(u'请输入邮箱地址！')
        elif re.match(r'[\w\.]+@\w+\.\w+', mailAddr):  # 邮箱地址合法，则执行添加用户动作 
           
            if self.mcityChk.IsChecked():  # 如果勾选“主城市”复选框，则新增加的用户为主城市
                self.searcher.clearMainCity()  # 数据库中只能有一个主城市，所以要先清除原主城市标记
                self.searcher.addItem(table='userInfo', values=(mailAddr, cityCode, 1, zoon))  # 把用户信息写入数据库
            else:
                self.searcher.addItem(table='userInfo', values=(mailAddr, cityCode, 0, zoon))
                
            self.stBar.SetStatusText(u'用户: %s 添加成功！' % mailAddr)  # 状态栏提示用户添加成功           
            row = self.Ptotaluser  # 获取原来列表中最后一行索引号
#            row = self.row
        # 将新增加的用户信息添加在列表里
            self.Plist.InsertStringItem(row, unicode(row + 1))
            self.Plist.SetStringItem(row, 1, mailAddr)
            self.Plist.SetStringItem(row, 2, cityCode)
            self.Plist.SetStringItem(row, 3, zoon)
            if self.mcityChk.IsChecked():  # 如果勾选“主城市”复选框，则新增加的用户为主城市
            # 将原主城市文字颜色设置为黑色
                self.Plist.SetItemTextColour(self.Pmaincity, wx.BLACK)
            # 将新主城市文字颜色设置为红色
                self.Plist.SetItemTextColour(row, wx.RED)
            # 记录新主城市所在行
                self.Pmaincity = row
        # 将新增加的行设置为选中状态
            currentSelected = self.Plist.GetFirstSelected()
        
            if currentSelected != -1:
                self.Plist.SetItemState(currentSelected, 0, wx.LIST_STATE_SELECTED)
            
            self.Plist.SetItemState(row, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.Ptotaluser += 1  # 当前用户总数加1        
            self.Hide()  # 操作完成，关闭“增加用户”对话框
        else:  # 如果邮箱地址格式合法，则状态栏提示'邮箱地址格式错误！'
            self.stBar.SetStatusText(u'邮箱地址格式错误！')
            
    def OnCancel(self, event):
        '''取消按钮回调函数'''
#        数据清空
        self.provCho.SetSelection(0)
        self.cityCho.SetSelection(0)
        self.zoonCho.SetSelection(0)
        self.mailTxt.Clear()
        
        self.Hide()
            
    def OnProvSel(self, event):
        '''省份下拉框回调函数'''
        prov = event.GetString()  # 获取当前选中的省份名称
        cityList = self.searcher.listCityOfProv(prov)  # 获取当前省份的市信息列表
        self.cityCho.SetItems(cityList)  # 更新市下拉框内容
        self.cityCho.SetSelection(0)  # 默认显示省会城市
        city = self.cityCho.GetStringSelection()  # 获取当前市的名称
        zoonList = self.searcher.listZoonOfCity(prov, city)  # 获取当前市的区/县信息列表
        self.zoonCho.SetItems(zoonList)  # 更新区/县下拉框内容
        self.zoonCho.SetSelection(0)  # 默认显示市区
    
    def OnCitySel(self, event):
        '''城市下拉回调函数'''        
        prov = self.provCho.GetStringSelection()  # 获取当前选中的省份名称
        city = event.GetString()  # 获取当前市的名称
        zoonList = self.searcher.listZoonOfCity(prov, city)  # 获取当前市的区/县信息列表
        self.zoonCho.SetItems(zoonList)  # 更新区/县下拉框内容
        self.zoonCho.SetSelection(0)  # 默认显示市区
        
        
class CfgDlg(wx.Dialog):
    '''配置窗口类'''
    def __init__(self, searcher):        
        super(CfgDlg, self).__init__(None, -1, u"设置")
        self.panel = wx.Panel(self)
        self.searcher = searcher
        
#        窗口第一部分
        self.cfgLb = wx.StaticText(self.panel, -1, u"当前用户")
        
#        窗口第二部分
        self.list = wx.ListCtrl(self.panel, -1, style = wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,size = (384,-1))
        self.list.InsertColumn(0, u'序号', format = wx.LIST_FORMAT_LEFT)
        self.list.InsertColumn(1, u'邮箱', format = wx.LIST_FORMAT_LEFT)
        self.list.InsertColumn(2, u'城市', format = wx.LIST_FORMAT_LEFT)
        self.list.InsertColumn(3, u'备注', format = wx.LIST_FORMAT_LEFT)
        self.list.SetColumnWidth(0,50)
#       生成已有用户列表界面      
#        获取用户信息，得到一个三元组列表
        userInfos = self.searcher.getUserInfo()
#        从第一行开始，第一行的索引为0
        row = 0
#        依次插入用户信息
        for (mail, city, note) in userInfos:
#            每个用户信息增加一行，并把首列显示为行号，从1开始
            self.list.InsertStringItem(row, unicode(row + 1))
#            接下来3列依次插入用户信息（邮箱、城市、备注）
            self.list.SetStringItem(row, 1, mail)
            self.list.SetStringItem(row, 2, city)
            self.list.SetStringItem(row, 3, note)
#            如果当前用户是主城市，则显示红色，并记录行号
            if self.searcher.isMainCity(mail, city):
                self.list.SetItemTextColour(row, wx.RED)
                self.main_city = row
#             下一个用户行号加1
            row += 1
#            全部用户信息插入完成后记录最后一行索引
        self.totaluser = row
#        第二列（邮箱）根据内容自动调整列宽
        self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
#        默认会选中第一行内容，此处我们使第一行不被选中
        self.list.SetItemState(0, 0, wx.LIST_STATE_SELECTED)
#        窗口第三部分 
        self.myIni = ConfigParser.ConfigParser()
        self.myIni.read('Config.ini')#读取配置文件
        self.isTimerOn  = self.myIni.get('Config','Timer')
        self.timer_hour = self.myIni.get('Config','Hour')
        self.timer_minute = self.myIni.get('Config', 'Minute')
        self.timer_second = self.myIni.get('Config', 'Second')
        self.setTimeChk = wx.CheckBox(self.panel, -1, label=u'定时发送')
        self.setTimeChk.SetValue(int(self.isTimerOn))
        self.Bind(wx.EVT_CHECKBOX, self.OnSetTimeChk, self.setTimeChk)

#       创建时间下拉框
        self.hourCho = wx.Choice(self.panel, -1, choices=[unicode(hour) for hour in range(24)])
        self.hourCho.SetSelection(int(self.timer_hour))
        
        self.minuteCho = wx.Choice(self.panel, -1, choices=[unicode(minute) for minute in range(60)])
        self.minuteCho.SetSelection(int(self.timer_minute))
        
        self.secondCho = wx.Choice(self.panel, -1, choices=[unicode(second) for second in range(60)])
        self.secondCho.SetSelection(int(self.timer_second))

        if self.isTimerOn:
            self.hourCho.Enable()
            self.minuteCho.Enable()
            self.secondCho.Enable()
        else:
            self.hourCho.Disable()
            self.minuteCho.Disable()
            self.secondCho.Disable()

#       绑定窗口关闭事件       
        self.Bind(wx.EVT_CLOSE, self.OnClose)
#       绑定右键菜单
        self.list.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.onAdd = AddCfgFrame(self.list, self.searcher, self.totaluser, self.main_city)
        self.onAdd.Hide()

        dsizer =  wx.BoxSizer(wx.VERTICAL) #Dlg Sizer
        dsizer.Add(self._DoLayOut(), 1, wx.EXPAND)
        self.SetSizer(dsizer)
        dsizer.Fit(self)
#        self.SetInitialSize((375,250))
        self.ShowModal()
#==============================================================================
#  布局函数           
#==============================================================================
    def _DoLayOut(self):
        '''配置窗口布局管理'''       
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add((25,-1), 0)
        box1.Add(self.cfgLb, 1, wx.EXPAND | wx.ALL, 5)

        box2 = wx.BoxSizer(wx.VERTICAL)
        box2.Add(self.list, 1,  wx.EXPAND | wx.ALL, 5)

        sbox = wx.StaticBox(self.panel,-1,u"定时发送")        
        sbsizer = wx.StaticBoxSizer(sbox,wx.HORIZONTAL)
        sbsizer.Add(self.setTimeChk, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sbsizer.Add((20,-1),0)
        sbsizer.Add(self.hourCho, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sbsizer.Add(wx.StaticText(self.panel, -1, u":"), 0, wx.ALIGN_CENTER | wx.ALL, 2)
        sbsizer.Add(self.minuteCho, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sbsizer.Add(wx.StaticText(self.panel, -1, u":"), 0, wx.ALIGN_CENTER | wx.ALL, 2)
        sbsizer.Add(self.secondCho, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        psizer = wx.BoxSizer(wx.VERTICAL)#panel sizer
        psizer.Add(box1, 0, wx.EXPAND)
        psizer.Add(box2, 1, wx.EXPAND)
        psizer.Add(sbsizer, 1, wx.EXPAND)
        
        self.panel.SetSizer(psizer)
        psizer.Fit(self)

        return psizer        

#==============================================================================
#回调函数
#==============================================================================
        
    def OnClose(self, event):
        '''关闭配置窗口回调函数'''
        if self.setTimeChk.IsChecked():  # 如果勾选定时发送复选框，就将Timer设置为1  
            self.myIni.set('Config', 'Timer', 1)  
        else:  # 如果未勾选定时发送复选框，就将Timer设置为0
            self.myIni.set('Config', 'Timer', 0)
        self.onAdd.Destroy()
        self.Destroy()

    # 保存时分秒信息  
        second = self.secondCho.GetSelection()
        minute = self.minuteCho.GetSelection()
        hour = self.hourCho.GetSelection()
        if hour < 10:
            hourValue = u'0' + unicode(hour)#小时的形式为两位，个位时需补零
        else:
            hourValue = hour
            
        if minute < 10:
            minuteValue = u'0' + unicode(minute)#分钟的形式为两位，个位时需补零
        else:
            minuteValue = minute
            
        if second < 10:
            secondValue = u'0' + unicode(second)#秒钟的形式为两位，个位时需补零
        else:
            secondValue = second

        self.myIni.set('Config', 'Hour', hourValue)
        self.myIni.set('Config', 'Minute', minuteValue)
        self.myIni.set('Config', 'Second', secondValue ) 
    # 保存ini文件  
        self.myIni.write(open('Config.ini', 'w'))
    # 销势设置窗口
#        self.onAdd.Destroy()
        self.Destroy() 

    def OnSetTimeChk(self, event):
        '''定时框回调函数'''
    # 勾选复选框时，3个下拉框可用
        if self.setTimeChk.IsChecked():
            self.hourCho.Enable()
            self.minuteCho.Enable()
            self.secondCho.Enable()
    # 未勾选复选框时，3个下拉框不可用
        else:
            self.hourCho.Disable()
            self.minuteCho.Disable()
            self.secondCho.Disable() 
        
    def OnShowPopup(self,event):
        '''右键菜单回调函数'''
#         创建右键菜单
        self.popupmenu = wx.Menu()
    # 添加“增加”菜单项，这个菜单项一直都有
        item_add = self.popupmenu.Append(-1, u'增加')
    # “增加”菜单项绑定处理器方法
        self.list.Bind(wx.EVT_MENU, self.OnAdd, item_add)
    # 当选中某行时才显示“删除”、“设置主城市”菜单
        if self.list.GetFirstSelected() != -1:
        # 添加“删除”菜单项
            item_del = self.popupmenu.Append(-1, u'删除')
        # “删除”菜单项绑定处理器方法
            self.list.Bind(wx.EVT_MENU, self.OnDel, item_del)
        # 添加“设为主城市”菜单项
            item_setMain = self.popupmenu.Append(-1, u'设为主城市')
        # “设为主城市”菜单项绑定处理器方法
            self.list.Bind(wx.EVT_MENU, self.OnSetMain, item_setMain)
    # 获取事件发生的坐标，即点击右键的地方，这个坐标是相对于整个屏幕来计算的
        pos = event.GetPosition()
    # 把坐标转换为以本程序界面为基准的坐标
        pos = self.list.ScreenToClient(pos)
    # 在点击右键的地方显示右键菜单
        self.list.PopupMenu(self.popupmenu,pos)
    
    def OnAdd(self,event):
        '''“增加”菜单项的功能实现'''
        self.onAdd.Ptotaluser = self.totaluser  # 将当前user的序号更新给新增用户界面
        self.onAdd.Show()
        self.main_city = self.onAdd.Pmaincity
        self.totaluser = self.onAdd.Ptotaluser
        
    def OnDel(self, event):
        '''“删除”菜单项的功能实现'''
    # 弹出警告框，供用户确认
        retCode = wx.MessageBox(u'确定要删除该用户？\n请注意：该操作不可撤销！', u'请确认删除', wx.YES_NO | wx.ICON_QUESTION)
    # 用户点击“是”才执行删除动作
        if retCode == wx.YES:
            row = self.list.GetFirstSelected() # 获取当前选中的行索引
            mail = self.list.GetItem(row, 1).Text
            city = self.list.GetItem(row, 2).Text  # 从选中行中取得城市信息
            self.list.DeleteItem(row)  # 删除列表中的行
            self.totaluser -= 1  # 总用户数量减1
        
            if self.searcher.isMainCity(mail, city) and self.totaluser:  # 如果被删除的是主城市，且list还有至少一个项目，则设置删除之后列表第一行为主城市
                self.list.SetItemTextColour(0, wx.RED)
                self.searcher.setMainCity(self.list.GetItem(0, 1).Text, self.list.GetItem(0, 2).Text)
            self.searcher.delItem(mail, city)  # 清除数据库中相应信息
            for i in range(row, self.totaluser):  # 重新调整被删除行以后的行序号
                self.list.SetItemText(i, unicode(i + 1))
                
    def OnSetMain(self, event):
        '''“设为主城市”菜单项的功能实现'''
        self.searcher.clearMainCity()  # 清除原主城市
        row = self.list.GetFirstSelected()  # 获取选中的行索引
        mail = self.list.GetItem(row, 1).Text  # 获取邮箱地址
        city = self.list.GetItem(row, 2).Text  # 获取城市信息
        self.searcher.setMainCity(mail, city)  # 设置新的主城市
        self.list.SetItemTextColour(self.main_city, wx.BLACK)  # 原主城市行字体回归黑色
        self.list.SetItemTextColour(row, wx.RED)  # 新主城市字体设置为红色
        self.main_city = row  # 更新主城市行号全局变量
        
if __name__ == '__main__':

    app = wx.PySimpleApp(redirect = False)
    cfg = CfgDlg(MySearcher())
    app.MainLoop()