# -*- coding: utf-8 -*-
# @Time    : 2019/10/21 10:30
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : save_orcl.py

import cx_Oracle
import sqlite3
from src.coord import xy2bl, gcj02_to_wgs84
from src.common import debug_time


@debug_time
def save_oracle(road_list):
    """
    :param road_list: list[ModLine] 
    :return: 
    """
    # conn = cx_Oracle.connect('hz/hz@192.168.11.88/orcl')
    conn = cx_Oracle.connect('hzczdsj/tw85450077@192.168.0.80/orcl')
    cursor = conn.cursor()
    sql = "delete from tb_road_point_on_map where map_level = 1"
    cursor.execute(sql)
    conn.commit()
    sql = "insert into tb_road_point_on_map values(:1,:2,:3,:4,1)"
    tup_list = []
    for road in road_list:
        rid = road.lid
        valid = True
        for pt in road.point_list:
            if pt is None:
                valid = False
        if not valid:
            continue
        for i, pt in enumerate(road.point_list):
            x, y = pt.x, pt.y
            lat, lng = xy2bl(x, y)
            wlng, wlat = gcj02_to_wgs84(lng, lat)
            tup = (rid, i, wlng, wlat)
            tup_list.append(tup)
    cursor.executemany(sql, tup_list)
    conn.commit()
    cursor.close()
    conn.close()


@debug_time
def main():
    conn = cx_Oracle.connect('hzczdsj/tw85450077@192.168.0.80/orcl')
    cursor = conn.cursor()
    sql = "select * from tb_road_point_on_map where map_level = 1"
    cursor.execute(sql)
    cnt = 0
    for item in cursor:
        cnt += 1
    print cnt
    cursor.close()
    conn.close()


def save_road_map(filename="../data/hz3.db"):
    cx = sqlite3.connect(filename)
    cu = cx.cursor()
    sql = "select lid, fwd, rid from tb_map"
    cu.execute(sql)
    tup_list = []
    for item in cu:
        tup_list.append(item)
    cu.close()
    cx.close()
    conn = cx_Oracle.connect('hz/hz@192.168.11.88/orcl')
    cur = conn.cursor()
    sql = "insert into tb_map values(:1, :2, :3)"
    cur.executemany(sql, tup_list)
    conn.commit()
    cur.close()
    conn.close()


def save_segment(filename="../data/hz3.db"):
    cx = sqlite3.connect(filename)
    cu = cx.cursor()
    sql = "select s_id, s_name, direction, rank from tb_segment"
    cu.execute(sql)
    tup_list = []
    for item in cu:
        tup_list.append(item)
    cu.close()
    cx.close()
    conn = cx_Oracle.connect('hz/hz@192.168.11.88/orcl')
    cur = conn.cursor()
    sql = "insert into tb_segment(s_id, s_name, direction, rank) values(:1, :2, :3, :4)"
    cur.executemany(sql, tup_list)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    save_segment()
