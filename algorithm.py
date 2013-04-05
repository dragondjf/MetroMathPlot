#!/usr/bin/python
# -*- coding: utf-8 -*-

Names = [
    'min',
    'max',
    'davg',
    'alarmflag',
    'alarmrate',
    'time'  # for front-end wave display
] + ['f%d' % n for n in range(0, 8)] + ['data%d' % n for n in range(0, 10)]


def creat_data(keys, dsize=4096):
    d = {}
    for i in keys:
        d[i] = [0] * dsize
    return d
