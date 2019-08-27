# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 11:02
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : fetch_data.py

from common import TaxiData, data_dist, debug_time, data_angle
from collections import defaultdict
from datetime import datetime


def split_trace(xy_dict):
    trace_list = []
    for veh, gps_list in xy_dict.items():
        last_data = None
        trace = []
        for data in gps_list:
            if last_data:
                dist = data_dist(data, last_data)
                # too near to ignore
                if dist < 10:
                    continue
                itv = data - last_data
                # too faraway to split
                if itv >= 120:
                    if len(trace) > 1:
                        trace_list.append(trace)
                    trace = [data]
                else:
                    trace.append(data)
            last_data = data
        if len(trace) > 1:
            trace_list.append(trace)
    return trace_list


def calc_trace_info(trace_list, merge_list):
    """
    将trace列表转换为xy坐标值列表，附带计算方向角
    为了计算倒排索引，以用于后面聚类后的轨迹计算
    :param trace_list: list(list(TaxiData))
    :param merge_list: 原始为空的 list([x, y, angle]) 待转换
    :return: reverse index
    """
    rev_index = {}
    ind = 0
    for j, trace in enumerate(trace_list):
        for i, data in enumerate(trace):
            if i == len(trace) - 1:
                ort = data.angle
            else:
                ort = data_angle(data, trace[i + 1])
            data.ort = ort
            # if 75.0 < ort < 105:
            merge_list.append([data.x, data.y, ort])
            rev_index[ind] = (j, i)
            ind += 1
    return rev_index


def load_txt():
    """
    :return: all_list list[x, y, angle]  reverse index
    """
    xy_dict = defaultdict(list)
    fp = open("../data/yhtl.txt")
    idx = 0
    for line in fp.readlines():
        items = line.strip('\n').split(',')
        veh, x, y, angle, st = items[:]
        x, y = float(x), float(y)
        st = datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
        angle = float(angle)
        data = TaxiData(veh, x, y, angle, st)
        xy_dict[veh].append(data)
        idx += 1
        if idx >= 50000:        # for debug & test
            break
    fp.close()
    all_list = []
    trace_list = split_trace(xy_dict)
    rev_index = calc_trace_info(trace_list, all_list)
    return all_list, rev_index, trace_list
