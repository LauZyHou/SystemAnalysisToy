# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 16:53
# @Author  : LauZyHou
# @File    : 主文件

import json
from typing import List, Dict

if __name__ == '__main__':
    # 从JSON文件中读取Program Graph
    with open('./in_pg.json', encoding='utf8') as f:
        ok = json.load(f)
    Loc: List[str] = ok['Loc']
    Act: List[str] = ok['Act']
    Effect: Dict[str, List[str]] = ok['Effect']
    Hooks: List[List[str]] = ok['Hooks']
    Loc_0: List[str] = ok['Loc_0']
    g_0: Dict[str, int] = ok['g_0']
    # 从g_0中读取变量名称
    var_list = list(g_0.keys())
    print(var_list)
