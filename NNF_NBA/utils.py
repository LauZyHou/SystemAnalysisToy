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

def parseToDNF(f: str):
    """输入析取已经在外面的公式,转成DNF"""
    # 清除最外层括号
    f = _cleanOuterBrackets(f)
    # print(f)
    # 检查其模式,为G()或X()或F()形式
    if re.match(r'[GXF]\(.*\)$', f) is not None:
        if f.startswith('G'):
            return parseToDNF('(False)R' + f[1:])
        elif f.startswith('F'):
            return parseToDNF('(True)U' + f[1:])
        else:  # X
            return [('True', f[2:-1])]  # True∧X(phi)
    # DNF(False)=[]
    elif f == 'False':
        return []
    # 对不含LTL符号的一阶逻辑公式,DNF(alpha)=alpha∧X(True)
    elif _isOneOrder(f):
        return [(f, 'True')]
    # 以上都不成立时,要检查根项,然后根据根的不同做不同的解析
    # 获得根元素下标
    root_idx = _parseRootSymbol(f)
    phi_1, phi_2 = f[:root_idx], f[root_idx + 1:]
    # DNF(ϕ1Uϕ2) = DNF(ϕ2)∪DNF(ϕ1∧X(ϕ1Uϕ2))
    if f[root_idx] == 'U':
        left_dnf = parseToDNF(phi_2)
        right_dnf = parseToDNF('(' + phi_1 + ')∧X(' + f + ')')
        left_dnf.extend(right_dnf)
        return left_dnf
    # DNF(ϕ1Rϕ2) = DNF(ϕ1∧ϕ2)∪DNF(ϕ2∧X(ϕ1Rϕ2))
    elif f[root_idx] == 'R':
        left_dnf = parseToDNF('(' + phi_1 + ')∧(' + phi_2 + ')')
        right_dnf = parseToDNF('(' + phi_2 + ')∧X(' + f + ')')
        left_dnf.extend(right_dnf)
        return left_dnf
    # DNF(ϕ1∨ϕ2) = DNF(ϕ1)∪DNF(ϕ2)
    elif f[root_idx] == '∨':
        left_dnf = parseToDNF(phi_1)
        right_dnf = parseToDNF(phi_2)
        left_dnf.extend(right_dnf)
        return left_dnf
    #  DNF(ϕ1∧ϕ2) = {(α1∧α2)∧X(ψ1∧ψ2) |∀i = 1,2. αi∧X(ψi) ∈ DNF(ϕi)}
    else:
        dnf_phi_1 = parseToDNF(phi_1)
        # print(">1>", dnf_phi_1)
        dnf_phi_2 = parseToDNF(phi_2)
        # print(">2>", dnf_phi_2)
        ret_dnf = []
        for p1 in dnf_phi_1:
            for p2 in dnf_phi_2:
                # 清理多余'True'
                if p1[0] == 'True':
                    _alpha = p2[0]
                elif p2[0] == 'True':
                    _alpha = p1[0]
                else:
                    _alpha = p1[0] if (p1[0] == p2[0]) else (p1[0] + '∧' + p2[0])
                if p1[1] == 'True':
                    _phi = p2[1]
                elif p2[1] == 'True':
                    _phi = p1[1]
                else:
                    _phi = p1[1] if (p1[1] == p2[1]) else (p1[1] + '∧' + p2[1])
                ret_dnf.append((_alpha, _phi))
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
    print(parseToDNF('(a)U((b)U(c))'))
