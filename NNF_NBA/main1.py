import re
from typing import List, Tuple, Set, Dict

from NNF_NBA import utils
from NNF_NBA.ltl_transition_system import LTS, Transfer
from NNF_NBA.nondeterministic_buchi_automaton import NBA, Delta
from NNF_NBA.nondeterministic_buchi_automaton import out_nba_graph

# 输入的原始LTL公式
# ltl_formula = 'F((a)U(F(a)))'
# ltl_formula = '(a)U(b)'
# ltl_formula = '(b)R(G(a))'

# ltl_formula = '((b)U(c))∧((d)U(e))'
# ltl_formula = '((b)R(c))∧((d)R(e))'
# ltl_formula = 'X((a)∨(b))'
# ltl_formula = '(a)R(X((b)∨(c)))'
# ltl_formula = '((┐a)∨(b))∧((c)R(d))'
# ltl_formula = '((a)∧((c)R(d)))∨((b)∧((c)R(d)))'
# ltl_formula = '(a)R(b)R(c)'


# 状态公式到DNF的映射,用于快速判断状态相等
state2dnf: Dict[str, Set[Tuple[str, str]]] = dict()

if __name__ == '__main__':
    # nnf_formula = 'aRbRc'
    nnf_formula = input('请输入LTL公式:')
    ltl_formula = utils.addBrackets(nnf_formula)
    # 解析原始LTL公式的标准型
    origin_dnf: Set[Tuple[str, str]] = utils.parseToDNF(ltl_formula)
    # 构造LTS
    lts: LTS = LTS()
    # 状态公式到清除原子命题外括号的映射,用于快速清除原子命题外的括号
    lts.state2nonbraker = dict()
    # 生成字母表
    ap_set: Set[str] = utils.parseAP(ltl_formula)
    lts.sigma = utils.powSet(ap_set)
    # 写入初始状态
    lts.s0 = ltl_formula
    # 将初始状态写入状态集合
    lts.s = [lts.s0]
    state2dnf[lts.s0] = origin_dnf
    lts.state2nonbraker[lts.s0] = utils.cleanBracketsOnAP(lts.s0)
    # 准备转移边列表
    lts.trans = []
    # 遍历初始状态集合,解析标准型并尝试得到向后的转移
    idx = 0  # idx=len(lts.s)时算法终止
    while idx < len(lts.s):
        # print('当前状态' + lts.s[idx])
        # 解析当前状态的公式的标准型,集合转为列表
        dnf: List[Tuple[str, str]] = list(utils.parseToDNF(lts.s[idx]))
        # 遍历DNF中的标准型,生成转移边
        for alpha, phi in dnf:
            now_state = phi  # 当前状态公式的引用,用于保证同一状态不多形式出现
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
                lts.state2nonbraker[phi] = utils.cleanBracketsOnAP(phi)
            # 去重
            alpha_set = set(a.strip('()') for a in alpha.split('∧')) - {''}
            # 从当前状态经识别alpha可以转移到状态phi
            lts.trans.append(Transfer(lts.s[idx],
                                      list(alpha_set),
                                      now_state))  # DNF一样的状态也只用旧公式
        idx += 1
    # 集合{c}减去集合{a,b,c}为空,则将{a,b,c}去掉
    # 保留转移边上最松弛的条件
    _trans = lts.trans[::-1]
    for t in lts.trans[::-1]:
        for r in _trans:
            if r == t:  # 跳过自己
                continue
            # 转移的起始状态相同,终止状态相同,转移存在语义上的偏序关系时
            elif (t.phi1 == r.phi1 and t.phi2 == r.phi2) \
                    and (set(r.alpha) - set(t.alpha) == set() or set(r.alpha) == {'True'}):
                lts.trans.remove(t)
                break  # 找到了能将t移除的r,就不必再找了
    # 用LTS构造NBA
    nba: NBA = NBA(lts)
    # 添加转移关系
    nba.delta = [
        Delta(
            lts.state2nonbraker[t.phi1],
            t.alpha,
            lts.state2nonbraker[t.phi2],
        )
        for t in lts.trans
    ]
    # 接下来用论文4.2中的特判方式设置可接受状态集
    # 判断是Release-free
    if re.search(r'[RG]', ltl_formula) is None:
        # 查找为True的状态
        for s in nba.s:
            if s.formula == 'True':
                nba.f.append(s)
    # 在不是Release-free的条件下,判断是Until-free
    elif re.search(r'[UF]', ltl_formula) is None:
        nba.f = nba.s
    print('-' * 50)
    print('[字母表]' + '-' * 40)
    print(nba.sigma)
    print('[状态集合]' + '-' * 40)
    print(nba.s)
    print('[初始状态]' + '-' * 40)
    print(nba.s0)
    print('[转移关系]' + '-' * 40)
    for d in nba.delta:
        print(d)
    print('[终止状态]' + '-' * 40)
    print(nba.f)
    print('[输出图像]见新打开的窗口')
    out_nba_graph(nba, 'png')
