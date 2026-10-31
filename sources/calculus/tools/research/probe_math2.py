# -*- coding: utf-8 -*-
"""探查考研数学二仓库：解析文件里有没有题干、papers 是 PDF 还是 Markdown。

用法: python research/probe_math2.py
"""
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
Z = os.path.join(CACHE, "TsekaLuk_Kaoyan-Math2-Papers.zip")

z = zipfile.ZipFile(Z)
ns = z.namelist()
print("entries:", len(ns))
ext = {}
for n in ns:
    e = os.path.splitext(n)[1].lower() or "(dir)"
    ext[e] = ext.get(e, 0) + 1
print("按扩展名:", ext)
print()
print("papers/ 下的文件（按年份目录）:")
pdirs = sorted({n.split("/")[2] for n in ns if n.startswith("Kaoyan-Math2-Papers-main/papers/") and n.count("/") > 3})
print("   ", pdirs)

target = "Kaoyan-Math2-Papers-main/solutions/math2_1987-2019/math2_1987-2019.md"
text = z.read(target).decode("utf-8", "replace")
print("\n=== %s  长度 %d ===" % (target, len(text)))
lines = text.split("\n")
print("行数:", len(lines))
print("--- 前 60 行 ---")
for i, ln in enumerate(lines[:60]):
    print("L%-4d %s" % (i + 1, ln[:150]))
print("--- 标题行 ---")
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("#"):
        print("L%-4d %s" % (i + 1, ln[:110]))
print("--- 块起始标记抽样 ---")
cnt = 0
for i, ln in enumerate(lines):
    if re.match(r"^\s*[\(（]\s*\d{1,2}\s*[\)）]", ln):
        print("L%-4d %s" % (i + 1, ln[:120]))
        cnt += 1
        if cnt > 30:
            break
print("带题块标记的行数(抽样上限30):", cnt)
