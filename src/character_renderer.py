import sys
import math

import numpy as np
import yaml

import glfw
from OpenGL.GL import *

from psd_tools import PSDImage

import face_capture
import matrix


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
    with open('../assets/layer_depth.yaml', encoding='utf8') as f:
        depth_info = yaml.load(f, yaml.FullLoader)
    for layer in all_layers:
        if layer['layer_path'] in depth_info:
            layer['layer_depth'] = depth_info[layer['layer_path']]


motion_buffer = None


def use_motion_buffer():
    global motion_buffer
    buffer_strength = 0.95
    face_orientation = face_capture.get_current_face_orientation()
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

    vtuber_window_size = 800, 800

    glfw.init()
    show_transparent_window()
    glfw.window_hint(glfw.RESIZABLE, False)
    window = glfw.create_window(*vtuber_window_size, 'vtuber', None, None)
    glfw.make_context_current(window)
    monitor_size = glfw.get_video_mode(glfw.get_primary_monitor()).size
    glfw.set_window_pos(window, monitor_size.width - vtuber_window_size[0], monitor_size.height - vtuber_window_size[1])

    glViewport(0, 0, *vtuber_window_size)

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

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        horizontal_rotation_val, vertical_rotation_val = use_motion_buffer()
        for layer in all_layers:
            if layer['layer_path'] in face_capture.psd_eye_layers + face_capture.psd_mouth_layers:
                if layer['layer_path'] != '表情上/目/' + str(face_capture.get_current_eye_size()) and layer['layer_path'] != '表情上/口/' + str(face_capture.get_current_mouth_size()):
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
                if not layer['layer_path'] == '身体基本/体':
                    a = a @ matrix.translate(0, 0, -1) \
                        @ matrix.rotate_ax(horizontal_rotation_val, axis=(0, 2)) \
                        @ matrix.rotate_ax(vertical_rotation_val, axis=(2, 1)) \
                        @ matrix.translate(0, 0, 1)
                a = a @ matrix.perspective(999)
                glTexCoord4f(*b)
                glVertex4f(*a)
            glEnd()
        glfw.swap_buffers(window)


if __name__ == '__main__':
    psd = PSDImage.open('../assets/空色れん水結様簡略版.psd')
    all_layers, size = extract_layers_from_psd(psd)
    add_depth_to_layers(all_layers)
    gl_drawing_loop(all_layers, size)
