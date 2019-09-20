# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 16:24
# @Author  : yhdu@tongwoo.cn
# @简介    : 合并cluster的分段线段
# @File    : merge_geo.py

from data import load_road
from src.common import xy_angle, mean_angle, rotate, debug_time, \
    xy_radian, mean_y_filter, median_y_filter
import numpy as np
import math
from src.draw import draw_center, draw_png
from src.geo import dog_last
import matplotlib.pyplot as plt
import pandas as pd


def save_road(road, filename):
    fp = open(filename, 'w')
    sp_list = ["{0:.2f},{1:.2f}".format(pt[0], pt[1]) for pt in road]
    str_road = ';'.join(sp_list)
    fp.write(str_road + '\n')
    fp.close()


def norm_road(road_list):
    """
    使道路正向(0-90, 270-360)
    :param road_list: 
    :return: 
    """
    ma_list = []
    ret_list = []
    for road in road_list:
        a_list = []
        last_pt = None
        for pt in road:
            if last_pt:
                a = xy_angle(last_pt[0], last_pt[1], pt[0], pt[1])
                a_list.append(a)
            last_pt = pt
        ma = mean_angle(a_list)
        print ma
        ret_list.append(road)
        ma_list.append(ma)
    # then rotate
    ama = np.mean(ma_list)
    final_list = []
    for road in ret_list:
        road = rotate(road, 90 - ama)
        final_list.append(road)
    return final_list, ama


def calc_y(pt0, pt1, x0):
    ax = pt1[0] - pt0[0]
    dx = x0 - pt0[0]
    if ax == 0 or dx == 0:
        return pt0[1]
    ay = pt1[1] - pt0[1]
    return dx / ax * ay + pt0[1]


def merge_road(road_list):
    tup_list = []
    max_x = -1e10
    for i, road in enumerate(road_list):
        tup = (road[0][0], road[-1][0], road)
        max_x = max(max_x, road[-1][0])
        tup_list.append(tup)
    tup_list.sort()

    cur_idx = 0
    n_road = len(tup_list)
    pos = [0] * n_road
    scan_list = [cur_idx]
    ret_road = []
    cur_idx = 1

    while True:
        # add new road into scan list
        if len(scan_list) == 0:
            if cur_idx == n_road:
                break
            scan_list.append(cur_idx)
            cur_idx += 1
        # find minx to update y
        minx, sel_idx = 1e10, -1
        for idx in scan_list:
            p = pos[idx]            # idx
            r = tup_list[idx][2]    # road
            x = r[p][0]             # x
            if x < minx:
                minx, sel_idx = x, idx
        # check if new segment should be added
        if cur_idx < n_road:
            new_x = tup_list[cur_idx][2][0][0]
            if new_x < minx:
                scan_list.append(cur_idx)
                sel_idx = cur_idx
                cur_idx += 1
                minx = new_x
        # get mean y
        s, w = 0.0, 0
        for idx in scan_list:
            p = pos[idx]
            r = tup_list[idx][2]
            l = len(r)
            d = min(p, l - 1 - p)
            if d > 10:
                d = 10
            per = math.pow(1.1, d) - 0.9
            if sel_idx == idx:
                y = r[p][1]
            else:
                y = calc_y(r[p - 1], r[p], minx)
            s, w = s + y * per, w + per
        # get new point
        ret_road.append([minx, s / w])
        pos[sel_idx] += 1
        # check if any segment will be removed
        l = len(tup_list[sel_idx][2])
        # print pos[sel_idx], l
        if pos[sel_idx] == l:
            print sel_idx
            scan_list.remove(sel_idx)
    return ret_road


def find_convex(road):
    ma_list = []
    last_pt = None
    for pt in road:
        if last_pt is not None:
            r = xy_radian(last_pt[0], last_pt[1], pt[0], pt[1])
            # a = xy_angle(last_pt[0], last_pt[1], pt[0], pt[1])
            # ma_list.append(a)
            ma_list.append(r)
        last_pt = pt
    data = pd.Series(ma_list)


def draw_outline(road):
    last_pt, last_r = None, None
    window = []
    for i, pt in enumerate(road):
        if last_pt is not None:
            r = xy_radian(last_pt[0], last_pt[1], pt[0], pt[1])
            if len(window) < 10:
                window.append(r)
            else:
                window = window[1:]
                window.append(r)
            if last_r is not None:
                mr = np.mean(window)
                a = r - last_r
                if 1400 < i < 1700:
                    if mr > .5:
                        c = 'r'
                    elif mr < -.5:
                        c = 'g'
                    else:
                        c = 'k'
                    plt.text(pt[0], pt[1], "{0:.1f}".format(mr), color=c)
            last_r = r
        last_pt = pt
    x_list, y_list = zip(*road)
    plt.plot(x_list, y_list)


def merge(road_list):
    """
    :param road_list: list(list(x,y))
    :return: 
    """
    road_list, ama = norm_road(road_list)
    final_road = merge_road(road_list)
    # find_convex(final_road)
    final_road = rotate(final_road, ama - 90)
    final_road = mean_y_filter(final_road)
    final_road = median_y_filter(final_road)
    # final_road = dog_last(final_road, 5)
    # find_convex(final_road)
    # draw_outline(final_road)
    # for road in road_list:
    #     draw_center(road)
    draw_center(final_road, 'k')
    return final_road


def main():
    total_list = load_road(0)
    road = merge(total_list)
    save_road(road, '..\data\yh.txt')
    draw_png()
    plt.show()


if __name__ == '__main__':
    main()
