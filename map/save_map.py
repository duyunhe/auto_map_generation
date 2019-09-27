# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 11:07
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : save_map.py


import sqlite3


def delete_all():
    cx = sqlite3.connect("../data/hz1.db")
    cu = cx.cursor()
    cx.execute("delete from tb_seg_point")
    cx.execute("delete from tb_segment")
    cx.commit()
    cu.close()
    cx.close()


def save_sqlite(line_list):
    """
    :param line_list: Road 中name rank 都为unicode 
    :return: 
    """
    cx = sqlite3.connect("../data/hz1.db")
    cu = cx.cursor()
    tup_list = []
    for i, road in enumerate(line_list):
        uname = road.name
        tup_list.append([i, uname, road.ort, road.rank])

    sql = "insert into tb_segment(s_id, S_NAME, direction, rank) values (?,?,?,?)"
    cx.executemany(sql, tup_list)

    sql = "insert into tb_seg_point values(?,?,?,?,?)"
    tup_list = []
    pid = 0
    for i, road in enumerate(line_list):
        for j, mp in enumerate(road.point_list):
            tup = (pid, i, j, mp.x, mp.y)
            pid += 1
            tup_list.append(tup)
    cx.executemany(sql, tup_list)

    cx.commit()
    cu.close()
    cx.close()


def main():
    delete_all()
    save_sqlite()


if __name__ == '__main__':
    main()
