# -*- coding: utf-8 -*-
# @Time    : 2019/9/30 12:59
# @Author  : LauZyHou
# @File    : 与文件相关的操作

import os


def read_list(filename: str) -> list:
    """读入并处理每行数据"""
    with open(filename) as f:
        lines = f.read().split('\n')
    new_lines = []
    is_change = True
    while is_change:
        pass


if __name__ == '__main__':
    read_list('./in_imp.txt')
