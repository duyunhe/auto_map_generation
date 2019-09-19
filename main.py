# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 14:11
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : main.py

from two_way.dab_scan import DAB_SCAN
from two_way.gene_map import gene_center_line
from src.fetch_data import load_txt
import matplotlib.pyplot as plt


def main():
    data_list, rev_index, trace_list = load_txt()
    # step 1. clustering by angle
    labels, ma_list = DAB_SCAN(data_list)
    # step 2. generate center line
    gene_center_line(labels, data_list, rev_index, trace_list, ma_list, False)
    plt.show()


if __name__ == '__main__':
    main()
