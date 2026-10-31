# -*- coding: utf-8 -*-
"""抽样打印真题主观题的解析原文与当前采分点，用于判断切分粒度。

用法: python research/peek_sol.py 3
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

from qa_bank import load_bank  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
only_prefix = sys.argv[2] if len(sys.argv) > 2 else ""

bank = [q for q in load_bank()
        if q.get("type") == "calc" and len(q.get("points") or []) == 1
        and (not only_prefix or q["id"].startswith(only_prefix))]
print("单采分点的主观题：", len(bank))
for q in bank[:n]:
    print("=" * 78)
    print(q["id"], "|", q.get("source", {}).get("paper"), "|", len(q.get("points") or []), "个采分点")
    print("-- 解析原文 --")
    print(q.get("answerText") or "")
    print("-- 采分点 --")
    for i, p in enumerate(q.get("points") or []):
        print("  [%d] %s" % (i + 1, p.get("text")))
    print()
