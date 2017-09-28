"""界面功能函数文件"""

import basic
from error import *
import pickle
import os
from collections import deque
import webbrowser
import rules

bname = ".fnbackup"
rname = ".rules"
bigDir = 1024 ** 3
hname = "help"
infoKey = {
	"modifyTime" : "修改时间",
	"createTime" : "创建时间",
	"fileLength" : "文件大小",
	"parentDir" : "上级目录",
	"fileName" : "文件名",
	"fileType" : "文件类型"
}
arguments = deque(maxlen = 1)
analyser = rules.Analyser('', []) # 文件分析器
opreators = rules.opreators.functions # 所有注册操作
opreatorList = list(opreators.keys()) # 显示用操作列表
division = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'] # 文件单位
rulefunctions = rules.Rules() # 操作函数实例
opreatorList.sort()


webOpen = lambda target : webbrowser.open(target)
cleanTree = lambda treeview : treeview.delete(*treeview.get_children())
removeSelect = lambda treeview : [treeview.delete(treeview.selection()[0]) if treeview.focus() else None]
getSelectValue = lambda treeview : treeview.item(treeview.focus())
openDir = lambda location : os.system("explorer.exe %s" % location)

# author : guiqiqi187@gmail.com
# 返回文件详情页面需要的字符
def fileInfo(location, fileName):
	fileLocation = location + "/" + fileName
	fileInfo = basic.getFileInfo(fileLocation)
	string = list()
	for key, value in fileInfo.items():
		if key == "fileLength" : value = basic.humanSize(value)
		string.append(infoKey[key] + " : " + value)
	string = "\n".join(string)
	return string

# author : guiqiqi187@gmail.com
# 计算界面的偏移量字符串
def calSize(width, height, sHeight, sWidth):
	# raise DeprecationWarning
	xoffset = str(int((sWidth - width)/2))
	yoffset = str(int((sHeight - height)/2) - 50)
	sizeInfo = [str(height), "x", str(width), "+", xoffset, "+", yoffset]
	return "".join(sizeInfo)

# author : guiqiqi187@gmail.com
# backupFileName( location_str ) : nameWithMD5_dict
# 备份某一文件夹下所有的文件名
#
# 思路：
# 获取该文件夹下所有的文件及MD5值
# 以JSON格式pickle到备份文件
def backupFilename(location):
	if not location : return None
	backFilename = location + "/" + bname
	nameMd5 = basic.dirMd5(location)
	with open(backFilename, "wb") as fileHandler:
		pickle.dump(nameMd5, fileHandler, True)
	return nameMd5

# author : guiqiqi187@gmail.com
# analysis(location_str, files_list) : analysis_str
# 返回文件名的分析信息
def analysistr(location, files):
	analyser = rules.Analyser(location, files)
	bytypes = analyser.bytypes
	bylength = analyser.bylength
	types = analyser.types()
	sizeCount = basic.humanSize(analyser.sizeCount())
	fileCount = analyser.fileCount()
	typeCount = len(types)
	message = \
	"""
当前选中的文件共计{0}个；
文件共有{1}种类型，分别为：\n{2}
总大小为：{3}
	""".format(fileCount, typeCount, " ; ".join(types), sizeCount)
	return message.strip()

# author : guiqiqi187@gmail.com
# restoreFileName( location_str ) : nameWithMD5_dict
# 还原某一文件夹下所有的文件名
#
# 思路：
# 获取该文件夹下所有的文件及MD5值
# 还原所有MD5值对应文件
def restoreFilename(location, cbname = None):
	if not location : return None
	backFile = location + "/" + bname
	if cbname : backFile = cbname
	if not os.path.isfile(backFile) : raise FileNotExistsError
	nameMd5 = pickle.load(open(backFile, "rb"))
	md5List = nameMd5.keys()
	fileList = basic.listFile(location)
	for file in fileList:
		fileLocation = location + "/" + file
		md5 = basic.fileMd5(fileLocation)
		if not md5 in md5List : continue
		oldname = file
		newname = nameMd5[md5]
		basic.rename(location, oldname, newname)
		fileNameIndex = fileList.index(oldname)
		fileList[fileNameIndex] = newname
	return nameMd5

# Author : guiqiqi187@gmail.com
# cleanTreeColumn( treeview_ttk.treeview, column_int ) : None
# 清除某treeview中的第column列
def cleanTreeColumn(treeview, column):
	assert(isinstance(column, int))
	children = treeview.get_children()
	for child in children:
		raw = treeview.item(child)['values']
		raw[column] = str()
		treeview.item(child, values = raw)

# Author : guiqiqi187@gmail.com
# setFiletree( newdir_str, treeview_ttk.treeview ) : None
# 设置文件treeview
def setFiletree(newdir, treeview):
	filelist = basic.listFile(newdir)
	analyser.path(newdir)
	analyser.files(filelist)
	if not filelist: return None
	for name in filelist:
		newname = name
		treeview.insert('', 'end', values = (name, ""))

# Author : guiqiq187@gmail.com
# getRawFiles( treeview_ttk.treeview ) : allInfos_list
# 获取treeview中原文件名
def getRawFiles(treeview):
	files = treeview.get_children()
	allInfos = list()
	for file in files:
		allInfos.append(treeview.item(file)['values'][0])
	return allInfos

