#coding=gbk
"""
Created on Wed Jul 29 20:19:32 2015

@author: yesheng
py2exe转换脚本
"""
from distutils.core import setup
import py2exe
import glob

options = {"py2exe":{"bundle_files":1}}
setup(windows = [{"script":'WeatherReport.py'}],options = options,zipfile = None)
