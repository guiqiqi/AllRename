"""GUI 界面文件"""

import functions
import basic
import rules
import error

import tkinter.filedialog as filedialog
from tkinter import *
import tkinter.messagebox as msgbox
from tkinter.ttk import *

root = Tk()

# 常量定义
lastselect = StringVar() # rulePanel中上一次选择
selectdir = StringVar() # 当前文件夹路径
strarting = True # 程序未初始化完成的标志位
geometry = basic.Register() # 规则面板布局函数注册表
geometryflag = "_布局" # 布局函数查询标志
arguments = functions.arguments # 界面参数提取
descriptions = rules.descriptions # 描述生成注册表
headValue = BooleanVar() # 选择开头插入
endValue = BooleanVar() # 选择结尾插入
specifySelect = ["按位置增添"] # 使用开始结尾选项的规则
currentEvent = None # 当前选择的规则事件
analyser = functions.analyser # 文件分析器
headValue.set(False)
endValue.set(False)

# 函数
_exit = lambda : root.destroy()
_askfile = lambda : filedialog.askopenfilename()
_showexdir = lambda : msgbox.showinfo("提示", "当前文件夹路径为：" + selectdir.get())
_shownodir = lambda : msgbox.showerror("错误", "还未设置文件夹路径！")
_askbig = lambda : msgbox.askyesno("提示", "需要计算的数据量超过1G，继续吗？")
_showdir = lambda : [_showexdir() if selectdir.get() else _shownodir()]
_showfileinfo = lambda : [msgbox.showinfo("文件信息", functions.fileInfo(selectdir.get(),
	functions.getSelectValue(_file)['values'][0])) if _file.focus() else None]
_fail = lambda msg : msgbox.showerror("错误", str(msg) + "失败！")
_success = lambda msg : msgbox.showinfo("成功", str(msg) + "成功！")
_backrule = lambda : [msgbox.showinfo("成功", "成功备份至.rules文件") if functions.backupRules(
	selectdir.get(), _operation) else msgbox.showerror("失败", "备份失败！")]
_restorerule = lambda : functions.restoreRules(_askfile(), _operation, _file)

@basic.thread()
def _backup():
	if strarting : return None
	location = selectdir.get()
	backup, ret = True, True
	if not location : return _shownodir()
	if functions.isBig(location) : backup = _askbig()
	if not backup : return None
	_toolmenu.entryconfig(0, label = "正在备份中", state = DISABLED)
	_toolmenu.entryconfig(1, state = DISABLED)
	try : ret = functions.backupFilename(location)
	except : ret = False
	_toolmenu.entryconfig(0, label = "备份文件名", state = NORMAL)
	_toolmenu.entryconfig(1, state = NORMAL)
	if not ret : return _fail("备份")
	return _success("备份")

@basic.thread()
def _restore():
	if strarting : return None
	location = selectdir.get()
	restore, ret = True, True
	if not location : return _shownodir()
	if functions.isBig(location) : restore = _askbig()
	if not restore : return None
	_toolmenu.entryconfig(0, state = DISABLED)
	_toolmenu.entryconfig(1, label = "正在恢复中", state = DISABLED)
	try : ret = functions.restoreFilename(location)
	except FileNotFoundError:
		try : functions.restoreFilename(location, _askfile())
		except : ret = False
	except : ret = False
	_toolmenu.entryconfig(0, state = NORMAL)
	_toolmenu.entryconfig(1, label = "恢复文件名", state = NORMAL)
	if not ret : return _fail("恢复")
	functions.cleanTree(_file)
	functions.setFiletree(selectdir.get(), _file)
	return _success("恢复")

def _analysis():
	files = functions.getRawFiles(_file)
	if not files : return str()
	message = functions.analysistr(selectdir.get(), files)
	_countPanel.deiconify()
	_countText.configure(state = NORMAL)
	_countText.delete(0.0, END)
	_countText.insert(END, message)
	_countText.configure(state = DISABLED)

def _cleandir():
	if not msgbox.askyesno("确认", "清除路径吗？"):
		return None
	selectdir.set("")
	functions.cleanTree(_file)

def _askdir():
	newdir = filedialog.askdirectory()
	if not newdir : return None
	selectdir.set(newdir)
	functions.cleanTree(_file)
	functions.setFiletree(newdir, _file)

