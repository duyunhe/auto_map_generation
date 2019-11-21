# -*- coding: utf-8 -*-
# @Time    : 2019/9/30 10:04
# @Author  : yhdu@tongwoo.cn
# @简介    : 显示地图，双向车道
# @File    : outline.py


from topo.readMap import read_sqlite, make_kdtree
import matplotlib.pyplot as plt
from topo.draw import draw_line_idx
from src.draw import draw_png
from save_map import save_map
from save_orcl import save_oracle
from src.geo import get_cross_point, get_vector_angle, calc_point_dist, dog_last, \
    point2segment, point_on_segment, cross_point, pt2segment, pt_project
from geo import get_parallel
import math
from topo.map_struct import MapSegment
from mod_struct import ModPoint, PointLineInfo, LineInfo, ModLine


ort_oneway = 1
ort_dbway = 0


def draw_seg(segment, c='b', linewidth=1):
    x_list, y_list = [], []
    try:
        for pt in segment.point_list:
            x_list.append(pt.x)
            y_list.append(pt.y)
        plt.plot(x_list, y_list, c=c, linewidth=linewidth)
    except AttributeError:
        print segment.lid


def draw_sgmt(p0, p1, i):
    x_list = [p0.x, p1.x]
    y_list = [p0.y, p1.y]
    plt.plot(x_list, y_list, c='orange')
    plt.text((p0.x + p1.x) / 2, (p0.y + p1.y) / 2, str(i))


def oneway_road(road):
    road_list = [u'文二路', u'文三路', u'文晖路', u'潮王路', u'浣纱路', u'延安路', u'余杭塘路']
    return road.name in road_list


def in_gene_list(road):
    if road.ort == ort_oneway and oneway_road(road):
        return True
    if road.ort == ort_oneway or road.rank == u'步行街' or road.rank == u'匝道' or road.rank == u'连杆道路' or \
            road.rank == u'次要支路':
        return False
    return True


def get_route():
    ln_list, pt_list = read_sqlite('../data/hz1.db')
    return ln_list


def gene_topo(road_list):
    express_hash = {}
    express_hash[0] = (5141, 132)
    express_hash[1] = (258, 5044)
    express_hash[2] = (1599, 1565)
    express_hash[3] = (6065, 4381)
    express_hash[4] = (5602, 462)
    express_hash[5] = (4562, 794)
    express_hash[6] = (6582, 1354)
    express_hash[7] = (5280, 424)
    express_hash[8] = (94, 5110)

    exp_index = {}
    exp_index[u"中河高架路"] = 0
    exp_index[u"钱江四桥（复兴大桥）"] = 1
    exp_index[u"时代大道高架"] = 2
    exp_index[u"钱江三桥（西兴大桥）"] = 3
    exp_index[u"德胜高架路"] = 4
    exp_index[u"石祥高架路"] = 5
    exp_index[u"上塘高架路"] = 6
    exp_index[u"石桥高架路"] = 7
    exp_index[u"石大快速路"] = 8

    exp_name = [""] * 9
    for name, value in exp_index.items():
        exp_name[value] = name

    express_set_list = []
    link_list = []
    cnt = 9
    for i in range(cnt):
        temp = set()
        temp_hash = {}
        express_set_list.append(temp)
        link_list.append(temp_hash)

    for line in road_list:
        if line.ort == ort_oneway and line.rank == u'快速路':
            idx = exp_index[line.name]
            express_set_list[idx].add(line.lid)
            pid = line.point_list[0].pid
            # 记录下pid的下一个lid
            link_list[idx][pid] = line.lid

    # 寻路？
    info_list = []
    for i in range(cnt):
        # if i != 4:
        #     continue
        stop = set()
        stop.add(express_hash[i][0])
        stop.add(express_hash[i][1])
        link_map = link_list[i]
        lid = express_hash[i][0]
        temp_list, lid_list0, lid_list1 = [], [], []
        while True:
            lid_list0.append(lid)
            pid = road_list[lid].point_list[-1].pid
            if pid not in link_map:
                break
            lid = link_map[pid]
            if lid in stop:
                break
        temp_list.append(lid_list0)
        lid = express_hash[i][1]
        while True:
            lid_list1.append(lid)
            pid = road_list[lid].point_list[-1].pid
            if pid not in link_map:
                break
            lid = link_map[pid]
            if lid in stop:
                break
        temp_list.append(lid_list1)
        info_list.append([temp_list, exp_name[i]])

    return info_list


