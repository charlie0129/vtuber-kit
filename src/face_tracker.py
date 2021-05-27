import logging
import threading
import time

import cv2
import numpy as np
import dlib
from itertools import chain

config_data = {}

detector = dlib.get_frontal_face_detector()


def set_config_data(data_in):
    global config_data
    config_data = data_in


def locate_main_face(img):
    dets = detector(img, 0)
    if not dets:
        return None
    return max(dets, key=lambda det: (det.right() - det.left()) * (det.bottom() - det.top()))


def extract_face_landmarks(img, face_location):
    landmark_shape = predictor(img, face_location)
    face_landmarks = []
    for i in range(68):
        pos = landmark_shape.part(i)
        face_landmarks.append(np.array([pos.x, pos.y], dtype=np.float32))
    return face_landmarks


def generate_face_identifiers(face_landmarks):
    def get_center(array_in):
        return sum([face_landmarks[i] for i in array_in]) / len(array_in)

    left_eyebrow = [18, 19, 20, 21]
    right_eyebrow = [22, 23, 24, 25]
    chin = [6, 7, 8, 9, 10]
    nose = [29, 30]
    return get_center(left_eyebrow + right_eyebrow), get_center(chin), get_center(nose)


def get_face_orientation(face_identifiers):
    center_of_eyebrows, center_of_chin, center_of_nose = face_identifiers
    middle_line = center_of_eyebrows - center_of_chin
    hypotenuse = center_of_eyebrows - center_of_nose
    horizontal_rotation_val = np.cross(middle_line, hypotenuse) / np.linalg.norm(middle_line) ** 2
    vertical_rotation_val = middle_line @ hypotenuse / np.linalg.norm(middle_line) ** 2
    return np.array([horizontal_rotation_val, vertical_rotation_val])


cam_capture_count = 0
_cam_capture_count_ = 0
cam_fps_count_start_time = time.time()
fps_count_interval = 4


def get_face_orientation_from_picture(img):
    global eye_height, _cam_capture_count_, cam_fps_count_start_time, cam_capture_count
    global mouth_height

    main_face_location = locate_main_face(img)
    if not main_face_location:
        return None
    face_landmarks = extract_face_landmarks(img, main_face_location)
    if config_data['debug']:
        global debug_face_landmarks
        debug_face_landmarks = face_landmarks
        _cam_capture_count_ += 1
        if time.time() - cam_fps_count_start_time >= fps_count_interval:
            cam_fps_count_start_time = time.time()
            cam_capture_count = _cam_capture_count_
            _cam_capture_count_ = 0
    key_points = face_landmarks
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
    face_identifiers = generate_face_identifiers(face_landmarks)
    rotation_vals = get_face_orientation(face_identifiers)
    return rotation_vals


face_orientation = None


def camera_capture_loop():
    while 'config_name' not in config_data:
        time.sleep(0.1)
    global predictor
    global reference_face_orientation
    global face_orientation
    global current_eye_height
    global current_mouth_height
    global closed_mouth_height
    global closed_eye_height
    global open_mouth_height
    global open_eye_height
    global eye_height_step
    global mouth_height_step
    predictor = dlib.shape_predictor(config_data['face_landmarks_path'])
    reference_face_orientation = get_face_orientation_from_picture(cv2.imread(config_data['std_face_open_image_path']))
    face_orientation = reference_face_orientation - reference_face_orientation
    current_eye_height = open_eye_height = eye_height
    current_mouth_height = open_mouth_height = mouth_height
    get_face_orientation_from_picture(cv2.imread(config_data['std_face_closed_image_path']))
    closed_mouth_height = eye_height
    closed_eye_height = mouth_height

    eye_height_step = (open_eye_height - closed_eye_height) / (len(config_data['psd_eye_layers']) - 1)
    mouth_height_step = (open_mouth_height - closed_mouth_height) / (len(config_data['psd_mouth_layers']) - 1)

    cap = cv2.VideoCapture(config_data['camera_path'])
    logging.info('Face capture has started...')
    while True:
        global cam_img
        ret, cam_img = cap.read()
        new_face_orientation = get_face_orientation_from_picture(cam_img)
        current_eye_height = eye_height
        current_mouth_height = mouth_height
        if new_face_orientation is not None:
            face_orientation = new_face_orientation - reference_face_orientation
        time.sleep(1 / 60)


def debug_draw_line(img, start_point_idx, end_point_idx, color):
    cv2.line(img,
             (int(debug_face_landmarks[start_point_idx][0]), int(debug_face_landmarks[start_point_idx][1])),
             (int(debug_face_landmarks[end_point_idx][0]), int(debug_face_landmarks[end_point_idx][1])),
             color,
             2)


character_render_count = 0
_character_render_count_ = 0
render_fps_count_start_time = time.time()


def get_debug_camera_image():
    global cam_capture_count, fps_count_interval, character_render_count, _character_render_count_, start_time, render_fps_count_start_time

    _character_render_count_ += 1
    if time.time() - render_fps_count_start_time >= fps_count_interval:
        render_fps_count_start_time = time.time()
        character_render_count = _character_render_count_
        _character_render_count_ = 0

    debug_cam_img = cam_img.copy()
    color = (255, 255, 255)

    cv2.putText(debug_cam_img,
                'Capture FPS: %.2f' % (cam_capture_count / fps_count_interval),
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)
    cv2.putText(debug_cam_img,
                'Render FPS: %.2f' % (character_render_count / fps_count_interval),
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)
    cv2.putText(debug_cam_img,
                'Eye Size: %d %s' % (get_current_eye_size(),
                                     '' if get_current_eye_size() < len(config_data['psd_eye_layers']) - 1
                                     else '(max)'),
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)
    cv2.putText(debug_cam_img,
                'Mouth Size: %d %s' % (get_current_mouth_size(),
                                       '' if get_current_mouth_size() < len(config_data['psd_mouth_layers']) - 1
                                       else '(max)'),
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)
    for i, (px, py) in enumerate(debug_face_landmarks):
        cv2.putText(debug_cam_img, str(i), (int(px), int(py)), cv2.FONT_HERSHEY_COMPLEX, 0.25, (0, 255, 255))

    for i in chain(range(0, 16), range(36, 41), range(42, 47), range(48, 60), range(27, 30), range(31, 35),
                   range(17, 21), range(22, 26)):
        debug_draw_line(debug_cam_img, i, i + 1, color)

    debug_draw_line(debug_cam_img, 36, 41, color)
    debug_draw_line(debug_cam_img, 42, 47, color)
    return debug_cam_img


def get_current_face_orientation():
    return face_orientation


def get_current_eye_size():
    size = int((current_eye_height - closed_eye_height) / eye_height_step)
    size = size if size < len(config_data['psd_eye_layers']) else len(config_data['psd_eye_layers']) - 1
    return size if size >= 0 else 0


def get_current_mouth_size():
    size = int((current_mouth_height - closed_mouth_height) / mouth_height_step)
    size = size if size < len(config_data['psd_mouth_layers']) else len(config_data['psd_mouth_layers']) - 1
    return size if size >= 0 else 0


t = threading.Thread(target=camera_capture_loop)
# t.setDaemon(True)
t.start()

if __name__ == '__main__':
    while True:
        time.sleep(0.1)
