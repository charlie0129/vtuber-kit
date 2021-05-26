# vtuber-kit

## 环境依赖

1. `python` >=`3.8`
2. `dlib` >=`19.22.0`
3. `opencv-python` >=`4.5.1.48`
4. `numpy` >=`1.19.2`
5. `glfw` >=`2.1.0`
6. `psd-tools` >=`1.9.17`

## 运行方法

1. 安装依赖
2. 查阅 `assets/sample_config.json` 来获取配置文件样例，大概看一下有些啥，等会你可能需要修改，里面的属性应该很好理解（指那些文件路径，复杂的不用管）。你可以直接用这个样例配置文件（那就先得问我要~~萝莉~~模型）或自己写一个
3. 准备必要数据
    1. 拍一张你直视电脑摄像头的照片（***张开***眼睛和嘴巴，不要张太大，差不多就行，因为你要让萝莉张开嘴和眼睛到最大的话也得做这个动作，防止别人看你在张牙舞爪）
    2. 拍一张你直视电脑摄像头的照片（***闭上***眼睛和嘴巴）
    3. 下载 `shape_predictor_68_face_landmarks.dat`，你可以从[这里](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)获得它。
    4. 准备一张~~萝莉~~ or 任意 `psd` 图片，以及每个图层的深度信息，深度信息写在配置文件中（见配置文件样例）如果你没有这种图片，你可以自己画 or 找别人画 ~~or 问我要~~
    5. 将以上所有文件放到你找得到的地方（建议放在 `assets` 文件夹里）
4. 编辑配置文件
    1. 将 `std_face_open_image_path` 的值改为你张开眼睛和嘴巴的图片的位置（以下路径均建议使用相对路径）
    2. 将 `std_face_closed_image_path` 的值改为你闭上眼睛和嘴巴的图片的位置
    3. 将 `face_landmarks_path` 的值改为你下载的 `shape_predictor_68_face_landmarks.dat` 文件的位置
    4. 将 `psd_file_path` 的值改为 `psd` 图片的位置
    5. 将 `camera_path` 改为你电脑摄像头的路径，一般来说保持 `0` 即可，除非你电脑有多个摄像头
    6. 深度信息等根据 `psd` 人物的不同酌情修改（要是用我给的萝莉的话就不用改了）
    7. 其他设置以后再说🙄
5. 在命令行参数里指定你要用的配置文件，比如 `python3 src/character_renderer.py assets/sample_config.json` 使用样例配置文件运行

## Acknowledgements

1. [RimoChan/Vtuber_Tutorial: 【教程】从零开始的自制Vtuber！ (github.com)](https://github.com/RimoChan/Vtuber_Tutorial)