def _changeRule(event):
	widget = event.widget
	global currentEvent
	currentEvent = event
	index = int(widget.curselection()[0])
	value = widget.get(index)
	lastselect.set(value)
	for child in _ruleInfo.winfo_children():
		child.destroy()
	query = value + geometryflag
	geoFunc = geometry.function(query)
	frame = _ruleInfo
	geoFunc(frame)

def _addRule():
	select = lastselect.get()
	if not select : return None
	args = arguments.pop()
	if select in specifySelect:
		if endValue.get():
			args['index'] = lambda : "结尾"
		if headValue.get():
			args['index'] = lambda : "开头"
	for label, express in args.items():
		args[label] = express()
	descriptionMaker = descriptions.function(select)
	description = descriptionMaker(**args)
	Geometry.setfalse(headValue, endValue)
	_changeRule(currentEvent)
	_operation.insert('', 'end', values = (select, description, args))
	functions.cleanTreeColumn(_file, 1)

def _loadTypes():
	listbox = _filterLeftListbox
	listbox.delete(0, END)
	if not selectdir.get() : return None
	types = analyser.types()
	listbox.insert(END, *types)
	_filterRightListbox.delete(0, END)

def _loadFilterPanel():
	_filterPanel.deiconify()
	_loadTypes()

def _showPreview():
	msg = functions.effection(_operation)
	if not msg : return None
	msgbox.showinfo("规则预览", msg)

def _done():
	location = selectdir.get()
	do = msgbox.askyesno("确认？", "重命名操作不可逆，请确认是否继续？")
	if not do : return False
	functions.done(location, _file)
	location = location.replace("/","\\")
	functions.openDir(location)
	functions.cleanTree(_file)
	functions.cleanTree(_operation)
	selectdir.set("")
	do = msgbox.askyesno("退出软件？", "成功重命名，退出软件？")
	if do : _exit()

# 设定
_sWidth = root.winfo_screenwidth()
_sHeight = root.winfo_screenheight()
_width = 620
_height = 670
_sizeInfo = functions.calSize(_height, _width, _sHeight, _sWidth)
_geometry = "".join(_sizeInfo)
_resizableX = False
_resizableY = False
_title = "allRename : 文件批量重命名工具"
_srcIcon = "src/icon.ico"
_address = "https://github.com/guiqiqi/allRename"

# 资源文件
_iconAdd = PhotoImage(file = "src/add.gif")
_iconMinus = PhotoImage(file = "src/minus.gif")
_iconInfo = PhotoImage(file = "src/info.gif")
_iconDir = PhotoImage(file = "src/dir.gif")
_iconRule = PhotoImage(file = "src/rules.gif")
_iconCheck = PhotoImage(file = "src/check.gif")
_iconDone = PhotoImage(file = "src/done.gif")
_iconClear = PhotoImage(file = "src/clear.gif")
_abouticon = PhotoImage(file = "src/icon.gif")
_iconAll = PhotoImage(file = "src/all.gif")
_iconArrow = PhotoImage(file = "src/arrow.gif")

