# -*- coding: utf-8 -*-
# @Time    : 2019/9/24 17:16
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : match.py


from src.fetch_data import load_txt
from src.draw import draw_png
from src.common import debug_time
from clip import get_all_data, draw_seg
from map.save_map import delete_all, save_sqlite
from map_struct import MapPoint
import matplotlib.pyplot as plt
import math
from geo import point2segment, calc_included_angle, inter_seg, get_cross_point_v0
from collections import defaultdict


MAX_OFFSET = 100


def draw_trace(trace):
    x_list, y_list = [], []
    for data in trace:
        x_list.append(data.x)
        y_list.append(data.y)
    plt.plot(x_list, y_list, linestyle='', marker='+')


def check_line_projection(line_dist, gps_point, line_desc, last_point=None):
    line, seq = line_desc.line, line_desc.seq
    lid = line.lid
    p0, p1 = line.point_list[seq:seq + 2]

    if last_point is not None:
        a0, a1 = [p0.x, p0.y], [p1.x, p1.y]
        d0, d1 = [gps_point.x, gps_point.y], [last_point.x, last_point.y]
        ia = math.fabs(calc_included_angle(a0, a1, d0, d1))
        # print lid, ia
        if ia < 0.5:
            return
    dist = point2segment(gps_point, p0, p1)
    if dist > MAX_OFFSET:
        return
    try:
        if dist < line_dist[lid][1]:
            line_dist[lid] = [seq, dist]
    except KeyError:
        line_dist[lid] = [seq, dist]


def check_newline(line_dist, gps_point, newline, last_point=None):
    n = len(newline.point_list)
    lid = newline.lid
    for i in range(n - 1):
        p0, p1 = newline.point_list[i:i + 2]
        if last_point is not None:
            a0, a1 = [p0.x, p0.y], [p1.x, p1.y]
            d0, d1 = [gps_point.x, gps_point.y], [last_point.x, last_point.y]
            ia = math.fabs(calc_included_angle(a0, a1, d0, d1))
            # print lid, ia
            if ia < 0.5:
                continue
        dist = point2segment(gps_point, p0, p1)
        if dist > MAX_OFFSET:
            continue
        try:
            if dist < line_dist[lid][1]:
                line_dist[lid] = [i, dist]
        except KeyError:
            line_dist[lid] = [i, dist]


def match_road(point_list, kdt, trace, newline):
    xy_list = []
    n = len(trace)
    for data in trace:
        xy_list.append([data.x, data.y])
    idx, dst = kdt.query_radius(xy_list, r=250, return_distance=True)

    trace_match = {}
    for t in range(n):
        line_dist = {}
        if t != 0:
            last_point = trace[t - 1]
        else:
            last_point = None
        for i in idx[t]:
            pt = point_list[i]
            for ld, mp in pt.link_list:
                check_line_projection(line_dist, trace[t], ld, last_point)
            for ld, mp in pt.rlink_list:
                check_line_projection(line_dist, trace[t], ld, last_point)
        check_newline(line_dist, trace[t], newline, last_point)
        min_dist, sel_lid, sel_seq = 1e10, -2, 0
        for lid, match_item in line_dist.iteritems():
            seq, dist = match_item[:]
            if dist < min_dist:
                min_dist, sel_lid, sel_seq = dist, lid, seq
        trace_match[t] = [sel_lid, sel_seq, min_dist]
    path = []
    last_t = -2
    cur_list = []
    for i, item in trace_match.items():
        t = item[0]
        if last_t != t:
            if last_t != -2 and len(cur_list) >= 2:
                path.append(last_t)
            elif last_t == -2 and len(cur_list) > 0:
                path.append(last_t)
            cur_list = [t]
        else:
            cur_list.append(t)
        last_t = t
    if last_t != -2 and len(cur_list) >= 2:
        path.append(last_t)
    elif last_t == -2 and len(cur_list) > 0:
        path.append(last_t)

    return path


def proc_intersect(road, new_road):
    sel_i, sel_j, sel_px, sel_py = None, None, None, None
    for i in range(len(road.point_list)):
        if i == 0:
            continue
        p0, p1 = road.point_list[i - 1], road.point_list[i]
        for j in range(len(new_road.point_list)):
            if j == 0:
                continue
            p2, p3 = new_road.point_list[j - 1], new_road.point_list[j]
            if inter_seg(p0, p1, p2, p3):
                _, px, py = get_cross_point_v0(p0, p1, p2, p3)
                print p0, p1, p2, p3, px, py
                sel_i, sel_j, sel_px, sel_py = i, j, px, py

    if sel_i is not None:
        mp = MapPoint(sel_px, sel_py)
        road.point_list.insert(sel_i, mp)
        new_road.point_list.insert(sel_j, mp)


@debug_time
def main():
    _, _, trace_list = load_txt()
    all_road_list, road_list, pt_list, kdt, yhtl = get_all_data()      # yhtl 余杭塘路
    yhtl.name = u'余杭塘路'
    yhtl.ort = 0
    yhtl.rank = u'主干路'

    draw_seg(yhtl, 'b')
    print len(trace_list)

    turn_round = defaultdict(int)
    trace_cnt = defaultdict(int)
    for trace in trace_list[:400]:
        # draw_trace(trace_list[i])
        path = match_road(pt_list, kdt, trace, yhtl)
        for i, idx in enumerate(path):
            if idx == -1:
                if i > 0:
                    turn_round[path[i - 1]] += 1
                if i < len(path) - 1:
                    turn_round[path[i + 1]] += 1
            if idx >= 0:
                trace_cnt[idx] += 1
    print trace_cnt
    print turn_round
    mod_list = []
    for road in road_list:
        if road.lid in turn_round.keys():
            p = 1.0 * turn_round[road.lid] / trace_cnt[road.lid]
            if p > 0.25:
                w = math.pow(math.e, p)
                print road.lid, p
                lw = math.log(turn_round[road.lid]) + 1
                mod_list.append(road)
                draw_seg(road, 'r', lw)
            else:
                draw_seg(road, 'k')
        else:
            draw_seg(road, 'k')

    for road in mod_list:
        print "lid", road.lid
        print len(road.point_list), len(yhtl.point_list)
        proc_intersect(road, yhtl)
        print len(road.point_list), len(yhtl.point_list)

    all_road_list.append(yhtl)
    delete_all()
    save_sqlite(all_road_list)

    draw_png()
    plt.show()


if __name__ == '__main__':
    main()
