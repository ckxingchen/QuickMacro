from platform import system
from PyQt5.QtCore import pyqtSlot
import runapp.recorder.globals

# 槽函数:改变鼠标精度
@pyqtSlot(int)
def set_interval(value):
    globals.mouse_interval_ms = value
