import json
from typing import List, Dict, Set
from deprecated import deprecated
from graphviz import Digraph


class State:
    """Transition System的状态类"""
    loc: str = None  # 来自PG的Loc
    eval_var: Dict[str, int] = None  # 所有Var的取值Eval(Var)，这里用字典表示

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

    def to_graph_use(self):
        """给绘图用的字符串表示：如start,nsoda=1,nbeer=1"""
        return self.loc + "," + ",".join([k + "=" + str(v) for k, v in self.eval_var.items()])

    def __eq__(self, other):
        """判断两Stat相等：Location相同且所有变量值相同"""
        if self.loc != other.loc:
            return False
        for k in self.eval_var.keys():
            if self.eval_var[k] != other.eval_var[k]:
                return False
        return True


class Transfer:
    """Transition System的转移类"""
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
    """Transition System中，对应于每个Stat，标签映射后的结果"""
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


class TransitionSystem:
    """Transition System"""
    states: List[State] = None
    actions: Set[str] = None
    transitions: List[Transfer] = None
    initial_states: List[State] = None
    atomic_propositions: Set[str] = None
    labels: List[Label] = None

    def __init__(self,
                 s_: List[State] = None,
                 act_: Set[str] = None,
                 trans_: List[Transfer] = None,
                 i_: List[State] = None,
                 ap_: Set[str] = None,
                 l_: List[Label] = None):
        self.states = s_ if s_ is not None else list()
        self.actions = act_ if act_ is not None else set()
        self.transitions = trans_ if trans_ is not None else list()
        self.initial_states = i_ if i_ is not None else list()
        self.atomic_propositions = ap_ if ap_ is not None else set()
        self.labels = l_ if l_ is not None else list()

    def to_dict(self) -> Dict:
        """转为字典"""
        return {
            'S': [str(s) for s in self.states],
            'Act': list(self.actions),
            'Trans': [str(t) for t in self.transitions],
            'I': [str(i) for i in self.initial_states],
            'AP': list(self.atomic_propositions),
            'L': [l.to_list() for l in self.labels]
        }

    def to_dict2(self) -> Dict:
        """[*]转为字典(标签中含对应状态)"""
        label_list: List[str] = list()
        for l, s in zip(self.labels, self.states):
            temp: str = 'L（' + str(s.to_graph_use()) + ") = {" + str(l) + "}"
            label_list.append(temp)

        return {
            'S': [str(s) for s in self.states],
            'Act': list(self.actions),
            'Trans': [str(t) for t in self.transitions],
            'I': [str(i) for i in self.initial_states],
            'AP': list(self.atomic_propositions),
            'L': label_list
        }


def write_ts_in_json(ts_dict: Dict, file_path: str) -> None:
    """将Transition System写入JSON文件
    :param ts_dict: 要持久化的Transition System的字典表示
    :param file_path: 文件路径
    """
    with open(file_path, "w", encoding='utf-8') as f:
        # json.dump(out, f)
        f.write(json.dumps(ts_dict, indent=1).encode('utf-8').decode('unicode_escape'))
    print("完成！输出结果于", file_path)


def out_ts_graph(ts: TransitionSystem, file_type: str) -> None:
    """将Transition System有向图输出
    :param ts: 要输出的Transition System
    :param file_type: 文件类型(扩展名)
    """
    # 为Transaction System的字段创建引用
    S: List[State] = ts.states  # 存所有状态
    Trans: List[Transfer] = ts.transitions  # 存所有转移关系

    # 生成TS的GraphViz有向图
    dot = Digraph(comment='Transition System')
    for s in S:  # 生成结点(状态)
        str_s = s.to_graph_use()
        dot.node(str_s, str_s)  # 第一参数是其唯一标识,第二参数是外显的文字,这里都用其字符串
    for t in Trans:  # 生成边(转移关系上的动作)
        str_s1 = t.s1.to_graph_use()
        str_act = str(t.act)
        str_s2 = t.s2.to_graph_use()
        dot.edge(str_s1, str_s2, str_act)
    dot.render('transition_system.gv', view=True, format=file_type)
