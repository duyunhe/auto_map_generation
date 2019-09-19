# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 17:15
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : data.py

from src.common import xy_angle, mean_angle


def read_road(idx=None):
    if idx is None:
        filename = '../data/road.txt'
    else:
        filename = '../data/road{0}.txt'.format(idx)
    fp = open(filename)
    rd_list = []
    for line in fp.readlines():
        pts = line.strip('\n').split(';')
        road = []
        # for convenience
        y_min, y_max = 100000, 0
        for pt in pts:
            x, y = map(float, pt.split(','))
            road.append([x, y])
            y_min, y_max = min(y, y_min), max(y, y_max)
        if y_min > 85200 and y_max < 85500:
            rd_list.append(road)
    return rd_list


def info(idx, road):
    n = len(road)
    a_list = [xy_angle(road[i - 1][0], road[i - 1][1], road[i][0], road[i][1]) for i in range(1, n)]
    ma = mean_angle(a_list)
    print idx, ma, n
    return ma, n


def load_road(ort=0):
    road_list = read_road()
    ret_list = []
    for i, road in enumerate(road_list):
        ma, l = info(i, road)
        if l > 50:
            if ort == 0:
                if ma < 180:
                    ret_list.append(road)
            else:
                if ma > 180:
                    ret_list.append(road)
    return ret_list
