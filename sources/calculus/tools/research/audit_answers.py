# -*- coding: utf-8 -*-
r"""真题答案 ↔ 解析交叉核对 + 随机抽检。

对题库里所有 exam-original 题：
  1. 选择题：解析末尾的「故选 X」必须与答案键一致；
  2. 填空题：答案值必须能在解析里找到；
  3. 随机抽样打印，供人工核对题干/选项/答案/解析是否真的对得上。
"""
import collections
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)

from qa_bank import load_bank  # noqa: E402
from typst_extract import choice_from_tail, SOURCE_CONFLICT  # noqa: E402


def tail_choice(sol):
    return choice_from_tail(sol)


def norm_math(s):
    import re
    return re.sub(r"[\s\\{}()$]", "", s or "")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    bank = load_bank()
    exams = [q for q in bank
             if (q.get("provenance") or {}).get("level") == "original"]
    print("真题题量：%d" % len(exams))
    if mode == "check":
        bad = collections.Counter()
        samples = collections.defaultdict(list)
        for q in exams:
            t = q.get("type")
            expl = q.get("explanation") or ""
            if t in ("single", "multi"):
                ans = "".join(q.get("answer") or [])
                tail = tail_choice(expl)
                if tail and set(tail) != set(ans):
                    bad["选择题答案与解析末尾不一致"] += 1
                    if len(samples["choice"]) < 8:
                        samples["choice"].append((q.get("id"), ans, tail,
                                                  (q.get("stem") or "")[:90]))
            elif t == "blank":
                accepts = q.get("accept") or []
                sol = norm_math(expl)
                if accepts and not any(norm_math(a) in sol for a in accepts):
                    bad["填空答案未出现在解析中"] += 1
                    if len(samples["blank"]) < 8:
                        samples["blank"].append((q.get("id"), accepts[:2],
                                                 (q.get("stem") or "")[:90]))
            if SOURCE_CONFLICT.search(expl or ""):
                bad["解析里带源卷面冲突说明"] += 1
        print("交叉核对异常：", dict(bad) or "无")
        for k, rows in samples.items():
            print("== %s ==" % k)
            for r in rows:
                print("   ", r)
        return 0

    # 抽样人工核对
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261028
    random.seed(seed)
    for q in random.sample(exams, min(n, len(exams))):
        print("=" * 74)
        print("id：%s ｜ 题型 %s ｜ 难度 %s ｜ 知识点 %s" % (
            q.get("id"), q.get("type"), q.get("difficulty"), q.get("knowledgePoint")))
        print("来源：%s ｜ %s" % (q.get("source"), (q.get("provenance") or {}).get("url")))
        print("题干：%s" % (q.get("stem") or "")[:400])
        for i, o in enumerate(q.get("options") or []):
            print("   %s) %s" % ("ABCD"[i] if i < 4 else i, str(o)[:160]))
        print("答案：%r" % (q.get("answer"),))
        print("解析：%s" % (q.get("explanation") or "")[:360])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
