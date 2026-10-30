# -*- coding: utf-8 -*-
"""《线性代数》题库包。

对外接口：
    load_bank()  -> list[dict]   载入 ch1..ch6 全部题目并稳定排序、分配 idx
    audit(qs)    -> (report, err) 题库结构自检（A1–A6）
    Q(...)                      构造函数
    SEC                         知识点 -> 教材出处表
"""
from .common import (  # noqa: F401
    load_bank, audit, Q, SEC,
    SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC,
    GROUP, TYPE_GROUP_LABEL, LOCAL_ML,
)
from . import target  # noqa: F401  题库口径的单一事实源

__all__ = [
    "load_bank", "audit", "Q", "SEC", "target",
    "SINGLE", "MULTI", "JUDGE", "BLANK", "TERM", "SHORT", "CALC",
    "GROUP", "TYPE_GROUP_LABEL", "LOCAL_ML",
]
