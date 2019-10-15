# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 10:17
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : tdbscan.py


import numpy as np
from geo import xy_radian, hausdorff_par_dist, calc_dist
from src.common import debug_time
from concurrent.futures import ProcessPoolExecutor as Pool
from uf import UnionFind
from topo.draw import draw_png
import matplotlib.pyplot as plt
import math


def proc(a_list, tunnel):
    ret_list = []
    n, m = tunnel.shape[:]
    for i in range(n):
        x0, y0, x1, y1 = tunnel[i][:]
        b_list = [[x0, y0], [x1, y1]]
        d = hausdorff_par_dist(a_list, b_list)
        ret_list.append(d)
    return ret_list


@debug_time
def get_trace():
    tunnel = np.loadtxt('../data/tunnel.txt', delimiter=',')
    n, m = tunnel.shape[:]
    mat = np.zeros([n, n])
    work_list = []

    MAXN = n
    args = []
    for i in range(MAXN):
        x0, y0, x1, y1 = tunnel[i][:]
        a_list = [[x0, y0], [x1, y1]]
        work_list.append(a_list)
        args.append(tunnel)
        a = xy_radian(x0, y0, x1, y1)
        # ret = proc(a_list, tunnel)
        # for j in range(len(ret)):
        #     mat[i][j] = ret[j]

    with Pool(max_workers=4) as pool:
        results = pool.map(proc, work_list, args)
        for i, ret in enumerate(results):
            for j in range(len(ret)):
                mat[i][j] = ret[j]

    np.savetxt("./data/dist.txt", mat, fmt="%.2f")


def trans():
    tunnel = np.loadtxt('../data/tunnel.txt', delimiter=',')
    dist_mat = np.loadtxt('./data/dist.txt')
    n, _ = dist_mat.shape[:]
    tup_list = []
    for i in range(n):
        p0, p1, p2, p3 = tunnel[i][:]
        if calc_dist([p0, p1], [p2, p3]) < 1000:
            continue
        for j in range(i + 1, n):
            p0, p1, p2, p3 = tunnel[j][:]
            if calc_dist([p0, p1], [p2, p3]) < 1000:
                continue
            if dist_mat[j][i] < 50 and dist_mat[i][j] < 50:
                tup_list.append("{0},{1},{2:.2f}\n".format(i, j, dist_mat[i][j]))

    np.savetxt('./data/parse.txt', tup_list, fmt='%s')


def draw_pair(pt_list):
    p0, p1, p2, p3 = pt_list[:]
    x_list = [p0, p2]
    y_list = [p1, p3]
    plt.plot(x_list, y_list, marker='+', ls='')


def near_radian(a0, a1):
    d0 = math.fabs(a0 - a1)
    d1 = 2 * math.pi - d0
    d = min(d0, d1)
    return d < math.pi / 8


def near_endpoint(t0, t1):
    thread = 100
    x0, y0, x1, y1 = t0
    _x0, _y0, _x1, _y1 = t1
    d0, d1 = calc_dist([x0, y0], [_x0, _y0]), calc_dist([x1, y1], [_x1, _y1])
    _d0, _d1 = calc_dist([x0, y0], [_x1, _y1]), calc_dist([x1, y1], [_x0, _y0])
    return d0 < thread and d1 < thread or _d0 < thread and _d1 < thread


def check():
    tunnel = np.loadtxt('../data/tunnel.txt', delimiter=',')
    n, m = tunnel.shape
    us = UnionFind(n)
    parse = np.loadtxt('./data/parse.txt', delimiter=',')
    len_p, _ = parse.shape
    for i in range(len_p):
        p, q, dist = map(int, parse[i])
        x0, y0, x1, y1 = tunnel[p]
        a0 = xy_radian(x0, y0, x1, y1)
        x0, y0, x1, y1 = tunnel[q]
        a1 = xy_radian(x0, y0, x1, y1)
        if near_radian(a0, a1) and near_endpoint(tunnel[p], tunnel[q]):
            us.union(p, q)

    a = us.cluster()
    for key, item in a.items():
        if len(item) > 50:
            print key, len(item)
            for i in item:
                draw_pair(tunnel[i])
            break

    draw_png()
    plt.show()


if __name__ == '__main__':
    check()
