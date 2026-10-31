# -*- coding: utf-8 -*-
"""统计考研 solutions 文件里的「题块起始标记」词表。

用法: python research/probe_ky_blocks.py 2017
"""
import collections
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache", "TsekaLuk_Kaoyan-Math1-Papers.zip")

if not os.path.exists(CACHE):
    print("缺少缓存 zip:", CACHE)
    raise SystemExit(1)

year = sys.argv[1] if len(sys.argv) > 1 else "2017"
target = "solutions/%s年解析/%s年解析.md" % (year, year)

z = zipfile.ZipFile(CACHE)
names = [n for n in z.namelist() if n.endswith("%s年解析.md" % year)]
print("候选 solutions 文件:")
for n in names:
    print("   ", n)
if not names:
    raise SystemExit(0)

name = target if target in names else names[0]
text = z.read(name).decode("utf-8", "replace")
print("\n使用:", name, "长度", len(text))

lines = text.split("\n")
print("\n--- 所有 '（数字）' 开头的行（前 60 字符）---")
marks = collections.Counter()
for i, ln in enumerate(lines):
    m = re.match(r"^\s*[（(]\s*(\d{1,2})\s*[)）]\s*(.{0,12})", ln)
    if m:
        tail = m.group(2)
        mm = re.match(r"【([^】]{0,6})】", tail)
        marks[mm.group(1) if mm else ("<无标记>" + tail[:6].strip())] += 1
        print("  L%-5d (%s)%s" % (i + 1, m.group(1), ln[:60]))
print("\n--- 标记词表 ---")
for k, v in marks.most_common():
    print("  %-14s %d" % (k, v))

print("\n--- 所有 Markdown 标题 ---")
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("#"):
        print("  L%-5d %s" % (i + 1, ln[:90]))
