from typing import List, Set
from dataclasses import dataclass


@dataclass
class State:
    """Buchi自动机的状态"""
    formula: str  # 公式部分
    pset: Set[str]  # 集合部分


@dataclass
class Delta:
    """Buchi自动机的转移类"""
    s1: State  # 转移前的状态
    formula: str  # 转移上的公式
    s2: State  # 转移后的状态


class NBA:
    """非确定性Buchizi自动机"""
    sigma: List[List[str]]  # 字母表，原子命题集合的幂集
    s: List[State]  # 状态集合
    s0: State  # 初始状态(实际上应是初始状态集合{s0})
    delta: List[Delta]  # 转移集合
    f: List[State]  # 可接受状态集合
