"""基础函数库文件"""

import error

import pickle
import threading
import queue
import datetime
import hashlib
import time
import os

# author : guiqiqi87@gmail.com
# humanSize(fileSize_int) : fileSize_str
# 该函数用于将传入的文件大小（字节单位）转换成可读大小
#
# 思路：
# 创建文件单位列表，不断除文件大小，运算次数即为单位
# 最后所得结果即为大小
def humanSize(size):
	size = float(size)
	assert (size >= 0)
	division = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
	standard = 1024
	modTimes = 0
	while size > standard:
		size /= standard
		modTimes += 1
	result = str(round(size, 2)) + division[modTimes]
	return result

# author : guiqiqi87@gmail.com
# numberToHans(number_int) : numberHans_str
# 该函数用于将输入的数字转化为汉字
#
# 思路：
# 遇到数字零时不处理，将其他数字按照数组位权拼接字符串
# 并设置一个标志位标志零的出现。当输入数字为10的倍数时：
# 则末尾的零可以一直不处理；当数字中夹有零时，可以插入一个零，
# 而后由于循环一直被continue，保证只插入一个零。
# 另外，由于汉语的使用习惯，20以下的数字做特殊判断处理。
def numberToHans(convertNum):
	if not isinstance(convertNum, int):
		raise ValueError("convertNum must be int.")
	weightHans = ["", "十", "百", "千", "万", "十万", "百万", "千万", "亿"]
	bitsHans = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
	if convertNum <= 10 : return bitsHans[convertNum]
	if 10 < convertNum < 20 : return ("十" + bitsHans[convertNum - 10])
	convertNum = str(convertNum)
	numLength = len(convertNum)
	result = []
	zeroFlag = True
	currentBit = -1
	for char in convertNum[::-1]:
		currentBit += 1
		char = int(char)
		if char == 0 and zeroFlag == True : continue
		zeroFlag = False
		rank = weightHans[currentBit]
		if char == 0:
			rank = ""
			zeroFlag = True
		number = bitsHans[char]
		result.append(number + rank)
	result = "".join(result[::-1])
	return result

# author : guiqiqi87@gmail.com
# getTimeString([useTime_int, format_str, ]) : timeStr_str
# 该函数返回当前时间（或指定时间）的字符串
#
# 思路：
# 判断是否传入给定时间
# 从datetime函数库获取的当前时间戳
# 格式化之后返回时间字符串
def getTimeString(useTime = False, formation = '%Y-%m-%d %H:%M:%S'):
	if useTime:
		timeTuple = time.localtime(useTime)
		timeString = time.strftime(formation, timeTuple)
	else:
		now = datetime.datetime.now()
		timeString = now.strftime(formation)
	return timeString

# author : guiqiqi87@gmail.com
# listFile(location_str) : fileList_list
# 该函数返回指定目录下的所有文件名
#
# 思路：
# 通过os.listdir获取列表，遍历去除所有的文件夹
def listFile(location):
	location = location.strip("\\")
	fileList = os.listdir(location)
	for name in fileList[:]:
		fullName = location + "/" + name
		if name.startswith("."):
			fileList.remove(name)
		if os.path.isdir(fullName):
			fileList.remove(name)
	return fileList

# author : guiqiqi187@gmail.com
# getFileInfo(location_str) : fileInfo_dict
# 该函数返回指定文件的详细信息
#
# 思路：
# 用相关的系统函数库获取文件的各种信息
def getFileInfo(location):
	assert(os.path.isfile(location))
	formation = '%Y/%m/%d %H:%M:%S'
	fileLength = os.path.getsize(location)
	createTime = os.path.getctime(location)
	modifyTime = os.path.getmtime(location)
	createTime = getTimeString(createTime, formation)
	modifyTime = getTimeString(modifyTime, formation)
	parentDir = os.path.dirname(location)
	fileName = os.path.split(location)[-1]
	fileType = os.path.splitext(location)[1].strip(".")
	result = {
		"modifyTime" : modifyTime,
		"createTime" : createTime,
		"fileLength" : fileLength,
		"parentDir" : parentDir,
		"fileName" : fileName,
		"fileType" : fileType
	}
	return result