# 规则选择器界面布局
class Geometry(object):
	@staticmethod
	def setfalse(*args):
		for item in args : item.set(False)

	def welcome(frame):
		header = "规则面板"
		body = "在这里您可以添加规则，\n使用多种规则的组合来重命名文件"
		Label(frame, text = header, font = ("Microsoft YaHei", 10)).pack()
		Label(frame, text = body).pack(anchor = N, ipady = 100)

	@geometry.register
	def add(frame):
		"""按位置增添_布局"""
		text = "此规则将在文件名的指定位置增加指定字符"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		inner = Frame(frame)
		Label(inner, text = "增添字符串：").grid(row = 1, column = 1)
		insert = Entry(inner, width = 20)
		insert.grid(row = 1, column = 2, pady = 10)
		isdigit = lambda content : [True if content.isdigit()  or content == "" else False][0]
		isdigit = inner.register(isdigit), '%P'
		Label(inner, text = "要插入位置：").grid(row = 2, column = 1)
		index = Entry(inner, width = 15, validate = 'key', validatecommand = isdigit)
		index.grid(row = 2, column = 2, pady = 10)
		headValue.set(False)
		endValue.set(False)
		head = Radiobutton(inner, variable = headValue, text = "开始处", command = lambda : endValue.set(False))
		end = Radiobutton(inner, variable = endValue, text = "结尾处", command = lambda : headValue.set(False))
		head.grid(row = 3, column = 1)
		end.grid(row = 3, column = 2)
		Label(inner, text = "*此处的位置为修改点前一字符位置！").grid(row = 4, column = 1, columnspan = 2)
		args = {'target' : lambda : insert.get(), 'index' : lambda : [int(index.get()) if index.get() else ""][0]}
		arguments.append(args)
		index.bind("<Button-1>", lambda event : Geometry.setfalse(endValue, headValue))
		inner.pack()

	@geometry.register
	def delete(frame):
		"""按位置删除_布局"""
		text = "此规则将在文件名的指定位置删除指定个数的字符"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		inner = Frame(frame)
		isdigit = lambda content : [True if content.isdigit() or content == "" else False][0]
		isdigit = inner.register(isdigit), '%P'
		Label(inner, text = "开始删除的位置：").grid(row = 1, column = 1)
		delete = Entry(inner, width = 10, validate = 'key', validatecommand = isdigit)
		delete.grid(row = 1, column = 2, pady = 10)
		Label(inner, text = "删除字符的个数：").grid(row = 2, column = 1)
		number = Entry(inner, width = 10, validate = 'key', validatecommand = isdigit)
		number.grid(row = 2, column = 2, pady = 10)
		Label(inner, text = "*此处的位置为修改点前一字符位置！").grid(row = 3, column = 1, columnspan = 2)
		args = {'start' : lambda : int(delete.get()), 'end' : lambda : int(delete.get()) + int(number.get())}
		arguments.append(args)
		inner.pack()

	@geometry.register
	def remove(frame):
		"""移除指定字符_布局"""
		text = "此规则将删除文件名中的指定字符"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		inner = Frame(frame)
		Label(inner, text = "要删除的字符串：").grid(row = 1, column = 1)
		remove = Entry(inner, width = 20)
		remove.grid(row = 1, column = 2, pady = 10)
		args = {'target' : lambda : remove.get()}
		arguments.append(args)
		inner.pack()

	@geometry.register
	def lower(frame):
		"""小写化_布局"""
		text = "此规则将文件名中所有英文字母变为小写"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		msg = "此规则无可选参数"
		args = {}
		arguments.append(args)
		Label(frame, text = msg).pack(ipady = 50)

	@geometry.register
	def upper(frame):
		"""大写化_布局"""
		text = "此规则将文件名中所有英文字母变为大写"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		msg = "此规则无可选参数"
		args = {}
		arguments.append(args)
		Label(frame, text = msg).pack(ipady = 50)

	@geometry.register
	def clear(frame):
		"""清空所有字符_布局"""
		text = "此规则将会将文件名设置为空"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		msg = "此规则无可选参数"
		args = {}
		arguments.append(args)
		Label(frame, text = msg).pack(ipady = 50)

	@geometry.register
	def replace(frame):
		"""替换指定字符_布局"""
		text = "此规则将文件名中指定字符替换为另外的字符"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		inner = Frame(frame)
		Label(inner, text = "被替换的字符：").grid(row = 1, column = 1)
		repalce = Entry(inner, width = 15)
		repalce.grid(row = 1, column = 2, pady = 10)
		Label(inner, text = "要替换的字符：").grid(row = 2, column = 1)
		new = Entry(inner, width = 15)
		new.grid(row = 2, column = 2, pady = 10)
		Label(inner, text = "*文件名中所有该字符均会被替换！").grid(row = 3, column = 1, columnspan = 2)
		args = {'target' : lambda : repalce.get(), 'new' : lambda : new.get()}
		arguments.append(args)
		inner.pack()

	@geometry.register
	def numberHans(frame):
		"""添加汉字编号_布局"""
		text = "此规则将为文件名从 1 开始添加汉字编号"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		msg = "此规则无可选参数"
		args = {}
		arguments.append(args)
		Label(frame, text = msg).pack(ipady = 50)

	@geometry.register
	def number(frame):
		"""添加数字编号_布局"""
		text = "此规则将为文件名从 1 开始添加数字编号"
		Label(frame, text = text, font = ("Microsoft YaHei", 10)).pack()
		Separator(frame, orient = HORIZONTAL).pack(pady = 10, fill = X)
		msg = "此规则无可选参数"
		args = {}
		arguments.append(args)
		Label(frame, text = msg).pack(ipady = 50)

