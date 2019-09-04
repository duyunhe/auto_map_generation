# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 11:19
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : common.py


import numpy as np
from time import clock
from math import atan2, pi, fabs, cos, sin, radians
from collections import defaultdict


def debug_time(func):
    def wrapper(*args, **kwargs):
        bt = clock()
        a = func(*args, **kwargs)
        et = clock()
        print func.__name__, "cost", round(et - bt, 3), "secs"
        return a
    return wrapper


class TaxiData(object):
    """
    车牌号 veh
    坐标的xy值
    GPS显示角度 angle
    实际计算得到角度 ort
    GPS时间 speed_time
    """
    def __init__(self, veh, x, y, angle, speed_time):
        self.x, self.y, self.angle, self.speed_time = x, y, angle, speed_time
        self.veh = veh
        self.ort = self.angle           # angle in fact

    def __sub__(self, other):
        return (self.speed_time - other.speed_time).total_seconds()


def data_dist(d0, d1):
    return calc_dist([d0.x, d0.y], [d1.x, d1.y])


def calc_dist(pt0, pt1):
    """
    distance of two points
    :param pt0: [x0, y0]
    :param pt1: [x1, y1]
    :return: 
    """
    v0 = np.array(pt0)
    v1 = np.array(pt1)
    dist = np.linalg.norm(v0 - v1)
    return dist


def xy_angle(x0, y0, x1, y1):
    """
    :param x0: src x 
    :param y0: src y
    :param x1: dest x
    :param y1: dest y
    :return: degree of intersection angle [0-360)
    """
    dy, dx = y1 - y0, x1 - x0
    angle = 90 - 180 * atan2(dy, dx) / pi
    if angle < 0:
        angle += 360
    if angle >= 360:
        angle -= 360
    return angle


def data_angle(last_data, cur_data):
    x0, y0 = last_data.x, last_data.y
    x1, y1 = cur_data.x, cur_data.y
    return xy_angle(x0, y0, x1, y1)


def mean_angle(angle_list):
    """
    :param angle_list: list of angle(float) 
    :return: 
    """
    ans1, ans4, ans23 = 0, 0, 0
    n1, n4, n23 = 0, 0, 0
    for i, angle in enumerate(angle_list):
        if 0 <= angle < 90:
            ans1, n1 = ans1 + angle, n1 + 1
        elif 270 <= angle < 360:
            ans4, n4 = ans4 + angle, n4 + 1
        else:
            ans23, n23 = ans23 + angle, n23 + 1
    if n1 > 0 and n4 > 0:
        t = (((ans1 / n1) + 360) * n1 + ans4) / (n1 + n4)
        if t >= 360:
            t -= 360
        return t
    else:
        return (ans1 + ans23 + ans4) / (n1 + n23 + n4)


def near_angle(a0, a1, delta):
    dif = fabs(a0 - a1)
    return dif < delta or dif > 360 - delta


def near_angle_counter(a0, a1, delta):
    dif = fabs(a0 - a1)
    return dif < delta or dif > 360 - delta or 180 - delta < dif < 180 + delta


def mean_route_angle(pt_list, rev_index_list):
    """
    计算原数据集中的平均角度
    :param pt_list: list of Point
    无特别说明，本项目中的Point意为[x, y]
    :param rev_index_list: 针对每个Point的倒排索引list[i, j]
    :return: 
    """
    line_dict = defaultdict(list)
    for i, rev in enumerate(rev_index_list):
        ti, tj = rev[:]
        line_dict[ti].append(pt_list[i])
    a_list = []
    for lid, line in line_dict.items():
        if len(line) > 1:
            x0, y0 = line[0][:]
            x1, y1 = line[-1][:]
            a = xy_angle(x0, y0, x1, y1)
            a_list.append(a)
    if len(a_list) == 0:
        return -1
    return np.mean(a_list)


def rotate(pt_list, a):
    """
    核心代码
    :param pt_list: 原数据集
    :param a: 坐标旋转角度，deg，逆时针
    :return: 在新坐标系中的数据集
    """
    T = np.array(pt_list)
    rmat = np.array([[cos(radians(a)), -sin(radians(a))], [sin(radians(a)), cos(radians(a))]])
    ret = np.dot(T, rmat)
    return ret


def mean_delta(pt_list):
    a_list = []
    for i, pt in enumerate(pt_list):
        if i < len(pt_list) - 1:
            dy, dx = pt_list[i + 1][1] - pt_list[i][1], pt_list[i + 1][0] - pt_list[i][0]
            a_list.append(atan2(dy, dx))
    a = np.median(a_list)
    return a


def mean_y_filter(pt_list):
    ret_list = []
    for i, pt in enumerate(pt_list):
        bi = i - 1
        x = pt_list[i][0]
        for j in range(bi, max(0, i - 10), -1):
            x0 = pt_list[j][0]
            if x - x0 > 30:
                bi = j + 1
                break
        else:
            bi = max(0, i - 10)
        ei = i + 1
        for j in range(ei, min(len(pt_list) - 1, i + 10)):
            x0 = pt_list[j][0]
            if x0 - x > 30:
                ei = j - 1
                break
        else:
            ei = min(len(pt_list) - 1, i + 10)
        _, y_list = zip(*pt_list[bi:ei])
        y = np.mean(y_list)
        ret_list.append([x, y])
    return ret_list


def median_y_filter(pt_list):
    ret_list = []
    for i, pt in enumerate(pt_list):
        bi, ei = max(0, i - 10), min(len(pt_list), i + 10)
        x = pt_list[i][0]
        _, y_list = zip(*pt_list[bi:ei])
        y = np.median(y_list)
        ret_list.append([x, y])
    return ret_list
