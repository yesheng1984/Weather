# coding=utf-8
"""
Created on Tue Aug 04 15:05:21 2015

@author: yesheng
数据库查询模块
"""
import sqlite3 as sqlite


class MySearcher():
    '''天气数据库搜索类'''
    
    def __init__(self, database = 'data.db'):
        self.database = database
        self.conn = sqlite.connect(self.database)
        self.curs = self.conn.cursor()
    
    def addItem(self, table, values):
        '''添加项目'''
        query = 'INSERT INTO ' + table + ' VALUES (?,?,?,?)'
        self.curs.execute(query, values)
        self.conn.commit()
        
        return True
    
    def delItem(self, mail, city):
        '''删除项目'''
        query = 'DELETE FROM userInfo WHERE mail=? AND city=?'
        self.curs.execute(query, (mail, city))
        self.conn.commit()
        
        return True
    
    def searchItem(self, table, item, value):
        if item == '':
            query = 'SELECT * FROM ' + table
            self.curs.execute(query)
        else:
            query = 'SELECT * FROM ' + table + ' WHERE ' + item + ' =?'
            self.curs.execute(query, (value,))
        rows = self.curs.fetchall()
        
        return rows
    
    def getRowCount(self, table):
        query = 'SELECT * FROM ' + table
        self.curs.execute(query)
        rowCount = len(self.curs.fetchall())
        
        return rowCount
    
    def listProvs(self):
        '''省列表'''
        query = 'SELECT DISTINCT prov FROM cityInfo ORDER BY id'
        self.curs.execute(query)
        rows = self.curs.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
            
        return result
    
    def listCityOfProv(self, prov=u'北京'):
        '''城市列表'''
        query = 'SELECT DISTINCT city FROM cityInfo WHERE prov = ? ORDER BY id'
        self.curs.execute(query, (prov,))
        rows = self.curs.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
            
        return result
    
    def listZoonOfCity(self, prov=u'北京', city=u'北京'):
        '''城区列表'''
        query = 'SELECT zoon FROM cityInfo WHERE prov = ? AND city = ? ORDER BY id'
        self.curs.execute(query, (prov, city))
        rows = self.curs.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
            
        return result
    
    def getCityCode(self, prov=u'北京', city=u'北京', zoon=u'北京'):
        '''搜索城市代码'''
        query = 'SELECT id FROM cityInfo WHERE prov=? AND city=? AND zoon = ?'
        self.curs.execute(query, (prov, city, zoon))
        rows = self.curs.fetchall()
        
        return rows[0][0]
    
    def getMainCityCode(self):
        query = 'SELECT city FROM userInfo WHERE main = 1'
        self.curs.execute(query)
        rows = self.curs.fetchall()
        
        return rows[0][0]
    
    def setMainCity(self, mail, city):
        query = 'UPDATE userInfo set main=? WHERE mail=? AND city=?'
        self.curs.execute(query, (True, mail, city))
        self.conn.commit()
        
        return True
    
    def isMainCity(self, mail, city):
        query = 'SELECT main FROM userInfo WHERE mail=? AND city=?'
        self.curs.execute(query, (mail, city))
        rows = self.curs.fetchall()
        
        return rows[0][0]
    
    def getUserInfo(self):
        query = 'SELECT mail,city,note FROM userInfo'
        self.curs.execute(query)
        rows = self.curs.fetchall()
        
        return rows
        
    def clearMainCity(self):
        query = 'UPDATE userInfo SET main=0 WHERE main=1'
        self.curs.execute(query)
        self.conn.commit()
        
        return True

    def close(self):
        self.conn.close()
        
if __name__ == '__main__':
    mysch = MySearcher()

    for zoon in mysch.listZoonOfCity(u'广东',u'广州'):
        print zoon + '\n'