def check_near_line(mod_line, line):
    """
    此处可以做的好一点，如计算走向
    用一个距离阙值也可以了
    :param mod_line: 
    :param line: 
    :return: 
    """
    near_cnt = 0
    for pt in line.point_list:
        min_dist = 1e10
        for i, mpt in enumerate(mod_line.point_list[:-1]):
            mpt1 = mod_line.point_list[i + 1]
            dist = point2segment([pt.x, pt.y], [mpt.x, mpt.y], [mpt1.x, mpt1.y])
            min_dist = min(min_dist, dist)
        if min_dist < 20:
            near_cnt += 1
    near_per = float(near_cnt) / len(line.point_list)
    return near_per > 0.5


def find_near_surface(mod_line, ln_list, point_list, kdt):
    xy_list = []
    for pt in mod_line.point_list:
        x, y = pt.x, pt.y
        xy_list.append([x, y])
    t = kdt.query_radius(xy_list, r=1000)
    pid_set = set()
    for pid_list in t:
        for pid in pid_list:
            pid_set.add(pid)

    lid_set = set()
    for pid in pid_set:
        pt = point_list[pid]
        for ld in pt.link_list:
            line = ld[0].line
            if in_gene_list(line):
                lid_set.add(line.lid)

    for lid in lid_set:
        line = ln_list[lid]
        if check_near_line(mod_line, line):
            line.surface = 1


def analysis_surface(mod_lines, ln_list, point_list):
    kdt, _ = make_kdtree(point_list)
    for mod_line in mod_lines:
        find_near_surface(mod_line, ln_list, point_list, kdt)


def get_point_offset_on_segment(x0, y0, x1, y1, offset):
    dx, dy = x1 - x0, y1 - y0
    l = math.sqrt(dx ** 2 + dy ** 2)
    x, y = x0 + offset / l * dx, y0 + offset / l * dy
    dst_pt = ModPoint(x=x, y=y)
    return dst_pt


def insert_points(pts):
    """
    :param pts: list ModPoint 
    :return: 
    """
    ret = []
    off = 10
    for i, pt in enumerate(pts[:-1]):
        p0, p1 = pt, pts[i + 1]
        dist = calc_point_dist(p0, p1)
        ret.append(p0)
        offset = off
        if dist > off:
            while offset < dist:
                mod_pt = get_point_offset_on_segment(p0.x, p0.y, p1.x, p1.y, offset)
                ret.append(mod_pt)
                offset += off
    ret.append(pts[-1])
    return ret


def get_center_points(pts0, pts1):
    ret = []
    i, j = 0, 0
    while i < len(pts0) - 1 and j < len(pts1) - 1:
        x, y = (pts0[i].x + pts1[j].x) / 2, (pts0[i].y + pts1[j].y) / 2
        pt = [x, y]
        ret.append(pt)
        distij = calc_point_dist(pts0[i], pts1[j])
        if distij < 20:
            i, j = i + 1, j + 1
            continue
        ni, nj = i + 1, j + 1
        disti, distj = calc_point_dist(pts0[ni], pts1[j]), calc_point_dist(pts0[i], pts1[nj])
        if disti <= distj:
            i = ni
        else:
            j = nj
    if i == len(pts0) - 1:
        while j < len(pts1):
            x, y = (pts0[i].x + pts1[j].x) / 2, (pts0[i].y + pts1[j].y) / 2
            ret.append([x, y])
            j += 1
    else:
        while i < len(pts0):
            x, y = (pts0[i].x + pts1[j].x) / 2, (pts0[i].y + pts1[j].y) / 2
            ret.append([x, y])
            i += 1
    mod_ret = dog_last(ret, 2)
    ret = []
    for pt in mod_ret:
        mp = ModPoint(x=pt[0], y=pt[1])
        ret.append(mp)
    return ret


