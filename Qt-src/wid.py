# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wid.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Chara_setting = QtWidgets.QGroupBox(self.centralwidget)
        self.Chara_setting.setEnabled(True)
        self.Chara_setting.setGeometry(QtCore.QRect(30, 50, 491, 191))
        self.Chara_setting.setObjectName("Chara_setting")
        self.pushButton_shootPhoto = QtWidgets.QPushButton(self.Chara_setting)
        self.pushButton_shootPhoto.setGeometry(QtCore.QRect(40, 120, 93, 28))
        self.pushButton_shootPhoto.setObjectName("pushButton_shootPhoto")
        self.checkBox_finish = QtWidgets.QCheckBox(self.Chara_setting)
        self.checkBox_finish.setEnabled(False)
        self.checkBox_finish.setGeometry(QtCore.QRect(160, 130, 91, 19))
        self.checkBox_finish.setObjectName("checkBox_finish")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.Chara_setting)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 30, 441, 81))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_Chara = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_Chara.sizePolicy().hasHeightForWidth())
        self.label_Chara.setSizePolicy(sizePolicy)
        self.label_Chara.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Chara.setObjectName("label_Chara")
        self.horizontalLayout.addWidget(self.label_Chara)
        self.comboBox_chooseChara = QtWidgets.QComboBox(self.horizontalLayoutWidget)
        self.comboBox_chooseChara.setObjectName("comboBox_chooseChara")
        self.horizontalLayout.addWidget(self.comboBox_chooseChara)
        self.pushButton_choosePsd = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_choosePsd.sizePolicy().hasHeightForWidth())
        self.pushButton_choosePsd.setSizePolicy(sizePolicy)
        self.pushButton_choosePsd.setObjectName("pushButton_choosePsd")
        self.horizontalLayout.addWidget(self.pushButton_choosePsd)
        self.Vocie_setting = QtWidgets.QGroupBox(self.centralwidget)
        self.Vocie_setting.setEnabled(True)
        self.Vocie_setting.setGeometry(QtCore.QRect(30, 260, 491, 191))
        self.Vocie_setting.setObjectName("Vocie_setting")
        self.label_voiceKind = QtWidgets.QLabel(self.Vocie_setting)
        self.label_voiceKind.setGeometry(QtCore.QRect(40, 60, 72, 15))
        self.label_voiceKind.setObjectName("label_voiceKind")
        self.label_volumn = QtWidgets.QLabel(self.Vocie_setting)
        self.label_volumn.setGeometry(QtCore.QRect(40, 110, 72, 15))
        self.label_volumn.setObjectName("label_volumn")
        self.horizontalSlider = QtWidgets.QSlider(self.Vocie_setting)
        self.horizontalSlider.setGeometry(QtCore.QRect(90, 110, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.label_volumnNum = QtWidgets.QLabel(self.Vocie_setting)
        self.label_volumnNum.setGeometry(QtCore.QRect(260, 110, 72, 15))
        self.label_volumnNum.setObjectName("label_volumnNum")
        self.pushButton_testMic = QtWidgets.QPushButton(self.Vocie_setting)
        self.pushButton_testMic.setGeometry(QtCore.QRect(40, 150, 93, 28))
        self.pushButton_testMic.setObjectName("pushButton_testMic")
        self.comboBox_vc = QtWidgets.QComboBox(self.Vocie_setting)
        self.comboBox_vc.setGeometry(QtCore.QRect(90, 60, 121, 22))
        self.comboBox_vc.setObjectName("comboBox_vc")
        self.label_charaPreview = QtWidgets.QLabel(self.centralwidget)
        self.label_charaPreview.setGeometry(QtCore.QRect(560, 50, 72, 15))
        self.label_charaPreview.setObjectName("label_charaPreview")
        self.Image_preview = QtWidgets.QLabel(self.centralwidget)
        self.Image_preview.setGeometry(QtCore.QRect(650, 50, 211, 241))
        self.Image_preview.setText("")
        self.Image_preview.setObjectName("Image_preview")
        self.pushButton_start = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_start.setGeometry(QtCore.QRect(610, 500, 181, 51))
        self.pushButton_start.setObjectName("pushButton_start")
        self.Other_setting = QtWidgets.QGroupBox(self.centralwidget)
        self.Other_setting.setGeometry(QtCore.QRect(30, 480, 381, 80))
        self.Other_setting.setObjectName("Other_setting")
        self.checkBox_debugOn = QtWidgets.QCheckBox(self.Other_setting)
        self.checkBox_debugOn.setGeometry(QtCore.QRect(40, 40, 281, 19))
        self.checkBox_debugOn.setObjectName("checkBox_debugOn")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Chara_setting.setTitle(_translate("MainWindow", "虚拟形象设置"))
        self.pushButton_shootPhoto.setText(_translate("MainWindow", "动作采集"))
        self.checkBox_finish.setText(_translate("MainWindow", "未完成"))
        self.label_Chara.setText(_translate("MainWindow", "形象选择"))
        self.pushButton_choosePsd.setText(_translate("MainWindow", "扫描"))
        self.Vocie_setting.setTitle(_translate("MainWindow", "变声器设置"))
        self.label_voiceKind.setText(_translate("MainWindow", "音色"))
        self.label_volumn.setText(_translate("MainWindow", "音量"))
        self.label_volumnNum.setText(_translate("MainWindow", "0"))
        self.pushButton_testMic.setText(_translate("MainWindow", "麦克风测试"))
        self.label_charaPreview.setText(_translate("MainWindow", "形象预览"))
        self.pushButton_start.setText(_translate("MainWindow", "链接形象！"))
        self.Other_setting.setTitle(_translate("MainWindow", "其他设置"))
        self.checkBox_debugOn.setText(_translate("MainWindow", "(Debug模式)渲染同时打开摄像头"))