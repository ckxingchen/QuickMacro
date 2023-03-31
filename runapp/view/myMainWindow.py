import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from common.path import BasePath
from runapp.recorder.record_signals import NewScript
from runapp.ui.ui_MainWindow import Ui_MainWindow
from runapp.view.myHomeWidget import QmyHomeWidget, MyLogoLabel
from runapp.view.myNewScriptWidget import QmyNewScriptWidget
from runapp.view.myPetWidget import QmyPetWidget
from runapp.view.myPicRegWidget import QmyPicRegWidget
from runapp.utils.theme import set_my_theme
from runapp.view.myRunScriptWidget import QmyRunScriptWidget
from runapp.view.myTextRegWidget import QmyTextRegWidget


class QmyMainWindow(QMainWindow):

    def __init__(self, global_dict=None, parent=None):
        super().__init__(parent)             # 调用父类的构造函数，创建QWidget窗体
        self.global_dict = global_dict
        self.global_dict.set_value('MainWindow', self)
        self.mainUI = Ui_MainWindow()        # 创建UI对象
        self.mainUI.setupUi(self)            # 构造U
        # 全局变量
        self.m_flag = None
        self.m_Position = None
        # 自定义页面初始化
        self.homeUI = QmyHomeWidget()
        self.newScriptUI = QmyNewScriptWidget()
        self.runScriptUI = QmyRunScriptWidget()
        self.picReg = QmyPicRegWidget()
        self.textReg = QmyTextRegWidget()
        # 创建多页面QStackedWidget
        self.mainUI.stackedWidget.addWidget(self.homeUI)
        self.mainUI.stackedWidget.addWidget(self.newScriptUI)
        self.mainUI.stackedWidget.addWidget(self.runScriptUI)
        self.mainUI.stackedWidget.addWidget(self.picReg)
        self.mainUI.stackedWidget.addWidget(self.textReg)
        self.customConfigUI()

    def customConfigUI(self):
        """自定义UI"""
        set_my_theme(self.mainUI.stackedWidget, 'blueDeep')
        self.mainUI.toolBox.setCurrentIndex(0)
        self.mainUI.stackedWidget.setCurrentIndex(0)
        # 隐藏框：
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.mainUI.toolBox.setItemIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'fold_down.png')))
        self.mainUI.toolBox.setItemIcon(1, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'fold_right.png')))
        # logo点击事件
        self.mainUI.logoLabel = MyLogoLabel(self.mainUI.logoFrame)
        self.mainUI.logoLabel.connect_customized_slot(self.on_logoLabel_clicked)
        # 创建脚本重新加载脚本目录
        NewScript.new_signal.connect(self.runScriptUI.setupScriptWidgetItem)
        NewScript.new_signal.connect(self.newScriptUI.setupScriptTreeWidgetItem)
        NewScript.new_signal.connect(self.newScriptUI.setupScriptPlainTextEdit)

    def on_logoLabel_clicked(self):
        try:
            self.mainUI.stackedWidget.setCurrentIndex(0)
        except Exception as e:
            print(e)

    def on_newPushButton_clicked(self):
        try:
            self.mainUI.stackedWidget.setCurrentIndex(1)
        except Exception as e:
            print(e)

    def on_runPushButton_clicked(self):
        try:
            self.mainUI.stackedWidget.setCurrentIndex(2)
        except Exception as e:
            print(e)

    def on_picPushButton_clicked(self):
        try:
            self.mainUI.stackedWidget.setCurrentIndex(3)
        except Exception as e:
            print(e)

    def on_textPushButton_clicked(self):
        try:
            self.mainUI.stackedWidget.setCurrentIndex(4)
        except Exception as e:
            print(e)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def on_minimizeButton_clicked(self):
        """【自定义槽函数】最小化"""
        # self.showMinimized()
        self.close()
        pet_window = QmyPetWidget(self.global_dict)
        self.global_dict.set_value('PetWidget', pet_window)
        self.global_dict.get_value('PetWidget').show()

    def on_closeButton_clicked(self):
        """【自定义槽函数】关闭"""
        self.close()

    def on_toolBox_currentChanged(self, index):
        """导航栏折叠"""
        for i in range(2):
            self.mainUI.toolBox.setItemIcon(i, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'fold_right.png')))
        if self.mainUI.toolBox.currentWidget().isVisible():
            self.mainUI.toolBox.setItemIcon(index, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'fold_down.png')))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myMainWindow = QmyMainWindow()
    myMainWindow.show()
    sys.exit(app.exec_())