def gene_center_express(exp_list, ln_list):
    mp0, mp1 = [], []
    for i, lid in enumerate(exp_list[0]):
        line = ln_list[lid]
        if i == 0:
            for pt in line.point_list:
                mod_pt = ModPoint(pt=pt)
                mp0.append(mod_pt)
        else:
            for pt in line.point_list[1:]:
                mod_pt = ModPoint(pt=pt)
                mp0.append(mod_pt)

    for i, lid in enumerate(exp_list[1]):
        line = ln_list[lid]
        if i == 0:
            for pt in line.point_list:
                mod_pt = ModPoint(pt=pt)
                mp1.append(mod_pt)
        else:
            for pt in line.point_list[1:]:
                mod_pt = ModPoint(pt=pt)
                mp1.append(mod_pt)
    # 同序
    mp1 = mp1[::-1]
    # 插值
    new_mp0, new_mp1 = insert_points(mp0), insert_points(mp1)
    center_list = get_center_points(new_mp0, new_mp1)
    return new_mp0, new_mp1, center_list


def analysis_express(road_list):
    """
    :param road_list: 所有road 
    :return: 
    """
    info_list = gene_topo(road_list)
    mod_list = []
    gene_list = []
    for info, name in info_list:
        new_mp0, new_mp1, center_list = gene_center_express(info, road_list)
        line0 = MapSegment(0)
        line0.point_list = new_mp0
        line1 = MapSegment(0)
        line1.point_list = new_mp1
        center_seg = ModLine()
        center_seg.point_list = center_list
        center_seg.name = name
        mod_list.append(center_seg)
        # info[[idx....], [idx.....]]
        # 两个列表，表示哪些线段是左右两侧的地面道路
        gene_list.extend(gene_express_line(center_seg, info, road_list))
    return mod_list, gene_list


def main():
    line_list, point_list = read_sqlite('../data/hz3.db', build_map=True)
    gene_list = []
    for line in line_list:
        if in_gene_list(line):
            gene_list.append(line)

    mod_lines, gene_express_lines = analysis_express(line_list)
    analysis_surface(mod_lines, line_list, point_list)
    gene_lines = analysis_cross(line_list, gene_list)
    for road in mod_lines:
        draw_seg(road, 'y', linewidth=2)

    for road in gene_list:
        if road.surface:
            draw_seg(road, 'lime')
        else:
            draw_seg(road, 'orange')
    road_map = {}
    map_on_list = []
    for road in gene_express_lines:
        draw_seg(road, 'g')
        lid, fwd, rid = road.org_lid, 1 - road.left, road.lid
        road_map[rid] = (lid, fwd)
        map_on_list.append(road)
    for road in gene_lines:
        draw_seg(road, 'r')
        lid, fwd, rid = road.org_lid, 1 - road.left, road.lid
        map_on_list.append(road)
        if line_list[lid].ort == ort_oneway and fwd == 0:
            continue
        road_map[rid] = (lid, fwd)

        # if org_line.lid == 3819:
        #     draw_seg(road, 'r')
        #     draw_line_idx(road, road.org_lid)
    #     if road.lid == 35:
    #         draw_line_idx(road, road.lid)
    # save_map(road_map)
    save_oracle(map_on_list)
    # draw_png()
    # plt.xlim(75652, 77306)
    # plt.ylim(92174, 92713)
    # plt.show()


def gene_endpoint(pt, line_list, info):
    lid, seq = info[0]
    line = line_list[lid]
    if line.surface:
        road_width = 60
    else:
        road_width = 20
    pt0, pt1 = line.point_list[seq], line.point_list[seq + 1]
    sw = False
    if seq == 0 and pt.pid == pt0.pid:
        begin_pt = True
    else:
        begin_pt = False
    if pt.pid == pt1.pid:
        pt0, pt1 = pt1, pt0
        sw = True

    dp0, dp1, _dp0, _dp1 = get_parallel(pt0, pt1, road_width)

    ep0, ep1 = ModPoint(dp0), ModPoint(_dp0)
    left = False
    if sw:
        left = not left
    if not left:
        fwd = begin_pt
    else:
        fwd = not begin_pt

    pli = PointLineInfo(lid, seq, left, fwd, road_width)
    ep0.pli_list.append(pli)

    left = True
    if sw:
        left = not left
    if not left:
        fwd = begin_pt
    else:
        fwd = not begin_pt
    pli1 = PointLineInfo(lid, seq, left, fwd, road_width)
    ep1.pli_list.append(pli1)
    temp = [ep0, ep1]
    return temp


