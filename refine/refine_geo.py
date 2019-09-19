# -*- coding: utf-8 -*-
# @Time    : 2019/9/5 9:34
# @Author  : yhdu@tongwoo.cn
# @简介    : 从纯地理信息上对道路进行修正
# @File    : refine_geo.py

from src.draw import draw_center, draw_line_idx, draw_png
import matplotlib.pyplot as plt
from src.coord import bl2xy
from src.common import xy_angle, mean_angle
from data import read_road


def info(idx, road):
    n = len(road)
    a_list = [xy_angle(road[i - 1][0], road[i - 1][1], road[i][0], road[i][1]) for i in range(1, n)]
    ma = mean_angle(a_list)
    print idx, ma, n
    return ma, n


def draw():
    road_list = read_road()
    ex_list = [9]
    for i, road in enumerate(road_list):
        ma, l = info(i, road)
        if l > 50:
            draw_center(road)
            draw_line_idx(road, i)


if __name__ == '__main__':
    draw()
    draw_png()
    plt.show()
