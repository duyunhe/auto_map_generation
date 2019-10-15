# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 18:31
# @Author  : yhdu@tongwoo.cn
# @简介    : 
# @File    : uf.py


class UnionFind(object):
    def __init__(self, n):
        self.n = n
        self.parent = [-1] * n
        self.size = [1] * n
        for i in range(n):
            self.parent[i] = i

    def union(self, p, q):
        fp, fq = self.find_set(p), self.find_set(q)
        if fp == fq:
            return
        sp, sq = self.size[fp], self.size[fq]
        if sp < sq:
            self.parent[fp] = fq
        else:
            self.parent[fq] = fp
        self.size[fq] = sp + sq

    def find_set(self, p):
        fp = self.parent[p]
        if p != fp:
            fp = self.find_set(fp)
            self.parent[p] = fp
        return fp

    def cluster(self):
        set_list = {}
        for i in range(self.n):
            fi = self.find_set(i)
            if fi != i:
                try:
                    set_list[fi].append(i)
                except KeyError:
                    set_list[fi] = [i]
        return set_list

