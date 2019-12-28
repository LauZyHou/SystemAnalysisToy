import re
from typing import Set, List, Tuple
from itertools import combinations


def parseAP(formula: str) -> Set[str]:
    """从LTL公式解析出原子命题集合"""
    ap_list = re.split('[()XGFUR∧∨]', formula)
    ret = set(ap_list)
    ret -= {'', 'True', 'False'}
    return ret


def powSet(s: Set[str]) -> List[List[str]]:
    """求集合的幂集"""
    return [list(c) for i in range(len(s) + 1) for c in combinations(s, i)]


def parseToDNF(formula: str) -> List[Tuple[str, str]]:
    """LTL公式解析成标准型[(alpha,phi),...]每项表示alpha∧X(phi)"""
    # fixme
    if formula == 'aUb':
        return [('b', 'True'), ('a', 'aUb')]
    elif formula == 'True':
        return [('True', 'True')]
    return []
