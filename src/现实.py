import logging
import threading
import time

import cv2
import numpy as np
import dlib

detector = dlib.get_frontal_face_detector()

目 = ['表情上/目/0', '表情上/目/1', '表情上/目/2', '表情上/目/3', '表情上/目/4']
口 = ['表情上/口/0', '表情上/口/1', '表情上/口/2', '表情上/口/3']


def 人脸定位(img):
    dets = detector(img, 0)
    if not dets:
        return None
    return max(dets, key=lambda det: (det.right() - det.left()) * (det.bottom() - det.top()))


predictor = dlib.shape_predictor('../assets/shape_predictor_68_face_landmarks.dat')


def 提取关键点(img, 脸位置):
    landmark_shape = predictor(img, 脸位置)
    关键点 = []
    for i in range(68):
        pos = landmark_shape.part(i)
        关键点.append(np.array([pos.x, pos.y], dtype=np.float32))
    return 关键点


def 生成构造点(关键点):
    def 中心(索引数组):
        return sum([关键点[i] for i in 索引数组]) / len(索引数组)

    左眉 = [18, 19, 20, 21]
    右眉 = [22, 23, 24, 25]
    下巴 = [6, 7, 8, 9, 10]
    鼻子 = [29, 30]
    return 中心(左眉 + 右眉), 中心(下巴), 中心(鼻子)


def 生成特征(构造点):
    眉中心, 下巴中心, 鼻子中心 = 构造点
    中线 = 眉中心 - 下巴中心
    斜边 = 眉中心 - 鼻子中心
    横旋转量 = np.cross(中线, 斜边) / np.linalg.norm(中线) ** 2
    竖旋转量 = 中线 @ 斜边 / np.linalg.norm(中线) ** 2
    return np.array([横旋转量, 竖旋转量])


def 提取图片特征(img):
    global eye_height
    global mouth_height
    脸位置 = 人脸定位(img)
    if not 脸位置:
        return None
    关键点 = 提取关键点(img, 脸位置)
    key_points = 关键点
    eye_height = -(key_points[37][1] - key_points[41][1] +
                   key_points[38][1] - key_points[40][1] +
                   key_points[43][1] - key_points[47][1] +
                   key_points[44][1] - key_points[46][1]
                   ) / (key_points[45][0] - key_points[42][0] +
                        key_points[49][0] - key_points[36][0])

    mouth_height = -(key_points[61][1] - key_points[67][1] +
                     key_points[62][1] - key_points[66][1] +
                     key_points[63][1] - key_points[65][1] +
                     key_points[51][1] - key_points[57][1]
                     ) / (key_points[54][0] - key_points[48][0] +
                          key_points[64][0] - key_points[60][0])
    构造点 = 生成构造点(关键点)
    旋转量组 = 生成特征(构造点)
    return 旋转量组


def 捕捉循环():
    global 原点特征组
    global 特征组
    global 当前眼睛高度
    global 当前嘴巴高度
    global 闭嘴高度
    global 闭眼高度
    global 张嘴高度
    global 张眼高度
    global 眼睛高度分级
    global 嘴巴高度分级
    原点特征组 = 提取图片特征(cv2.imread('../assets/std_face_open.png'))
    特征组 = 原点特征组 - 原点特征组
    当前眼睛高度 = 张眼高度 = eye_height
    当前嘴巴高度 = 张嘴高度 = mouth_height
    提取图片特征(cv2.imread('../assets/std_face_closed.png'))
    闭嘴高度 = eye_height
    闭眼高度 = mouth_height

    眼睛高度分级 = (张眼高度 - 闭眼高度) / (len(目) - 1)
    嘴巴高度分级 = (张嘴高度 - 闭嘴高度) / (len(口) - 1)

    cap = cv2.VideoCapture(0)
    logging.warning('开始捕捉了！')
    while True:
        ret, img = cap.read()
        新特征组 = 提取图片特征(img)
        当前眼睛高度 = eye_height
        当前嘴巴高度 = mouth_height
        if 新特征组 is not None:
            特征组 = 新特征组 - 原点特征组
        time.sleep(1 / 60)


def 获取特征组():
    return 特征组


def 获取眼睛大小等级():
    等级 = int((当前眼睛高度 - 闭眼高度) / 眼睛高度分级)
    等级 = 等级 if 等级 < len(目) else len(目) - 1
    return 等级 if 等级 >= 0 else 0


def 获取嘴巴大小等级():
    等级 = int((当前嘴巴高度 - 闭嘴高度) / 嘴巴高度分级)
    等级 = 等级 if 等级 < len(口) else len(口) - 1
    return 等级 if 等级 >= 0 else 0


t = threading.Thread(target=捕捉循环)
t.setDaemon(True)
t.start()
logging.warning('捕捉线程启动中……')

if __name__ == '__main__':
    while True:
        time.sleep(0.1)
        print(特征组)
