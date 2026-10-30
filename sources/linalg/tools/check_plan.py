# -*- coding: utf-8 -*-
"""实际题库 vs 原批准计划（500 题口径）逐格比对。

计划值存在 research/plan500.py（只作参照，不参与构建门禁）；
实际值从当前题库现算。两边对不上时逐格列出差值，用来判断是「计划算错了」
还是「题写歪了」。

用法：
    python tools/check_plan.py            # 比对并打印差异
    python tools/check_plan.py --quiet    # 只输出结论行
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "research"))

from qa_bank import load_bank  # noqa: E402
import plan500  # noqa: E402


def main():
    quiet = "--quiet" in sys.argv
    qs = load_bank()
    total = len(qs)

    c_type = Counter(q["typeGroup"] for q in qs)
    c_diff = Counter(q["difficulty"] for q in qs)
    c_ch = Counter(q["chapter"] for q in qs)
    cell = Counter((q["typeGroup"], q["chapter"]) for q in qs)

    diffs = []

    if total != plan500.TOTAL:
        diffs.append("总题数：实际 %d，计划 %d" % (total, plan500.TOTAL))

    for t in sorted(plan500.TYPE_N):
        got, want = c_type.get(t, 0), plan500.TYPE_N[t]
        if got != want:
            diffs.append("题型 %s：实际 %d，计划 %d" % (t, got, want))

    for ch in sorted(plan500.CHAPTER_N):
        got, want = c_ch.get(ch, 0), plan500.CHAPTER_N[ch]
        if got != want:
            diffs.append("章节 %d：实际 %d，计划 %d" % (ch, got, want))

    for d in sorted(plan500.DIFF_N):
        got, want = c_diff.get(d, 0), plan500.DIFF_N[d]
        if got != want:
            diffs.append("难度 %s：实际 %d，计划 %d" % (d, got, want))

    ncell = 0
    for t, row in plan500.MATRIX.items():
        for ch, want in row.items():
            got = cell.get((t, ch), 0)
            if got != want:
                ncell += 1
                diffs.append("矩阵 %s×ch%d：实际 %d，计划 %d" % (t, ch, got, want))

    if not quiet:
        print("=" * 72)
        print("实际题数：%d" % total)
        print("题型分布：%s" % dict(sorted(c_type.items())))
        print("难度分布：%s" % dict(sorted(c_diff.items())))
        print("章节分布：%s" % dict(sorted(c_ch.items())))
        print("-" * 72)
        if diffs:
            print("与计划不符 %d 处：" % len(diffs))
            for d in diffs:
                print("  ⚠ " + d)
        else:
            print("与计划逐格一致 ✅")
    else:
        print("计划比对：%d 处不符" % len(diffs))
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
