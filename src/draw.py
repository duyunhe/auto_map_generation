# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 13:58
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : draw.py


import numpy as np
import matplotlib.pyplot as plt
from coord import bl2xy


def draw_points(xy_list, marker, color, alpha, label):
    if len(xy_list) == 0:
        return
    x_list, y_list = zip(*xy_list)
    mx, my = np.mean(x_list), np.mean(y_list)
    plt.plot(x_list, y_list, marker=marker, color=color, linestyle='', alpha=alpha)
    if label >= 0:
        plt.text(mx, my, str(label))


def draw_center(pt_list, color=None):
    x_list, y_list = zip(*pt_list)
    plt.plot(x_list, y_list, color=color, marker='', linewidth=1)


def draw_line(pt_list):
    x_list, y_list = zip(*pt_list)
    plt.plot(x_list, y_list, color='orange', marker='+', linestyle='')
    plt.plot(x_list, y_list, color='k', alpha=.1)


def draw_line_idx(pt_list, idx):
    plt.text(pt_list[0][0], pt_list[0][1], str(idx))


def draw_png():
    image = plt.imread('../img/hz.png')
    pt0 = 120.05859375, 30.3302126854
    pt1 = 120.16845703125, 30.235340577517935
    x0, y0 = bl2xy(pt0[1], pt0[0])
    x1, y1 = bl2xy(pt1[1], pt1[0])
    extent = (x0, x1, y1, y0)
    plt.imshow(image, alpha=.8, origin='upper', extent=extent)


def draw_seg(segment, c='b', linewidth=1, alpha=1):
    x_list, y_list = [], []
    for pt in segment.point_list:
        x_list.append(pt.x)
        y_list.append(pt.y)
    plt.plot(x_list, y_list, c=c, alpha=alpha, linewidth=linewidth)
