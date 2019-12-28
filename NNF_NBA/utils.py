import re
from typing import Set, List, Tuple
from itertools import combinations
from deprecated import deprecated


def parseAP(formula: str) -> Set[str]:
    """从LTL公式解析出原子命题集合"""
    ap_list = re.split('[()XGFUR∧∨]', formula)
    ret = set(ap_list)
    ret -= {'', 'True', 'False'}
    return ret


def powSet(s: Set[str]) -> List[List[str]]:
    """求集合的幂集"""
    return [list(c) for i in range(len(s) + 1) for c in combinations(s, i)]


def _isOneOrder(formula: str) -> bool:
    """判断公式是否是不含LTL符号的一阶逻辑公式"""
    return re.search('[XGFUR]', formula) is None


def _parseRootSymbol(formula: str) -> int:
    """解析LTL公式的根(UR∧∨)，返回根所在下标"""
    # if len(formula) < 2:
    #     return -1
    # elif formula[0] != '(':
    #     print('[error]必须以左括号开头')
    #     return -1
    cnt = 0  # 计算左括号比右括号多的数量
    i = 0
    for i in range(len(formula)):  # 先找到开头的左括号
        if formula[i] == '(':
            cnt = 1
            break
    for i in range(i + 1, len(formula)):  # 从下一位置开始,向后找到左右闭合处
        if formula[i] == '(':
            cnt += 1
        elif formula[i] == ')':
            cnt -= 1
        if cnt == 0:
            break
    return i + 1


def _cleanOuterBrackets(formula: str) -> str:
    """去除最外层的垃圾括号,如((..(a∧b)R(c)..))变成(a∧b)R(c)"""
    if len(formula) == 0 or formula[0] != '(':
        return formula
    # 去除完成的标志是,左右括号数目匹配完成时不在公式结尾
    left_num = 1
    i = 1
    for i in range(1, len(formula)):
        if formula[i] == '(':
            left_num += 1
        elif formula[i] == ')':
            left_num -= 1
        if left_num == 0:
            break
    if i != len(formula) - 1:  # 去除完成
        return formula
    return _cleanOuterBrackets(formula[1: -1])  # 去掉头尾,递归去除


""""
def parseToDNF(formula: str) -> List[Tuple[str, str]]:
    # 去除垃圾括号
    formula = _cleanOuterBrackets(formula)
    # 递归解析
    if formula == 'False':
        return []  # 空集
    elif formula == 'True' or _isOneOrder(formula):
        return [(formula, 'True')]  # phi∧X(True)
    elif formula[0] == 'X' and formula[1] == '(' and formula[-1] == ')':
        return [('True', formula[2:-1])]
    else:
        root_idx = _parseRootSymbol(formula)
        print('-', root_idx)
        phi_1, phi_2 = formula[:root_idx], formula[root_idx + 1:]
        if formula[root_idx] == 'U':
            left_dnf = parseToDNF(phi_2)
            right_dnf = parseToDNF(phi_1 + '∧X(' + formula + ')')
            print(left_dnf, right_dnf)
            left_dnf.extend(right_dnf)
            return left_dnf

        return []
"""


# --------------------------------------------------------


def isNormalForm(f: str) -> int:
    """
    检查LTL公式是否已经是标准型,如a∧b∧X(c)
    如果是标准型,返回X位置,否则返回-1
    """
    # X前面只能有合取,X后面不能有析取
    # 先从后向前匹配括号,检查匹配到的位置是X
    flen: int = len(f)
    if f[flen - 1] != ')':
        return -1
    cnt: int = 1  # 右括号被左括号消掉后的数量
    i = flen - 2
    while i >= 0:
        if f[i] == '(':
            cnt -= 1
        elif f[i] == ')':
            cnt += 1
        if cnt == 0:
            break
        i -= 1
    if i < 3:  # 至少是a∧X(b),即停止的游标最小也应该是3
        return -1
    if f[i - 1] != 'X':  # '('前一个字符必须是'X'
        return -1
    # 最后,检查前面是否不出现G/F/U/R/∨
    if re.search('[GFUR∨]', f[:i - 2]) is not None:
        return -1
    return i - 1


# --------------------------------------------------------

def _parseCons(f: str) -> Set[str]:
    """递归生成公式f的合取项"""
    ret_set = set()
    # [-1,...,len]中间记录最外层合取'∧'的下标,以做两两拆分
    hq_idxes = [-1]
    f = _cleanOuterBrackets(f)  # 清除多余括号
    cnt = 0  # 记录左括号被右括号消除最后剩下的数目
    for i in range(len(f) - 1):
        if f[i] == '(':
            cnt += 1
        elif f[i] == ')':
            cnt -= 1
        if cnt == 0 and f[i + 1] == '∧':
            hq_idxes.append(i + 1)
    hq_idxes.append(len(f))
    if len(hq_idxes) == 2:  # 递归出口,最外层已经没有合取项
        return {f}
    for j in range(len(hq_idxes) - 1):
        ret_set |= _parseCons(f[hq_idxes[j] + 1:hq_idxes[j + 1]])
    return ret_set


def _clearConjunction(f1: str, f2: str) -> str:
    """
    公式合取,去除多余的括号和合取项
    :param f1: 公式1
    :param f2: 公式2
    :return: 合取后的公式
    """
    ret_list = list(_parseCons(f1) | _parseCons(f2))
    sorted(ret_list)
    return '((' + ')∧('.join(ret_list) + '))'


