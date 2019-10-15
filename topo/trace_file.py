# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 18:59
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : trace_file.py

from readMap import read_sqlite
from map.save_map import save_sqlite, delete_all
from src.geo import calc_dist
from copy import copy
import matplotlib.pyplot as plt
from topo.map_struct import MapSegment
from topo.draw import draw_seg, draw_line_idx
from src.draw import draw_png


def extract_tunnel(trace_list):
    last_data = None
    data_pair_list = []
    for trace in trace_list:
        for data in trace:
            if last_data:
                itv = data - last_data
                if itv > 180:
                    data_pair_list.append([last_data.x, last_data.y, data.x, data.y])
            last_data = data
    print "match ", len(data_pair_list)
    return data_pair_list


def get_route():
    ln_list, pt_list = read_sqlite('../data/hz1.db')
    return ln_list


def split(road):
    last_pt = None
    all_dist = 0
    road_pt_list = []
    temp_list = []
    for pt in road.point_list:
        if last_pt is not None:
            dist = calc_dist([pt.x, pt.y], [last_pt.x, last_pt.y])
            all_dist += dist
            temp_list.append(pt)
            if all_dist >= 300:
                # break
                all_dist = 0
                road_pt_list.append(temp_list)
                temp_list = [pt]
        last_pt = pt
    if len(temp_list) > 1:
        road_pt_list.append(temp_list)
    n = len(road_pt_list)
    road_list = []
    for i in range(n):
        new_road = copy(road)
        new_road.point_list = road_pt_list[i]
        road_list.append(new_road)
    return road_list


def mod_road(road_list):
    road_list[1353].point_list[1] = road_list[2152].point_list[0]


def step0():
    road_list = get_route()
    sel_i = 6704
    t = road_list.pop(sel_i)
    new_road_list = split(t)
    road_list.extend(new_road_list)
    mod_road(road_list)
    delete_all()
    save_sqlite(road_list)


if __name__ == '__main__':
    step0()
