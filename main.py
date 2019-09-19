# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 14:11
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : main.py

from src.dab_scan import DAB_SCAN
from spd_src.gene_map import gene_center_line
from src.fetch_data import load_txt
import matplotlib.pyplot as plt


def main():
    data_list, rev_index, trace_list = load_txt()
    # step 1. clustering by angle
    labels = DAB_SCAN(data_list)
    # step 2. generate center line
    gene_center_line(labels, data_list, rev_index, trace_list, False)
    plt.show()


if __name__ == '__main__':
    main()
