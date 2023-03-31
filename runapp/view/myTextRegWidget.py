import base64
import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QApplication
from runapp.ui.ui_textRegWidget import Ui_textRegWidget
from runapp.view.message_box import QMyMessageBox


class QmyTextRegWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)       # 调用父类的构造函数，创建QWidget窗体
        self.ui = Ui_textRegWidget()      # 创建UI对象
        self.ui.setupUi(self)          # 构造UI
        self.server = 'http://172.168.124.200:18200'
        self.picture_path = None
        self.customConfigUI()

    def customConfigUI(self):
        """自定义UI"""
        self.ui.serveLineEdit.setText(self.server)
        self.ui.serveLineEdit.setPlaceholderText("请输入已部署的AI服务URL")
        # 拖拽处理
        self.setAcceptDrops(True)
        self.ui.pictureLabel.setAcceptDrops(True)
        self.ui.pictureLabel.setScaledContents(True)

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
            self.ocr_predict()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("拖放", "拖放出错！\n错误:{}".format(e))

    def ocr_predict(self):
        """ocr识别"""
        try:
            if os.path.exists(self.picture_path):
                with open(self.picture_path, "rb") as f:
                    img = f.read()
                    img_base64 = str(base64.b64encode(img), encoding="utf-8")
                url = self.server + '/dias/ocr'
                headers = {
                    'Content-Type': 'application/json'
                }
                jsons = {
                    "mode": "imgstream",
                    "language": "chinese",
                    # 图片base64
                    "imgstring": img_base64
                }
                res = requests.post(url=url, headers=headers, json=jsons)
                self.ui.textBrowser.setText(res.text)
            else:
                QMyMessageBox(self).msgBoxCritical("识别", "图片不存在！")
                return
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("识别", "识别错误！\n错误:{}".format(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyTextRegWidget()
    myWidget.show()
    sys.exit(app.exec_())
