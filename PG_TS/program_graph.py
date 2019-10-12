import json
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ProgramGraph:
    """Program Graph"""
    locations: List[str]
    actions: List[str]
    effects: Dict[str, List[str]]
    hooks: List[List[str]]
    initial_locations: List[str]
    initial_guard: Dict[str, int]


def read_pg_from_json(file_path: str) -> ProgramGraph:
    """读入Program Graph
    :param file_path: 文件路径
    """
    with open(file_path, encoding='utf-8') as f:
        ok = json.load(f)
    return ProgramGraph(ok['Loc'], ok['Act'], ok['Effect'], ok['Hooks'], ok['Loc_0'], ok['g_0'])
