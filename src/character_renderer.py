import time
import datetime
import math

import numpy as np
import os
import sys
import argparse
import json
import glfw
import cv2
from OpenGL.GL import *

from psd_tools import PSDImage

path = os.getcwd()
sys.path.append(path)

import src.face_tracker as face_tracker
import src.matrix as matrix

config_data = {}

voice_mode_file = None
should_close_window = False


def extract_layers_from_psd(psd):
    all_layers = []

    def dfs(layer, path=''):
        if layer.is_group():
            for i in layer:
                dfs(i, path + layer.name + '/')
        else:
            a, b, c, d = layer.bbox
            npdata = layer.numpy()
            npdata[:, :, 0], npdata[:, :, 2] = npdata[:, :, 2].copy(), npdata[:, :, 0].copy()
            all_layers.append({'layer_path': path + layer.name, 'layer_location': (b, a, d, c), 'npdata': npdata})

    for layer in psd:
        dfs(layer)
    return all_layers, psd.size


def add_depth_to_layers(all_layers):
    depth_info = config_data['psd_layer_depths']
    for layer in all_layers:
        if layer['layer_path'] in depth_info:
            layer['layer_depth'] = depth_info[layer['layer_path']]


motion_buffer = None


def use_motion_buffer():
    global motion_buffer
    buffer_strength = config_data['motion_buffer_strength']
    face_orientation = face_tracker.get_current_face_orientation()
    if motion_buffer is None:
        motion_buffer = face_orientation
    else:
        motion_buffer = motion_buffer * buffer_strength + face_orientation * (1 - buffer_strength)
    return motion_buffer


def show_transparent_window():
    glfw.window_hint(glfw.DECORATED, False)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.FLOATING, True)


def gl_drawing_loop(all_layers, psd_size):
    def generate_texture(img):
        w, h = img.shape[:2]
        d = 2 ** int(max(math.log2(w), math.log2(h)) + 1)
        texture = np.zeros([d, d, 4], dtype=img.dtype)
        texture[:w, :h] = img
        return texture, (w / d, h / d)

    glfw.init()
    show_transparent_window()
    glfw.window_hint(glfw.RESIZABLE, False)
    window = glfw.create_window(*config_data['renderer_window_size'], config_data['config_name'], None, None)
    glfw.make_context_current(window)
    monitor_size = glfw.get_video_mode(glfw.get_primary_monitor()).size
    glfw.set_window_pos(window, monitor_size.width - config_data['renderer_window_size'][0] +
                        config_data['renderer_window_position_offset'][0],
                        monitor_size.height - config_data['renderer_window_size'][1] +
                        config_data['renderer_window_position_offset'][1])

    glViewport(0, 0, *config_data['renderer_window_size'])

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)

    for layer in all_layers:
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        texture, texture_location = generate_texture(layer['npdata'])
        width, height = texture.shape[:2]
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_FLOAT, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)
        layer['layer_id'] = texture_id
        layer['texture_location'] = texture_location

    while not (glfw.window_should_close(window) or should_close_window):
        read_mode_from_voice_mode_file()
        glfw.poll_events()
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        horizontal_rotation_val, vertical_rotation_val = use_motion_buffer()

        for layer in all_layers:
            if layer['layer_path'] in config_data['psd_eye_layers'] + config_data['psd_mouth_layers']:
                if layer['layer_path'] != config_data['psd_eye_layer_prefix'] \
                        + config_data['psd_eye_layer_suffix'] % face_tracker.get_current_eye_size() \
                        and layer['layer_path'] != config_data['psd_mouth_layer_prefix'] + \
                        config_data['psd_mouth_layer_suffix'] % face_tracker.get_current_mouth_size():
                    continue

            a, b, c, d = layer['layer_location']
            z = layer['layer_depth']
            if type(z) in [int, float]:
                z1, z2, z3, z4 = [z, z, z, z]
            else:
                [z1, z2], [z3, z4] = z
            q, w = layer['texture_location']
            p1 = np.array([a, b, z1, 1, 0, 0, 0, z1])
            p2 = np.array([a, d, z2, 1, z2 * w, 0, 0, z2])
            p3 = np.array([c, d, z3, 1, z3 * w, z3 * q, 0, z3])
            p4 = np.array([c, b, z4, 1, 0, z4 * q, 0, z4])

            model = matrix.scale(2 / psd_size[0], 2 / psd_size[1], 1) @ \
                    matrix.translate(-1, -1, 0) @ \
                    matrix.rotate_ax(-math.pi / 2, axis=(0, 1))
            glBindTexture(GL_TEXTURE_2D, layer['layer_id'])
            glColor4f(1, 1, 1, 1)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBegin(GL_QUADS)
            for p in [p1, p2, p3, p4]:
                a = p[:4]
                b = p[4:8]
                a = a @ model
                a[0:2] *= a[2]
                if not layer['layer_path'] == config_data['psd_body_layer_name']:
                    a = a @ matrix.translate(0, 0, -1) \
                        @ matrix.rotate_ax(horizontal_rotation_val, axis=(0, 2)) \
                        @ matrix.rotate_ax(vertical_rotation_val, axis=(2, 1)) \
                        @ matrix.translate(0, 0, 1)
                a = a @ matrix.perspective(999)
                glTexCoord4f(*b)
                glVertex4f(*a)
            glEnd()
        glfw.swap_buffers(window)
        if config_data['debug']:
            cv2.imshow("Camera Debug", face_tracker.get_debug_camera_image())


