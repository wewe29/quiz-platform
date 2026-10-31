# -*- coding: utf-8 -*-
r"""按丢弃原因分组查看样本。"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

REASON = sys.argv[1] if len(sys.argv) > 1 else "无法归入高等数学知识点"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
PATH = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "_drops.jsonl")


def main():
    rows = [json.loads(l) for l in open(PATH, encoding="utf-8")]
    sel = [r for r in rows if r["reason"] == REASON]
    print("### %s —— 共 %d 条" % (REASON, len(sel)))
    for r in sel[:N]:
        print("-" * 72)
        print("[%d] %s 第%s题 ｜ 分节 %s ｜ 结构判定 %s" % (
            r["year"], r["base"], r["num"], r["section"], r["kind"]))
        print("题干：%s" % r["stem"][:300].replace("\n", " ⏎ "))
        if r["options"]:
            print("选项：%s" % " | ".join(o[:60] for o in r["options"]))
        print("答案：%r" % r["answer"][:80])
        print("解析：%s" % r["solution"][:240].replace("\n", " ⏎ "))


if __name__ == "__main__":
    raise SystemExit(main())