def gene_cross_point(pt, line_list, info_list, idx):
    buf_list = []
    temp = []
    for info in info_list:
        lid, seq = info
        line = line_list[lid]
        pt0, pt1 = line.point_list[seq], line.point_list[seq + 1]
        if pt.pid == pt1.pid:
            pt0, pt1 = pt1, pt0
            swap = True
        else:
            swap = False
        theta = get_vector_angle(pt0, pt1)
        buf = LineInfo(lid, seq, theta, swap)
        buf_list.append(buf)
    buf_list.sort(key=lambda x: x.theta)

    deg = len(buf_list)
    for i in range(deg):
        lid0, seq0 = buf_list[i].lid, buf_list[i].seq
        j = i + 1
        if j == deg:
            j = 0
        lid1, seq1 = buf_list[j].lid, buf_list[j].seq
        del_theta = math.fabs(buf_list[i].theta - buf_list[j].theta)
        cross_flag = True
        off_flag = False
        if del_theta > math.pi * 2:
            del_theta -= math.pi * 2
        if math.pi - 0.01 < del_theta < math.pi + 0.01:
            off_flag = True
        if del_theta < math.pi / 8:
            print "del theta", del_theta, lid0, seq0, lid1, seq1
            cross_flag = False
        sw0, sw1 = buf_list[i].swap, buf_list[j].swap
        line0, line1 = line_list[lid0], line_list[lid1]
        s0p0, s0p1 = line0.point_list[seq0], line0.point_list[seq0 + 1]
        s1p0, s1p1 = line1.point_list[seq1], line1.point_list[seq1 + 1]
        if sw0:
            s0p0, s0p1 = s0p1, s0p0
        if sw1:
            s1p0, s1p1 = s1p1, s1p0
        surface = line0.surface or line1.surface
        d0, d1 = 20, 20
        if deg == 2 and surface:
            d0, d1 = 60, 60
        elif deg > 2:
            if line0.surface:
                d0 = 60
            if line1.surface:
                d1 = 60
        dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, d0)
        dstp2, dstp3, _dstp2, _dstp3 = get_parallel(s1p0, s1p1, d1)
        if off_flag:
            # 由于计算交点会有精度误差，直接采用两个点的中间点作为新点
            px, py = (_dstp0.x + dstp2.x) / 2, (_dstp0.y + dstp2.y) / 2
            cr_pt = ModPoint(x=px, y=py)
            left = True
            if sw0:
                left = not left
            fwd = not sw0
            lid, seq = lid0, seq0
            cr_pt.pli_list.append(PointLineInfo(lid, seq, left, fwd, d0))
            left = False
            if sw1:
                left = not left
            fwd = not sw1
            lid, seq = lid1, seq1
            cr_pt.pli_list.append(PointLineInfo(lid, seq, left, fwd, d1))
            temp.append(cr_pt)
        elif cross_flag:
            _, px, py = get_cross_point(_dstp0, _dstp1, dstp2, dstp3)
            cr_pt = ModPoint(x=px, y=py)
            left = True
            if sw0:
                left = not left
            fwd = not sw0
            lid, seq = lid0, seq0
            cr_pt.pli_list.append(PointLineInfo(lid, seq, left, fwd, d0))
            left = False
            if sw1:
                left = not left
            fwd = not sw1
            lid, seq = lid1, seq1
            cr_pt.pli_list.append(PointLineInfo(lid, seq, left, fwd, d1))
            temp.append(cr_pt)
        else:
            # left
            cr_pt0 = ModPoint(pt=_dstp0)
            lid, seq = lid0, seq0
            pt0 = line_list[lid].point_list[seq]
            if pt.pid == pt0.pid:
                begin_pt = True
            else:
                begin_pt = False
            left = True
            if sw0:
                left = not left
            if not left:
                fwd = begin_pt
            else:
                fwd = not begin_pt
            cr_pt0.pli_list.append(PointLineInfo(lid, seq, left, fwd, d0))

            # right
            _cr_pt0 = ModPoint(pt=dstp0)
            left = False
            if sw0:
                left = not left
            if not left:
                fwd = begin_pt
            else:
                fwd = not begin_pt
            _cr_pt0.pli_list.append(PointLineInfo(lid, seq, left, fwd, d0))

            # another line
            lid, seq = lid1, seq1
            pt0 = line_list[lid].point_list[seq]
            if pt.pid == pt0.pid:
                begin_pt = True
            else:
                begin_pt = False
            cr_pt1 = ModPoint(pt=_dstp2)
            left = True
            if sw1:
                left = not left
            if not left:
                fwd = begin_pt
            else:
                fwd = not begin_pt
            cr_pt1.pli_list.append(PointLineInfo(lid, seq, left, fwd, d1))

            _cr_pt1 = ModPoint(pt=dstp2)
            left = False
            if sw1:
                left = not left
            if not left:
                fwd = begin_pt
            else:
                fwd = not begin_pt
            _cr_pt1.pli_list.append(PointLineInfo(lid, seq, left, fwd, d1))
            temp = [cr_pt0, _cr_pt0, cr_pt1, _cr_pt1]

    return temp


