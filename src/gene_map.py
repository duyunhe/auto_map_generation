# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 11:08
# @Author  : yhdu@tongwoo.cn
# @简介    : 写的是什么玩意
# @File    : gene_map.py


from collections import defaultdict
from common import xy_angle, mean_route_angle, rotate, mean_y_filter, mean_delta
import numpy as np
from draw import draw_center, draw_points


def refine_road(pt_list, cnt_list):
    bi, ei = 0, len(cnt_list) - 1
    for i, cnt in enumerate(cnt_list):
        if cnt > 20:
            bi = i
            break
    for i, cnt in enumerate(cnt_list):
        if cnt > 20:
            ei = i
    # print bi, ei
    ref_list = []
    d0 = mean_delta(pt_list[bi:bi + 50])
    d1 = mean_delta(pt_list[ei - 50:ei])
    for i, pt in enumerate(pt_list):
        if i < bi:
            x = pt_list[i][0]
            y = d0 * (x - pt_list[bi][0]) + pt_list[bi][1]
            ref_list.append([x, y])
        elif i > ei:
            x = pt_list[i][0]
            y = d1 * (x - pt_list[ei][0]) + pt_list[ei][1]
            ref_list.append([x, y])
        else:
            ref_list.append(pt)
    return ref_list


def draw_pt(labels, data_list, rev_index):
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
    for label, pt_list in pts_dict.items():
        rev = rev_dict[label]
        if label == -2:
            # draw_points(pt_list, '+', 'k', 0.1, -3)
            pass
        else:
            angle_list = angle_dict[label]
            # a = mean_angle(angle_list)
            a = mean_route_angle(pt_list, rev)
            try:
                idx = int(a / 45)
            except ValueError:
                continue
            # print a
            if len(pt_list) > 50:
                a = 90 - a
                pt_list = rotate(pt_list, a)
                org_list = rotate(pt_list, -a)
                # ma = mean_route_angle(pt_list, rev)
                # pt_list = rotate(pt_list, -a)
                draw_points(org_list, 'o', colors[idx], .2, label)
                try:
                    road = gene_road(pt_list, rev)
                    road = rotate(road, -a)
                    draw_center(road)
                except ValueError:
                    print label, "ValueError"


def gene_road(pt_list, rev_index):
    line_dict = defaultdict(list)
    for i, rev in enumerate(rev_index):
        ti, tj = rev[:]
        line_dict[ti].append(pt_list[i])
    # for lid, line in line_dict.items():
    #     if len(line) > 1:
    #         draw_line(line)
    road = center_road(pt_list, line_dict)
    return road


def center_road(pt_list, line_dict):
    class Line(object):
        def __init__(self, l):
            x_list, y_list = zip(*l)
            self.first_x = min(x_list)
            self.last_x = max(x_list)
            self.line = l

        def __lt__(self, other):
            return self.first_x < other.first_x

    def calc_y(pt0, pt1, x0):
        ax = pt1[0] - pt0[0]
        dx = x0 - pt0[0]
        if ax == 0 or dx == 0:
            return pt0[1]
        ay = pt1[1] - pt0[1]
        return dx / ax * ay + pt0[1]

    x_list = []
    ln_list = []
    # single_list = []
    for lid, line in line_dict.items():
        for pt in line:
            x_list.append(pt[0])
        # if len(line) == 1:
        #     single_list.append(line[0])
        if len(line) > 1:
            ln = Line(line)
            ln_list.append(ln)
    x_list.sort()
    ln_list.sort()

    # begin scan
    # from left to right
    gene_list = []
    cnt_list = []
    for x in x_list:
        y_list = []
        # for pt in single_list:
        #     if pt[0] == x:
        #         y_list.append(pt[1])
        for ln in ln_list:
            if ln.first_x <= x <= ln.last_x:
                for i in range(len(ln.line) - 1):
                    if ln.line[i][0] <= x <= ln.line[i + 1][0]:
                        y = calc_y(ln.line[i], ln.line[i + 1], x)
                        y_list.append(y)
                        break
                    if ln.line[i + 1][0] <= x <= ln.line[i][0]:
                        y = calc_y(ln.line[i], ln.line[i + 1], x)
                        y_list.append(y)
                        break
        if len(y_list) != 0:
            # print len(y_list)
            mean_y = np.mean(y_list)
            gene_list.append([x, mean_y])
            cnt_list.append(len(y_list))
    if len(gene_list) > 0:
        gene_list = mean_y_filter(gene_list)
        ref_list = refine_road(gene_list, cnt_list)
        gene_list = mean_y_filter(ref_list)
    return gene_list