# Author : guiqiqi187@gmail.com
# isBig( location_str ) : isBig_boolean
# 判断文件夹内文件总大小是不是过大
def isBig(location):
	isBig = False
	count = basic.countSize(location)
	if count > bigDir : isBig = True
	return isBig

# Author : guiqiqi187@gmail.com
# moveItem( firstListbox_ttk.Listbox, secondListbox_ttk.Listbox) : None
# 将一个Listbox正在选中的项目移到第二个Listbox中
def moveItem(flistbox, slistbox):
	if not flistbox.curselection() : return None
	itemNum = flistbox.curselection()[0]
	item = flistbox.get(itemNum)
	slistbox.insert(itemNum, item)
	flistbox.delete(itemNum)

# Author : guiqiqi187@gmail.com
# filterFile( selectTypeList_ttk.Listbox, fileTreeView_ttk.Treeview) : None
# 按类型将文件过滤并更新fileTreeview
def filterFile(selectTypeList, fileTreeview):
	bytypes = analyser.classify(analyser.bytypes)
	allTypes = selectTypeList.get(0, 'end')
	files = bytypes(allTypes)
	allfiles = list()
	for key, value in files.items():
		allfiles.extend(value)
	cleanTree(fileTreeview)
	for file in allfiles:
		fileTreeview.insert('', 'end', values = (file, ""))
	analyser.files(allfiles)

# Author : guiqiqi187@gmail.com
# effection( opreation_ttk.Treeview ) : msg_str
# 该函数提供单个规则的效果预览
def effection(opreation):
	if not opreation.focus() : return None
	current = opreation.item(opreation.focus())
	target = analyser.example()
	if not target : return None
	name, extend = analyser.getname(target)
	opreation = current['values'][0]
	args = eval(current['values'][2])
	opreation = rules.opreators.function(opreation)
	new = opreation(name, **args) + "." + extend
	msg = """例如：\n旧文件名：{0}\n新文件名：{1}""".format(target, new)
	rulefunctions.resetCurrent()
	return msg

# Author : guiqiqi187@gmail.com
# backupRules( opreation_ttk.Treeview ) : opreations_list
# 该函数提供备份操作的功能
def backupRules(location, opreationTreeview):
	if not location : return None
	backRulename = location + "/" + rname
	opreations = opreationTreeview.get_children()
	if not opreations : return None
	backupList = list()
	for opreation in opreations:
		opreation = opreationTreeview.item(opreation)['values']
		backupList.append(opreation)
	try:
		with open(backRulename, "wb") as fileHandler:
			pickle.dump(backupList, fileHandler, True)
	except:
		return None
	return backupList

# Author ; guiqiqi187@gmail.com
# restoreRules( file_str, opreation_ttk.Treeview, files_ttk.Treeview ) : opreation_list
# 该函数提供还原操作的功能
def restoreRules(file, opreationTreeview, fileTreeview):
	if not file : return None
	opreation = pickle.load(open(file, "rb"))
	cleanTree(opreationTreeview)
	for info in opreation:
		opreationTreeview.insert('', 'end', values = info)
	cleanTreeColumn(fileTreeview, 1)
	rulefunctions.resetCurrent()
	return opreation

# Author : guiqiqi187@gmail.com
# preview( opreations_ttk.Treeview, files_ttk.Treeview ) : fileNameChanged_list
# 该函数将所有文件名导入Executor类
# 并提供文件名预览功能
def preview(opreationTreeview, fileTreeview):
	executor = rules.Executor()
	opreations = opreationTreeview.get_children()
	files = fileTreeview.get_children()
	if not (opreations and files) : return None
	for opreation in opreations:
		opreation = opreationTreeview.item(opreation)['values']
		function = rules.opreators.function(opreation[0])
		args = eval(opreation[2])
		executor.addopreation(function, args)
	for file in files:
		filename = fileTreeview.item(file)['values'][0]
		executor.addfile(filename)
	result = executor.do()
	cleanTree(fileTreeview)
	for info in result:
		fileTreeview.insert('', 'end', values = info)
	rulefunctions.resetCurrent()
	return result

# Author : guiqiqi187@gmail.com
# done( files_ttk.Treeview ) : None
# 该函数用于批量更改文件名
def done(location, fileTreeview):
	files = fileTreeview.get_children()
	for file in files:
		name = fileTreeview.item(file)['values']
		try:
			basic.rename(location, name[0], name[1])
		except Exception as error:
			error.logger.error(error)
	return None

# Author : guiqiqi187@gmail.com
# treeviewMouseDown( event_tk.event ) : None
# 该函数捕捉Treeview中传来的MouseDown事件
def treeviewMouseDown(event):
	treeview = event.widget
	if treeview.identify_row(event.y) not in treeview.selection():
		treeview.selection_set(treeview.identify_row(event.y))

# Author : guiqiqi187@gmail.com
# treeviewMouseMove( event_tk.event ) : None
# 该函数捕捉Treeview中传来的MouseMove事件
def treeviewMouseMove(event):
	treeview = event.widget
	moveto = treeview.index(treeview.identify_row(event.y))
	for selection in treeview.selection():
		treeview.move(selection, '', moveto)
