# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 15:35
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : gene_map.py


from collections import defaultdict
from src.common import mean_route_angle, rotate, mean_y_filter, median_y_filter, \
    mean_delta, mean_angle, near_angle, debug_time
import numpy as np
from src.draw import draw_center, draw_points, draw_line
import multiprocessing as mp
import math


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
        if self.first_x == other.first_x:
            return self.last_x < self.last_x
        else:
            return self.first_x < other.first_x


def collect_line_around(pt_list, trace_list, rev, rot):
    """
    MOST important to road segment generation
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
                iset.add(j + 1)
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


def save_road(road_list):
    fp = open('./data/road.txt', 'w')
    for road in road_list:
        sp_list = ["{0},{1}".format(pt[0], pt[1]) for pt in road]
        str_road = ';'.join(sp_list)
        fp.write(str_road + '\n')
    fp.close()


def center_road(pt_list, line_list, debug=False):

    def calc_y(pt0, pt1, x0):
        ax = pt1[0] - pt0[0]
        dx = x0 - pt0[0]
        if ax == 0 or dx == 0:
            return pt0[1]
        ay = pt1[1] - pt0[1]
        return dx / ax * ay + pt0[1]

    x_list, y_list = zip(*pt_list)
    min_ptx, max_ptx = min(x_list), max(x_list)
    # get max range for scan

    ln_list = [Line(line) for i, line in enumerate(line_list)]
    if debug:
        for line in line_list:
            draw_line(line)
    ln_list.sort()

    # begin scan
    # from left to right
    gene_list = []      # list [x, y]
    cnt_list = []
    # not all points will affect the center point
    # avoid error on curve
    AFFECT_DIST = 30
    # need MIN_SEG segments to get the mean value, in order to avoid sample insufficiency
    MIN_SEG = 5
    cur_idx = 0
    n_road = len(ln_list)
    pos = [0] * n_road
    scan_list = [cur_idx]
    cur_idx = 1
    rm_cnt = 0
    # scanline
    while len(scan_list) != 0:
        # find minx to update y
        minx, sel_idx = 1e10, -1
        for idx in scan_list:
            p = pos[idx]            # idx
            r = ln_list[idx].line   # road
            x = r[p][0]             # x
            if x < minx:
                minx, sel_idx = x, idx
        # check if new segment should be added
        if cur_idx < n_road:
            new_x = ln_list[cur_idx].first_x
            if new_x < minx:
                scan_list.append(cur_idx)
                sel_idx = cur_idx
                cur_idx += 1
                minx = new_x
        if minx > max_ptx:
            break
        s, c, cnt = 0.0, 0, 0
        for idx in scan_list:
            p = pos[idx]
            r = ln_list[idx].line
            y = r[p][1]
            per = min(minx - ln_list[idx].first_x, ln_list[idx].last_x - minx) / \
                     (ln_list[idx].last_x - ln_list[idx].first_x)
            w = math.pow(10, per + 0.1) - 1
            if sel_idx == idx:
                ny = y
                s, c, cnt = s + ny * w, c + w, cnt + 1
            elif r[p][0] - minx < AFFECT_DIST or minx - r[p - 1][0] < AFFECT_DIST:
                ny = calc_y(r[p - 1], r[p], minx)
                s, c, cnt = s + ny * w, c + w, cnt + 1
        if cnt >= MIN_SEG:
            gene_list.append([minx, s / c])
        pos[sel_idx] += 1
        # check if any segment will be removed
        l = len(ln_list[sel_idx].line)
        if pos[sel_idx] == l:
            scan_list.remove(sel_idx)
            rm_cnt += 1

    # print n_road, rm_cnt
    if len(gene_list) > 0:
        ref_list = mean_y_filter(gene_list)
    else:
        ref_list = None
    return ref_list


def work(tup_list, rd_list):
    for item in tup_list:
        pt_list, line_list, a, lb = item[:]
        print "label", lb
        try:
            road = center_road(pt_list, line_list)
            road = rotate(road, -a)
            rd_list.append(road)
        except ValueError:
            print lb, "ValueError"
        except TypeError:
            print lb, "TypeError"


@debug_time
def gene_center_line(labels, data_list, rev_index, trace_list, debug=False):
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
            angle_list = angle_dict[label]
            a = mean_angle(angle_list)
            try:
                # print a
                idx = int(a / 45)
            except ValueError:
                continue
            # print a
            if len(pt_list) > 50:
                a = 90 - a
                line_list = collect_line_around(pt_list, trace_list, rev, a)
                pt_list = rotate(pt_list, a)
                tup_list.append([pt_list, line_list, a, label])

    mng = mp.Manager()
    ret_list = mng.list()
    proc_num = 4
    pool = mp.Pool(processes=proc_num)
    for i in range(proc_num):
        pool.apply_async(work, args=(tup_list[i::proc_num], ret_list))
    pool.close()
    pool.join()

    for road in ret_list:
        draw_center(road, 'k')

    save_road(ret_list)
