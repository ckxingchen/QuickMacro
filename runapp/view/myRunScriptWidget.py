import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QWidget, QApplication, QTreeWidgetItem
from common.path import BasePath
from common.utils import edit_config_data
from runapp.ui.ui_runScriptWidget import Ui_runScriptWidget
from runapp.utils.threads_group import RunScriptThread, LogThread
from runapp.utils.utils import get_directory_tree
from runapp.view.message_box import QMyMessageBox
from runapp.view.myRpcServeWidget import QmyRpcServeWidget


class QmyRunScriptWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)             # 调用父类的构造函数，创建QWidget窗体
        self.ui = Ui_runScriptWidget()       # 创建UI对象
        self.ui.setupUi(self)                # 构造UI
        self.setupScriptWidgetItem()
        self.config = BasePath().getConfig()['客户端自动化配置']
        self.run_script_list = []                # 当前运行的录制脚本路径
        self.run_times = 1
        self.threads_list = []
        self.logSignal = LogUpdateSignal()
        self.customConfigUI()

    def customConfigUI(self):
        """自定义组件设置"""
        self.ui.treeWidget.headerItem().setText(0, "注：请勾选要运行的脚本！")
        self.logSignal.textWritten.connect(self.on_logTextEdit_show)
        # 初始化配置
        self.ui.lineEdit.setText(self.config['duration'])
        self.ui.lineEdit_2.setText(self.config['interval'])
        self.ui.lineEdit_3.setText(self.config['timeout'])
        self.ui.lineEdit_4.setText(self.config['confidence'])
        self.ui.lineEdit_6.setText(str(self.run_times))
        self.ui.comboBox.addItems(['True', 'False'])
        # 设置悬浮提示
        self.ui.runScriptButton.setToolTip("运行本地脚本")
        self.ui.stopScriptButton.setToolTip("停止本地脚本")
        self.ui.startRpcButton.setToolTip("启动RPC服务，可以远程调用本地脚本执行（与大有工具结合使用）")

    def __init_file_tree_item(self, children, item):
        """文件树展示"""
        for file in children:
            tree_widget = self.__file_tree_display(file, item)
            if file.get('children'):
                self.__init_file_tree_item(file['children'], tree_widget)  # 递归

    @staticmethod
    def __file_tree_display(tree_dict, item):
        """文件树显示规则"""
        if os.path.isdir(tree_dict['href']):
            if 'lib' not in tree_dict['href']:
                tree_widget = QTreeWidgetItem(item)
                tree_widget.setText(0, tree_dict['name'])
                tree_widget.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, '文件夹.png')))
                tree_widget.setToolTip(0, tree_dict['name'])
                tree_widget.setCheckState(0, Qt.Unchecked)
                tree_widget.setData(0, Qt.UserRole, {"name": tree_dict['name'], "href": tree_dict['href']})
                return tree_widget
        else:
            if tree_dict['name'].split('.')[1] == 'yaml':
                tree_widget = QTreeWidgetItem(item)
                tree_widget.setText(0, tree_dict['name'].split('.')[0])
                tree_widget.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'YAML.png')))
                tree_widget.setToolTip(0, tree_dict['name'])
                tree_widget.setCheckState(0, Qt.Unchecked)
                tree_widget.setData(0, Qt.UserRole, {"name": tree_dict['name'], "href": tree_dict['href']})
                return tree_widget

    def __changeItemCaption(self, item, check):
        """递归勾选节点"""
        item.setCheckState(0, check)
        item_data = item.data(0, Qt.UserRole)
        if check == Qt.Checked:
            if item_data['href'] not in self.run_script_list:
                if os.path.isfile(item_data['href']):
                    self.run_script_list.append(item_data['href'])
        elif check == Qt.Unchecked:
            if item_data['href'] in self.run_script_list:
                if os.path.isfile(item_data['href']):
                    self.run_script_list.remove(item_data['href'])
        if item.childCount() > 0:
            for i in range(item.childCount()):
                self.__changeItemCaption(item.child(i), check)

    def __changeItemExpanded(self, item, exp):
        """递归展开关闭所有节点"""
        item.setExpanded(exp)
        if item.childCount() > 0:
            for i in range(item.childCount()):
                self.__changeItemExpanded(item.child(i), exp)

    def setupScriptWidgetItem(self):
        """【自定义组件】基础关键字TreeWidgetItem"""
        self.ui.treeWidget.clear()
        self.run_script_list = []
        project_floor = QTreeWidgetItem(self.ui.treeWidget)
        project_floor.setText(0, '脚本目录')
        project_floor.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, '项目列表.png')))
        project_floor.setCheckState(0, Qt.Unchecked)
        project_floor.setData(0, Qt.UserRole, {"type": "project",
                                               "name": os.path.basename(BasePath.SCRIPT_DIR),
                                               "href": BasePath.SCRIPT_DIR})
        project_floor.setExpanded(True)  # 默认展开一级文本
        file_tree = get_directory_tree(BasePath.SCRIPT_DIR).get('children')
        for script_file in file_tree:
            base_floor = self.__file_tree_display(script_file, project_floor)
            if script_file.get('children'):
                self.__init_file_tree_item(script_file['children'], base_floor)

    def on_treeWidget_itemClicked(self, item, column):
        """ 勾选槽函数 """
        try:
            if item is None or column is None:
                return
            if item.checkState(0) == Qt.Checked:
                self.__changeItemCaption(item, Qt.Checked)
            elif item.checkState(0) == Qt.Unchecked:
                self.__changeItemCaption(item, Qt.Unchecked)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("选择", "勾选脚本出错！\n错误:{}".format(e))

    def on_openRadioButton_toggled(self):
        """展开所有槽函数"""
        try:
            top_item = self.ui.treeWidget.topLevelItem(0)
            self.__changeItemExpanded(top_item, True)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("展开", "展开全部出错！\n错误:{}".format(e))

    def on_closeRadioButton_toggled(self):
        """收缩所有槽函数"""
        try:
            top_item = self.ui.treeWidget.topLevelItem(0)
            self.__changeItemExpanded(top_item, False)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("收缩", "收缩全部出错！\n错误:{}".format(e))

    def on_checkRadioButton_toggled(self):
        """全部勾选槽函数"""
        try:
            top_item = self.ui.treeWidget.topLevelItem(0)
            self.__changeItemCaption(top_item, Qt.Checked)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("勾选", "勾选全部出错！\n错误:{}".format(e))

    def on_uncheckRadioButton_toggled(self):
        """取消全选槽函数"""
        try:
            top_item = self.ui.treeWidget.topLevelItem(0)
            self.__changeItemCaption(top_item, Qt.Unchecked)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("取消", "取消全选出错！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_runScriptButton_clicked(self):
        """运行脚本-槽函数"""
        try:
            run_thread = RunScriptThread(self)
            self.threads_list.append(run_thread)
            run_thread.finished.connect(self.remove_thread)
            run_thread.start()
            log_thread = LogThread(self)
            self.threads_list.append(log_thread)
            log_thread.finished.connect(self.remove_thread)
            log_thread.start()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("运行", "脚本运行出错！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_stopScriptButton_clicked(self):
        """停止运行-槽函数"""
        try:
            pass
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("停止", "脚本停止出错！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_startRpcButton_clicked(self):
        """打开RPC服务-槽函数"""
        try:
            rpc_dialog = QmyRpcServeWidget(self)
            rpc_dialog.setAttribute(Qt.WA_DeleteOnClose)
            rpc_dialog.setWindowFlag(Qt.Window, True)
            rpc_dialog.show()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("RPC服务", "打开RPC服务未知错误！\n错误:{}".format(e))

    def on_logTextEdit_show(self, text):
        """日志内容"""
        cursor = self.ui.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.textBrowser.append(text)
        self.ui.textBrowser.setTextCursor(cursor)
        self.ui.textBrowser.ensureCursorVisible()

    def on_lineEdit_textChanged(self):
        """编辑鼠标移动速度"""
        try:
            text = self.ui.lineEdit.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'duration', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置鼠标移动速度！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_lineEdit_2_textChanged(self):
        """编辑鼠标点击间隔"""
        try:
            text = self.ui.lineEdit_2.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'interval', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置鼠标点击间隔！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_lineEdit_3_textChanged(self):
        """编辑图像识别超时时间"""
        try:
            text = self.ui.lineEdit_3.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'timeout', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置图像识别超时时间！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_lineEdit_4_textChanged(self):
        """编辑图像识别信任度"""
        try:
            text = self.ui.lineEdit_4.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'confidence', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置图像识别信任度！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_lineEdit_6_textChanged(self):
        """编辑执行次数"""
        try:
            text = self.ui.lineEdit_6.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    self.run_times = int(text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置执行次数！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_comboBox_currentIndexChanged(self):
        """编辑是否设置灰度匹配"""
        try:
            edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'grayscale', self.ui.comboBox.currentText())
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def remove_thread(self):
        """线程回收"""
        sender = self.sender()
        if sender in self.threads_list:
            try:
                self.threads_list.remove(sender)
            except Exception as e:
                print(e)


class LogUpdateSignal(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyRunScriptWidget()
    myWidget.show()
    sys.exit(app.exec_())
