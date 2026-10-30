# -*- coding: utf-8 -*-
"""题库结构盘点脚本（ASCII 输出，避免 Windows 控制台编码问题）。

用法：
    python tools/tally.py                    # 盘点全部已存在的章节
    python tools/tally.py ch1 ch2            # 只盘点指定章节
    python tools/tally.py --emit-target      # 额外打印可直接粘贴进 qa_bank/target.py 的口径块

为什么要有 --emit-target：
    题库口径（题量/题型配额/难度配额/章节配额/题型×章节矩阵/答案位置阈值）
    只写在 qa_bank/target.py 一个地方。题库一变，这个文件就与实际对不上，
    构建门禁会拦下（这是好事）。更新口径不该靠手抄数字——用本命令生成，
    粘贴即可，避免「抄错一个数，全站文案跟着错」。
"""
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ORDER = ["single", "multi", "judge", "blank", "short", "calc"]
DIFFS = ["basic", "medium", "hard"]
BASE_CHAPTERS = ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6"]
EXTRA_CHAPTERS = ["ch1b", "ch2b", "ch3b", "ch4b", "ch5b", "ch6b"]


def existing_chapters():
    """列出实际存在的章节模块（有 b 扩展的一并带上）。"""
    out = []
    for name in BASE_CHAPTERS + EXTRA_CHAPTERS:
        if os.path.exists(os.path.join(HERE, "qa_bank", name + ".py")):
            out.append(name)
    return out


def load(chapters):
    allq = []
    for name in chapters:
        try:
            mod = __import__("qa_bank." + name, fromlist=["Q"])
        except ImportError:
            print("[tally] 跳过缺失章节：%s" % name)
            continue
        allq.extend(mod.Q)
    return allq


def tally(chapters, questions):
    grand_total = len(questions)
    grand_diff = Counter()
    grand_type = Counter()
    grand_cell = defaultdict(Counter)
    by_ch = Counter()
    for name in chapters:
        qs = [q for q in questions if q.get("_mod") == name]
        if not qs:
            continue
        cell = defaultdict(Counter)
        for q in qs:
            cell[q["typeGroup"]][q["difficulty"]] += 1
            grand_cell[q["typeGroup"]][q["difficulty"]] += 1
            grand_diff[q["difficulty"]] += 1
            grand_type[q["typeGroup"]] += 1
            by_ch[q["chapter"]] += 1
        print("== %s : total=%d" % (name, len(qs)))
        chd = Counter()
        for t in ORDER:
            c = cell.get(t, Counter())
            chd.update(c)
            print("   %-7s n=%2d  b=%2d m=%2d h=%2d"
                  % (t, sum(c.values()), c["basic"], c["medium"], c["hard"]))
        print("   DIFF      b=%2d m=%2d h=%2d  (sum=%d)"
              % (chd["basic"], chd["medium"], chd["hard"], sum(chd.values())))
        kps = sorted(set(q["knowledgePoint"] for q in qs))
        print("   KP       %s" % ",".join(kps))
    print("")
    print("GRAND total=%d" % grand_total)
    for t in ORDER:
        c = grand_cell.get(t, Counter())
        print("   %-7s n=%2d  b=%2d m=%2d h=%2d"
              % (t, sum(c.values()), c["basic"], c["medium"], c["hard"]))
    print("   DIFF      b=%2d m=%2d h=%2d"
          % (grand_diff["basic"], grand_diff["medium"], grand_diff["hard"]))
    print("   CHAPTER  %s" % dict(sorted(by_ch.items())))


def emit_target(questions):
    """打印可直接粘贴进 qa_bank/target.py 的口径块。"""
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    cell = Counter((q["typeGroup"], q["chapter"]) for q in questions)
    single = Counter(q["answer"][0] for q in questions if q["type"] == "single")
    multi = Counter()
    for q in questions:
        if q["type"] == "multi":
            for a in q["answer"]:
                multi[a] += 1

    # 阈值按题量推导，不写死：
    #   单选：每档围绕期望值 N/4 上下浮动 ±35%
    #   多选：四档极差 ≤ 平均每档字母数的 55%
    ns = c_type.get("single", 0)
    exp_s = ns / 4.0
    s_lo = max(1, int(math.floor(exp_s * 0.65)))
    s_hi = int(math.ceil(exp_s * 1.35))
    m_letters = sum(multi.values())
    exp_m = m_letters / 4.0 if m_letters else 1
    m_range = max(1, int(math.floor(exp_m * 0.55)))

    print("")
    print("=" * 72)
    print("以下整段粘贴到 tools/qa_bank/target.py（替换对应常量）：")
    print("=" * 72)
    print("TOTAL = %d" % len(questions))
    print("BY_TYPE = {")
    for t in ORDER:
        print('    "%s": %d,' % (t, c_type.get(t, 0)))
    print("}")
    print("BY_DIFFICULTY = {")
    for d in DIFFS:
        print('    "%s": %d,' % (d, c_diff.get(d, 0)))
    print("}")
    print("BY_CHAPTER = {")
    for ch in sorted(c_ch):
        print("    %d: %d," % (ch, c_ch[ch]))
    print("}")
    print("MATRIX = {")
    for t in ORDER:
        cells = {ch: cell[(t, ch)] for ch in sorted(c_ch)}
        print('    "%s": {%s},' % (t, ", ".join("%d: %d" % (c, cells[c]) for c in cells)))
    print("}")
    print("SINGLE_LETTER_MIN = %d" % s_lo)
    print("SINGLE_LETTER_MAX = %d" % s_hi)
    print("MULTI_LETTER_RANGE = %d" % m_range)
    print("")
    print("# 实测：单选答案位置 %s" % dict(sorted(single.items())))
    print("# 实测：多选答案字母 %s" % dict(sorted(multi.items())))
    print("# 推导依据：单选每档期望 N/4=%.2f，容差 ±35%%；多选极差 ≤ 平均每档 %.2f 的 55%%"
          % (exp_s, exp_m))


def main():
    args = sys.argv[1:]
    emit = "--emit-target" in args
    names = [a for a in args if not a.startswith("-")]
    if not names:
        names = existing_chapters()
    questions = load(names)
    for name in names:
        try:
            mod = __import__("qa_bank." + name, fromlist=["Q"])
        except ImportError:
            continue
        for q in mod.Q:
            q["_mod"] = name
    tally(names, questions)
    if emit:
        emit_target(questions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
