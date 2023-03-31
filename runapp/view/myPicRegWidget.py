import base64
import os
import sys
import requests
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from runapp.ui.ui_picRegWidget import Ui_picRegWidget
from runapp.view.message_box import QMyMessageBox


class QmyPicRegWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)         # 调用父类的构造函数，创建QWidget窗体
        self.ui = Ui_picRegWidget()      # 创建UI对象
        self.ui.setupUi(self)            # 构造UI
        self.weight = 'yolov5s'          # 识别权重
        self.device = 'cpu'
        self.server = 'http://172.168.124.201:5000'
        self.picture_path = None
        self.pt_path = None
        self.yaml_path = None
        self.customConfigUI()

    def customConfigUI(self):
        """自定义UI"""
        self.ui.weightLineEdit.setText(self.weight)
        self.ui.serveLineEdit.setText(self.server)
        self.ui.deviceComboBox.addItems(['cpu', 'gpu'])
        self.ui.weightLineEdit.setPlaceholderText("请输入已上传的权重名称(不带后缀)")
        self.ui.serveLineEdit.setPlaceholderText("请输入已部署的AI服务URL")
        # 拖拽处理
        self.setAcceptDrops(True)
        self.ui.pictureLabel.setAcceptDrops(True)
        self.ui.pictureLabel.setScaledContents(True)

    @pyqtSlot(bool)
    def on_ptSelectButton_clicked(self):
        """选择PT文件-槽函数"""
        try:
            folder_path = QFileDialog.getOpenFileNames(self, '选择权重文件', '', "权重文件(*.pt)")
            if folder_path[0]:
                self.pt_path = folder_path[0][0]
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("选择权重文件", "选择文件未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_yamlSelectButton_clicked(self):
        """选择YAML文件-槽函数"""
        try:
            folder_path = QFileDialog.getOpenFileNames(self, '选择权重文件', '', "权重文件(*.yaml)")
            if folder_path[0]:
                self.yaml_path = folder_path[0][0]
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("选择文件", "选择文件未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_ptUploadButton_clicked(self):
        """上传PT文件-槽函数"""
        try:
            if not self.pt_path:
                QMyMessageBox(self).msgBoxCritical("上传", "请先选择要上传的PT文件！")
                return
            upload_url = self.server + '/uploadPt/'
            file_content = open(self.pt_path, 'rb')
            files = {'file': (self.weight + '.pt', file_content, 'application/octet-stream')}
            res = requests.post(url=upload_url, files=files)
            QMyMessageBox(self).msgBoxInformation("选择权重文件", "PT文件上传成功！！\n响应:{}".format(res.text))
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("上传", "上传文件未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_yamlUploadButton_clicked(self):
        """上传YAML文件-槽函数"""
        try:
            if not self.yaml_path:
                QMyMessageBox(self).msgBoxCritical("上传", "请先选择要上传的YAML文件！")
                return
            upload_url = self.server + '/uploadId2name/'
            file_content = open(self.pt_path, 'rb')
            files = {'file': (self.weight + '.yaml', file_content, 'application/octet-stream')}
            res = requests.post(url=upload_url, files=files)
            QMyMessageBox(self).msgBoxInformation("选择权重文件", "YAML文件上传成功！！\n响应:{}".format(res.text))
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("上传", "上传文件未知错误！\n错误:{}".format(e))

    def on_weightLineEdit_textChanged(self):
        """编辑识别权重-槽函数"""
        try:
            text = self.ui.weightLineEdit.text()
            if text:
                self.weight = text
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置训练好的识别权重名称！')
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_deviceComboBox_currentIndexChanged(self):
        try:
            self.device = self.ui.deviceComboBox.currentText()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def on_serveLineEdit_textChanged(self):
        """编辑识别服务-槽函数"""
        try:
            text = self.ui.serveLineEdit.text()
            if text:
                self.server = text
            else:
                QMyMessageBox(self).msgBoxCritical('编辑', '请设置部署好的识别服务url！')
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("编辑", "编辑出错！\n错误:{}".format(e))

    def dragEnterEvent(self, event) -> None:
        """拖入事件"""
        for url in event.mimeData().urls():
            self.picture_path = url.path()[1:]
        if event.mimeData().hasUrls():
            file_name = event.mimeData().urls()[0].fileName()
            base, ext = os.path.splitext(file_name)
            if ext in ['.jpg', '.png']:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        """拖放事件"""
        try:
            pix_map = QPixmap(self.picture_path)
            self.ui.pictureLabel.setPixmap(pix_map)
            event.accept()
            # 调用识别服务
            self.image_predict()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("拖放", "拖放出错！\n错误:{}".format(e))

    def image_to_base64(self):
        """图片转base64格式"""
        try:
            with open(self.picture_path, 'rb') as fp:
                content = fp.read()
            img_bytes = base64.b64encode(content)
            ext = self.picture_path.split('.')[-1]
            img_base64 = 'Data:image/%s;base64,%s' % (ext, img_bytes.decode())
            return img_base64
        except Exception as e:
            print("图片转base64失败：{}".format(e))

    def image_predict(self):
        """调用识别服务"""
        el_list = None
        try:
            url = self.server + '/predict/'
            header = {
                'Content-Type': 'application/json'
            }
            body = {
                "image": self.image_to_base64(),
                "weights": self.weight,
                "device": self.device
            }
            res = requests.post(url=url, headers=header, json=body)
            if (res.status_code == 200) and (res.json()['results']):
                el_list = res.json()['results']
                self.ui.textBrowser.setText(str(el_list))
            return str(el_list)
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("识别", "识别错误！\n错误:{}".format(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyPicRegWidget()
    myWidget.show()
    sys.exit(app.exec_())
