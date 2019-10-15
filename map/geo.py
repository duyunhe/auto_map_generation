# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 11:14
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : geo.py


import math
from topo.map_struct import Point


def get_parallel(p0, p1, d):
    """
    :param p0: 线段的两个点
    :param p1: 
    :param d: 平行线偏离的距离
    :return: dst_p0, dst_p1 右手边的两个点 dst_p2, dst_p3 左手边的两个点
    """
    x0, y0, x1, y1 = p0.x, p0.y, p1.x, p1.y
    dx, dy = x1 - x0, y1 - y0
    norm = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    unitx, unity = dx / norm, dy / norm
    # 右手边
    xh0, yh0 = x0 + unity * d, y0 - unitx * d
    xh1, yh1 = x1 + unity * d, y1 - unitx * d
    dst_p0, dst_p1 = Point(xh0, yh0), Point(xh1, yh1)

    xh2, yh2 = x0 - unity * d, y0 + unitx * d
    xh3, yh3 = x1 - unity * d, y1 + unitx * d
    dst_p2, dst_p3 = Point(xh2, yh2), Point(xh3, yh3)

    return dst_p0, dst_p1, dst_p2, dst_p3
