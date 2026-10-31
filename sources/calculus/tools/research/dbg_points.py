# -*- coding: utf-8 -*-
"""打印指定 id 的原始解析文本（repr），用于定位采分点切分缺陷。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

from qa_bank import load_bank  # noqa: E402

IDS = sys.argv[1:] or ["ky-2017-19-fa7e69", "ky-2018-2-cfc6be",
                       "ky-2010-19-c0d03e", "ky-2005-7-40f577"]

bank = load_bank()
by_id = {q["id"]: q for q in bank}
for qid in IDS:
    q = by_id.get(qid)
    print("=" * 78)
    if not q:
        print("NOT FOUND", qid)
        continue
    print(qid, "|", q.get("type"))
    print("-- answerText repr --")
    print(repr(q.get("answerText") or ""))
    print("-- points repr --")
    for i, p in enumerate(q.get("points") or []):
        text = p.get("text") if isinstance(p, dict) else str(p)
        print("  [%d] %s" % (i + 1, repr(text)))
    print()
