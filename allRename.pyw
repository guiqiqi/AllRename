"""应用主文件"""

import ui
import error

error.filerec = True
error.consolerec = False
error.work()

ui.strarting = False
ui.root.report_callback_exception = error.handler
ui.root.focus_get()
ui.root.mainloop()
