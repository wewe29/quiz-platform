# -*- coding: utf-8 -*-
"""按 id 打印题库单题详情，用于定点排查核验失败项。

用法：
    python tools/show_q.py q-110 q-051
    python tools/show_q.py --dup          # 列出疑似重复题干
"""
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(errors="replace")
    except Exception:
        pass

from qa_bank import load_bank  # noqa: E402


def dump(q):
    print("=" * 70)
    print("%s  type=%s  diff=%s  ch=%s  kp=%s" %
          (q["id"], q["type"], q["difficulty"], q["chapter"], q["knowledgePoint"]))
    print("tags:", q["tags"])
    print("source:", q["source"]["text"], "| kind:", q["source"]["kind"])
    print("-- stem --")
    print(q["stem"])
    if q.get("options"):
        for i, o in enumerate(q["options"]):
            print("   %s. %s" % ("ABCDE"[i], o))
    print("answer:", q["answer"])
    if q.get("accept"):
        print("accept:", q["accept"])
    if q.get("answerText"):
        print("-- answerText --")
        print(q["answerText"])
    if q.get("points"):
        print("-- points --")
        for p in q["points"]:
            print("   -", p["text"])
    print("-- explanation --")
    print(q["explanation"])
    if q.get("misconception"):
        print("-- misconception --")
        print(q["misconception"])
    if q.get("extension"):
        print("-- extension --")
        print(q["extension"])
    if q.get("verify"):
        print("-- verify --")
        for v in q["verify"]:
            print("   %s | code=%s | expected=%r" % (v.get("desc"), v.get("code"), v.get("expected")))


def main():
    args = sys.argv[1:]
    qs = load_bank()
    by_id = {q["id"]: q for q in qs}
    if "--dup" in args:
        buckets = defaultdict(list)
        for q in qs:
            buckets[(q["stem"] or "").strip()[:60]].append(q["id"])
        found = False
        for k, v in buckets.items():
            if len(v) > 1:
                found = True
                print("重复:", v, "|", k[:70])
        if not found:
            print("无重复题干（前 60 字口径）")
        return 0
    if "--list" in args:
        ch = None
        ty = None
        for a in args:
            if a.startswith("--chapter="):
                ch = int(a.split("=", 1)[1])
            if a.startswith("--type="):
                ty = a.split("=", 1)[1]
        for q in qs:
            if ch and q["chapter"] != ch:
                continue
            if ty and q["type"] != ty:
                continue
            print("%s  %-6s %-6s ch%d %s  answer=%s" %
                  (q["id"], q["type"], q["difficulty"], q["chapter"],
                   q["knowledgePoint"], q["answer"]))
            print("     ", (q["stem"] or "").replace("\n", " ")[:110])
        return 0
    for a in args:
        if a in by_id:
            dump(by_id[a])
        else:
            print("找不到 %s" % a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
