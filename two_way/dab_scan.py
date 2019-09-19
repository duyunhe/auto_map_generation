# -*- coding: utf-8 -*-
# @Time    : 2019/9/4 14:04
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : dab_scan.py

from Queue import Queue
from src.common import near_angle_counter, mean_angle, debug_time, near_angle
from sklearn.neighbors import KDTree


def search_bf(ind, angle_list, label_list, init_pos, count_thread, cur_label, ort_thread):
    """
    :param ind: kdtree下的索引
    :param angle_list:  
    :param label_list: 初始下是-1 访问了但未标记为中心点时为-2
    :param init_pos: 
    :param count_thread: B min cluster point number
    :param cur_label: 当前的index
    :param ort_thread: 角度值相近的阈值
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
        na_list, ave_list = [], []
        for i in ind[ci]:
            if near_angle(angle_list[i], angle_list[ci], ort_thread):
                ave_list.append(angle_list[i])
                na_list.append(angle_list[i])
            elif near_angle_counter(angle_list[i], angle_list[ci], ort_thread):
                na_list.append(angle_list[i])

        ma = mean_angle(ave_list)
        na_list = []
        # use mean angle instead of the point angle itself
        for i in ind[ci]:
            if near_angle_counter(angle_list[i], ma, ort_thread):
                near_list.append(i)
                na_list.append(angle_list[i])
        if len(near_list) >= count_thread:
            if first_angle == -1:
                first_angle = ma
            # if angle has changed compared with first point
            # then stop
            # it should be concluded into another line
            if near_angle_counter(angle_list[ci], first_angle, ort_thread):
                anchor_cnt += 1
                label_list[ci] = cur_label
                for i in near_list:
                    if label_list[i] == -1:
                        label_list[i] = -2
                        que.put(i)
    return anchor_cnt, first_angle


# @debug_time
def build_kdtree(data_list, min_radius):
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
    ind = kdt.query_radius(X=xy_list, r=min_radius)

    return ind, data_list


@debug_time
def DAB_SCAN(data_list, A=40, B=20, C=5):
    """
    in paper, this method is called as SLC (Spatial Linear Clustering)
    :param data_list: list([x, y, angle])
    :param A: min radius 
    :param B: points count thread
    :param C: anchor near angle
    :return: labels to each point in data_list, and each average angle of cluster
    """
    n = len(data_list)
    ind, data_list = build_kdtree(data_list, A)
    _, _, angle_list = zip(*data_list)
    labels = [-1] * n
    li = 0      # label index
    ma_list = []
    for i in range(n):
        if labels[i] == -1:     # unvisited
            cnt, ma = search_bf(ind, angle_list, labels, i, B, li, C)
            if cnt > 0:
                li += 1
                ma_list.append(ma)
    return labels, ma_list
