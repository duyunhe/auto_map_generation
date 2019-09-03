# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 13:58
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : draw.py


import numpy as np
import matplotlib.pyplot as plt


def draw_points(xy_list, marker, color, alpha, label):
    if len(xy_list) == 0:
        return
    x_list, y_list = zip(*xy_list)
    mx, my = np.mean(x_list), np.mean(y_list)
    plt.plot(x_list, y_list, marker=marker, color=color, linestyle='', alpha=alpha)
    if label >= 0:
        plt.text(mx, my, str(label))


def draw_center(pt_list, color):
    x_list, y_list = zip(*pt_list)
    plt.plot(x_list, y_list, color=color, marker='', linewidth=1)


def draw_line(pt_list):
    x_list, y_list = zip(*pt_list)
    plt.plot(x_list, y_list, color='orange', marker='+', linestyle='')
    plt.plot(x_list, y_list, color='k', alpha=.02)
