# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 11:07
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : save_map.py


import sqlite3


def delete_all(filename="../data/hz3.db"):
    cx = sqlite3.connect(filename)
    cu = cx.cursor()
    cx.execute("delete from tb_seg_point")
    cx.execute("delete from tb_segment")
    cx.commit()
    cu.close()
    cx.close()


def save_map(tb_map, filename="../data/hz3.db"):
    cx = sqlite3.connect(filename)
    cu = cx.cursor()
    sql = "delete from tb_map"
    cu.execute(sql)
    cx.commit()
    tup_list = []
    sql = "insert into tb_map (lid, fwd, rid) values(?,?,?)"
    for rid, value in tb_map.items():
        lid, fwd = value
        tup_list.append((lid, fwd, rid))
    cu.executemany(sql, tup_list)
    cx.commit()
    cu.close()
    cx.close()


def save_sqlite(line_list, filename="../data/hz3.db"):
    """
    :param line_list: Road 中name rank 都为unicode
    :param filename: 
    :return: 
    """
    cx = sqlite3.connect(filename)
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