# 文件统计页面
_countPanel = Toplevel(root)
_countPanel.withdraw()
_countPanel.title("文件统计")
_countHeight, _countWidth = 300, 300
_countSize = functions.calSize(_countHeight, _countWidth, _sHeight, _sWidth)
_countPanel.geometry(_countSize)
_countPanel.resizable(False, False)
_countPanel.iconbitmap(_srcIcon)
_font = ("Microsoft YaHei", 10)
_countText = Text(_countPanel, font = _font, width = 35)
_countScrollY = Scrollbar(_countPanel, orient = VERTICAL, command = _countText.yview)
_countText.configure(yscrollcommand = _countScrollY.set)
_countText.pack(side = LEFT)
_countScrollY.pack(side = RIGHT, fill = Y)
_countPanel.protocol("WM_DELETE_WINDOW", _countPanel.withdraw)

# 规则面板
_rulePanel = Toplevel(root)
_rulePanel.withdraw()
_rulePanel.title("添加规则")
_ruleHeight, _ruleWidth = 320, 605
_ruleSize = functions.calSize(_ruleHeight, _ruleWidth, _sHeight, _sWidth)
_rulePanel.geometry(_ruleSize)
_rulePanel.resizable(False, False)
_rulePanel.iconbitmap(_srcIcon)
_rulePanelSelector = Frame(_rulePanel, borderwidth = 1)
_ruleOpreatorYesNo = Frame(_rulePanel, borderwidth = 1)
_ruleInfo = Frame(_rulePanel, borderwidth = 1)
_ruleList = Listbox(_rulePanelSelector, height = 13, selectmode = BROWSE)
_ruleList.pack(side = LEFT)
_ruleList.insert(END, *functions.opreatorList[::-1])
_ruleListScroll = Scrollbar(_rulePanelSelector, orient = VERTICAL, command = _ruleList.yview)
_ruleList.configure(yscrollcommand = _ruleListScroll.set)
_ruleListScroll.pack(side = LEFT, fill = Y, pady = 20)
_rulePanelSelector.pack(side = LEFT, padx = 20, fill = Y, pady = 10)
_rulePanelSplitor = Separator(_rulePanel, orient = VERTICAL)
_rulePanelSplitor.pack(side = LEFT, fill = Y)
_ruleYesButton = Button(_ruleOpreatorYesNo, text = "添加", command = _addRule)
_ruleOpreatorYesNo.pack(side = BOTTOM, padx = 20, pady = 20, fill = X)
_ruleYesButton.pack(side = RIGHT)
_ruleInfo.pack(anchor = N, fill = BOTH, pady = 20, padx = 20)
_rulePanel.protocol("WM_DELETE_WINDOW", _rulePanel.withdraw)
_ruleList.bind('<<ListboxSelect>>', _changeRule)
Geometry.welcome(_ruleInfo)

# 关于页面
_aboutPanel = Toplevel(root)
_aboutPanel.withdraw()
_aboutPanel.title("关于本程序")
_aboutheight, _aboutwidth = 290, 290
_aboutsizeInfo = functions.calSize(_aboutheight, _aboutwidth, _sHeight, _sWidth)
_aboutPanel.geometry(_aboutsizeInfo)
_aboutPanel.resizable(False, False)
_aboutPanel.iconbitmap(_srcIcon)
_abouticonLabel = Label(_aboutPanel, image = _abouticon, compound = TOP, text = "allRename : 批量重命名软件")
_abouticonLabel.image = _abouticon
_abouticonLabel.pack(side = TOP, padx = 30)
Label(_aboutPanel, text = "这是一款开源软件，用来批量的重命名文件").pack(pady = 10)
Label(_aboutPanel, text = "软件许可：MIT许可证").pack(pady = 0)
Label(_aboutPanel, text = "作者：guiqiqi187@gmail.com").pack(pady = 10)
Label(_aboutPanel, text = "项目地址：https://github.com/\nguiqiqi/allRename").pack()
Button(_aboutPanel, text = "访问项目主页", command = lambda : functions.webOpen(_address)).pack(side = TOP, pady = 10)
_aboutPanel.protocol("WM_DELETE_WINDOW", _aboutPanel.withdraw)

