# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 14:58
# @Author  : yhdu@tongwoo.cn
# @简介    : Spatial Linear Clustering
# @File    : slc.py


from src.common import debug_time
from src.fetch_data import load_txt
from sklearn.neighbors import KDTree
from Queue import Queue
from time import clock
import multiprocessing as mp


def build_kdtree(data_list):
    if len(data_list) == 0:
        return None
    kdt = KDTree(data_list, leaf_size=10)
    return kdt


def search_bf(kdt_buckets, label_list, init_pos, count_thread,
              cur_label, bucket_index, data_list, min_radius):
    """
    :param kdt_buckets: 
    :param label_list: 
    :param init_pos: 
    :param count_thread: 
    :param cur_label: 
    :param bucket_index: 
    :param data_list: list of [x, y]
    :param min_radius 
    :return: 
    """
    que = Queue()
    anchor_cnt = 0
    que.put(init_pos)
    li = bucket_index[init_pos]
    label_list[li] = -2

    while not que.empty():
        cur = que.get()
        bi, bs = cur[:]
        li = bucket_index[cur]
        cur_cnt = 0
        near_list = []
        for bucket in range(bi - 5, bi + 6):
            if bucket >= 360:
                bucket -= 360
            if bucket < 0:
                bucket += 360
            kdt = kdt_buckets[bucket]
            if not kdt:
                continue
            ind = kdt.query_radius(X=[data_list[li]], r=min_radius)
            cur_cnt += len(ind[0])
            for s in ind[0]:
                near_list.append((bucket, s))
        # print cur, cur_cnt
        if cur_cnt >= count_thread:
            anchor_cnt += 1
            label_list[li] = cur_label
            for ni in near_list:
                next_li = bucket_index[ni]
                if label_list[next_li] == -1:
                    label_list[next_li] = -2
                    que.put(ni)

    # print init_pos, anchor_cnt, cur_label
    return anchor_cnt


def work_proc(arg):
    kdt, xy_list, radius, idx, ind_list = arg[:]
    ind = kdt.query_radius(X=xy_list, r=radius)
    ind_list[idx] = ind


@debug_time
def spatial_linear_clustering(data_list, A=40, B=20, C=5):
    """
    as the data size grow up, it can decrease time cost rapidly
    look up src.DAB_SCAN  .^-^.
    :param data_list: list([x, y, angle])
    :param A: min radius 
    :param B: points count thread
    :param C: anchor near angle
    :return: labels to each point in data_list
    """
    data_buckets = []
    for i in range(360):
        data_buckets.append([])
    kdt_buckets = [None] * 360
    index = {}      # buckets(i, j) -> data_list(idx)

    for i, data in enumerate(data_list):
        x, y = data[:2]
        ort = int(data[2])
        if ort == 360:
            ort = 0
        j = len(data_buckets[ort])
        data_buckets[ort].append([x, y])
        index[(ort, j)] = i
    for i in range(360):
        kdt_buckets[i] = build_kdtree(data_buckets[i])

    n = len(data_list)
    x_list, y_list, _ = zip(*data_list)
    xy_list = zip(x_list, y_list)

    labels = [-1] * n

    cur_label = 0
    for i in range(360):
        for j in range(len(data_buckets[i])):
            if labels[index[(i, j)]] == -1:
                if search_bf(kdt_buckets, labels, (i, j), B, cur_label, index, xy_list, A) > 0:
                    cur_label += 1

    return labels


def unit_test():
    data_list, _, _ = load_txt()
    spatial_linear_clustering(data_list)


if __name__ == '__main__':
    unit_test()
