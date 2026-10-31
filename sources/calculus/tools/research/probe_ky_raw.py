# -*- coding: utf-8 -*-
"""原样打印考研 solutions 文件里「以括号数字开头」的行（repr），确认块起始的实际写法。

用法: python research/probe_ky_raw.py 2018
"""
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache", "TsekaLuk_Kaoyan-Math1-Papers.zip")
year = sys.argv[1] if len(sys.argv) > 1 else "2018"

z = zipfile.ZipFile(CACHE)
names = [n for n in z.namelist() if n.endswith("%s年解析.md" % year)]
name = names[0]
text = z.read(name).decode("utf-8", "replace")
lines = text.split("\n")
print("文件:", name, "行数", len(lines))
for i, ln in enumerate(lines):
    if re.match(r"^\s*[（(]\s*\d", ln):
        print("L%-4d %s" % (i + 1, repr(ln[:110])))
