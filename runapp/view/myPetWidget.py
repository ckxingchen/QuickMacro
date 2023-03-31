import os
import random
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QIcon, QMovie

from common.path import BasePath


class QmyPetWidget(QWidget):

    def __init__(self, global_dict=None, parent=None):
        super().__init__(parent)       # 调用父类的构造函数，创建QWidget窗体
        self.global_dict = global_dict
        self.global_dict.set_value('PetWidget', self)
        self.m_flag = None
        self.m_Position = None
        self.pet_x = 100
        self.pet_y = 100
        self.pet_type = 'img1'
        self.pet_dir = os.path.join(BasePath.PET_IMG_DIR, self.pet_type)
        self.tip_list = ["hello 欢迎使用自动办公助手！",
                         "点点点累了怎么办？ 快来试试我的脚本录制功能吧！",
                         "我的创造者是测开星辰（V:ck_xingchen），有bug可以骚扰他（手动滑稽）!"]
        self.pet_actions = []
        for i in range(11):
            self.pet_actions.append(os.path.join(self.pet_dir, '{}.gif'.format(str(i))))

        self.label = QLabel(self)
        self.movie = QMovie(os.path.join(self.pet_dir, 'init1.gif'))
        self.setupUi()
        self.customConfigUI()
        self.tray_icon()
        # 每隔一段时间做个动作
        self.timer = QTimer()
        self.timer.timeout.connect(self.random_action)
        self.timer.start(7000)
        # 对话框
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.select_tip)
        self.timer1.start(5000)

    def setupUi(self):
        # 将窗口设置为动图大小
        self.resize(400, 400)
        # 使用label来显示动画
        self.label = QLabel("", self)
        # label大小设置为动画大小
        self.label.setFixedSize(self.pet_x, self.pet_y)
        # 宠物大小
        self.movie.setScaledSize(QSize(self.pet_x, self.pet_y))
        # 将动画添加到label中
        self.label.setMovie(self.movie)
        # 开始播放动画
        self.movie.start()
        # 透明窗口
        self.setWindowOpacity(1)
        # 添加窗口标题
        self.setWindowTitle("GIFDemo")

    def customConfigUI(self):
        """自定义UI"""
        self.move(1700, 800)
        # 窗口透明程度
        self.setWindowOpacity(1)
        # 初始化，不规则窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        # 右键菜单
        self.label.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.label.customContextMenuRequested.connect(self.petWidgetMenu)  # 绑定

    def select_tip(self):
        """随机选择描述"""
        num_items = len(self.tip_list)
        random_index = random.randrange(num_items)
        cur_tip = self.tip_list[random_index]
        self.label.setToolTip(cur_tip)

    def tray_icon(self):
        mini_icon = QSystemTrayIcon(self)
        mini_icon.setIcon(QIcon(BasePath.ICON_PICTURE))
        taskbar_menu = QMenu(self)
        quit_menu = QAction('退出', self, triggered=self.quit)
        taskbar_menu.addAction(quit_menu)
        mini_icon.setContextMenu(taskbar_menu)
        mini_icon.show()

    def quit(self):
        self.close()
        sys.exit()

    def show_pet(self):
        self.setWindowOpacity(1)

    def random_action(self):
        self.movie = QMovie(random.choice(self.pet_actions))
        # 宠物大小
        self.movie.setScaledSize(QSize(self.pet_x, self.pet_y))
        # 将动画添加到label中
        self.label.setMovie(self.movie)
        # 开始播放动画
        self.movie.start()

    def petWidgetMenu(self):
        """右键菜单"""
        try:
            right_menu = QMenu(self.label)
            right_menu.addAction('打开主界面')
            right_menu.addAction('程序退出')
            right_menu.triggered[QAction].connect(self.on_petWidget_menu)  # 右键点击清空之后执行的操作
            right_menu.exec_(QCursor.pos())  # 执行之后菜单可以显示
        except Exception as e:
            print(e)

    def on_petWidget_menu(self, action):
        """右键事件行为"""
        try:
            command = action.text()
            if command == "打开主界面":
                self.close()
                self.global_dict.get_value('MainWindow').show()
            elif command == "程序退出":
                self.quit()
        except Exception as e:
            print(e)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标
            self.movie = QMovie(os.path.join(self.pet_dir, 'init2.gif'))
            # 宠物大小
            self.movie.setScaledSize(QSize(self.pet_x, self.pet_y))
            # 将动画添加到label中
            self.label.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.movie = QMovie(os.path.join(self.pet_dir, 'init1.gif'))
        # 宠物大小
        self.movie.setScaledSize(QSize(self.pet_x, self.pet_y))
        # 将动画添加到label中
        self.label.setMovie(self.movie)
        # 开始播放动画
        self.movie.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyPetWidget()
    myWidget.show()
    sys.exit(app.exec_())
