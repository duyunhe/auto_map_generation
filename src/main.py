# -*- coding: utf-8 -*-
# @Time    : 2019/8/27 14:11
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : main.py

from dab_scan import DAB_SCAN
from gene_map import draw_pt
from fetch_data import load_txt
import matplotlib.pyplot as plt


def main():
    # plt.xlim(72576, 76484)
    # plt.ylim(84367, 86846)
    data_list, rev_index, trace_list = load_txt()
    labels = DAB_SCAN(data_list, 30, 10)
    draw_pt(labels, data_list, rev_index)
    plt.show()


if __name__ == '__main__':
    main()
