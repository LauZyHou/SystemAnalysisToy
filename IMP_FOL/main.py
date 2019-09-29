import re

divide_str = '-' * 30


def formalize(olds):
    """规格化原始表达式"""
    lst_s = olds.split(' ')
    lst_news = []
    for s in lst_s:
        if len(s) > 0:
            lst_news.append(s)
    return "".join(lst_news)


class TYPE():
    """用于枚举语句类型"""
    IF_THEN_ELSE = 'ITE'
    DO_WHILE = 'DW'
    SKIP = 'S'
    ASSIGN = 'A'
    UNKNOWN = 'U'


def v_tup(s):
    if s == 'skip':
        return 'V', None
    else:
        return 'V', s.split(' :=')[0]


if __name__ == '__main__':
    f = open('./in_imp.txt')
    # 读取的每行原始数据
    lines = f.read().split('\n')
    print('\n'.join(lines))
    print(divide_str)
    # 第一轮处理
    for i in range(len(lines)):
        now_str = lines[i]
        # 对原始数据标号
        label = 'L' + str(i)
        # 添加类型
        sentence_type = TYPE.UNKNOWN
        if re.match(r"if (.*) then (.*) else (.*)", now_str) is not None:
            sentence_type = TYPE.IF_THEN_ELSE
        elif re.match(r"do (.*) while", now_str) is not None:
            sentence_type = TYPE.DO_WHILE
        elif re.match(r"skip", now_str) is not None:
            sentence_type = TYPE.SKIP
        elif re.match(r"(.*):=(.*)", now_str) is not None:
            sentence_type = TYPE.ASSIGN
        lines[i] = (label, lines[i], sentence_type)
    print(lines)
    # 处理成一阶逻辑公式，每个list项[类型,pc,pc',(大集合,要去除的集合),操作]
    fols = [[TYPE.SKIP, 'm', 'L0', ('V', None), None]]
    for i in range(len(lines)):
        sentence_type = lines[i][-1]
        sentence_str = lines[i][1]
        sentence_label = lines[i][0]
        fols.append([sentence_type,
                     sentence_label,
                     lines[i + 1][0] if i + 1 < len(lines) else 'm\'',
                     v_tup(sentence_str),
                     sentence_str if sentence_type != TYPE.SKIP else None])
    print(divide_str)
    for fol in fols:
        sentence_type = fol[0]
        pc = fol[1]
        pc2 = fol[2]
        variable = fol[3]
        sentence_str = fol[4]
        # 合成范式的命题项
        same_str = 'same(' + variable[0]
        same_str += ')' if variable[1] is None else ('\\' + '{' + variable[1] + '})')
        pc_str = 'pc=' + pc
        pc2_str = 'pc\'=' + pc2
        # 合成一条合取范式
        if sentence_str is None:
            sentence_str = ''
        else:
            sentence_str = ' ∧ ' + sentence_str
        conjunction = pc_str + ' ∧ ' + pc2_str + sentence_str + ' ∧ ' + same_str
        print(conjunction)
