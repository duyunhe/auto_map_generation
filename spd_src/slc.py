# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 14:58
# @Author  : yhdu@tongwoo.cn
# @简介    : Spatial Linear Clustering
# @File    : slc.py


from src.common import debug_time
from src.fetch_data import load_txt
from sklearn.neighbors import KDTree
from Queue import Queue
import multiprocessing as mp


def build_kdtree(data_list):
    kdt = KDTree(data_list, leaf_size=10)
    return kdt


def search_bf(kdt_buckets, label_list, init_pos, count_thread, cur_label, ort_thread, bucket_index, data_list):
    """
    :param kdt_buckets: 
    :param label_list: 
    :param init_pos: 
    :param count_thread: 
    :param cur_label: 
    :param ort_thread: 
    :param bucket_index: 
    :param data_list: list of [x, y]
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
        bi = bucket_index[cur]
        cur_cnt = 0
        for bucket in range(bi - 5, bi + 6):
            kdt = kdt_buckets[bucket]
            # ind = kdt.query_radius(X=[[data_list[bi].x, data_list[bi].y]], r=A)


def work_proc(arg):
    kdt, xy_list, radius, idx, ind_list = arg[:]
    ind = kdt.query_radius(X=xy_list, r=radius)
    ind_list[idx] = ind


def call_back(x):
    _, _, _, i, _ = x[:]
    print "finish", i


@debug_time
def spatial_linear_clustering(data_list, A=40, B=20, C=5):
    """
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

    print mp.cpu_count()
    p = mp.Pool(processes=8)
    m = mp.Manager()
    ind_list = m.list()
    for i in range(20):
        ind_list.append(None)
    args = [(kdt_buckets[i], xy_list, A, i, ind_list) for i in range(20)]

    for a in args:
        p.apply_async(work_proc, args=(a, ), callback=call_back(a))
        # ind = kdt_buckets[i].query_radius(X=xy_list, r=A)
    p.close()
    p.join()
    labels = [-1] * n


def unit_test():
    data_list, _, _ = load_txt()
    spatial_linear_clustering(data_list)


if __name__ == '__main__':
    unit_test()