# 帮助页面
_helpPanel = Toplevel(root)
_helpPanel.withdraw()
_helpPanel.title("帮助")
_helpheight, _helpwidth = 400, 500
_helpsizeInfo = functions.calSize(_helpheight, _helpwidth, _sHeight, _sWidth)
_helpPanel.geometry(_helpsizeInfo)
_helpPanel.resizable(False, False)
_helpPanel.iconbitmap(_srcIcon)
_filehandler = open("help", "r")
_content = _filehandler.read()
_filehandler.close()
_font = ("Microsoft YaHei", 10)
_helpText = Text(_helpPanel, font = _font, width = 48)
_helpScrollY = Scrollbar(_helpPanel, orient = VERTICAL, command = _helpText.yview)
_helpText.configure(yscrollcommand = _helpScrollY.set)
_helpText.pack(side = LEFT, anchor = CENTER)
_helpScrollY.pack(side = RIGHT, fill = Y)
_helpText.insert(END, _content)
_helpText.configure(state = DISABLED)
_helpPanel.protocol("WM_DELETE_WINDOW", _helpPanel.withdraw)

# 文件过滤器
_filterPanel = Toplevel(root)
_filterPanel.withdraw()
_filterPanel.title("文件过滤器")
_filterheight, _filterwidth = 290, 400
_filtersizeInfo = functions.calSize(_filterheight, _filterwidth, _sHeight, _sWidth)
_filterPanel.geometry(_filtersizeInfo)
_filterPanel.resizable(False, False)
_filterPanel.iconbitmap(_srcIcon)
Label(_filterPanel, text = "按照文件类型", font = ("Microsoft YaHei", 10)).pack(pady = 8, anchor = W, padx = 20)
_filterUpper = Frame(_filterPanel)
_filterUpperLeft = Frame(_filterUpper)
_filterLeftListbox = Listbox(_filterUpperLeft, height = 7, width = 12)
_filterLeftListboxScroll = Scrollbar(_filterUpperLeft, orient = VERTICAL, command = _filterLeftListbox.yview)
_filterLeftListbox.configure(yscrollcommand = _filterLeftListboxScroll.set)
_filterLeftListbox.pack(side = LEFT)
_filterLeftListboxScroll.pack(fill = Y, side = RIGHT)
_filterUpperLeft.grid(row = 1, column = 1, rowspan = 7)
_filterSelectButton = Button(_filterUpper, compound = TOP, text = "选择", image = _iconArrow, width = 5,
	command = lambda : functions.moveItem(_filterLeftListbox, _filterRightListbox))
_filterSelectButton.grid(row = 4, column = 2, padx = 20)
_filterUpperRight = Frame(_filterUpper)
_filterRightListbox = Listbox(_filterUpperRight, height = 7, width = 12)
_filterRightListboxScroll = Scrollbar(_filterUpperRight, orient = VERTICAL, command = _filterRightListbox.yview)
_filterRightListbox.configure(yscrollcommand = _filterRightListboxScroll.set)
_filterRightListbox.pack(side = LEFT)
_filterRightListboxScroll.pack(fill = Y, side = RIGHT)
_filterUpperRight.grid(row = 1, column = 3, rowspan = 7)
_filterUpper.pack(anchor = CENTER, pady = 10)
Separator(_filterPanel).pack(fill = X, pady = 8)
# Label(_filterPanel, text = "按照文件大小", font = ("Microsoft YaHei", 10)).pack(anchor = W, padx = 20)
# _filterLower = Frame(_filterPanel)
# _ruleChoose = Combobox(_filterLower, state = "readonly", values = ["大于", "小于"], width = "7", justify = CENTER)
# _ruleChoose.grid(row = 1, column = 1, padx = 10)
# _sizeEntry = Entry(_filterLower, width = 10)
# _sizeEntry.grid(row = 1, column = 2)
# _multiChoose = Combobox(_filterLower, state = "readonly", values = functions.division, width = "5", justify = CENTER)
# _multiChoose.grid(row = 1, column = 3, padx = 10)
# _filterLower.pack(anchor = CENTER, pady = 10)
# Separator(_filterPanel).pack(fill = X)
# _ruleChoose.set("大于")
# _multiChoose.set("MB")
_buttonFrame = Frame(_filterPanel)
_loadButton = Button(_buttonFrame, text = "刷新", command = _loadTypes)
_loadButton.grid(row = 1, column = 1, padx = 20)
_saveButton = Button(_buttonFrame, text = "确定", command = lambda : functions.filterFile(_filterRightListbox, _file))
_saveButton.grid(row = 1, column = 2)
_buttonFrame.pack(anchor = CENTER, pady = 10)
_filterPanel.protocol("WM_DELETE_WINDOW", _filterPanel.withdraw)