def modify_line(line, ln_list):
    """
    变窄的地方画的漂亮一点
    :param line: 
    :param ln_list:
    :return: 
    """
    last_dist = 0
    for i, dist in enumerate(line.dist_list):
        if last_dist and (dist == 60 and last_dist == 20 or dist == 20 and last_dist == 60):
            # print "mod", line.org_lid
            org_line = ln_list[line.org_lid]
            if last_dist == 20 and dist == 60:
                if line.left == 0:      # right
                    # print "add right"
                    pt = point_on_segment(org_line.point_list[i], org_line.point_list[i - 1], 20)
                    _, _, p0, p1 = get_parallel(org_line.point_list[i], pt, 20)
                    # add point p1
                    mp = ModPoint(pt=p1)
                    line.point_list.insert(i, mp)
                else:
                    # print "add left", i
                    seq = len(org_line.point_list) - 1 - i
                    pt = point_on_segment(org_line.point_list[seq], org_line.point_list[seq + 1], 20)
                    _, _, p0, p1 = get_parallel(org_line.point_list[seq], pt, 20)
                    mp = ModPoint(pt=p1)
                    line.point_list.insert(i, mp)
            else:
                if line.left == 0:
                    # print "add right", i
                    pt = point_on_segment(org_line.point_list[i - 1], org_line.point_list[i], 20)
                    p0, p1, _, _ = get_parallel(org_line.point_list[i - 1], pt, 20)
                    mp = ModPoint(pt=p1)
                    line.point_list.insert(i, mp)
                else:
                    # print "add left", i
                    seq = len(org_line.point_list) - 1 - i
                    pt = point_on_segment(org_line.point_list[seq + 1], org_line.point_list[seq], 20)
                    p0, p1, _, _ = get_parallel(org_line.point_list[seq + 1], pt, 20)
                    mp = ModPoint(pt=p1)
                    line.point_list.insert(i, mp)
        last_dist = dist


