import json
from threading import Thread
import os, sys

path = os.getcwd()
sys.path.append(path)

import cv2
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from psd_tools import PSDImage

from wid import Ui_VtbKit
from camWid import Ui_Form as Cam_Ui_Form
import src.character_renderer as CR


class myPhotoShooter(QWidget):
    checkSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.timer = QtCore.QTimer()
        self.cap = cv2.VideoCapture()  # 摄像头视频流
        self.CAM_MAX_NUM = 5
        self.CAM_NUM = 0  # 摄像头编号，0为默认
        self.faceOpenImage = None
        self.faceCloseImage = None
        self.user_step = 0

        self.ui = Cam_Ui_Form()
        # 初始化界面
        self.ui.setupUi(self)
        self.ui.button_confrim.setEnabled(False)
        self.ui.button_back.setEnabled(False)

        self.ui.button_shoot.clicked.connect(self.shoot_photo)
        self.ui.button_back.clicked.connect(self.back_step)
        self.ui.button_openCam.clicked.connect(self.start_camera)
        self.timer.timeout.connect(self.show_camera)

        self.get_cam_num()
        # TODO：检测照片采集是否已经完成

    def get_cam_num(self):
        # 通过遍历摄像头编号开启视频流，判断摄像头数量
        cnt = 0
        for device in range(0, self.CAM_MAX_NUM):
            stream = cv2.VideoCapture(device)
            grabbed = stream.grab()
            stream.release()
            if not grabbed:
                break
            cnt = cnt + 1
        for i in range(cnt):
            self.ui.comboBox.addItem("Camera %d" % i)

    def start_camera(self):
        if self.timer.isActive() == False:
            self.CAM_NUM = int(self.ui.comboBox.currentIndex())
            openf = self.cap.open(self.CAM_NUM)
            if openf == False:
                msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查摄像头是否启用", buttons=QtWidgets.QMessageBox.Ok)
            else:
                self.timer.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                self.ui.button_openCam.setText("关闭摄像头")
                self.ui.camerashow.setText("【摄像头未启用】")
                self.user_step = 1
        else:
            self.timer.stop()
            self.cap.release()
            self.ui.button_openCam.setText("打开摄像头")

    def show_camera(self):
        flag, self.image = self.cap.read()  # 从视频流中读取
        show = self.image
        # show = cv2.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                 QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.ui.camerashow.setPixmap(QtGui.QPixmap.fromImage(showImage).scaled(
            640, 480, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding))  # 往显示视频的Label里显示QImage

    def shoot_photo(self):
        try:
            img = self.cap.read()[1]
            show = cv2.resize(img, (244, 168))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_RGB888)
            sav = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            saveImage = QtGui.QImage(sav.data, sav.shape[1], sav.shape[0],
                                     QtGui.QImage.Format_RGB888)
            if self.user_step == 1:
                self.ui.label_openImg.setPixmap(QtGui.QPixmap.fromImage(showImage))
                saveImage.save("assets/std_face_open.png", format="PNG")
                self.user_step = 2
                self.ui.label_step1.setTextFormat(Qt.RichText)
                self.ui.label_step1.setText("<font color=\"#01B468\">1.张开眼睛和嘴巴，点击拍摄照片</font>")
                self.ui.button_back.setEnabled(True)
            elif self.user_step == 2:
                self.ui.label_closeImg.setPixmap(QtGui.QPixmap.fromImage(showImage))
                saveImage.save("assets/std_face_closed.png", format="PNG")
                self.ui.label_step2.setTextFormat(Qt.RichText)
                self.ui.label_step2.setText("<font color=\"#01B468\">2.闭上眼睛和嘴巴，点击拍摄照片</font>")
                self.user_step = 3
                self.ui.button_confrim.setEnabled(True)
        except Exception as e:
            print(e)

    def back_step(self):
        if self.user_step == 2:
            self.ui.label_step1.setTextFormat(Qt.AutoText)
            self.ui.label_step1.setText("1.张开眼睛和嘴巴，点击拍摄照片")
            self.ui.label_openImg.clear()
            self.ui.label_openImg.setText("睁眼动作图像")
            self.user_step = 1
            self.ui.button_back.setEnabled(False)
        if self.user_step == 3:
            self.ui.label_step2.setTextFormat(Qt.AutoText)
            self.ui.label_step2.setText("2.闭上眼睛和嘴巴，点击拍摄照片")
            self.ui.label_closeImg.clear()
            self.ui.label_closeImg.setText("睁眼动作图像")
            self.user_step = 2
            self.ui.button_confrim.setEnabled(False)

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        event.accept()


class QSSHelper:
    def __init__(self):
        pass

    @staticmethod
    def LoadQSSFile():
        styleFile = "Qt-src/qss/MacOS.qss"
        with open(styleFile, 'r') as f:
            return f.read()


