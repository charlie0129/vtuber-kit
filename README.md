# vtuber-kit

## 环境依赖

1. python >=3.8
2. dlib >=19.22.0
3. opencv-python >=4.5.1.48
4. numpy >=1.19.2
5. glfw >=2.1.0
6. psd-tools >=1.9.17
7. pyyaml >=5.3.1

## 运行方法

1. 安装依赖
2. 在 `assets` 文件夹里面放入 `shape_predictor_68_face_landmarks.dat`。你可以从[这里](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)获得它。
3. 拍一张你直视电脑摄像头的照片（**张开**眼睛和嘴巴），并命名为 `std_face_open.png`，放入 `assets` 文件夹中。
4. 拍一张你直视电脑摄像头的照片（**闭上**眼睛和嘴巴），并命名为 `std_face_closed.png`，放入 `assets` 文件夹中。
5. 准备一张~~萝莉~~任意图片，以及每个图层的深度信息，将 `psd` 格式图片和 `yaml` 格式的深度信息放入 `assets` 文件夹中。（如果你没有这种图片，你可以自己画 or 找别人画 ~~or 问我要~~）
6. `cd src; python3 character_renderer.py` 开始运行。

## Acknowledgements

1. [RimoChan/Vtuber_Tutorial: 【教程】从零开始的自制Vtuber！ (github.com)](https://github.com/RimoChan/Vtuber_Tutorial)

