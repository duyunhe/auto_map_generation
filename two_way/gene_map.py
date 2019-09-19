# -*- coding: utf-8 -*-
# @Time    : 2019/9/4 14:46
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : gene_map.py

from collections import defaultdict
from src.common import mean_route_angle, rotate, mean_y_filter, median_y_filter, \
    mean_delta, mean_angle, near_angle, debug_time
import numpy as np
from src.draw import draw_center, draw_points, draw_line
import multiprocessing as mp


class Line(object):
    def __init__(self, line):
        """
        :param line: list of Point 
        """
        x_list, y_list = zip(*line)
        self.first_x = min(x_list)
        self.last_x = max(x_list)
        self.line = line

    def __lt__(self, other):
        return self.first_x < other.first_x


def save_road(road_list):
    fp = open('./data/road.txt', 'w')
    for road in road_list:
        sp_list = ["{0},{1}".format(pt[0], pt[1]) for pt in road]
        str_road = ';'.join(sp_list)
        fp.write(str_road + '\n')
    fp.close()


def collect_line_around(pt_list, trace_list, rev, rot):
    """
    important to road segment generation
    trace_list[ti][tj] is pt
    collect all the points from beginning to end as trace goes on if the point is anchor
    because the vehicle may turn around and trace back, the trace should be split when turning happened
    :param pt_list: list of anchor point
    :param trace_list: original trace list, list of TaxiData
    :param rev: each index
    :param rot: rotate angle
    :return: list of line(list of Point)
    """
    # begin, end = {}, {}
    trace_detail = {}
    for i, pt in enumerate(pt_list):
        ti, tj = rev[i][:]
        try:
            trace_detail[ti].append(tj)
        except KeyError:
            trace_detail[ti] = [tj]
    for ti in trace_detail.keys():
        trace_detail[ti].sort()

    line_list = []
    fact_ort = 90 - rot
    for i, idx_list in trace_detail.items():
        iset = set(idx_list)
        for j in idx_list:
            if j + 1 < len(trace_list[i]):
                iset.add(j)
        fill_list = list(iset)
        fill_list.sort()

        line = []
        last_j = None
        for j in fill_list:
            pt = trace_list[i][j]
            if last_j is not None and j - last_j > 3:
                if len(line) > 1:
                    line_list.append(rotate(line, rot))
                line = [[pt.x, pt.y]]
            else:
                line.append([pt.x, pt.y])
            last_j = j

        if len(line) > 1:
            line_list.append(rotate(line, rot))

    return line_list


def work(tup_list, rd_list):
    for item in tup_list:
        pt_list, line_list, a, lb = item[:]
        road = center_road(pt_list, line_list)
        # print "label", lb
        try:
            road = rotate(road, -a)
            rd_list.append(road)
        except ValueError:
            print "value error", lb


@debug_time
def gene_center_line(labels, data_list, rev_index, trace_list, ma_list, debug=False):
    n = len(labels)
    x_list, y_list, angle_list = zip(*data_list)
    pts_dict = defaultdict(list)
    angle_dict = defaultdict(list)
    rev_dict = defaultdict(list)

    for i in range(n):
        pts_dict[labels[i]].append([x_list[i], y_list[i]])
        angle_dict[labels[i]].append(angle_list[i])
        rev_dict[labels[i]].append(rev_index[i])

    colors = ['pink', 'orange', 'y',
              'blue', 'c', 'g', 'lime', 'red']

    tup_list = []
    for label, pt_list in pts_dict.items():
        rev = rev_dict[label]
        if label == -2:
            # draw_points(pt_list, '+', 'k', 0.1, -3)
            pass
        else:
            if debug and label != 20:
                continue
            a = ma_list[label]
            try:
                idx = int(a / 45)
            except ValueError:
                continue
            if len(pt_list) > 100:
                a = 90 - a
                line_list = collect_line_around(pt_list, trace_list, rev, a)
                pt_list = rotate(pt_list, a)
                tup_list.append([pt_list, line_list, a, label])

    mng = mp.Manager()
    ret_list = mng.list()
    proc_num = 32
    pool = mp.Pool(processes=proc_num)
    for i in range(proc_num):
        pool.apply_async(work, args=(tup_list[i::proc_num], ret_list))
    pool.close()
    pool.join()

    for road in ret_list:
        draw_center(road)

    save_road(ret_list)


def center_road(pt_list, line_list, debug=False):

    def calc_y(pt0, pt1, x0):
        ax = pt1[0] - pt0[0]
        dx = x0 - pt0[0]
        if ax == 0 or dx == 0:
            return pt0[1]
        ay = pt1[1] - pt0[1]
        return dx / ax * ay + pt0[1]

    x_list = [pt[0] for pt in pt_list]
    ln_list = [Line(line) for line in line_list if len(line) > 1]
    if debug:
        for line in line_list:
            if len(line) > 1:
                draw_line(line)
    x_list.sort()

    # begin scan
    # from left to right
    gene_list = []
    cnt_list = []
    # not all points will affect the center point
    # avoid error on curve
    AFFECT_DIST = 30
    # need MIN_SEG segments to get the mean value, in order to avoid sample insufficiency
    MIN_SEG = 5
    # BRUTE FORCE... not good enough
    for x in x_list:
        y_list = []
        for ln in ln_list:
            if ln.first_x <= x <= ln.last_x:
                for i in range(len(ln.line) - 1):
                    if ln.line[i][0] <= x <= ln.line[i + 1][0]:
                        if x <= ln.line[i][0] + AFFECT_DIST or x >= ln.line[i + 1][0] - AFFECT_DIST:
                            y = calc_y(ln.line[i], ln.line[i + 1], x)
                            y_list.append(y)
                            break
                    if ln.line[i + 1][0] <= x <= ln.line[i][0]:
                        if x <= ln.line[i + 1][0] + AFFECT_DIST or x >= ln.line[i][0] - AFFECT_DIST:
                            y = calc_y(ln.line[i], ln.line[i + 1], x)
                            y_list.append(y)
                            break
        if len(y_list) >= MIN_SEG:
            # print len(y_list)
            mean_y = np.mean(y_list)
            gene_list.append([x, mean_y])
            cnt_list.append(len(y_list))
    if len(gene_list) > 0:
        ref_list = mean_y_filter(gene_list)
    else:
        ref_list = None
    ref_list.sort()

    return ref_list
