# -*- coding: utf-8 -*-
# @Time    : 2019/9/29 15:41
# @Author  : yhdu@tongwoo.cn
# @简介    : 直接加一条隧道
# @File    : tn.py


import sqlite3
from topo.map_struct import MapPoint, MapSegment
from topo.draw import draw_png
from map.save_map import save_sqlite


def go():
    conn = sqlite3.connect("../data/hz1.db")
    cur = conn.cursor()
    sql = "select * from tb_seg_point s where s_id = 4468 order by seq desc"
    cur.execute(sql)
    bt = MapPoint(0, 0)
    for item in cur:
        bt.x, bt.y = item[3:]
        break
    sql = "select * from tb_seg_point s where s_id = 5360 order by seq"
    cur.execute(sql)
    et = MapPoint(0, 0)
    for item in cur:
        et.x, et.y = item[3:]
        break
    ms = MapSegment(6705)
    ms.ort = 0
    ms.rank = u'主干路'
    ms.name = u'庆春隧道'
    ms.add_point(bt)
    ms.add_point(et)
    cur.close()
    conn.close()

    save_sqlite([ms])


if __name__ == '__main__':
    go()
