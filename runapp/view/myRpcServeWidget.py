import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication
from common.path import BasePath
from common.utils import edit_config_data
from runapp.ui.ui_rpcServeWidget import Ui_rpcServeWidget
from runapp.utils.threads_group import RunRPCThread, LogThread
from runapp.view.message_box import QMyMessageBox


class QmyRpcServeWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)       # 调用父类的构造函数，创建QWidget窗体
        self.parent = parent
        self.ui = Ui_rpcServeWidget()      # 创建UI对象
        self.ui.setupUi(self)          # 构造UI
        self.config = BasePath().getConfig()['客户端自动化配置']
        self.threads_list = []
        self.customConfigUI()

    def customConfigUI(self):
        """自定义组件设置"""
        # 初始化配置
        self.ui.ipLineEdit.setText(self.config['rpc_host'])
        self.ui.portLineEdit.setText(self.config['rpc_port'])

    def on_ipLineEdit_textChanged(self):
        """编辑RPC启动IP"""
        try:
            text = self.ui.ipLineEdit.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'rpc_host', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置RPC启动IP！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_portLineEdit_textChanged(self):
        """编辑RPC启动端口号"""
        try:
            text = self.ui.portLineEdit.text()
            if text:
                if len(text) > 64:
                    QMyMessageBox(self).msgBoxCritical('编辑', '文本长度超过64位，请重新输入！')
                    return
                else:
                    edit_config_data(BasePath.CONFIG_PATH, '客户端自动化配置', 'rpc_port', text)
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置RPC启动端口号！')
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_runRpcButton_clicked(self):
        """启动RPC服务-槽函数"""
        try:
            run_thread = RunRPCThread(self)
            self.threads_list.append(run_thread)
            run_thread.finished.connect(self.remove_thread)
            run_thread.start()
            log_thread = LogThread(self.parent)
            self.threads_list.append(log_thread)
            log_thread.finished.connect(self.remove_thread)
            log_thread.start()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("RPC服务", "启动RPC服务出错！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_stopRpcButton_clicked(self):
        """停止RPC服务-槽函数"""
        try:
            pass
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("RPC服务", "停止RPC服务出错！\n错误:{}".format(e))

    def remove_thread(self):
        """线程回收"""
        sender = self.sender()
        if sender in self.threads_list:
            try:
                self.threads_list.remove(sender)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyRpcServeWidget()
    myWidget.show()
    sys.exit(app.exec_())
