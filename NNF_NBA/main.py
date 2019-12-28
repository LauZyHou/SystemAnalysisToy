import re
from typing import Set, List, Dict, Tuple
from itertools import combinations

from NNF_NBA.disjunction_normal_form import DNF
from NNF_NBA.nondeterministic_buchi_automaton import NBA, State

# 输入的原始LTL公式
ltl_formula = 'aUb'
# 转换成的标准型的析取范式(每个项是标准型,即normal form)
dnf_str = '(b∧X(True))∨(a∧X(aUb))'


def parseAP(formula: str) -> Set[str]:
    """从LTL公式解析出原子命题集合"""
    ap_list = re.split('[()XGFUR∧∨]', formula)
    ret = set(ap_list)
    ret -= {'', 'True', 'False'}
    return ret


def powSet(s: Set[str]) -> List[List[str]]:
    """求集合的幂集"""
    return [list(c) for i in range(len(s) + 1) for c in combinations(s, i)]


def parseNormalForm(formula: str) -> List[Tuple[str, str]]:
    """计算LTL公式的标准型"""
    # 特判,如果是题目中的原始LTL公式,其标准型以及解析过了就是dnf.form
    if formula == ltl_formula:
        return dnf.form
    return None


if __name__ == '__main__':
    # 将DNF字符串解析
    dnf: DNF = DNF(dnf_str)
    # 创建要写入的NBA对象
    nba: NBA = NBA()
    # 写入原子命题集合
    ap_set: Set[str] = parseAP(ltl_formula)
    nba.sigma = powSet(ap_set)
    # 写入初始状态，即<原始LTL公式,空集>
    nba.s0 = State(ltl_formula, set())
    # 将初始状态也写入状态集合
    nba.s = [nba.s0]
    # 接下来要生成NBA的转移关系
    nba.delta = []
    # 从i=0开始，不断加入状态以及从状态搜索转移边
    i = 0
    # phi_1经alpha转移到phi_2，当且仅当在phi_1的标准型中有alpha∧X(phi_2)
    # 当i=len(nba.s)时所有状态所有转移都找完，算法终止
    while i < len(nba.s):  # 当前考察的状态是nba.s[i]
        # 取出该状态的公式
        formula = nba.s[i].formula
        # 计算其标准型的列表
        normal_form_list = parseNormalForm(formula)
        # 遍历原始LTL公式的每个标准型项<alpha,X(phi)>中的alpha和phi
        # 只有这里的状态phi是可能的状态
        for alpha, phi in dnf.form:
            pass

