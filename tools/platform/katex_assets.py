# -*- coding: utf-8 -*-
"""KaTeX 自托管资产：woff2 裁剪 + 拷贝到学科子站。

单文件版把 KaTeX 全部内联（base64），平台版改为自托管目录；
现代浏览器只需要 woff2，woff/ttf 候选源全部裁掉（省约 2MB 传输）。

用法：python tools/platform/katex_assets.py --subject-dir subjects/linalg
源优先级：环境变量 KATEX_DIR > sources/<id>/tools/vendor/katex/dist > 本机 node_modules。
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))

SRC_TRIPLE = re.compile(
    r'url\(fonts/([A-Za-z0-9_\-]+\.woff2)\)\s*format\("woff2"\),'
    r'url\(fonts/[A-Za-z0-9_\-]+\.woff\)\s*format\("woff"\),'
    r'url\(fonts/[A-Za-z0-9_\-]+\.ttf\)\s*format\("truetype"\)')
SRC_SINGLE = re.compile(r'url\(fonts/([A-Za-z0-9_\-]+\.(?:woff2|woff|ttf))\)')


def find_katex_dist(subject_dir):
    env = os.environ.get("KATEX_DIR")
    candidates = []
    if env:
        candidates.append(env)
    # 平台级共享 vendor（一次拷贝，全学科用；CI/异机不依赖本机 node_modules）
    candidates.append(os.path.join(PLATFORM, "tools", "vendor", "katex", "dist"))
    sid = os.path.basename(os.path.normpath(subject_dir))
    candidates.append(os.path.join(PLATFORM, "sources", sid, "tools", "vendor", "katex", "dist"))
    candidates.append(r"D:\workspace\5-docs\exam\数据库\node_modules\katex\dist")
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    raise SystemExit("[katex] 找不到 KaTeX 发行版；设 KATEX_DIR 或在 tools/vendor/katex/dist 放置发行版")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject-dir", required=True, help="subjects/<id> 目录")
    args = ap.parse_args()

    src = find_katex_dist(args.subject_dir)
    dst = os.path.join(args.subject_dir, "assets", "vendor", "katex")
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(dst, "contrib"), exist_ok=True)

    # css：三候选源裁成 woff2-only，字体走相对路径 fonts/
    with open(os.path.join(src, "katex.min.css"), encoding="utf-8") as f:
        css = f.read()
    css, n1 = SRC_TRIPLE.subn(lambda m: 'url(fonts/%s) format("woff2")' % m.group(1), css)
    css, n2 = SRC_SINGLE.subn(lambda m: 'url(fonts/%s)' % m.group(1) if m.group(1).endswith("woff2") else "", css)
    with open(os.path.join(dst, "katex.min.css"), "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

    for name in ("katex.min.js", os.path.join("contrib", "auto-render.min.js")):
        shutil.copy2(os.path.join(src, name), os.path.join(dst, name))

    nfont = 0
    fonts_src = os.path.join(src, "fonts")
    for fn in os.listdir(fonts_src):
        if fn.endswith(".woff2"):
            shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn))
            nfont += 1

    total = 0
    for root, _, files in os.walk(dst):
        for fn in files:
            total += os.path.getsize(os.path.join(root, fn))
    print("[katex] %s：woff2 字体 %d 个，css 裁剪 %d+%d 处，目录合计 %.2f MB"
          % (dst, nfont, n1, n2, total / 1048576.0))


if __name__ == "__main__":
    sys.exit(main())