def build_map(gene_list, mod_points):
    """
    :param gene_list: list [Line] 
    :param mod_points: 
    :return: list of ModLine 
    """
    line_index = {}     # lid -> gene_lid0, gene_lid1
    lid_index = {}      # lid -> index in gene_lines
    gene_lines = []
    # take position
    for line in gene_list:
        ml = ModLine()
        # 右手侧，与原道路数据同向
        ml.left, ml.org_lid, ml.lid = 0, line.lid, line.lid * 2
        ml.point_list = [None] * len(line.point_list)
        ml.dist_list = [0] * len(line.point_list)
        lid_index[ml.lid] = len(gene_lines)
        gene_lines.append(ml)
        lid0 = ml.lid

        ml = ModLine()
        ml.left, ml.org_lid, ml.lid = 1, line.lid, line.lid * 2 + 1
        ml.point_list = [None] * len(line.point_list)
        ml.dist_list = [0] * len(line.point_list)
        lid_index[ml.lid] = len(gene_lines)
        gene_lines.append(ml)
        lid1 = ml.lid

        line_index[line.lid] = (lid0, lid1)

    for mp in mod_points:
        if len(mp.pli_list) == 2:
            lid0, seq0, left0, fwd0 = mp.pli_list[0].lid, mp.pli_list[0].seq, mp.pli_list[0].left, mp.pli_list[0].fwd
            lid1, seq1, left1, fwd1 = mp.pli_list[1].lid, mp.pli_list[1].seq, mp.pli_list[1].left, mp.pli_list[1].fwd
            dist0, dist1 = mp.pli_list[0].dist, mp.pli_list[1].dist
            if lid0 == lid1:        # 同一道路
                max_seq = max(seq0, seq1)
                if left0 == 0:
                    lid = line_index[lid0][0]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[max_seq] = mp
                    ml.dist_list[max_seq] = dist0
                else:
                    lid = line_index[lid0][1]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[-max_seq - 1] = mp
                    ml.dist_list[-max_seq - 1] = dist0
            else:           # 不同道路
                if left0 == 0:
                    seq = seq0
                    if not fwd0:
                        seq += 1
                    lid = line_index[lid0][0]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[seq] = mp
                    ml.dist_list[seq] = dist0
                else:
                    seq = seq0
                    if not fwd0:
                        seq += 1
                    lid = line_index[lid0][1]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[-seq - 1] = mp
                    ml.dist_list[-seq - 1] = dist0
                if left1 == 0:
                    seq = seq1
                    if not fwd1:
                        seq += 1
                    lid = line_index[lid1][0]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[seq] = mp
                    ml.dist_list[seq] = dist1
                else:
                    seq = seq1
                    if not fwd1:
                        seq += 1
                    lid = line_index[lid1][1]
                    ml = gene_lines[lid_index[lid]]
                    ml.point_list[-seq - 1] = mp
                    ml.dist_list[-seq - 1] = dist1
        else:
            lid0, seq0, left0, fwd0 = mp.pli_list[0].lid, mp.pli_list[0].seq, mp.pli_list[0].left, mp.pli_list[0].fwd
            dist0 = mp.pli_list[0].dist
            if left0 == 0:
                lid = line_index[lid0][0]
                ml = gene_lines[lid_index[lid]]
                if fwd0:
                    ml.point_list[0] = mp
                    ml.dist_list[0] = dist0
                else:
                    ml.point_list[-1] = mp
                    ml.dist_list[-1] = dist0
            else:
                lid = line_index[lid0][1]
                ml = gene_lines[lid_index[lid]]
                if fwd0:
                    ml.point_list[0] = mp
                    ml.dist_list[0] = dist0
                else:
                    ml.point_list[-1] = mp
                    ml.dist_list[-1] = dist0
    return gene_lines


def gene_points(pt, gene_set, line_list, idx=None):
    """
    :param pt: Point 
    :param gene_set: lid in gene lines, for not all line in gene lines 
    :param line_list: 
    :param idx:
    :return: list [ModPoint]
    """
    deg = 0
    # print pt.pid, idx
    info_list = []
    for link, mp in pt.link_list:
        lid, seq = link.line.lid, link.seq
        if lid in gene_set:
            deg += 1
            info_list.append([lid, seq])
    # end point
    if deg == 1:
        return gene_endpoint(pt, line_list, info_list)
    else:
        return gene_cross_point(pt, line_list, info_list, idx)


def check_info_orient(center_line, info, line_list):
    idx_list = info[0]
    left_cnt, right_cnt = 0, 0
    for idx in idx_list:
        line = line_list[idx]
        for pt in line.point_list:
            min_dist, pa, pb = 1e10, None, None
            for i, p0 in enumerate(center_line.point_list[:-1]):
                p1 = center_line.point_list[i + 1]
                dist = pt2segment(pt, p0, p1)
                if dist < min_dist:
                    min_dist, pa, pb = dist, p0, p1
            cross = cross_point(pa, pb, pt)
            if cross > 0:
                right_cnt += 1
            else:
                left_cnt += 1
    # print left_cnt, right_cnt
    # 计算得先右后左