def read_mode_from_voice_mode_file():
    global voice_mode_file, should_close_window

    if voice_mode_file == None:
        return

    voice_mode_file.seek(0)
    file_content = voice_mode_file.read()

    if file_content == '-1':
        should_close_window = True


def dir_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)


def manual_start(_config_data_, is_debug_enabled=False):
    global config_data
    global should_close_window
    should_close_window = False

    config_data = _config_data_
    config_data['debug'] = is_debug_enabled

    print('loaded config: ' + config_data['config_name'])

    face_tracker.set_config_data(config_data)

    while face_tracker.get_camera_image() is None:
        time.sleep(0.1)

    global psd, all_layers, size
    psd = PSDImage.open(config_data['psd_file_path'])

    all_layers, size = extract_layers_from_psd(psd)
    add_depth_to_layers(all_layers)
    gl_drawing_loop(all_layers, size)


def manual_stop():
    global should_close_window
    should_close_window = True


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ConsoleTextHeaders:
    INFO = '[' + Colors.OKBLUE + 'INFO' + Colors.ENDC + '] '


def print_logging_info(string):
    print(str(datetime.datetime.now().time()) + ' ' + ConsoleTextHeaders.INFO + string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('config',
                        type=dir_path,
                        help='path to the config file (json)')

    parser.add_argument('-d', '--debug',
                        dest='debug',
                        action='store_true',
                        help='toggle debug mode (show face landmarks)')

    args = parser.parse_args()

    if args.debug:
        print_logging_info('debug mode is ON')
        global face_tracker_initialize_time, psd_load_time

    config_file = open(args.config, encoding='utf8')
    config_data = json.load(config_file)
    config_file.close()

    config_data['debug'] = args.debug

    print_logging_info('loaded config: ' + config_data['config_name'])

    face_tracker.set_config_data(config_data)

    if args.debug:
        print_logging_info('initializing face tracker...')
        face_tracker_initialize_time = time.time()

    while face_tracker.get_camera_image() is None:
        time.sleep(0.1)

    if args.debug:
        face_tracker_initialize_time = time.time() - face_tracker_initialize_time
        print_logging_info('face tracker initialized in ' + '%.0fms' % (face_tracker_initialize_time * 1000))

    if args.debug:
        print_logging_info('loading PSD file...')
        psd_load_time = time.time()

    psd = PSDImage.open(config_data['psd_file_path'])

    all_layers, size = extract_layers_from_psd(psd)
    add_depth_to_layers(all_layers)

    if args.debug:
        psd_load_time = time.time() - psd_load_time
        print_logging_info('PSD file loaded in ' + '%.0fms' % (psd_load_time * 1000))
        print_logging_info('OpenGL drawing will start NOW...')

    gl_drawing_loop(all_layers, size)
    exit(0)