# author : guiqiqi187@gmail.com
# fileMd5(location_str) : MD5_str
# 该函数返回指定文件的MD5值
#
# 思路：
# 利用hashlib计算MD5值
def fileMd5(location):
	assert(os.path.isfile(location))
	md5Value = hashlib.md5()
	with open(location, "rb") as file:
		while True:
			data = file.read(4096)
			if not data:
				break
			md5Value.update(data)
	result = md5Value.hexdigest()
	return result

# author : guiqiqi187@gmail.com
# rename(location_str, oldName_str, newName_str) : ok_bool
# 该函数用来重命名文件
# 
# 思路：
# 利用os.rename函数重命名
def rename(location, oldName, newName):
	oldName = os.path.join(location, oldName)
	newName = os.path.join(location, newName)
	os.rename(oldName, newName)
	return True

# author : guiqiqi187@gmail.com
# dirMd5( location_str ) : nameWithMD5_dict
# 获取文件夹下所有文件名及对应MD5值
#
# 思路：
# 获取所有文件，逐一计算MD5值
def dirMd5(location):
	fileList = listFile(location)
	nameMd5 = dict()
	for file in fileList:
		fileLocation = location + "/" + file
		md5 = fileMd5(fileLocation)
		nameMd5[md5] = file
	return nameMd5

# author : guiqiqi187@gmail.com
# countSize(location_str) : size_int
# 计算文件夹下所有文件的总大小
#
# 思路：
# 获取文件列表，遍历求和
def countSize(location):
	assert(os.path.isdir(location))
	fileList = listFile(location)
	totalSize = 0
	for file in fileList:
		fileLocation = location + "/" + file
		totalSize += os.path.getsize(fileLocation)
	return totalSize

# author : guiqiqi187@gmail.com
# @basic.clock func()
# 这是一个简易的函数计时器
#
# 思路：
# 用装饰器实现传参及函数计时
def clock(function):
	def wrapper(*args, **kwargs):
		startTime = time.time()
		result = function(*args, **kwargs)
		endTime = time.time()
		usedTime = (endTime - startTime) * 1000
		print ("-> elapsed time: %.2f ms" % usedTime)
		return result
	return wrapper

# author : guiqiqi187@gmail.com
# @basic.thread([resultQueue_Queue, ]) func() : result
# 通过该函数可以从一个新线程运行一个函数
#
# 思路：
# 开一个新线程并通过队列将函数返回值同步
def thread(resultQueue = None):
	def wrapper(function):
		def proWarp(*args, **kwargs):
			def process(*args, **kwargs):
				ret = function(*args, **kwargs)
				if resultQueue : resultQueue.put(ret)
				return resultQueue
			thread = threading.Thread(target = process,
			args = args, kwargs = kwargs)
			thread.setDaemon(True)
			thread.start()
			return process
		return proWarp
	return wrapper

# Author : guiqiqi187@gmail.com
class Register(object):
	"""注册类，该类提供一个注册表
	可以动态添加删减"""
	# __init__( **kwargs) : None
	# 类初始化函数 : 传入参数
	def __init__(self, **kwargs):
		self.functions = dict()
		self.add(**kwargs)

	# add(**kwargs) : True
	# 增添到functions字典的值
	def add(self, **kwargs):
		self.functions.update(kwargs)
		return True

	# addFunction( func ) : infodict_dict
	# 添加到类内部的注册表：传入函数
	def addFunction(self, func):
		assert(callable(func))
		info = func.__doc__
		dictionary = {info : func}
		self.functions.update(dictionary)
		return dictionary

	# reset( ) : True
	# 将注册表值初始化
	def reset(self):
		self.__init__()

	# @register : 装饰于被修饰函数前
	# 用函数doc作为value，而函数本身作为key
	# 添加至函数列表内
	def register(self, function):
		if not function in self.functions.keys():
			info = function.__doc__
			self.functions[info] = function
		return function

	# function( key_str ) : function_func
	# 返回指定文档的函数
	def function(self, key):
		assert(key in self.functions.keys())
		return self.functions[key]

	# doc( function_func ) : doc_str
	def doc(self, function):
		assert(function in self.functions.values())
		maps = tuple(self.functions.items())
		for item in maps:
			if item[1] == function : return item[0]
		return None
