# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 16:53
# @Author  : LauZyHou
# @File    : 主文件

import json
from typing import List, Dict, Set, Tuple
from deprecated import deprecated
from functools import cmp_to_key

FILE_IN = r'./in_pg.json'
FILE_OUT = r'./out_ts.json'


class State:
    """生成的Transition System的状态类"""
    loc: str = None  # 来自PG的Loc
    eval_var: Dict[str, int] = None  # 所有Var的取值Eval(Var)，这里用字典表示

    # is_alive: bool = True  # 指示该状态是否是活动的（已全部计算完后继的状态设置为False）

    def __init__(self, loc_: str, eval_var_: Dict):
        """构造器：直接传入location名称和变量字典"""
        self.loc = loc_
        self.eval_var = eval_var_

    def __str__(self):
        """转为字符串表示：如<start,nsoda=1∧nbeer=1>"""
        return "<" + self.loc + "," + "∧".join([k + "=" + str(v) for k, v in self.eval_var.items()]) + ">"

    @deprecated(version='1.0', reason='写入JSON时直接写入字符串')
    def to_list(self) -> List:
        """转为list表示"""
        return [self.loc, self.eval_var]

    def __eq__(self, other):
        """判断两Stat相等：Location相同且所有变量值相同"""
        if self.loc != other.loc:
            return False
        for k in var_list:
            if self.eval_var[k] != other.eval_var[k]:
                return False
        return True


class Transfer:
    """生成的Transition System的转移类"""
    s1: State = None  # 转移前的状态
    act: str = None  # 转移经过的动作
    s2: State = None  # 转移后的状态

    def __init__(self, s1_: State, act_: str, s2_: State):
        """构造器：状态，动作，状态"""
        self.s1 = s1_
        self.act = act_
        self.s2 = s2_

    def __str__(self):
        """转为字符串表示：如<select,nsoda=1∧nbeer=1> -sget-> <start,nsoda=0∧nbeer=1>"""
        return str(self.s1) + " -" + self.act + "-> " + str(self.s2)


class Label:
    """生成的Transition System中，对应于每个Stat，标签映射后的结果"""
    loc: str = None  # Location部分
    guard: List[str] = None  # 所满足条件部分

    def __init__(self, loc_: str, guard_: List[str]):
        """构造器：位置，条件"""
        self.loc = loc_
        self.guard = guard_

    def __str__(self):
        """转为字符串表示，如：select,nsoda>0,nbeer>0"""
        if len(self.guard) == 0:
            return self.loc
        return self.loc + ',' + ','.join(self.guard)

    def to_list(self) -> List[str]:
        """转为list表示，如：[select,nsoda>0,nbeer>0]"""
        ret: List[str] = [self.loc]
        ret.extend(self.guard)
        return ret


def myeval(ev: Dict[str, int], exp: str) -> int:
    """对表达式求值
    :param ev: 当前变量取值字典
    :param exp: 表达式，如"nbeer+1"
    :return: 求值后的结果
    """
    # 获取变量字典的List[tuple]表示，为防止在后续替换中破坏掉变量（如先替换'a'会破坏变量'ba'），将其按len降序
    evs: List = list(ev.items())  # 具体是List[Tuple[str, int]]，PyCharm误报
    assert type(evs[0]) is tuple
    evs.sort(key=cmp_to_key(lambda x, y: len(y[0]) - len(x[0])))
    # 先将全部变量替换成值
    for k, v in evs:
        exp = exp.replace(k, str(v))
    # 现在变成了例如"2+1"这样的字符串，直接用eval求值即可
    return eval(exp)


def satisfy_ap(ev: Dict[str, int], ap: str) -> bool:
    """判断当前变量取值ev是否满足原子命题ap
    :param ev: 当前变量取值字典
    :param ap: 原子命题字符串，如"nsoda>=nbeer+1"
    :return : 是否满足条件
    """
    if ap == "true":
        return True
    if ap == "false":
        return False
    # 拆分成左右条件部分
    if ap.find('>=') > 0:
        left, right = ap.split('>=')
        return myeval(ev, left) >= myeval(ev, right)
    elif ap.find('<=') > 0:
        left, right = ap.split('<=')
        return myeval(ev, left) <= myeval(ev, right)
    elif ap.find('=') > 0:
        left, right = ap.split('=')
        return myeval(ev, left) == myeval(ev, right)
    elif ap.find('<') > 0:
        left, right = ap.split('<')
        return myeval(ev, left) < myeval(ev, right)
    elif ap.find('>') > 0:
        left, right = ap.split('>')
        return myeval(ev, left) > myeval(ev, right)
    print("[error]无法识别的原子命题:", ap)
    return False


def satisfy(ev: Dict[str, int], g: str) -> bool:
    """判断当前变量取值ev是否满足复合条件g
    :param ev: 当前变量取值字典
    :param g: 条件字符串，如"nsoda=0∧nbeer=0"
    :return : 是否满足条件
    """
    # 先按析取符号拆分成多条件的"或"
    conditons: List[str] = g.split('∨')
    # 对每个条件项（它们最后析取起来，所以只要有一项满足就返回True）
    for cond in conditons:
        # 拆分成多个项的合取
        hqs: List[str] = cond.split('∧')
        # 判断这些项是否都满足条件，如果是立即返回True
        sat: bool = True
        for hq in hqs:
            if not satisfy_ap(ev, hq):
                sat = False
                break
        if sat:
            return True
    return False


