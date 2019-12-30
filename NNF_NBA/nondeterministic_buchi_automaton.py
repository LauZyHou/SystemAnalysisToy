from typing import List, Set
from dataclasses import dataclass
from graphviz import Digraph
import re

from NNF_NBA.ltl_transition_system import LTS, Transfer
from NNF_NBA import utils


@dataclass
class State:
    """非确定性Büchi自动机的状态"""
    formula: str  # 公式部分
    pset: Set[str]  # 集合部分,仅当需要通用的构造方式时,使用此字段

    def __init__(self, _f: str, _ps: Set[str] = None):
        """构造时至少应提供公式部分"""
        self.formula = _f
        self.pset = _ps

    def __eq__(self, other):
        """判断状态相等"""
        return self.formula == other.formula and self.pset == other.pset

    def __str__(self):
        return self.formula


@dataclass
class Delta:
    """非确定性Büchi自动机的转移类"""
    s1: State  # 转移前的状态
    formula: str  # 转移上的公式
    s2: State  # 转移后的状态

    # def __init__(self, _trans: Transfer):
    #     """用LTS的转移关系构造NBA的转移关系"""
    #     self.s1 = State(_trans.phi1)
    #     ret = ''
    #     for t in _trans.alpha:
    #         t = utils.cleanOuterBrackets(t)
    #         if re.search(r'[)(]', t) is None:
    #             ret += t + '∧'
    #         else:
    #             clean_list = list(utils.cleanInnerBrackets(t))
    #             sorted(clean_list)
    #             ret += '(' + '∨'.join(clean_list) + ')∧'
    #     self.formula = ret[:-1]
    #     self.s2 = State(_trans.phi2)

    def __init__(self, _p1: str, _alpha: List[str], _p2: str):
        """用传入phi1,alpha,phi2的方式构造NBA的转移关系"""
        self.s1 = State(_p1)
        ret = ''
        for t in _alpha:
            t = utils.cleanOuterBrackets(t)
            if re.search(r'[)(]', t) is None:
                ret += t + '∧'
            else:
                clean_list = list(utils.cleanInnerBrackets(t))
                sorted(clean_list)
                ret += '(' + '∨'.join(clean_list) + ')∧'
        self.formula = ret[:-1]
        self.s2 = State(_p2)

    def __str__(self):
        return str(self.s1) + '--' + self.formula + '-->' + str(self.s2)


class NBA:
    """非确定性Büchi自动机"""
    sigma: List[List[str]]  # 字母表，原子命题集合的幂集
    s: List[State]  # 状态集合
    s0: State  # 初始状态集合
    delta: List[Delta]  # 转移集合
    f: List[State]  # 可接受状态集合

    def __init__(self, _lts: LTS):
        """用LTS构造NBA"""
        self.sigma = _lts.sigma
        self.s = [State(_lts.state2nonbraker[s]) for s in _lts.s]
        self.s0 = State(_lts.state2nonbraker[_lts.s0])
        # [bugfix]此处改成手动传入
        # self.delta = [Delta(t) for t in _lts.trans]
        self.f = []


def out_nba_graph(nba: NBA, file_type: str) -> None:
    """将Nondeterministic Buchi Automaton有向图输出
    :param nba: 要输出的NBA
    :param file_type: 文件类型(扩展名)
    """
    # 生成NBA的GraphViz有向图
    dot = Digraph(comment='Nondeterministic Buchi Automaton')
    # 绘制状态
    for s in nba.s:
        _formula = s.formula
        # 初始状态
        if s == nba.s0:
            dot.node(_formula, _formula, fontname="Microsoft YaHei",
                     style="filled", color="#ff99cc", fontcolor="#000000",
                     shape='doubleoctagon' if s in nba.f else 'ellipse')
        # 可接受状态
        elif s in nba.f:
            dot.node(_formula, _formula, fontname="Microsoft YaHei",
                     style="filled", color="#7EC0EE", fontcolor="#000000",
                     shape='doubleoctagon')
        # 普通状态
        else:
            dot.node(_formula, _formula, fontname="Microsoft YaHei",
                     style="filled", color="#7EC0EE",
                     fontcolor="#000000")
    # 生成边(alpha)
    for d in nba.delta:
        dot.edge(d.s1.formula, d.s2.formula, d.formula,
                 fontname="Microsoft YaHei")
    dot.render('NBA.gv', view=True, format=file_type)
