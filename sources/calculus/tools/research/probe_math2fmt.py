# -*- coding: utf-8 -*-
"""抽样打印考研数学二解析文件的原始行，用于设计解析器。

用法: python research/probe_math2fmt.py 2007 [起行] [行数]
"""
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
Z = os.path.join(HERE, "_cache", "TsekaLuk_Kaoyan-Math2-Papers.zip")

z = zipfile.ZipFile(Z)
names = z.namelist()
CN = "一二三四五六七八九"
YEAR_CN = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "零": 0,
}


def cn2int(s):
    """四字中文年号（二〇〇七 / 一九八七）→ int。"""
    s = s.strip().replace("〇", "零")
    if len(s) != 4:
        return None
    digits = []
    for ch in s:
        if ch not in YEAR_CN:
            return None
        digits.append(YEAR_CN[ch])
    return digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]


year = sys.argv[1] if len(sys.argv) > 1 else "2007"
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
count = int(sys.argv[3]) if len(sys.argv) > 3 else 40

# 1987-2019 合并文件里按年份标题切；2020+ 单独文件
target = None
text = None
for n in names:
    if n.endswith(".md") and "/solutions/" in n:
        if year == "2020" and "2020" in n:
            target, text = n, z.read(n).decode("utf-8", "replace")
            break
big = [n for n in names if n.endswith("math2_1987-2019.md")]
if text is None and big:
    n = big[0]
    t = z.read(n).decode("utf-8", "replace")
    lines = t.split("\n")
    idx = None
    for i, ln in enumerate(lines):
        m = re.match(r"^#\s*([〇零一二三四五六七八九]{4})年考研数学试卷([二三一])解答\s*$", ln)
        if m and cn2int(m.group(1)) == int(year):
            idx = i
            break
    if idx is None:
        print("未找到年份标题")
        raise SystemExit(1)
    print("年份标题在 L%d" % (idx + 1))
    lines = lines[idx:]
    text = "\n".join(lines)
    target = n + " @" + year

print("源:", target)
out = text.split("\n")
for i, ln in enumerate(out[start:start + count], start=start):
    print("L%-4d %s" % (i, ln[:220]))
