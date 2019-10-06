# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 16:53
# @Author  : LauZyHou
# @File    : 主文件

import json
from typing import List, Dict, Set
from deprecated import deprecated


class Stat:
    """生成的Transition System的状态类"""
    loc: str = None  # 来自PG的Loc
    eval_var: Dict[str, int] = None  # 所有Var的取值Eval(Var)，这里用字典表示
    is_alive: bool = True  # 指示该状态是否是活动的（已全部计算完后继的状态设置为False）

    def __init__(self, loc_: str, eval_var_: Dict):
        """构造器：直接传入location名称和变量字典"""
        self.loc = loc_
        self.eval_var = eval_var_

    def __str__(self):
        """转为字符串表示：如<start,nsoda=1∧nbeer=1>"""
        return "<" + self.loc + "," + "∧".join([k + "=" + str(v) for k, v in self.eval_var.items()]) + ">"

    @deprecated(version='1.0', reason='写入JSON时直接写入字符串')
    def to_list(self) -> List:
        """转为list表示"""
        return [self.loc, self.eval_var]

    def __eq__(self, other):
        """判断两Stat相等：Location相同且所有变量值相同"""
        if self.loc != other.loc:
            return False
        for k in var_list:
            if self.eval_var[k] != other.eval_var[k]:
                return False
        return True


class Transfer:
    """生成的Transition System的转移类"""

    def __init__(self, s1_: Stat, act: str, s2_: Stat):
        """构造器：对外屏蔽内部只记录Stat在S中下标这一实现"""
        pass  # todo


class Label:
    """生成的Transition System中，对应于每个Stat，标签映射后的结果"""
    pass  # todo


if __name__ == '__main__':
    # 从JSON文件中读取Program Graph
    with open('./in_pg.json', encoding='utf8') as f:
        ok = json.load(f)
    Loc: List[str] = ok['Loc']  # 存所有Location
    Act: List[str] = ok['Act']  # 存所有Action
    Effect: Dict[str, List[str]] = ok['Effect']  # 存每个Action对变量的影响（无影响的Action不被记录）
    Hooks: List[List[str]] = ok['Hooks']  # 存PG的所有转移（符号上是个弯钩箭头所以叫Hooks）
    Loc_0: List[str] = ok['Loc_0']  # 初始Location
    g_0: Dict[str, int] = ok['g_0']  # 初始条件，可指示变量的初值
    # 从g_0中读取变量名称
    var_list = list(g_0.keys())
    print('读取变量名称: ', var_list)
    # 定义转换后的Transaction System的内容，它们最终会写入JSON文件
    S: List[Stat] = []  # 存所有状态
    Act_: Set[str] = set()  # 存所有动作（PG中未必所有Act都用到，所以用set去重）
    Trans: List[Transfer] = []  # 存所有转移关系
    AP: Set[str] = set()  # 原子命题集合（也是用set去重）
    L: List[Label] = []  # 存S中每个状态通过标签函数映射的结果
