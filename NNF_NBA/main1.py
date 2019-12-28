"""
Release-free 或者 非Release-free且是Until-free的情况
"""

from typing import List, Tuple

from NNF_NBA import utils
from NNF_NBA.ltl_transition_system import LTS, Transfer
from NNF_NBA.ltl_transition_system import out_lts_graph

# 输入的原始LTL公式
# ltl_formula = 'G(((b)U(c))∧((d)U(e)))'
ltl_formula = 'G((a)U(b))'
# ltl_formula = 'F((a)U(F(a)))'
# ltl_formula = 'G((a)U(G(a)))'

# ltl_formula = '(a)U(b)'
#
# 存DNF到状态公式的映射,用于快速判断状态相等
state2dnf = dict()

if __name__ == '__main__':
    # 解析原始LTL公式的标准型
    origin_dnf = utils.parseToDNF(ltl_formula)
    # 构造LTS
    lts: LTS = LTS()
    # 写入初始状态
    lts.s0 = ltl_formula
    # 将初始状态写入状态集合
    lts.s = [lts.s0]
    state2dnf[lts.s0] = origin_dnf
    # 准备转移边列表
    lts.trans = []
    # 遍历初始状态集合,解析标准型并尝试得到向后的转移
    idx = 0  # idx=len(lts.s)时算法终止
    while idx < len(lts.s):
        print('当前状态' + lts.s[idx])
        # 解析当前状态的公式的标准型,集合转为列表
        dnf: List[Tuple[str, str]] = list(utils.parseToDNF(lts.s[idx]))
        # 遍历标准型,生成转移边
        for alpha, phi in dnf:
            now_state = phi  # 当前状态公式的引用,用于保证同一状态不多形式出现
            """
            now_dnf = utils.parseToDNF(phi)  # 当前状态DNF
            # 遍历已计算的DNF,判断当前DNF是不是已经是某个状态的DNF
            is_old = False
            for state in state2dnf:
                if state2dnf[state] == now_dnf:
                    now_state = state
                    is_old = True
                    break
            if not is_old:  # 是新状态,加入状态列表
                lts.s.append(phi)
                state2dnf[phi] = now_dnf
            """
            if phi not in lts.s:
                lts.s.append(phi)
            # 从当前状态经识别alpha可以转移到状态phi
            lts.trans.append(Transfer(lts.s[idx],
                                      list(set(alpha.split('∧'))),  # 去重
                                      now_state))  # DNF一样的状态也只用旧公式
        idx += 1
    print('[状态集合]' + '-' * 40)
    print(lts.s)
    print('[初始状态]' + '-' * 40)
    print(lts.s0)
    print('[转移关系]' + '-' * 40)
    for t in lts.trans:
        print(t)
    out_lts_graph(lts, 'png')
