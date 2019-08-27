# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 11:05
# @Author  : yhdu@tongwoo.cn
# @简介    : Density & Angle Based Spatial Clustering of Applications with Noise
# @File    : dab-scan.py

from queue import Queue
from common import near_angle, mean_angle, debug_time
from sklearn.neighbors import KDTree


def search_bf(ind, angle_list, label_list, init_pos, count_thread, label_index):
    """
    :param ind: 
    :param angle_list:  
    :param label_list: 
    :param init_pos: 
    :param count_thread: B min cluster point number
    :param label_index: 当前的index
    :return: 
    """
    que = Queue()
    anchor_cnt = 0
    que.put(init_pos)
    label_list[init_pos] = -2       # mark as visited
    first_angle = -1
    # print init_pos
    while not que.empty():
        ci = que.get()
        # print cur
        near_list = []
        na_list = []
        for i in ind[ci]:
            if near_angle(angle_list[i], angle_list[ci], 15):
                na_list.append(angle_list[i])
        ma = mean_angle(na_list)
        na_list = []
        for i in ind[ci]:
            if near_angle(angle_list[i], ma, 5):
                near_list.append(i)
                na_list.append(angle_list[i])
        if len(near_list) >= count_thread:
            if first_angle == -1:
                first_angle = mean_angle(na_list)

            if near_angle(angle_list[ci], first_angle, 5):
                anchor_cnt += 1
                label_list[ci] = label_index
                for i in near_list:
                    if label_list[i] == -1:
                        label_list[i] = -2
                        que.put(i)
    return anchor_cnt


@debug_time
def build_kdtree(data_list, A):
    x_list, y_list, a_list = zip(*data_list)
    data_list = []
    for i, a in enumerate(a_list):
        try:
            data_list.append((x_list[i], y_list[i], a_list[i]))
        except IndexError:
            print a

    x_list, y_list, a_list = zip(*data_list)
    xy_list = zip(x_list, y_list)
    kdt = KDTree(xy_list, leaf_size=10)
    ind = kdt.query_radius(X=xy_list, r=A)

    return ind, data_list


@debug_time
def DAB_SCAN(data_list, A, B):
    """
    :param data_list: list([x, y, angle])
    :param A: min radius 
    :param B: points count thread
    :return: 
    """
    n = len(data_list)
    ind, data_list = build_kdtree(data_list, A)
    _, _, angle_list = zip(*data_list)
    labels = [-1] * n
    li = 0      # label index
    for i in range(n):
        if labels[i] == -1:     # unvisited
            if search_bf(ind, angle_list, labels, i, B, li) > 0:
                li += 1
    return labels
