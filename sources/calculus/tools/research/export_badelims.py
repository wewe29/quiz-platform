# -*- coding: utf-8 -*-
"""把「疑似非法定界符」的候选公式导出成 JSON，交给 katex_probe.js 逐条判定。"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank import load_bank  # noqa: E402
from scan_badelims import BAD_ELIM, MATH, formulas_of  # noqa: E402

bank = load_bank()
cands = []
for q in bank:
    for tex in formulas_of(q):
        if BAD_ELIM.search(tex):
            cands.append({"id": q["id"], "tex": tex})
out = os.path.join(HERE, "_badelim_cands.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"formulas": [c["tex"] for c in cands]}, f, ensure_ascii=False)
print("候选 %d 条 → %s" % (len(cands), out))
for c in cands[:5]:
    print("  ", c["id"], c["tex"][:90])