class myMainForm(QMainWindow):
    def __init__(self):
        # 调用父类构造函数，初始化空窗口
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = Ui_VtbKit()
        # 初始化界面
        self.ui.setupUi(self)

        self.chara_name = None
        self.camWindow = None
        self.vtb_thread = None
        self.vc_thread = None
        self.is_vtbAlive = False
        self.is_photo_shooted = False
        self.CRfilepath = "src/character_renderer.py"
        self.configFilePath = "assets/sample_config.json"
        self.vc_configFilePath = "assets/type.txt"

        self.ui.pushButton_shootPhoto.clicked.connect(self.open_camera_capture)
        self.ui.pushButton_start.clicked.connect(self.start_vtb)
        self.ui.pushButton_choosePsd.clicked.connect(self.scan_psd_files)
        self.initVCcomboBox()
        self.ui.comboBox_vc.currentIndexChanged.connect(self.on_voiceKind_Changed)
        self.checkPhotoShoot()

    def initVCcomboBox(self):
        voice_texts = ["正常",
                       "萝莉",
                       "大叔",
                       "惊悚",
                       "搞怪",
                       "电音",
                       "回声",
                       "颤音"]
        self.ui.comboBox_vc.addItems(voice_texts)

    def checkPhotoShoot(self):
        for roots, dirs, files in os.walk("./assets"):
            photo1 = "std_face_closed.png"
            photo2 = "std_face_open.png"
            if photo1 in files and photo2 in files:
                print("fin")
                self.ui.checkBox_finish.setChecked(True)
                self.ui.checkBox_finish.setText("已完成")
                self.is_photo_shooted = True

    def scan_psd_files(self):
        self.ui.comboBox_chooseChara.disconnect()
        self.ui.comboBox_chooseChara.clear()
        self.ui.comboBox_chooseChara.addItem("无")
        psd_file_paths = []
        for roots, dirs, files in os.walk("./assets"):
            for filename in files:
                if filename.endswith("psd"):
                    psd_file_paths.append(filename)
        for filename in psd_file_paths:
            name = filename.split("/")[-1].split(".")[0]
            self.ui.comboBox_chooseChara.addItem(name)
        self.ui.comboBox_chooseChara.currentIndexChanged.connect(self.on_chara_choose)

    def on_chara_choose(self):
        text = self.ui.comboBox_chooseChara.currentText()
        if text not in (None, "无"):
            filename = "assets/" + text
            psd = PSDImage.open(filename + ".psd")
            if not os.path.exists(filename + ".png"):
                psd.composite().save(filename + ".png")
            pixmap_chara = QPixmap(filename + ".png").scaled(
                self.ui.Image_preview.width(), self.ui.Image_preview.height())
            self.ui.Image_preview.setPixmap(pixmap_chara)
            self.chara_name = text
        else:
            self.ui.Image_preview.setText("暂无预览")
            self.chara_name = None

    def open_camera_capture(self):
        self.camWindow = myPhotoShooter()
        qssStyle = QSSHelper.LoadQSSFile()
        self.camWindow.setStyleSheet(qssStyle)
        self.camWindow.ui.button_confrim.clicked.connect(self.updateCaptureChecked)
        self.camWindow.show()

    def updateCaptureChecked(self):
        self.ui.checkBox_finish.setChecked(True)
        self.ui.checkBox_finish.setText("已完成")
        self.is_photo_shooted = True
        self.camWindow.close()

    def on_voiceKind_Changed(self):

        vc_configFile = open(self.vc_configFilePath, "w")
        vc_configFile.writelines(str(self.ui.comboBox_vc.currentIndex()))
        vc_configFile.close()

    def start_voiceChangeThreadFunc(self):
        try:
            p_res = os.popen("cd assets/ & start Sound.exe")
            print(p_res)

            vc_configFile = open(self.vc_configFilePath, "w")
            vc_configFile.writelines(str(self.ui.comboBox_vc.currentIndex()))
            vc_configFile.close()

        except Exception as e:
            print(e)

    def start_vtbThreadFunc(self):
        config_file = open(self.configFilePath, encoding="utf-8")
        config_data = json.load(config_file)
        config_data["psd_file_path"] = "assets/" + self.chara_name + ".psd"
        config_file.close()
        with open(self.configFilePath, 'w', encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        CR.manual_start(config_data, self.ui.checkBox_debugOn.isChecked())

    def start_vtb(self):
        print("main: %d" % os.getpid())
        isEnableVC = self.ui.checkBox_enableVC.isChecked()
        if self.vtb_thread is None:
            self.is_vtbAlive = False
        else:
            self.is_vtbAlive = self.vtb_thread.is_alive()

        if not self.is_vtbAlive:
            if self.chara_name is not None:
                if self.is_photo_shooted:
                    self.vtb_thread = Thread(target=self.start_vtbThreadFunc)
                    self.vtb_thread.start()
                    if isEnableVC:
                        self.vc_thread = Thread(target=self.start_voiceChangeThreadFunc)
                        self.vc_thread.start()
                    self.ui.pushButton_start.setText("停止")
                    self.setEnvButtons(False)
                    self.ui.pushButton_shootPhoto.setEnabled(False)
                else:
                    msg = QtWidgets.QMessageBox.warning(self, '无法启动', "动作采集未完成！", buttons=QtWidgets.QMessageBox.Ok)
                    return
            else:
                msg = QtWidgets.QMessageBox.warning(self, '无法启动', "未选中角色！", buttons=QtWidgets.QMessageBox.Ok)
                return
        else:
            vc_configFile = open(self.vc_configFilePath, "w")
            vc_configFile.writelines("-1")
            vc_configFile.close()

            # 结束vtb渲染
            CR.manual_stop()
            self.vtb_thread.join()
            self.ui.pushButton_start.setText("启动！")
            self.setEnvButtons(True)

    def setEnvButtons(self, bool):
        self.ui.pushButton_choosePsd.setEnabled(bool)
        self.ui.comboBox_chooseChara.setEnabled(bool)
        self.ui.pushButton_shootPhoto.setEnabled(bool)
        self.ui.checkBox_enableVC.setEnabled(bool)
        self.ui.checkBox_debugOn.setEnabled(bool)


if __name__ == '__main__':
    app = QApplication([])
    wid = myMainForm()

    id = QFontDatabase.addApplicationFont("assets/Aa20.ttf")
    fontstr = QFontDatabase.applicationFontFamilies(id)[0]
    font = QFont(fontstr, 8)
    app.setFont(font)

    qssStyle = QSSHelper.LoadQSSFile()
    wid.setStyleSheet(qssStyle)

    wid.show()
    app.exec_()
