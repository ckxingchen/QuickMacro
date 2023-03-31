import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from common.path import BasePath
from runapp.view.myMainWindow import QmyMainWindow
from common.container import GlobalManager


# 运行GUI界面
global_dict = GlobalManager()
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 适应高DPI设备
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)     # 解决图片在不同分辨率显示模糊问题
app = QApplication(sys.argv)
main_window = QmyMainWindow(global_dict)
main_window.setWindowIcon(QIcon(BasePath.ICON_PICTURE))

main_window.show()
sys.exit(app.exec_())
