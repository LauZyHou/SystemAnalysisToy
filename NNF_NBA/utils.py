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


def cleanOuterBrackets(formula: str) -> str:
    """去除最外层的垃圾括号,如((..(a∧b)R(c)..))变成(a∧b)R(c)"""
    # print('*' + formula)
    if len(formula) <= 1 or formula[0] != '(':
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
    return cleanOuterBrackets(formula[1: -1])  # 去掉头尾,递归去除


def cleanInnerBrackets(formula: str) -> Set[str]:
    """为析取式内部去除括号"""
    ret: Set[str] = set()
    f = cleanOuterBrackets(formula)
    cnt = 0  # 左括号被右括号减少的数目
    left = 0  # 子串开始位置
    for i in range(len(f) - 2):
        if f[i] == '(':
            cnt += 1
        elif f[i] == ')':
            cnt -= 1
        if cnt == 0 and f[i + 1] == '∨':
            ret |= cleanInnerBrackets(f[left:i + 1])
            left = i + 2
    if left != 0:
        ret |= cleanInnerBrackets(f[left:])
    else:
        ret = {f}
    return ret


def cleanBracketsOnAP(formula: str) -> str:
    """清除原子命题两边的括号"""
    # 先将True和False替换成其它字符串,保护起来
    f = formula.replace('True', '#')
    f = f.replace('False', '*')
    # 记录不保留的数组下标,即'(a)'这样的三个字符
    bye_set: Set[int] = set()
    for i in range(1, len(f) - 1):
        if ('z' >= f[i] >= 'a' or f[i] == '#' or f[i] == '*') and f[i - 1] == '(' and f[i + 1] == ')':
            bye_set |= {i - 1, i + 1}
    # 遍历,只保留那些留下的下标,同时将True和False还原
    ret_str = ''
    for i in range(len(f)):
        if i not in bye_set:
            ret_str += 'True' if f[i] == '#' else ('False' if f[i] == '*' else f[i])
    return ret_str


""""
def parseToDNF(formula: str) -> List[Tuple[str, str]]:
    # 去除垃圾括号
    formula = cleanOuterBrackets(formula)
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
    f = cleanOuterBrackets(f)  # 清除多余括号
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
    f = cleanOuterBrackets(f)
    # 检查是否已经计算过了
    if f in formula_dict:
        print('-' * dgnum + '已经计算过了' + f)
        dgnum -= 1
        return formula_dict[f]
    # 检查是否已经是标准型(新的递归出口)
    x_idx = isNormalForm(f)
    if x_idx >= 2:  # 用>0也行,但实际最小a∧X(b)中X最小是2
        _alpha = cleanOuterBrackets(f[:x_idx - 1])
        _phi = cleanOuterBrackets(f[x_idx + 1:])
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
                    # _alpha = _clearConjunction(p1[0], p2[0])
                    _alpha = (p1[0] + '∧' + p2[0]) if p1[0] > p2[0] else (p2[0] + '∧' + p1[0])

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

def preHandle(formula: str) -> str:
    """对输入LTL公式的预处理"""
    # 为True,False,所有原子命题(单字母)加括号
    _f = formula
    _f = re.sub(r'\(True\)|True', '(#)', _f)
    _f = re.sub(r'\(False\)|False', '(*)', _f)
    for i in range(26):
        symbol = chr(i + ord('a'))
        pattern = '(' + symbol + ')|' + symbol
        to = '(' + symbol + ')'
        _f = re.sub(pattern, to, _f)
    _f = re.sub(r'\(#\)', '(True)', _f)
    _f = re.sub(r'\(\*\)', '(False)', _f)
    return _f


"""
@deprecated
def judgeBracketsMatch(formula: str) -> bool:
    # 判断公式是否满足:存在第一个括号和最后一个括号且匹配
    _f = formula
    if len(_f)<2:
        return False
    if _f[0]!='(' or _f[-1]!=')':
        return False
    pass
"""


def addBrackets(formula: str) -> str:
    """
    为公式添加括号,即形成程序要求的输入形式(分治法)
    LTL公式符号优先级
    ﹁,X,G,F
    U,R
    ∧
    ∨
    """
    _f = formula
    # 优先级->值的字典
    level_dict = {
        'U': 0, 'R': 0, '∧': 1, '∨': 2
    }
    # 如果在0优先级,还要标识每个位置是U还是R
    ur_list = []
    # 查找可能的根元素位置,优先级最低的二元关系
    now_lev = 0  # 优先级下降法,初始在{'U','R'}层
    cnt = 0  # 左括号被右括号消除的剩余数量
    split_list = [-1]  # 分离数组,存最低优先级根元素下标[-1,下标,len(_f)]
    for i in range(0, len(_f)):
        if _f[i] == '(':
            cnt += 1
        elif _f[i] == ')':
            cnt -= 1
        if cnt == 0 and 0 < i < len(_f) - 1:  # 考虑优先级
            if _f[i] in level_dict:  # 如果是可能的根元素
                if level_dict[_f[i]] < now_lev:  # 优先级过高
                    continue  # 跳过
                elif level_dict[_f[i]] == now_lev:  # 相等优先级
                    split_list.append(i)  # 添加分割位置
                    if now_lev == 0:  # 0级要标识是U还是R
                        ur_list.append(_f[i])
                else:  # 新找到的根优先级比现在的低
                    now_lev = level_dict[_f[i]]  # 修改优先级
                    split_list = [-1, i]  # 清空分割位置,只放当前位置
    if len(split_list) > 1:  # 默认有个-1,最终>1说明找到了根,要按根分割
        ret = ''
        split_list.append(len(_f))
        if now_lev == 0:
            ur_list.append('#')
        for j in range(len(split_list) - 1):
            if now_lev == 0:
                root = ur_list[j]
            elif now_lev == 1:
                root = '∧'
            elif now_lev == 2:
                root = '∨'
            else:
                root = '###'
                print('*error*错误的优先层级')
            # print(_f[split_list[j] + 1:split_list[j + 1]]) # 已测试
            ret += '(' + cleanOuterBrackets(addBrackets(_f[split_list[j] + 1:split_list[j + 1]])) + ')' + root
            # ret += addBrackets(_f[split_list[j] + 1:split_list[j + 1]]) + root
        return ret[:-1]
    else:  # 不存在根,为原子命题添加括号并返回
        return preHandle(_f)


# --------------------------------------------------------


if __name__ == '__main__':
    # print(parseToDNF('G(((b)U(c))∧((d)U(e)))'))
    # print(parseToDNF('(a)U(G(a))'))
    # print(_clearConjunction('(a)∧((a)∧(d))', '((b)∧(c))'))
    # print(cleanInnerBrackets('(b∨c)'))
    # print(cleanBracketsOnAP('(True)∧(a)∧((a)∧(d))'))
    print(addBrackets('(a∨b)∧cRd'))
