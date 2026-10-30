# -*- coding: utf-8 -*-
"""《高等数学》题库包。

对外接口：
    load_bank()  -> list[dict]   载入 ch1..ch12 全部题目并稳定排序、分配 idx
    audit(qs)    -> (report, err) 题库结构自检（A1–A6）
    Q(...)                      构造函数
    SEC                         知识点 -> 教材出处表
"""
from .common import (  # noqa: F401
    load_bank, audit, Q, SEC,
    SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC,
    GROUP, TYPE_GROUP_LABEL,
)

__all__ = [
    "load_bank", "audit", "Q", "SEC",
    "SINGLE", "MULTI", "JUDGE", "BLANK", "TERM", "SHORT", "CALC",
    "GROUP", "TYPE_GROUP_LABEL",
]