# 框架 Frame
_btFrame = Frame(root)
_opFrame = Frame(root)
_opFrameS = Frame(_opFrame)
_rubtnFrame = Frame(root)
_fileFrame = Frame(root)
_fileFrameS = Frame(_fileFrame)
_filebtnFrame = Frame(root)

# 顶部菜单栏 Menubar
_menubar = Menu(root)
_aboutmenu = Menu(_menubar, tearoff = 0)
_aboutmenu.add_command(label = "帮助", command = _helpPanel.deiconify)
_aboutmenu.add_command(label = "关于软件", command = _aboutPanel.deiconify)
_filemenu = Menu(_menubar, tearoff = 0)
_filemenu.add_command(label = "选择文件夹", command = _askdir)
_filemenu.add_command(label = "显示当前文件夹", command = _showdir)
_filemenu.add_command(label = "清除设置的路径", command = _cleandir)
_filemenu.add_separator()
_filemenu.add_command(label = "保存规则到文件", command = _backrule)
_filemenu.add_command(label = "导入规则文件", command = _restorerule)
_filemenu.add_separator()
_filemenu.add_command(label = "文件过滤器", command = _loadFilterPanel)
_toolmenu = Menu(_menubar, tearoff = 0)
_toolmenu.add_command(label = "备份文件名", command = _backup)
_toolmenu.add_command(label = "恢复文件名", command = _restore)
_menubar.add_cascade(label = "文件", menu = _filemenu)
_menubar.add_cascade(label = "工具", menu = _toolmenu)
_menubar.add_cascade(label = "关于", menu = _aboutmenu)
_menubar.add_command(label = "退出", command = _exit)

# 上部分控制按钮 Button
_selectDirButton = Button(_btFrame, compound = TOP, text = "选择文件夹",
	image = _iconDir, width = 10, command = _askdir)
_rulesButton = Button(_btFrame, compound = TOP, text = "添加规则",
	image = _iconRule, width = 10, command = _rulePanel.deiconify)
_checkButton = Button(_btFrame, compound = TOP, text = "预览名称",
	image = _iconCheck, width = 10, command = lambda : functions.preview(_operation, _file))
_doneButton = Button(_btFrame, compound = TOP, text = "应用变化", 
	image = _iconDone, width = 10, command = _done)
_selectDirButton.pack(side = LEFT)
Label(_btFrame, text = " → ", font = ("Microsoft YaHei", 16)).pack(side = LEFT, padx = 5)
_rulesButton.pack(side = LEFT)
Label(_btFrame, text = " → ", font = ("Microsoft YaHei", 16)).pack(side = LEFT, padx = 5)
_checkButton.pack(side = LEFT)
Label(_btFrame, text = " → ", font = ("Microsoft YaHei", 16)).pack(side = LEFT, padx = 5)
_doneButton.pack(side = LEFT)

# 规则 TreeView
_opTitle = ("规则", "说明")
_operation = Treeview(_opFrameS, height = 5, columns = _opTitle, show = "headings", selectmode = BROWSE)
_opScorllY = Scrollbar(_opFrameS, orient = VERTICAL, command = _operation.yview)
_opScorllX = Scrollbar(_opFrame, orient = HORIZONTAL, command = _operation.xview)
_operation.configure(yscrollcommand = _opScorllY.set, xscrollcommand = _opScorllX.set)
_operation.column("#1", width = 200, minwidth = 200, anchor = CENTER)
_operation.heading("#1", text = "规则")
_operation.column("#2", width = 310, minwidth = 310, anchor = CENTER)
_operation.heading("#2", text = "说明")
_operation.pack(side = LEFT)
_opScorllY.pack(side = RIGHT, fill = Y)
_opScorllX.pack(side = BOTTOM, fill = X)
_opFrameS.pack(side = BOTTOM)
_operation.bind("<Delete>", lambda event : functions.removeSelect(_operation))
_operation.bind("<ButtonPress-1>", lambda event : functions.treeviewMouseDown(event))
_operation.bind("<B1-Motion>", lambda event : functions.treeviewMouseMove(event))

