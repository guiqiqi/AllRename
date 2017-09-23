"""自定义异常类文件"""

import logging
import traceback

filerec = False
consolerec = False

logFormat = "%(asctime)s %(levelname)s : %(message)s"
logFile = "error.log"
logger = logging.getLogger('')

def work():
	logger.setLevel(logging.INFO)
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	filehandler = logging.FileHandler(logFile)
	filehandler.setLevel(logging.ERROR)
	formatter = logging.Formatter(logFormat)
	filehandler.setFormatter(formatter)
	console.setFormatter(formatter)
	if filerec : logger.addHandler(filehandler)
	if consolerec : logger.addHandler(console)

# author : guiqiqi187@gmail.com
# error( *args ) : None
#
# 接管root.mainloop中的错误
def handler(*args):
	tb, *error = args
	errorinfo = traceback.format_exception(tb, *error)
	errorinfo = "".join(errorinfo).strip()
	logger.error(errorinfo)

class Success(Exception):
	def __init__(self, msg = str()):
		self.__successmsg__ = msg
		self.__stat__ = True
	def _setstat(self, stat):
		self.__stat__ = stat
	def showstat(self):
		return self.__stat__
	def showmsg(self):
		return self.__successmsg__

class Error(Exception):
	def __init__(self):
		self.__errmsg__ = None
		self.__stat__ = False
	def _setmsg(self, msg):
		self.__errmsg__ = msg
	def _setstat(self, stat):
		self.__stat__ = stat
	def showmsg(self):
		return self.__errmsg__
	def showstat(self):
		return self.__stat__

class FileNotExistsError(Error, FileNotFoundError):
	"""要操作的文件不存在异常"""
	def __init__(self):
		super().__init__()
		self._setmsg("无法找到被操作文件.")

class FileHasExistedError(Error, FileExistsError):
	"""要修改的文件名已经存在异常"""
	def __init__(self):
		super().__init__()
		self._setmsg("要修改的文件名已经存在.")

class PermissionDenied(Error, PermissionError):
	"""操作权限不足异常"""
	def __init__(self):
		super().__init__()
		self._setmsg("权限错误.")
