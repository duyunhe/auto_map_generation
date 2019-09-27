# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 18:59
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : trace_file.py


def extract_tunnel(trace_list):
    last_data = None
    data_pair_list = []
    for trace in trace_list:
        for data in trace:
            if last_data:
                itv = data - last_data
                if itv > 180:
                    data_pair_list.append([last_data.x, last_data.y, data.x, data.y])
            last_data = data
    print "match ", len(data_pair_list)
    return data_pair_list

