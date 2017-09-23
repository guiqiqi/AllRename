"""规则库文件"""

import basic
from error import *

# 常量定义
opreators = basic.Register() # 操作类注册表
descriptions = basic.Register() # 操作描述注册表
begin = lambda string : 0 # 字符串开头lambda表达式
end = lambda string : len(string) # 字符串结尾lambda表达式

# Author : guiqiqi187@gmail.com
class Description(object):
	@staticmethod
	@descriptions.register
	def delete(**kwargs):
		"""按位置删除"""
		description = "删除文件名的第 {start} 位到第 {end} 位"
		description = description.format(**kwargs)
		return description

	@staticmethod
	@descriptions.register
	def add(**kwargs):
		"""按位置增添"""
		if kwargs['index'].isdigit():
			description = "在文件名的第 {index} 位后添加字符 '{target}'"
		else:
			description = "在文件名的 {index} 添加字符 '{target}'"
		description = description.format(**kwargs)
		return description

	@staticmethod
	@descriptions.register
	def remove(**kwargs):
		"""移除指定字符"""
		description = "删除文件名中的 '{target}'"
		description = description.format(**kwargs)
		return description

	@staticmethod
	@descriptions.register
	def lower(**kwargs):
		"""小写化"""
		description = "将文件名中的字母变为小写"
		return description

	@staticmethod
	@descriptions.register
	def upper(*kwargs):
		"""大写化"""
		description = "将文件名中的字母变为大写"
		return description

	@staticmethod
	@descriptions.register
	def clear(**kwargs):
		"""清空所有字符"""
		description = "清空文件名"
		return description

	@staticmethod
	@descriptions.register
	def replace(**kwargs):
		"""替换指定字符"""
		description = "将文件名中的 '{target}' 替换为字符 '{new}'"
		description = description.format(**kwargs)
		return description

	@staticmethod
	@descriptions.register
	def number(**kwargs):
		"""添加数字编号"""
		description = "在文件名的末尾添加从 1 开始的数字编号"
		description = description.format(**kwargs)
		return description

	@staticmethod
	@descriptions.register
	def numberHans(**kwargs):
		"""添加汉字编号"""
		description = "在文件名的末尾添加从 1 开始的汉字编号"
		description = description.format(**kwargs)
		return description

# Author : guiqiqi187@gmail.com
class StringOpreators(object):
	"""字符串操作类"""
	@staticmethod
	@opreators.register
	def delete(original, **kwargs):
		"""按位置删除"""
		start = kwargs['start']
		end = kwargs['end']
		if not isinstance(start, int):
			start = start(original)
		if not isinstance(end, int):
			end = end(original)
		head = original[0 : start]
		tail = original[end : len(original)]
		return head + tail

	@staticmethod
	@opreators.register
	def add(original, **kwargs):
		"""按位置增添"""
		target = kwargs['target']
		index = kwargs['index']
		if index == "开头" : index = begin
		if index == "结尾" : index = end
		if not isinstance(index, int):
			index = index(original)
		ending = len(original)
		head = original[0 : index]
		tail = original[index : ending]
		return head + target + tail

	@staticmethod
	@opreators.register
	def remove(original, **kwargs):
		"""移除指定字符"""
		target = kwargs['target']
		return original.replace(target, '')

	@staticmethod
	@opreators.register
	def lower(original, **kwargs):
		"""小写化"""
		return original.lower()

	@staticmethod
	@opreators.register
	def upper(original, **kwargs):
		"""大写化"""
		return original.upper()

	@staticmethod
	@opreators.register
	def clear(original, **kwargs):
		"""清空所有字符"""
		return str()

	@staticmethod
	@opreators.register
	def replace(original, **kwargs):
		"""替换指定字符"""
		target = kwargs['target']
		new = kwargs['new']
		return original.replace(target, new)

	@classmethod
	def number(cls, original, **kwargs):
		"""添加数字编号"""
		cls._hcurrent = int(cls._hcurrent)
		number = str(cls._hcurrent)
		cls._hcurrent += 1
		new = StringOpreators.add(original, target = number, index = end)
		return new

	@classmethod
	def numberHans(cls, original, **kwargs):
		"""添加汉字编号"""
		cls._ncurrent = int(cls._ncurrent)
		number = basic.numberToHans(cls._ncurrent)
		cls._ncurrent += 1
		new = StringOpreators.add(original, target = number, index = end)
		return new

# Author : guiqiqi187@gmail.com
class Rules(StringOpreators):
	"""对StringOpreator类的进一步封装
	添加一部分动态功能
	需要初始化后使用"""
	def __init__(self):
		StringOpreators._hcurrent = 1
		StringOpreators._ncurrent = 1

	@staticmethod
	@opreators.register
	def number(original, **kwargs):
		"""添加数字编号"""
		result = StringOpreators.number(original, **kwargs)
		return result

	@staticmethod
	@opreators.register
	def numberHans(original, **kwargs):
		"""添加汉字编号"""
		result = StringOpreators.numberHans(original, **kwargs)
		return result

	def resetCurrent(self):
		StringOpreators._hcurrent = 1
		StringOpreators._ncurrent = 1

