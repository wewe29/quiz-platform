# -*- coding: utf-8 -*-
"""扫描题库里「带上下限的大定界符」这类**源卷面就非法**的 LaTeX。

典型形态：`\\Bigg{|}_{0}^{\\frac{\\pi}{2}}` —— 给 \\Bigg 加上下限，
LaTeX/KaTeX 都不允许（KaTeX: Invalid delimiter type 'ordgroup'）。

这类公式是源卷面转写残损，不是我们写错的。修它等于替源卷面重新排版，
所以处置方式是**整题丢弃**，而不是猜一个写法。

用法:
    python research/scan_badelims.py            # 只报告
    python research/scan_badelims.py --blacklist # 追加进 _latex_bad_ids.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank import load_bank  # noqa: E402

MATH = re.compile(r"\$\$(.+?)\$\$|\$([^$]+)\$", re.S)
# 只有「有尺寸的定界符」带上下限才非法：\Bigg{|}_{a}^{b}。
# \left(…\right)^{2}、\left. … \right|_{x=0} 都是合法 LaTeX，不能误伤。
BAD_ELIM = re.compile(
    r"\\(?:Big|Bigg|Biggl|Biggm|Bigr|Bigl|big|bigg)\s*"
    r"(?:\{[^{}]*\}|[\(\)\[\]\|])"
    r"\s*[_^]")


def formulas_of(q):
    out = []
    fields = [q.get("stem") or "", q.get("answerText") or "", q.get("explanation") or "",
              q.get("misconception") or ""]
    fields += list(q.get("options") or [])
    fields += [p.get("text", "") if isinstance(p, dict) else str(p)
               for p in (q.get("points") or [])]
    for f in fields:
        if not f:
            continue
        for m in MATH.finditer(f):
            tex = (m.group(1) or m.group(2) or "").strip()
            if tex:
                out.append(tex)
    return out


def main():
    blacklist = "--blacklist" in sys.argv
    bank = load_bank()
    hits = {}
    for q in bank:
        for tex in formulas_of(q):
            if BAD_ELIM.search(tex):
                hits.setdefault(q["id"], []).append(tex)
                break
    print("含非法定界符的题目：%d 道" % len(hits))
    for qid, texs in list(hits.items())[:20]:
        print("  %-28s %s" % (qid, texs[0][:110].replace("\n", " ")))
    if not blacklist:
        return 0
    path = os.path.join(HERE, "_latex_bad_ids.json")
    cur = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cur = json.load(f)
    merged = sorted(set(cur) | set(hits))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print("已并入黑名单：%d → %d" % (len(cur), len(merged)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