# --------------------------------------------------------

formula_dict = dict()

dgnum = 0  # 递归层数,用于调试


def parseToDNF(f: str) -> Set[Tuple[str, str]]:
    global dgnum
    dgnum += 1
    """输入析取已经在外面的公式,转成DNF"""
    # 清除最外层括号
    f = _cleanOuterBrackets(f)
    # 检查是否已经计算过了
    if f in formula_dict:
        print('-' * dgnum + '已经计算过了' + f)
        dgnum -= 1
        return formula_dict[f]
    # 检查是否已经是标准型(新的递归出口)
    x_idx = isNormalForm(f)
    if x_idx >= 2:  # 用>0也行,但实际最小a∧X(b)中X最小是2
        _alpha = _cleanOuterBrackets(f[:x_idx - 1])
        _phi = _cleanOuterBrackets(f[x_idx + 1:])
        formula_dict[f] = {(_alpha, _phi)}
        print('-' * dgnum + '是标准型的' + f)
        dgnum -= 1
        return formula_dict[f]
    print('-' * dgnum + '待计算的' + f)
    # 检查其模式,为G()或X()或F()形式
    if re.match(r'[GXF]\(.*\)$', f) is not None:
        if f.startswith('G'):
            formula_dict[f] = parseToDNF('(False)R' + f[1:])
        elif f.startswith('F'):
            formula_dict[f] = parseToDNF('(True)U' + f[1:])
        else:  # X
            formula_dict[f] = {('True', f[2:-1])}  # True∧X(phi)
        dgnum -= 1
        return formula_dict[f]
    # DNF(False)=[]
    elif f == 'False':
        formula_dict[f] = set()
        dgnum -= 1
        return formula_dict[f]
    # 对不含LTL符号的一阶逻辑公式,DNF(alpha)=alpha∧X(True)
    elif _isOneOrder(f):
        formula_dict[f] = {(f, 'True')}
        dgnum -= 1
        return formula_dict[f]
    # 以上都不成立时,要检查根项,然后根据根的不同做不同的解析
    # 获得根元素下标
    root_idx = _parseRootSymbol(f)
    phi_1, phi_2 = f[:root_idx], f[root_idx + 1:]
    # DNF(ϕ1Uϕ2) = DNF(ϕ2)∪DNF(ϕ1∧X(ϕ1Uϕ2))
    if f[root_idx] == 'U':
        left_dnf = parseToDNF(phi_2)
        right_dnf = parseToDNF('(' + phi_1 + ')∧X(' + f + ')')
        formula_dict[f] = left_dnf | right_dnf
        dgnum -= 1
        return formula_dict[f]
    # DNF(ϕ1Rϕ2) = DNF(ϕ1∧ϕ2)∪DNF(ϕ2∧X(ϕ1Rϕ2))
    elif f[root_idx] == 'R':
        left_dnf = parseToDNF(_clearConjunction(phi_1, phi_2))
        right_dnf = parseToDNF('(' + phi_2 + ')∧X(' + f + ')')
        formula_dict[f] = left_dnf | right_dnf
        dgnum -= 1
        return formula_dict[f]
    # DNF(ϕ1∨ϕ2) = DNF(ϕ1)∪DNF(ϕ2)
    elif f[root_idx] == '∨':
        left_dnf = parseToDNF(phi_1)
        right_dnf = parseToDNF(phi_2)
        formula_dict[f] = left_dnf | right_dnf
        dgnum -= 1
        return formula_dict[f]
    #  DNF(ϕ1∧ϕ2) = {(α1∧α2)∧X(ψ1∧ψ2) |∀i = 1,2. αi∧X(ψi) ∈ DNF(ϕi)}
    else:  # ∧
        dnf_phi_1 = parseToDNF(phi_1)
        print('-' * dgnum + ">1>", dnf_phi_1)
        dnf_phi_2 = parseToDNF(phi_2)
        print('-' * dgnum + ">2>", dnf_phi_2)
        ret_dnf = set()
        for p1 in dnf_phi_1:
            for p2 in dnf_phi_2:
                # 清理多余'True',多余的合取项,并保证出现次序
                if p1[0] == 'True':
                    _alpha = p2[0]
                elif p2[0] == 'True':
                    _alpha = p1[0]
                elif p1[0] == p2[0]:  # 重复的只保留一个
                    _alpha = p1[0]
                else:
                    _alpha = _clearConjunction(p1[0], p2[0])

                if p1[1] == 'True':
                    _phi = p2[1]
                elif p2[1] == 'True':
                    _phi = p1[1]
                elif p1[1] == p2[1]:
                    _phi = p1[1]
                else:
                    _phi = _clearConjunction(p1[1], p2[1])
                ret_dnf.add((_alpha, _phi))
        formula_dict[f] = ret_dnf
        dgnum -= 1
        return ret_dnf


# --------------------------------------------------------

"""
@deprecated
def parseToDNF2(formula: str) -> List[Tuple[str, str]]:
    # fixme
    if formula == '(a)U(b)':
        return [('b', 'True'), ('a', '(a)U(b)')]
    elif formula == 'True':
        return [('True', 'True')]
    return []
"""

if __name__ == '__main__':
    # print(parseToDNF('G(((b)U(c))∧((d)U(e)))'))
    # print(parseToDNF('(a)U(G(a))'))
    print(_clearConjunction('(a)∧((a)∧(d))', '((b)∧(c))'))
