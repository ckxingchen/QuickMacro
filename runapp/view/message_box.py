from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class QMyInputDialog(QInputDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    # 文本输入框
    def inputDialogText(self, title, label, text=''):
        inputDlgT = QInputDialog(self)
        inputDlgT.setWindowTitle(title)
        inputDlgT.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        inputDlgT.setLabelText(label)
        if text != '':
            inputDlgT.setTextValue(text)

        inputDlgT.setOkButtonText("确定")
        inputDlgT.setCancelButtonText("取消")
        reply = inputDlgT.exec()
        return inputDlgT.textValue(), reply


class QMyMessageBox(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)

    def msgBoxQuestion(self, title, text):
        msgBoxQ = QMessageBox(QMessageBox.Question, title, text, QMessageBox.Yes | QMessageBox.No, self)
        msgBoxQ.button(QMessageBox.Yes).setText("是")
        msgBoxQ.button(QMessageBox.No).setText("否")
        return msgBoxQ.exec()

    def msgBoxInformation(self, title, text):
        msgBoxI = QMessageBox(QMessageBox.Information, title, text, QMessageBox.Ok, self)
        msgBoxI.button(QMessageBox.Ok).setText("确定")
        msgBoxI.exec()

    def msgBoxCritical(self, title, text):
        msgBoxC = QMessageBox(QMessageBox.Critical, title, text, QMessageBox.Ok, self)
        msgBoxC.button(QMessageBox.Ok).setText("确定")
        msgBoxC.exec()

    def msgBoxWarning(self, title, text):
        msgBoxW = QMessageBox(QMessageBox.Warning, title, text, QMessageBox.Ok, self)
        msgBoxW.button(QMessageBox.Ok).setText("确定")
        msgBoxW.exec()



