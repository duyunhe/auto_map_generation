# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 11:35
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : mod_struct.py


from topo.map_struct import Point


class PointLineInfo:
    def __init__(self, lid, seq, left, fwd, dist):
        self.lid, self.seq, self.left, self.fwd = lid, seq, left, fwd
        self.dist = dist


class LineInfo:
    def __init__(self, lid, seq, theta, swap):
        self.lid, self.seq, self.theta, self.swap = lid, seq, theta, swap


class ModPoint(Point):
    def __init__(self, pt=None, x=None, y=None):
        """
        :param pt: Point 
        """
        if pt is not None:
            super(ModPoint, self).__init__(pt.x, pt.y)
        else:
            super(ModPoint, self).__init__(x, y)
        self.pli_list = []


class ModLine:
    def __init__(self):
        self.point_list = None
        self.org_lid, self.lid, self.left = None, None, None
        self.dist_list = None
        self.name = ""
