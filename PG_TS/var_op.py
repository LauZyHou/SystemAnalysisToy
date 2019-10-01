# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 22:05
# @Author  : LauZyHou
# @File    : Variable Operation

from typing import List, Dict


def get_variable_names(effect: Dict[str, List[str]]) -> List[str]:
    """从Effect中获取所有变量的名称构成的列表"""
    ret = set()
    for v in effect.values():
        for sequence in v:
            ret.add(sequence.split(':=')[0])
    return list(ret)


if __name__ == '__main__':
    ans = get_variable_names(
        {'bget': ['nbeer:=nbeer-1'], 'sget': ['nsoda:=nsoda-1'], 'refill': ['nbeer:=1', 'nsoda:=1']}
    )
    print(ans)
