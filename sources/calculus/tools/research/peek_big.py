# -*- coding: utf-8 -*-
"""打印题库里含 Bigg 的原始片段（定位 KaTeX 报错的具体写法）。"""
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from qa_bank import load_bank  # noqa: E402

bank = load_bank()
for q in bank:
    blob = " ".join([q.get("stem") or "", q.get("answerText") or "",
                     q.get("explanation") or "", str(q.get("points") or "")])
    if "Bigg" not in blob and "Big{" not in blob:
        continue
    print("=" * 70)
    print(q["id"])
    for m in re.finditer(r".{25}Big.{40}", blob, re.S):
        print("   ", repr(m.group(0)))
