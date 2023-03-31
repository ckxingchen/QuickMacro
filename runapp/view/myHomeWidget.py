import sys
import webbrowser

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QApplication
from runapp.ui.ui_homeWidget import Ui_homeWidget


class MyLogoLabel(QtWidgets.QLabel):
    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MyLogoLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
            self.setCursor(QCursor(Qt.PointingHandCursor))  # 更改鼠标图标

    def mouseReleaseEvent(self, event):
        self.button_clicked_signal.emit()
        self.setCursor(QCursor(Qt.ArrowCursor))

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)


class QmyHomeWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)       # 调用父类的构造函数，创建QWidget窗体
        self.ui = Ui_homeWidget()      # 创建UI对象
        self.ui.setupUi(self)          # 构造UI
        self.url = 'https://student-api.iyincaishijiao.com/t/MfBsRnN/'
        self.ui.urlLabel.setText("学习自动化测试、自动化办公、脚本编写，请点这--><a href='{}' style='color:red'>购课链接</a>".format(self.url))
        self.ui.urlLabel.setOpenExternalLinks(True)  # 允许访问超链接
        self.ui.urlLabel.linkActivated.connect(self.on_urlLabel_clicked)  # 针对链接点击事件

    def on_urlLabel_clicked(self):
        """测试报告按钮点击"""
        try:
            webbrowser.open(self.url)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyHomeWidget()
    myWidget.show()
    sys.exit(app.exec_())
