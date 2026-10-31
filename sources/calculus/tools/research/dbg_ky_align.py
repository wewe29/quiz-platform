# -*- coding: utf-8 -*-
r"""抽样查看考研对齐校验不通过的题目对。"""
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import build_kaoyan_bank as B  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TYPES = sys.argv[2].split(",") if len(sys.argv) > 2 else ["calc"]

z = zipfile.ZipFile(B.ZIP)
papers, sols = B.find_files(z)
shown = 0
for y in sorted(set(papers) & set(sols)):
    if y < B.MIN_YEAR:
        continue
    if shown >= N:
        break
    pn = sorted(papers[y], key=lambda s: ("及参考答案" in s, "+答案" in s))[0]
    sn = sorted(sols[y])[0]
    pq = B.parse_papers(z.read(pn).decode("utf-8", "replace"))
    sq = B.parse_solutions(z.read(sn).decode("utf-8", "replace"))
    for qt in TYPES:
        P = pq.get(qt) or []
        S = sq.get(qt) or []
        smap = {}
        for b in S:
            if isinstance(b["num"], int) and b["num"] not in smap:
                smap[b["num"]] = b
        pnums = [q["num"] for q in P if isinstance(q["num"], int)]
        snums = [b["num"] for b in S if isinstance(b["num"], int)]
        offset = (min(snums) - min(pnums)) if (pnums and snums) else 0
        used = set()
        for i, q in enumerate(P):
            a = None
            n = q.get("num")
            if isinstance(n, int):
                if n in smap and id(smap[n]) not in used:
                    a = smap[n]
                elif (n + offset) in smap and id(smap[n + offset]) not in used:
                    a = smap[n + offset]
            if a is None:
                for j in range(len(S)):
                    if j not in used:
                        a = S[j]
                        break
            if a is None:
                continue
            used.add(id(a))
            why = B.verify_pair(qt, q, a)
            if why:
                print("=" * 72)
                print("[%d] %s ｜ %s" % (y, qt, why))
                print("题干：%s" % q["stem"][:240].replace("\n", " ⏎ "))
                print("解析：%s" % a["solution"][:240].replace("\n", " ⏎ "))
                toks = B.stem_tokens(q["stem"])
                print("词元：%s" % list(toks)[:8])
                shown += 1
                break
        if shown >= N:
            break
