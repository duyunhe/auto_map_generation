# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 10:17
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : tdbscan.py


import numpy as np
from geo import xy_radian, hausdorff_par_dist
from src.common import debug_time


@debug_time
def get_trace():
    tunnel = np.loadtxt('../data/tunnel.txt', delimiter=',')
    n, m = tunnel.shape[:]
    mat = np.zeros([n, n])
    MAXN = 200
    for i in range(MAXN):
        x0, y0, x1, y1 = tunnel[i][:]
        a_list = [[x0, y0], [x1, y1]]
        a = xy_radian(x0, y0, x1, y1)
        for j in range(MAXN):
            _x0, _y0, _x1, _y1 = tunnel[j][:]
            b_list = [[_x0, _y0], [_x1, _y1]]
            d = hausdorff_par_dist(a_list, b_list)
            mat[i][j] = d
    pass


if __name__ == '__main__':
    get_trace()
