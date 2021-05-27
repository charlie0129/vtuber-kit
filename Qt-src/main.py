import os
<<<<<<< HEAD
from threading import Thread
=======
>>>>>>> c1686f1b2a30162a87d589f822c70793308d2d28

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QCamera
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget

from wid import Ui_MainWindow
from camWid import Ui_Form as Cam_Ui_Form


class myPhotoShooter(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QtCore.QTimer()
        self.cap = cv2.VideoCapture()  # 开启视频流
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
        self.ui.button_confrim.clicked.connect(self.capture_finish)
        self.timer.timeout.connect(self.show_camera)

    def start_camera(self):
        if self.timer.isActive() == False:
            openf = self.cap.open(self.CAM_NUM)
            if openf == False:
                msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查摄像头是否启用", buttons=QtWidgets.QMessageBox.Ok)
            else:
                self.timer.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                self.user_step = 1
        else:
            self.timer.stop()
            self.cap.release()
        self.ui.button_openCam.setEnabled(False)

    def show_camera(self):
        flag, self.image = self.cap.read()  # 从视频流中读取

        show = cv2.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                 QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.ui.camerashow.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage

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
                saveImage.save("../assets/std_face_open.png", format="PNG")
                self.user_step = 2
                self.ui.label_step1.setTextFormat(Qt.RichText)
                self.ui.label_step1.setText("<font color=\"#00FF00\">1.张开眼睛和嘴巴，点击拍摄照片</font>")
                self.ui.button_back.setEnabled(True)
            elif self.user_step == 2:
                self.ui.label_closeImg.setPixmap(QtGui.QPixmap.fromImage(showImage))
                saveImage.save("../assets/std_face_closed.png", format="PNG")
                self.ui.label_step2.setTextFormat(Qt.RichText)
                self.ui.label_step2.setText("<font color=\"#00FF00\">2.闭上眼睛和嘴巴，点击拍摄照片</font>")
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

    def capture_finish(self):
        self.close()


class myMainForm(QMainWindow):
    def __init__(self):
        # 调用父类构造函数，初始化空窗口
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.ui.setupUi(self)

        self.camWindow = None
<<<<<<< HEAD
        self.vtb_thread = None
=======
>>>>>>> c1686f1b2a30162a87d589f822c70793308d2d28

        self.ui.pushButton_shootPhoto.clicked.connect(self.open_camera_capture)
        self.ui.pushButton_start.clicked.connect(self.start_vtb)

    def open_camera_capture(self):
        self.camWindow = myPhotoShooter()
        self.camWindow.show()

    def start_vtb(self):
<<<<<<< HEAD
        isAlive = False
        if self.vtb_thread == None:
            isAlive = False
        elif self.vtb_thread.is_alive():
            isAlive = True
        if not isAlive:
            self.vtb_thread = Thread(target=self.start_vtbThreadFunc)
            self.vtb_thread.start()
        else:
            # TODO:关闭线程
            pass

    def start_vtbThreadFunc(self):
        pyfilepath = "../src/character_renderer.py"
=======
        pyfilepath = "E:\Vtb\\vtuber-kit\src\character_renderer.py"
>>>>>>> c1686f1b2a30162a87d589f822c70793308d2d28
        cmdMSD = "python %s" % pyfilepath
        p_res = os.popen(cmdMSD)
        print(p_res.read())

<<<<<<< HEAD

=======
>>>>>>> c1686f1b2a30162a87d589f822c70793308d2d28
if __name__ == '__main__':
    app = QApplication([])
    wid = myMainForm()
    wid.show()
    app.exec_()
