# -*- coding: utf-8 -*-
"""全库扫描主观题采分点的质量缺陷。

检查项：
  · 采分点文本重复（同一题里出现完全相同的采分点 = 用复制凑数）
  · 采分点为空 / 只有 $$ 这类空壳
  · 采分点里混入了别的题目的题块标记（考研解析串题）
  · LaTeX 花括号是否配对（朴素计数 vs LaTeX 感知计数）

用法: python research/scan_points.py
"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

from qa_bank import load_bank  # noqa: E402

DELIM_RE = re.compile(r"\\(?:left|right)\s*[\{\}\(\).]")


def naive_unbalanced(t):
    return t.count("{") != t.count("}")


def latex_unbalanced(t):
    """LaTeX 感知的花括号配对检查。"""
    s = DELIM_RE.sub("", t or "")
    depth = 0
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2          # 跳过转义序列（\{ \} \\ \, …）
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return True
        i += 1
    return depth != 0


def main():
    bank = load_bank()
    dup = []
    empty = []
    foreign = []
    naive_only = []
    counts = collections.Counter()
    for q in bank:
        t = q.get("type")
        if t not in ("term", "short", "calc"):
            continue
        pts = q.get("points") or []
        kind = (q.get("source") or {}).get("kind")
        counts[(kind, t, len(pts))] += 1
        texts = [p.get("text") if isinstance(p, dict) else str(p) for p in pts]
        if len(set(x.strip() for x in texts)) != len(texts):
            dup.append(q["id"])
        for i, x in enumerate(texts):
            if not x.strip() or re.fullmatch(r"\$\$(\s*)\$\$", x.strip()):
                empty.append("%s#%d" % (q["id"], i + 1))
            if re.search(r"(?m)^\s*[（(]\s*\d{1,2}\s*[)）]\s*【", x):
                foreign.append("%s#%d" % (q["id"], i + 1))
            if naive_unbalanced(x) and not latex_unbalanced(x):
                naive_only.append("%s#%d" % (q["id"], i + 1))
    print("主观题总数：", sum(1 for q in bank
                           if q.get("type") in ("term", "short", "calc")))
    print("重复采分点：%d 题  %s" % (len(dup), dup[:10]))
    print("空壳采分点：%d 处  %s" % (len(empty), empty[:10]))
    print("含外题块标记：%d 处  %s" % (len(foreign), foreign[:10]))
    print("仅朴素计数判不平衡（LaTeX 感知后正常）：%d 处  %s"
          % (len(naive_only), naive_only[:10]))
    print("\n按 (来源类型, 题型, 采分点数) 分布：")
    for k, v in sorted(counts.items(), key=lambda kv: (str(kv[0]))):
        print("   %-42s %d" % (str(k), v))


if __name__ == "__main__":
    main()
