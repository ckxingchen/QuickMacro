import os
import sys
from copy import deepcopy
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication
from common.logger import Logger
from common.path import BasePath
from common.rw_yaml import write_yaml
from runapp.ui.ui_recordScriptWidget import Ui_recordScriptWidget
from runapp.view.message_box import QMyMessageBox
from runapp.recorder.record_signals import RecordSignal, NewScript
from runapp.recorder.globals import record_data

logger = Logger('myRecordScriptWidget.py').getLogger()


class QmyRecordScriptWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)               # 调用父类的构造函数，创建QWidget窗体
        self.parent = parent
        self.ui = Ui_recordScriptWidget()      # 创建UI对象
        self.ui.setupUi(self)                  # 构造UI
        # 全局参数
        self.run_thread = None
        self.listener = None
        self.old_event = None
        self.cur_event = None
        self.customConfigUI()
        self.recorde_signal = RecordSignal()
        self.listener = self.recorde_signal.setup_hook()
        self.recorde_signal.event_signal.connect(self.on_record_event)

    def customConfigUI(self):
        """自定义UI"""
        self.init_button_state()
        self.setWindowTitle('录制脚本')
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        # 滑动条
        # 设置最小值
        self.ui.percentSlider.setMinimum(0)
        # 设置最大值
        self.ui.percentSlider.setMaximum(record_data['mouse_interval_ms'])
        # 步长
        self.ui.percentSlider.setSingleStep(10)
        # 设置当前值
        self.ui.percentSlider.setValue(record_data['mouse_interval_ms']/2)
        # 连接信号槽
        self.ui.percentSlider.valueChanged.connect(self.on_slider_change)
        # # 隐藏框：
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

    def init_button_state(self):
        self.ui.startRecordButton.setEnabled(True)
        self.ui.stopRecordButton.setEnabled(False)
        record_data['is_recording'] = False
        record_data['pause_record'] = False

    def on_slider_change(self):
        value = self.ui.percentSlider.value()
        self.ui.percentSlider.setToolTip('录制精度：{}ms'.format(value))
        record_data['mouse_interval_ms'] = int(value)

    def on_nameLineEdit_textChanged(self):
        name_text = self.ui.nameLineEdit.text()
        if name_text:
            if len(name_text) > 64:
                QMyMessageBox(self).msgBoxCritical('编辑', '脚本名称长度超过64位，请重新输入名称！')
                record_data['script_name'] = name_text
            else:
                record_data['script_name'] = name_text
        else:
            record_data['script_name'] = name_text

    @pyqtSlot(bool)
    def on_startRecordButton_clicked(self):
        try:
            script_path = os.path.join(BasePath.RECORD_SCRIPT_DIR, record_data['script_name'] + '.yaml')
            if not script_path:
                QMyMessageBox(self).msgBoxCritical('录制', '请先输入要生成的脚本名称！')
                return
            elif os.path.exists(script_path):
                QMyMessageBox(self).msgBoxCritical('录制', '用例名称已存在，请重新输入用例名称！')
                return
            record_data['script_path'] = script_path
            self.ui.startRecordButton.setEnabled(False)
            self.ui.stopRecordButton.setEnabled(True)
            self.setWindowTitle('正在录制...')
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("录制", "开始录制未知错误！\n错误:{}".format(e))
            self.init_button_state()
        finally:
            record_data['is_recording'] = True
            record_data['pause_record'] = False

    @pyqtSlot(bool)
    def on_stopRecordButton_clicked(self):
        try:
            if not record_data['script_path']:
                QMyMessageBox(self).msgBoxCritical("录制", "您还没有录制脚本，请先点击开始录制！")
            temp_content = deepcopy(BasePath.SCRIPT_TEMPLATE)
            temp_content['step'] = record_data['record']
            write_yaml(record_data['script_path'], temp_content)
            NewScript.new_signal.emit()
            self.ui.startRecordButton.setEnabled(True)
            self.ui.stopRecordButton.setEnabled(False)
            self.setWindowTitle('录制脚本')
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("录制", "结束录制未知错误！\n错误:{}".format(e))
            self.init_button_state()
        finally:
            record_data['is_recording'] = False
            record_data['pause_record'] = False
            record_data['record'] = []
            self.listener['mouse'].stop()
            self.listener['keyboard'].stop()

    def pause_record_method(self):
        record_data['pause_record'] = True
        self.ui.startRecordButton.setEnabled(True)
        self.ui.stopRecordButton.setEnabled(False)
        self.setWindowTitle('录制暂停...')

    # 热键响应逻辑
    def hotkey_method(self, key_name):
        if (key_name == 'f1' and not record_data['is_recording']) or (
                key_name == 'f1' and record_data['pause_record']
        ):
            self.on_startRecordButton_clicked()
            logger.debug('{0} host start record'.format(key_name))
        elif key_name == 'f2' and record_data['is_recording']:
            self.pause_record_method()
            logger.debug('{0} host pause record'.format(key_name))
        elif key_name == 'f3' and record_data['is_recording']:
            self.on_stopRecordButton_clicked()
            logger.debug('{0} host stop record'.format(key_name))

    def on_record_event(self, event: dict):
        """录制事件"""
        # 判断热键
        key_name = event['action']['params'].get('key')
        if key_name:
            key_name = key_name.lower()
            if event['action']['method'] in ['press_down', 'press_up']:
                self.hotkey_method(key_name)
            elif key_name in ['f1', 'f2', 'f3']:
                return
        # 录制事件
        if (record_data['is_recording']) and (not record_data['pause_record']) and (key_name != 'f1'):
            if record_data['record']:
                if event['action'] == record_data['record'][-1]:
                    return
            record_data['record'].append(event['delay'])
            record_data['record'].append(event['action'])
            record_data['action_count'] += 1
            print(event)

    def closeEvent(self, event) -> None:
        """录制窗口关闭"""
        try:
            self.close()
            self.listener['mouse'].stop()
            self.listener['keyboard'].stop()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("关闭", "关闭窗口未知错误！\n错误:{}".format(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyRecordScriptWidget()
    myWidget.show()
    sys.exit(app.exec_())
