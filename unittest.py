"""单元测试文件"""

import time
import queue

import basic
# for i in range(1000) : print (basic.numberToHans(i))
# print (basic.humanSize(4771840))
# print (basic.getTimeString())
# print (basic.getTimeString(817817387))
# print (basic.listFile("C:\\我的文件\\Python源码"))
# print (basic.getFileInfo("C:\\CloudMusic\\风之诗-现场版.mp3"))
# print (basic.fileMd5("C:\\CloudMusic\\风之诗-现场版.mp3"))
# basic.rename("C:\\CloudMusic", "牛奶咖啡 - 明天你好.mp3", "明天你好.mp3")
# @basic.clock
# def test(l):
# 	print (basic.dirMd5(l)) # 12.2S - 4.44G
# test("C:\\Users\\桂琦\\Pictures")
# print (basic.countSize("C:\\我的文件\\战斗民族养成记"))
# basic.rename("C:\\Windows\\System32","azman.msc","1.msc")
# basic.rename("C:\\我的文件", "3.txt", "4.txt")
# basic.rename("C:\\我的文件", "2.txt", "1.txt")
# a = queue.Queue()
# @basic.thread(a)
# def test(arg):
# 	print (arg)
# 	return arg[::-1]
# test("Hello World!")
# print ("Hello, Fools!")
# print (a.get())

import functions
# functions.backupFilename("C:\\CloudMusic")
# basic.rename("C:\\CloudMusic", "牛奶咖啡 - 明天你好.mp3", "明天你好.mp3")
# functions.restoreFilename("C:\\CloudMusic")
# functions.fileInfo("C:\\CloudMusic","牛奶咖啡 - 明天你好.mp3")

# from error import *
# def rasieError():
# 	raise FileNotFoundError

# try:
# 	rasieError()
# except FileNotFoundError as error:
# 	print (error.showmsg())
# 	print (error.showstat())

# try:
# 	raise Success("")
# except Exception as error:
# 	print (error.showstat())

# try:
# 	raise PermissionError()
# except Exception as error:
# 	print (error.showstat())

import rules

# path = "C:\\我的文件\\照片\\彼得堡"
# files = basic.listFile(path)
# analyser = rules.Analyser(path, files)
# bytypes = analyser.bytypes
# bylength = analyser.bylength
# lengthfilters = analyser.classfiy(bylength)
# typefilters = analyser.classfiy(bytypes)
# lengthrule = lambda size : size > 1024 ** 2

# print (typefilters([]))
# print (lengthfilters(lengthrule))

# print (analyser.types())
# print (basic.humanSize(analyser.sizeCount()))
# print (analyser.fileCount())

# maps = dict()
# def register(function):
# 	if not function in maps.keys():
# 		info = function.__doc__
# 		maps.update({function : info})
# 	return function

# @register
# def show(*args, **kwargs):
# 	print (args)
# 	print (kwargs)

# print (rules.StringOpreators.add(original = "媳妇我你", target = "爱", index = 3))
# print (rules.StringOpreators.delete(original = "Windows10可能是最垃圾的系统", start = 9, end = 11))

# test = rules.Rules()
# test.setStart(0)
# target = "文件"
# for i in range(1,100):
# 	print (test.numberHans(test.add(target, "_", rules.end), rules.end))