def var_trans(ev: Dict[str, int], ef: List[str]) -> Dict[str, int]:
    """变量值的变换
    :param ev: 当前变量取值字典
    :param ef: 变换过程（是Effect中的一项，可能包含多个顺序语句），如["nbeer:=nbeer-1","nsoda:=1"]
    :return : 变换后的变量取值
    """
    # 变换后的变量值字典
    new_ev: Dict[str, int] = ev.copy()
    # 一句一句顺序执行
    for e in ef:  # 对每个语句
        left, right = e.split(':=')  # 切分成左右值
        new_ev[left] = myeval(new_ev, right)  # 计算右值计算结果，写入左值变量中
    return new_ev


def refresh_all(s: State) -> None:
    """从状态s更新S,Act_,Trans,AP,L
    :param s: 当前状态
    """
    loc: str = s.loc
    eval_var: Dict[str, int] = s.eval_var
    # AP中添加Loc部分
    AP.add(loc)
    # 用于生成状态S的Label时所使用的后面的条件部分（\eta满足的g的集合）
    gs: Set[str] = set()
    # 对每个转移尝试能否从s进行转移
    for h in Hooks:  # 对每个允许的转移关系
        if h[0] == loc and satisfy(eval_var, h[1]):  # 若是从当前Location出发，且满足guard条件
            # (S)生成转移后的状态
            if h[2] not in Effect:  # 如果是没有影响的动作，变量都不变，只要考虑h[3]即转移后的Loc
                trs: State = State(h[3], eval_var.copy())
            else:
                trs: State = State(h[3], var_trans(eval_var, Effect[h[2]]))
            # 判断是否是新状态
            is_new_s: bool = True
            for old_s in S:
                if old_s == trs:
                    is_new_s = False
                    break
            # 如果是新状态，将其加入到S中
            if is_new_s:
                S.append(trs)

            # (Trans)生成TS的转移关系
            trtr: Transfer = Transfer(s, h[2], trs)
            # 转移关系一定是新的，添加到Trans中
            Trans.append(trtr)

            # (AP)原子命题中添加条件部分。(L)当前Label的条件部分gs也添加此条件。
            if h[1] != 'true' and h[1] != 'false':
                AP.add(h[1])
                gs.add(h[1])

            # (Act_)添加切实使用了的当前转移的动作
            Act_.add(h[2])
    # (L)添加本状态的Label，只要依次调用此函数，然后生成Label添加到L即可和S中的状态一一对应
    L.append(Label(loc, list(gs)))


if __name__ == '__main__':
    # 从JSON文件中读取Program Graph
    with open(FILE_IN, encoding='utf8') as f:
        ok = json.load(f)
    Loc: List[str] = ok['Loc']  # 存所有Location
    Act: List[str] = ok['Act']  # 存所有Action
    Effect: Dict[str, List[str]] = ok['Effect']  # 存每个Action对变量的影响（无影响的Action不被记录）
    Hooks: List[List[str]] = ok['Hooks']  # 存PG的所有转移（符号上是个弯钩箭头所以叫Hooks）
    Loc_0: List[str] = ok['Loc_0']  # 初始Location
    g_0: Dict[str, int] = ok['g_0']  # 初始条件，可指示变量的初值
    # 从g_0中读取变量名称
    var_list = list(g_0.keys())
    print("读取变量名称: ", var_list)
    # 定义转换后的Transaction System的内容，它们最终会写入JSON文件
    S: List[State] = []  # 存所有状态
    Act_: Set[str] = set()  # 存所有动作（PG中未必所有Act都用到，所以用set去重）
    Trans: List[Transfer] = []  # 存所有转移关系
    I: List[State] = []  # 初始状态集合
    AP: Set[str] = set()  # 原子命题集合（也是用set去重）
    L: List[Label] = []  # 存S中每个状态通过标签函数映射的结果
    # 从Loc_0生成初始状态I，并在S中也写入初始状态
    for loc0 in Loc_0:
        s0 = State(loc0, g_0.copy())
        I.append(s0)
        S.append(s0)
    print("初始状态集合：I=", [str(s) for s in I])
    # 从S和PG上的Act(用Effect实际就不必用Act了)、Hooks和Effect生成TS的其它内容
    idx = 0  # 指示BFS搜索到S中的哪个状态，已经搜过的状态设is_active=False
    while idx < len(S):  # S的大小会随新状态append进来而逐渐变大
        s = S[idx]  # 当前要BFS的状态
        # 从这个状态s找到能一步到达的状态，更新S,Act_,Trans,AP,L
        refresh_all(s)
        # s.is_alive = False
        idx += 1
    # 写入JSON文件
    out = {
        'S': [str(s) for s in S],
        'Act': list(Act_),
        'Trans': [str(t) for t in Trans],
        'I': [str(i) for i in I],
        'AP': list(AP),
        'L': [l.to_list() for l in L]
    }
    with open(FILE_OUT, "w", encoding='utf-8') as f:
        # json.dump(out, f)
        f.write(json.dumps(out).encode('utf-8').decode('unicode_escape'))
    print("完成！输出结果于", FILE_OUT)
