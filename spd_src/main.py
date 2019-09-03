# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 16:57
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : main.py


from src.dab_scan import DAB_SCAN
from spd_src.mul_gene_map import gene_center_line
from src.fetch_data import load_txt
import matplotlib.pyplot as plt


def main():
    data_list, rev_index, trace_list = load_txt()
    # step 1. clustering by angle
    labels = DAB_SCAN(data_list)
    # step 2. generate center line
    gene_center_line(labels, data_list, rev_index, trace_list)
    # plt.show()


if __name__ == '__main__':
    main()
