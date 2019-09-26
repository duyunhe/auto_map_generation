# -*- coding: utf-8 -*-
# @Time    : 2019/9/23 18:34
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : clip.py

from readMap import read_sqlite, make_kdtree
import matplotlib.pyplot as plt
from geo import hausdorff_dist, point2segment_xy, calc_dist
from src.common import debug_time
import numpy as np
from map_struct import MapPoint, MapSegment
from map.save_map import save, delete_all


def in_area(line):
    minx, miny, maxx, maxy = 1e10, 1e10, 0, 0
    for mp in line.point_list:
        x, y = mp.x, mp.y
        minx, miny, maxx, maxy = min(minx, x), min(miny, y), max(maxx, x), max(maxy, y)
    if minx > 72000 and maxx < 77000 and miny > 83000 and maxy < 88000:
        return True
    else:
        return False


def get_route_data():
    ln_list, pt_list = read_sqlite('../data/hz3.db')
    map_list = []
    all_list = []
    for line in ln_list:
        all_list.append(line)
        if in_area(line):
            map_list.append(line)
    kdt, _ = make_kdtree(pt_list)
    return all_list, map_list, pt_list, kdt


def get_data():
    ln_list, pt_list = read_sqlite('../data/hz3.db')
    map_list = []
    for line in ln_list:
        if in_area(line):
            map_list.append(line)
    kdt, _ = make_kdtree(pt_list)
    return map_list, pt_list, kdt


def get_yhtl():
    road = np.loadtxt('../data/np.txt', delimiter=',')
    return road


def draw_seg(segment, c='b', linewidth=1):
    x_list, y_list = [], []
    for pt in segment.point_list:
        x_list.append(pt.x)
        y_list.append(pt.y)
    plt.plot(x_list, y_list, c=c, linewidth=linewidth)


def draw_road(road, c='r'):
    x_list, y_list = zip(*road)
    plt.plot(x_list, y_list, c=c)


def merge(new_line, xy_list):
    in_idx = -1
    for i, new_pt in enumerate(new_line):
        last_pt = None
        min_dist = 1e10
        for pt in xy_list:
            if last_pt is not None:
                dist = point2segment_xy(new_pt, last_pt, pt)
                min_dist = min(dist, min_dist)
            last_pt = pt
        # print min_dist
        if min_dist < 50 and in_idx == -1:
            in_idx = i
    new_line = new_line[:in_idx]
    new_pt = new_line[-1]
    dist0, dist1 = calc_dist(new_pt, xy_list[0]), calc_dist(new_pt, xy_list[-1])
    if dist0 < dist1:
        new_line = np.append(new_line, [xy_list[0]], axis=0)
    else:
        new_line = np.append(new_line, [xy_list[-1]], axis=0)
    return new_line


def build_road(road_list, pt_list, new_road):
    sel_road = None
    for road in road_list:
        road_xy = []
        for pt in road.point_list:
            road_xy.append([pt.x, pt.y])
        dist = hausdorff_dist(road_xy, new_road)
        if dist < 50:
            print road.lid, road.name, dist
            sel_road = road_xy
    new_road = merge(new_road, sel_road)

    ms = MapSegment(-1)
    for xy in new_road:
        x, y = xy[:]
        mp = MapPoint(x, y)
        ms.add_point(mp)
    return ms


@debug_time
def get_all_data():
    all_road_list, road_list, pt_list, kdt = get_route_data()
    # for road in road_list:
    #     draw_seg(road)
    yh = get_yhtl()
    yh_road = build_road(road_list, pt_list, yh)
    # draw_road(yh)
    # draw_png()
    # plt.show()
    return all_road_list, road_list, pt_list, kdt, yh_road


def main():
    road_list, _, _, _, yh = get_all_data()
    delete_all()
    save(road_list)


if __name__ == '__main__':
    main()
