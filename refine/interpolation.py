# -*- coding: utf-8 -*-
# @Time    : 2019/9/20 10:26
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : interpolation.py

import numpy as np
from scipy import interpolate
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from smooth_tst import smooth
from src.geo import dog_last
from src.draw import draw_png


def read_txt():
    fp = open('..\data\yh.txt')
    pt_list = []
    last_x = None
    for line in fp.readlines():
        coords = line.strip('\n').split(';')
        for xy in coords:
            x, y = map(float, xy.split(','))
            if last_x is not None and x == last_x:
                continue
            pt_list.append([x, y])
            last_x = x
    fp.close()
    return pt_list


def draw_road(road, color='k', alpha=.5):
    x_list, y_list = zip(*road)
    plt.plot(x_list, y_list, color=color, alpha=alpha)


def filt(road):
    n = len(road)
    window_len = 201
    x, y = map(np.array, zip(*road))
    # ny = smooth(y, window_len, "bartlett")[int(window_len / 2):-(int(window_len / 2))]
    # plt.plot(x, ny, 'r')
    ny = smooth(y, window_len, "hanning")[int(window_len / 2):-(int(window_len / 2))]
    road = zip(x, ny)
    road = dog_last(road, .5)
    x, ny = zip(*road)
    print len(road)
    np.savetxt('../data/np.txt', road, fmt='%.2f,%.2f', delimiter=',')
    plt.plot(x, ny, 'b')


def inter(road):
    x_list, y_list = zip(*road)
    x_new = np.arange(min(x_list), max(x_list), 0.5)
    f = interpolate.interp1d(x_list, y_list, kind='linear')
    y_new = f(x_new)
    ret = zip(x_new, y_new)
    return ret


def main():
    road = read_txt()
    road = inter(road)
    draw_road(road)
    filt(road)
    draw_png()
    plt.show()


def change():
    y0 = np.array([2, 4, 6, 2, 3, 5, 9, 7, 4, 1])
    x = [i for i in range(len(y0))]
    plt.plot(x, y0, 'k')
    y = savgol_filter(y0, 5, 2)
    plt.plot(x, y, 'r')
    plt.show()


if __name__ == '__main__':
    main()
