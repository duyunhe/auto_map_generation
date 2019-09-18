# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 17:15
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : data.py


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


def load_road():
    road_list = read_road()
    yh_list = [10, 8, 16, 17, 18, 20]
    yhtl = []
    for i, road in enumerate(road_list):
        if i in yh_list:
            yhtl.append(road)
    return yhtl
