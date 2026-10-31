# -*- coding: utf-8 -*-
"""题库结构盘点脚本（ASCII 输出，避免 Windows 控制台编码问题）。

用法：python tools/tally.py [ch1 ch2 ...]
"""
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ORDER = ["single", "multi", "judge", "blank", "short", "calc"]
DIFFS = ["basic", "medium", "hard"]


def tally(chapters):
    from qa_bank import common
    grand_total = 0
    grand_diff = Counter()
    grand_type = Counter()
    grand_cell = defaultdict(Counter)
    for name in chapters:
        mod = __import__("qa_bank." + name, fromlist=["Q"])
        qs = mod.Q
        grand_total += len(qs)
        cell = defaultdict(Counter)
        for q in qs:
            cell[q["typeGroup"]][q["difficulty"]] += 1
            grand_cell[q["typeGroup"]][q["difficulty"]] += 1
            grand_diff[q["difficulty"]] += 1
            grand_type[q["typeGroup"]] += 1
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
    return grand_total


if __name__ == "__main__":
    names = sys.argv[1:] or ["ch1"]
    tally(names)
