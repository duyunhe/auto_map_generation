# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 16:15
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : draw.py


import matplotlib.pyplot as plt
from clip import get_route_data, draw_seg
from src.coord import bl2xy
from src.fetch_data import load_txt
import numpy as np


def draw_trace(trace):
    """
    :param trace: list of TaxiData 
    :return: 
    """
    x_list, y_list = [taxi_data.x for taxi_data in trace], [taxi_data.y for taxi_data in trace]
    plt.plot(x_list, y_list, linestyle='-', marker='', alpha=.1, color='k')


def draw_trace_point(trace):
    """
    :param trace: list of [x, y] 
    :return: 
    """
    x_list, y_list = zip(*trace)
    plt.plot(x_list, y_list, linestyle='', marker='+', alpha=.5, color='k')


def draw_line_idx(segment, idx):
    pt0 = segment.point_list[0]
    pt1 = segment.point_list[-1]
    plt.text((pt0.x + pt1.x) / 2, (pt0.y + pt1.y) / 2, str(idx))
    for i, pt in enumerate(segment.point_list):
        str_pt = "{0},{1}".format(i, pt.pid)
        plt.text(pt.x, pt.y, str_pt)


def draw_png():
    image = plt.imread('../img/hz1.png')
    pt0 = 120.2069091796875, 30.263811840754933
    pt1 = 120.2728271484375, 30.20686106595262
    x0, y0 = bl2xy(pt0[1], pt0[0])
    x1, y1 = bl2xy(pt1[1], pt1[0])
    extent = (x0, x1, y1, y0)
    plt.imshow(image, alpha=.8, origin='upper', extent=extent)


def main():
    all_road, map_road, _, _ = get_route_data()
    # _, _, trace_list = load_txt("../data/thirdBridge.txt")
    # print len(trace_list)
    # tunnel_list = extract_tunnel(trace_list)
    # np.savetxt('../data/tunnel.txt', tunnel_list, fmt='%.2f', delimiter=',')

    for road in map_road:
        draw_seg(road)
        # draw_line_idx(road, road.lid)
    # draw_png()
    plt.show()


if __name__ == '__main__':
    main()
