# -*- coding: utf-8 -*-
# @Time    : 2019/9/30 13:07
# @Author  : LauZyHou
# @File    : 语句处理
from typing import List
import re

PAT_WHILE_PURE = r'^while (\S+) do (\S+)$'
PAT_WHILE_IMPURE = r'^while (\S+) do (\S+) (.*)$'
PAT_IF_PURE = r'^if (\S+) then (\S+) else (\S+)$'
PAT_IF_IMPURE = r'^if (\S+) then (\S+) else (\S+) (.*)$'


def split_sentence(sentence: str) -> List[str]:
    """拆分一个句子，如a:=3;b:=5拆分成前后的两句"""
    # 无需拆分的情况
    if sentence == 'skip' \
            or sentence.startswith('if ') \
            or sentence.startswith('while ') \
            or sentence.find(';') < 0:
        return [sentence]
    # 需要拆分的情况
    first, second = sentence.split(';', 1)
    ret = [first]
    ret.extend(split_sentence(second))
    return ret


# ----------------------------------------------------------------------------------

def split_sentence_test():
    test1 = split_sentence('a:=3;b:=5;if a>0 then a:=3;b:=2 else c:=1;d:=d+1')
    print(test1)
    test2 = split_sentence('a:=3;b:=5;c:=a*2;d:=d+1;skip;a:=a+b-3')
    print(test2)
    test3 = split_sentence('a:=3;b:=5;while a>0 do a:=3;b:=2')
    print(test3)


def match_test():
    # while-do正则测试
    mystr1 = r'while a>0 do a:=3;b:=2 c:=44'
    mystr2 = r'while a>0 do a:=3;b:=2'
    assert re.match(PAT_WHILE_PURE, mystr1) is None
    assert re.match(PAT_WHILE_PURE, mystr2) is not None
    assert re.match(PAT_WHILE_IMPURE, mystr1) is not None
    assert re.match(PAT_WHILE_IMPURE, mystr2) is None
    # if-then-else正则测试
    mystr1 = r'if a>0 then a:=3 else b:=2 c:=44'
    mystr2 = r'if a>0 then a:=3 else b:=2'
    assert re.match(PAT_IF_PURE, mystr1) is None
    assert re.match(PAT_IF_PURE, mystr2) is not None
    assert re.match(PAT_IF_IMPURE, mystr1) is not None
    assert re.match(PAT_IF_IMPURE, mystr2) is None


if __name__ == '__main__':
    match_test()
