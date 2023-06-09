# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'homeWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_homeWidget(object):
    def setupUi(self, homeWidget):
        homeWidget.setObjectName("homeWidget")
        homeWidget.resize(869, 674)
        homeWidget.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(homeWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.homeFrame = QtWidgets.QFrame(homeWidget)
        self.homeFrame.setStyleSheet("#homeFrame{\n"
                                     "border-image:url(../Images/icon/背景.jpg);\n"
                                     "border-bottom-right-radius:30px;\n"
                                     "}")
        self.homeFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.homeFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.homeFrame.setObjectName("homeFrame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.homeFrame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.homeLabel = QtWidgets.QLabel(self.homeFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeLabel.sizePolicy().hasHeightForWidth())
        self.homeLabel.setSizePolicy(sizePolicy)
        self.homeLabel.setMinimumSize(QtCore.QSize(0, 300))
        self.homeLabel.setMaximumSize(QtCore.QSize(16777215, 1000))
        self.homeLabel.setStyleSheet("#homeLabel{\n"
                                     "font: 50pt \"华文琥珀\";\n"
                                     "text-align: center;\n"
                                     "}\n"
                                     "")
        self.homeLabel.setTextFormat(QtCore.Qt.PlainText)
        self.homeLabel.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.homeLabel.setObjectName("homeLabel")
        self.verticalLayout_2.addWidget(self.homeLabel)
        self.psLabel = QtWidgets.QLabel(self.homeFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.psLabel.sizePolicy().hasHeightForWidth())
        self.psLabel.setSizePolicy(sizePolicy)
        self.psLabel.setMinimumSize(QtCore.QSize(0, 100))
        self.psLabel.setMaximumSize(QtCore.QSize(16777215, 100))
        self.psLabel.setStyleSheet("#psLabel{\n"
                                   "font: 15pt \"华文琥珀\";\n"
                                   "    color: rgb(255, 255, 255);\n"
                                   "text-align: center;\n"
                                   "}\n"
                                   "")
        self.psLabel.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.psLabel.setObjectName("psLabel")
        self.verticalLayout_2.addWidget(self.psLabel)
        self.urlLabel = QtWidgets.QLabel(self.homeFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.urlLabel.sizePolicy().hasHeightForWidth())
        self.urlLabel.setSizePolicy(sizePolicy)
        self.urlLabel.setMinimumSize(QtCore.QSize(0, 100))
        self.urlLabel.setMaximumSize(QtCore.QSize(16777215, 100))
        self.urlLabel.setStyleSheet("#urlLabel{\n"
                                    "    color: rgb(255,20,147);\n"
                                    "    font: 15pt \"华文新魏\";\n"
                                    "text-align: center;\n"
                                    "}\n"
                                    "")
        self.urlLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.urlLabel.setObjectName("urlLabel")
        self.verticalLayout_2.addWidget(self.urlLabel)
        self.verticalLayout.addWidget(self.homeFrame)

        self.retranslateUi(homeWidget)
        QtCore.QMetaObject.connectSlotsByName(homeWidget)

    def retranslateUi(self, homeWidget):
        _translate = QtCore.QCoreApplication.translate
        homeWidget.setWindowTitle(_translate("homeWidget", "Form"))
        self.homeLabel.setText(_translate("homeWidget", "欢迎使用\n"
                                                        "   自动化办公助手！\n"
                                                        "\n"
                                                        "按键精灵\n"
                                                        "\n"
                                                        ""))
        self.psLabel.setText(_translate("homeWidget", "开发者：测开星辰（收徒微信：ck_xingchen）"))
        self.urlLabel.setText(_translate("homeWidget", "学习自动化测试、自动化办公、脚本编写，请点这！！！"))