# Author : guiqiqi187@gmail.com
class Executor(object):
	"""规则执行器，将规则全部加入之后对文件名批量操作"""
	# Manager类初始化函数
	def __init__(self):
		self.opreations = list()
		self.files = list()

	# 向操作中添加
	def addopreation(self, opreation, args):
		info = {'opreation' : opreation, 'args' : args}
		self.opreations.append(info)

	# 载入文件列表
	def loadfiles(self, files):
		self.files = files

	# 添加文件
	def addfile(self, file):
		self.files.append(file)

	# 操作
	def do(self):
		results = list()
		for file in self.files:
			name, extend = Analyser.getname(file)
			oldname = file
			for opreation in self.opreations:
				func = opreation['opreation']
				args = opreation['args']
				name = func(name, **args)
			newname = name + "." + extend
			results.append((oldname, newname))
		return results

# Author : guiqiqi187@gmail.com
class Analyser(object):
	"""一个文件名分析器，初始化时传入的参数有：
		当前文件夹地址，文件名列表"""
	# Analyser类初始化函数
	def __init__(self, location, filenames):
		assert(isinstance(filenames, list))
		assert(isinstance(location, str))
		self.filenames = filenames
		self.location = location
		self.getinfo()

	# getinfo() : fileInfos_dict
	# 该函数返回当前设定所有的文件详细信息
	def getinfo(self):
		if not (self.location and self.filenames) : return False
		filenames = self.filenames
		self.fileInfos = dict()
		for file in filenames:
			fullpath = self._sjoin(file)
			self.fileInfos[file] = basic.getFileInfo(fullpath) 
		self.infos = self.fileInfos.values()
		return self.fileInfos

	# bylength(fileInfos_dict, infoValue_list) : filters_function
	# 该函数返回一个闭包函数 filters，用于过滤符合 filters参数
	# condition_function 的文件；可以用于按照大小过滤文件
	# 
	# 思路：
	# 返回一个闭包函数，参数为指定大小的lambda表达式，而包装函数
	# 作为参数传入总的过滤器中
	def bylength(self, fileInfos, infoValue):
		search = "fileLength"
		def filters(condition):
			assert callable(condition)
			classfiy = list()
			for file, info in fileInfos.items():
				length = info[search]
				if condition(length) : classfiy.append(file)
			return list(classfiy)
		return filters

	# bytype(fileInfos_dict, infoValue_list) : filters_function
	# 该函数返回一个闭包函数 filters，用于过滤符合 filters参数
	# match_set 的文件；可以将文件按照文件类型分组
	# 当闭包函数参数为空时，按照现有的文件类型分组
	# 
	# 思路：
	# 返回一个闭包函数，参数为需要过滤出的文件类型，而包装函数
	# 作为参数传入总的过滤器中
	def bytypes(self, fileInfos, infoValue):
		search = "fileType"
		def filters(match = None):
			allTypes = self.types()
			allTypes = set(allTypes)
			match = set(match) if match else allTypes
			searchType = match & allTypes
			classfiy = dict()
			for item in searchType : classfiy[item] = list()
			for file, info in fileInfos.items():
				filetype = info[search]
				if filetype in searchType:
					classfiy[filetype].append(file)
			return classfiy
		return filters

	# classfiy(by_function) : filter_function
	# 该函数为过滤器引发函数，返回值为闭包过后的过滤器
	def classify(self, by):
		fileInfos = self.fileInfos
		infoValue = self.infos
		return by(fileInfos, infoValue)

	# _sjoin(filename_str) : fullpath_str
	# 内部函数组装完整文件路径
	def _sjoin(self, filename):
		location = self.location
		return self.joiner(location, filename)

	# joiner(filename_str) : fullpath_str
	# 静态函数组装完整文件路径	
	@staticmethod
	def joiner(location, filename):
		assert(isinstance(filename, str))
		return location + "/" + filename

	# types() : fileTypes_list
	# 函数返回找到的所有的文件类型
	def types(self):
		infos = self.infos
		fileTypes = [file["fileType"] for file in infos]
		fileTypes = set(fileTypes)
		return fileTypes

	# sizeCount() : size_int
	# 函数返回总的文件大小
	def sizeCount(self):
		infos = self.infos
		size = [file["fileLength"] for file in infos]
		size = sum(size)
		return size

	# fileCount() : count_int
	# 函数返回文件个数
	def fileCount(self):
		return len(self.filenames)

	# path([newPath, ]) : location_str
	# 当参数存在时，设定当前路径为参数初始化其他信息
	# 返回当前路径
	def path(self, newPath = False):
		if newPath : self.__init__(newPath, list())
		return self.location

	# files([newFiles, ]) : files_list
	# 当参数存在时，设定当前文件为参数并重新计算文件信息
	# 返回当前文件列表
	def files(self, newFiles = False):
		if newFiles:
			self.filenames = newFiles
			self.getinfo()
		return self.filenames

	# example() : filename_str
	# 该函数返回文件名列表的一个例子
	def example(self):
		return self.filenames[0]

	# getname( fullname_str ) : name_str
	# 该函数返回文件的文件名（除去扩展名）
	@staticmethod
	def getname(fullname):
		nameList = fullname.split('.')
		name = ".".join(nameList[0 : -1])
		extend = nameList[-1]
		return name, extend
