# -*- coding: utf-8 -*-
"""打印「解析过短」告警对应的题目原文，核对是源卷面本来就这么短，还是切错了。

用法: python research/peek_short.py 3
"""
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from qa_bank import load_bank  # noqa: E402

IDS = ["ky2-1987-2-bdeead", "ky2-1990-2-c7bf84", "ky2-1993-1-0793b0",
       "ky2-1996-1-4ac733", "ky2-1992-3-4ea038", "ky2-1991-5-729bbe"]

bank = {q["id"]: q for q in load_bank()}
for qid in IDS:
    q = bank.get(qid)
    if not q:
        print("NOT FOUND", qid)
        continue
    print("=" * 74)
    print(qid, "|", q["type"], "|", q.get("source", {}).get("paper"),
          "| 第", q.get("source", {}).get("number"), "题")
    print("-- 题干 --")
    print(q.get("stem"))
    print("-- 选项 --", q.get("options"))
    print("-- 答案 --", q.get("answer"))
    print("-- 解析（answerText）--")
    print(repr(q.get("answerText")))
    print("-- explanation --")
    print(repr(q.get("explanation"))[:400])
    print()