def cutting(line, mod_line):
    gene_line = ModLine()
    gene_line.point_list = []
    gene_line.org_lid = line.lid
    gene_line.lid = line.lid * 2
    gene_line.left = 0      # 单向路都为同向
    for pt in line.point_list:
        min_dist, pa, pb = 1e10, None, None
        for i, p0 in enumerate(mod_line.point_list[:-1]):
            p1 = mod_line.point_list[i + 1]
            dist = pt2segment(pt, p0, p1)
            if dist < min_dist:
                min_dist, pa, pb = dist, p0, p1
        x, y = pt_project(pt, pa, pb)
        pj = ModPoint(x=x, y=y)
        gene_line.point_list.append(pj)
    return gene_line


def gene_express_line(center_line, info, line_list):
    """
    :param center_line: 中间线 
    :param info: 见调用函数处
    :param line_list: 所有道路 
    :return: 
    """
    gene_line0 = ModLine()
    # 右手侧
    gene_line0.point_list = []
    n = len(center_line.point_list)
    for i, pt in enumerate(center_line.point_list):
        if i == 0:
            s0p0, s0p1 = center_line.point_list[i], center_line.point_list[i + 1]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            mp = ModPoint(pt=dstp0)
            gene_line0.point_list.append(mp)
        elif i == n - 1:
            s0p0, s0p1 = center_line.point_list[i - 1], center_line.point_list[i]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            mp = ModPoint(pt=dstp1)
            gene_line0.point_list.append(mp)
        else:
            s0p0, s0p1, s0p2 = center_line.point_list[i - 1:i + 2]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            dstp2, dstp3, _dstp2, _dstp3 = get_parallel(s0p1, s0p2, 20)
            mp = ModPoint(x=(dstp0.x + dstp2.x) / 2, y=(dstp0.y + dstp2.y) / 2)
            gene_line0.point_list.append(mp)

    gene_line1 = ModLine()
    gene_line1.point_list = []
    pt_list = center_line.point_list[::-1]
    for i, pt in enumerate(pt_list):
        if i == 0:
            s0p0, s0p1 = pt_list[i], pt_list[i + 1]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            mp = ModPoint(pt=dstp0)
            gene_line1.point_list.append(mp)
        elif i == n - 1:
            s0p0, s0p1 = pt_list[i - 1], pt_list[i]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            mp = ModPoint(pt=dstp1)
            gene_line1.point_list.append(mp)
        else:
            s0p0, s0p1, s0p2 = pt_list[i - 1:i + 2]
            dstp0, dstp1, _dstp0, _dstp1 = get_parallel(s0p0, s0p1, 20)
            dstp2, dstp3, _dstp2, _dstp3 = get_parallel(s0p1, s0p2, 20)
            mp = ModPoint(x=(dstp0.x + dstp2.x) / 2, y=(dstp0.y + dstp2.y) / 2)
            gene_line1.point_list.append(mp)

    check_info_orient(center_line, info, line_list)
    gene_list = []
    for idx in info[0]:
        line = line_list[idx]
        gene_list.append(cutting(line, gene_line0))
    for idx in info[1]:
        line = line_list[idx]
        gene_list.append(cutting(line, gene_line1))
    return gene_list


def analysis_cross(line_list, gene_list):
    gene_set = set()
    for road in gene_list:
        gene_set.add(road.lid)

    mod_points = []
    vis = set()
    for j, line in enumerate(gene_list):
        for i, pt in enumerate(line.point_list):
            if pt.pid not in vis:
                mod_points.extend(gene_points(pt, gene_set, line_list, i))
                vis.add(pt.pid)

    gene_lines = build_map(gene_list, mod_points)
    for line in gene_lines:
        modify_line(line, line_list)
    return gene_lines


if __name__ == '__main__':
    main()