# 规则按钮 Button
_addRuleButton = Button(_rubtnFrame, compound = LEFT, text = "添加规则",
	image = _iconAdd, width = 10, command = _rulePanel.deiconify)
_removeRuleButton = Button(_rubtnFrame, compound = LEFT, text = "移除规则",
	image = _iconMinus, width = 10, command = lambda : functions.removeSelect(_operation))
_infoRuleButton = Button(_rubtnFrame, compound = LEFT, text = "规则预览",
	image = _iconInfo, width = 10, command = _showPreview)
_clearRuleButton = Button(_rubtnFrame, compound = LEFT, text = "清空规则",
	image = _iconClear, width = 10, command = lambda : functions.cleanTree(_operation))
_addRuleButton.pack(side = LEFT, padx = 10)
_removeRuleButton.pack(side = LEFT, padx = 10)
_infoRuleButton.pack(side = LEFT, padx = 10)
_clearRuleButton.pack(side = LEFT, padx = 10)

# 文件 Treeview
_fileTitle = ("原文件名", "更改后文件名")
_file = Treeview(_fileFrameS, height = 8, columns = _fileTitle, show = "headings", selectmode = "extended")
_fileScorllY = Scrollbar(_fileFrameS, orient = VERTICAL, command = _file.yview)
_fileScorllX = Scrollbar(_fileFrame, orient = HORIZONTAL, command = _file.xview)
_file.configure(yscrollcommand = _fileScorllY.set, xscrollcommand = _fileScorllX.set)
_file.column("#1", width = 255, minwidth = 255)
_file.column("#2", width = 255, minwidth = 255)
_file.heading("#1", text = "原文件名")
_file.heading("#2", text = "更改后文件名")
_file.pack(side = LEFT)
_fileScorllY.pack(side = RIGHT, fill = Y)
_fileScorllX.pack(side = BOTTOM, fill = X)
_fileFrameS.pack(side = BOTTOM)
_file.bind("<Delete>", lambda event : functions.removeSelect(_file))

# 文件按钮 Button
_removeFileButton = Button(_filebtnFrame, compound = LEFT, text = "移除文件",
	image = _iconMinus, width = 10, command = lambda : functions.removeSelect(_file))
_infoFileButton = Button(_filebtnFrame, compound = LEFT, text = "文件信息",
	image = _iconInfo, width = 10, command = lambda : _showfileinfo())
_allFileButton = Button(_filebtnFrame, compound = LEFT, text = "文件统计",
	image = _iconAll, width = 10, command = _analysis)
_removeFileButton.pack(side = LEFT)
_infoFileButton.pack(side = LEFT, padx = 50)
_allFileButton.pack(side = LEFT)

# 基于根界面的布局
_separator = Separator(root, orient = HORIZONTAL)
_btFrame.grid(row = 1, column = 1, columnspan = 7, padx = 30, pady = 15)
_separator.grid(row = 2, column = 1, columnspan = 7, sticky = EW)
_opInfoLabel = Label(root, text = "现有的规则:", font = ("Microsoft YaHei", 10))
_opInfoLabel.grid(row = 3, column = 1, columnspan = 7, padx = 40, pady = 5, sticky = W)
_opFrame.grid(row = 4, column = 1, columnspan = 7, padx = 40, pady = 0)
_rubtnFrame.grid(row = 5, column = 1, columnspan = 7, pady = 0, padx = 40)
_separator = Separator(root, orient = HORIZONTAL)
_separator.grid(row = 6, column = 1, columnspan = 7, sticky = EW, pady = 15)
_fileLabel = Label(root, text = "选中的文件:", font = ("Microsoft YaHei", 10))
_fileLabel.grid(row = 7, column = 1, columnspan = 7, padx = 40, sticky = W)
_fileFrame.grid(row = 8, column = 1, columnspan = 7, pady = 5)
_filebtnFrame.grid(row = 9, column = 1, columnspan = 7, padx = 40)

root.title(_title)
root.resizable(_resizableX, _resizableY)
root.geometry(_geometry)
root.iconbitmap(_srcIcon)
root.config(menu = _menubar)
root.protocol("WM_DELETE_WINDOW", _exit)
