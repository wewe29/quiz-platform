# -*- coding: utf-8 -*-
r"""导出当前题库的全部题干，作为**去重基线**。

用法：
    python tools\export_stems.py                 # 写入 tools\research\existing_stems.txt
    python tools\export_stems.py --check         # 只比对，不写文件；基线过期时退出码 1

背景（真实踩过的坑）：
    `existing_stems.txt` 最早只是 180 题基础库的一次性快照，
    `check_new.py` 的 S4/B5 去重只拿它当「已出过的题干」基准。
    题库扩到 500 题后，这个基准仍停在 180 题 ——
    **新章的 320 道题彼此之间、以及与基础库之间，没有进基准**，
    下一章再写题时可能重复出已经在库的题。

    而且基准是对着**运行时题干值**存的（含 LaTeX 反斜杠），
    手改一个字就与运行时键对不上——曾经就有一道基础题改过题干后没同步基准，
    导致 180 条基准里失效 1 条（键对不上，去重对它失效）。
    所以基准**只能由本脚本从题库重新生成，不要手写**。

格式：``题号 | 模块 | 题型 | 题干``（一行一题；题干里的换行折成空格）

为什么要带「模块」这一列：
    1. 题号会随章节增删整体重排（加一章，后面的题号全变），
       光靠题号认不出「这条基准是不是本章自己的题」——曾经就因为这个，
       把本章的每一道题都误报成「与 q-xxx 重复」。
    2. 题干里带 | 的绝对值记号必须原样保留，所以分隔用 ``split("|", 3)``。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "research", "existing_stems.txt")

# 必须与 qa_bank.common.load_bank 的装载顺序一致：
# 题号由 common.py 里的全局计数器按**导入顺序**分配，顺序不同 → 题号不同。
ORDER = ["ch1", "ch1b", "ch2", "ch2b", "ch3", "ch3b",
         "ch4", "ch4b", "ch5", "ch5b", "ch6", "ch6b"]


def collect():
    """按 ORDER 逐个导入模块，返回 (模块名, 题目列表) 序列。

    直接 import 各模块（而不是 load_bank）才能知道每道题属于哪个模块；
    导入顺序与 load_bank 保持一致，题号才与库内一致。
    """
    out = []
    for name in ORDER:
        try:
            mod = __import__("qa_bank." + name, fromlist=["Q"])
        except ImportError:
            continue
        out.append((name, mod.Q))
    return out


def render_all(mods):
    lines = []
    for name, qs in mods:
        for q in qs:
            stem = (q.get("stem") or "").strip().replace("\r", " ").replace("\n", " ")
            lines.append("%s | %s | %s | %s" % (q["id"], name, q.get("type", ""), stem))
    return lines


def read_base(path):
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def main():
    mods = collect()
    lines = render_all(mods)
    total = sum(len(qs) for _, qs in mods)
    print("[export] 当前题库 %d 题（%d 个模块）" % (total, len(mods)))

    if "--check" in sys.argv:
        old = read_base(OUT)
        oldset = set(old)
        newset = set(lines)
        missing = newset - oldset
        extra = oldset - newset
        if missing or extra:
            print("[export] 基准已过期：新增 %d 条、失效 %d 条"
                  % (len(missing), len(extra)))
            for ln in list(missing)[:5]:
                print("  [新增] %s" % ln[:80])
            for ln in list(extra)[:5]:
                print("  [失效] %s" % ln[:80])
            print("[export] 修法：python tools\\export_stems.py")
            return 1
        print("[export] 基准与题库一致（%d 条）" % len(newset))
        return 0

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("[export] 已写入 %s（%d 条）" % (OUT, len(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
