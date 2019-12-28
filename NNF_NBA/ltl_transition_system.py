from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from graphviz import Digraph


@dataclass
class Transfer:
    """转移关系"""
    phi1: str
    alpha: List[str]
    phi2: str

    def __str__(self):
        return self.phi1 + '--' + '∧'.join(self.alpha) + '-->' + self.phi2


class LTS:
    """LTL Transition System"""
    sigma: List[List[str]]  # 字母表,即原子命题幂集2^AP
    s: List[str]  # 状态集合
    s0: str  # 初始状态,只有一个(应是初始状态集合{s0})
    trans: List[Transfer]  # 转移关系


def out_lts_graph(lts: LTS, file_type: str) -> None:
    """将LTL Transition System有向图输出
    :param lts: 要输出的LTL Transition System
    :param file_type: 文件类型(扩展名)
    """

    # 生成TS的GraphViz有向图
    dot = Digraph(comment='LTL Transition System')
    for s in lts.s:  # 生成结点(公式phi)
        # 第一参数是其唯一标识,第二参数是外显的文字,这里都用其字符串
        dot.node(s, s, fontname="Microsoft YaHei")
    for t in lts.trans:  # 生成边(alpha)
        _phi1 = t.phi1
        _edge = '∧'.join(t.alpha)
        _phi2 = t.phi2
        dot.edge(_phi1, _phi2, _edge, fontname="Microsoft YaHei")
    dot.render('LTS.gv', view=True, format=file_type)
