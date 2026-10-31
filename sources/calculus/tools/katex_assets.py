# -*- coding: utf-8 -*-
"""KaTeX 资源装配（双后端）。

本机不联网、不装 npm 包，KaTeX 发行版直接从已解压的 node_modules 取：
    D:\\workspace\\5-docs\\exam\\数据库\\node_modules\\katex\\dist

两种后端：
  * inline   —— 单文件离线包：@font-face 的 woff2 转 base64 data URI
  * multifile—— 多文件站点：保留 url(fonts/xxx.woff2) 相对路径，字体另存 fonts/

两种后端都只保留 woff2（现代浏览器全部支持，体积最小），
并把 KaTeX 原本的 woff / ttf 候选源删掉——否则多文件站会引用不存在的字体文件。

用法（脚本）：
    python katex_assets.py --check          # 打印字体清单与自检结果
"""
import base64
import io
import os
import re
import shutil

KATEX_DIR = r"D:\workspace\5-docs\exam\数据库\node_modules\katex\dist"

KATEX_CSS = os.path.join(KATEX_DIR, "katex.min.css")
KATEX_JS = os.path.join(KATEX_DIR, "katex.min.js")
AUTORENDER_JS = os.path.join(KATEX_DIR, "contrib", "auto-render.min.js")
FONTS_DIR = os.path.join(KATEX_DIR, "fonts")

# KaTeX 的 @font-face 里三个候选源的完整形态
SRC3 = re.compile(
    r'url\(fonts/([A-Za-z0-9_\-]+\.woff2)\)\s*format\("woff2"\),'
    r'url\(fonts/[A-Za-z0-9_\-]+\.woff\)\s*format\("woff"\),'
    r'url\(fonts/[A-Za-z0-9_\-]+\.ttf\)\s*format\("truetype"\)')
# 其它形态的单一引用
SRC1 = re.compile(r'url\(fonts/([A-Za-z0-9_\-]+\.(?:woff2|woff|ttf))\)')


class KaTeXError(RuntimeError):
    pass


def read_text(path):
    if not os.path.exists(path):
        raise KaTeXError("KaTeX 文件缺失：%s" % path)
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_fonts():
    """返回 (woff2 文件名列表, 缺失列表)。"""
    if not os.path.isdir(FONTS_DIR):
        raise KaTeXError("KaTeX 字体目录缺失：%s" % FONTS_DIR)
    fonts = sorted(f for f in os.listdir(FONTS_DIR) if f.endswith(".woff2"))
    missing = []
    for f in fonts:
        if not os.path.exists(os.path.join(FONTS_DIR, f)):
            missing.append(f)
    return fonts, missing


def _data_uri(fname):
    path = os.path.join(FONTS_DIR, fname)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return 'url(data:font/woff2;base64,%s) format("woff2")' % b64


def css_inline():
    """单文件后端：把 woff2 转成 base64 data URI。

    返回 (css_text, 内联字体数, 缺失列表)
    """
    css = read_text(KATEX_CSS)
    cache = {}
    missing = []

    def repl(m):
        name = m.group(1)
        if name in cache:
            return cache[name]
        uri = _data_uri(name)
        if uri is None:
            missing.append(name)
            return m.group(0)
        cache[name] = uri
        return uri

    out = SRC3.sub(repl, css)
    out = SRC1.sub(repl, out)
    if missing:
        raise KaTeXError("缺少字体文件：%s" % sorted(set(missing)))
    if re.search(r"url\(\s*fonts/", out):
        raise KaTeXError("仍有未内联的 fonts/ 相对路径")
    return out, len(cache), missing


def css_multifile():
    """多文件后端：只保留 woff2 相对引用。

    返回 (css_text, 需要复制的字体文件名列表)
    """
    css = read_text(KATEX_CSS)
    used = set()

    def repl(m):
        used.add(m.group(1))
        return 'url(fonts/%s) format("woff2")' % m.group(1)

    out = SRC3.sub(repl, css)
    out = SRC1.sub(repl, out)
    fonts = sorted(used)
    have, missing = list_fonts()
    gone = [f for f in fonts if f not in have]
    if gone:
        raise KaTeXError("缺少字体文件：%s" % gone)
    return out, fonts


def copy_fonts(dest_dir):
    """把用到的 woff2 复制到 dest_dir（多文件站用）。返回复制数量。"""
    _, fonts = css_multifile()
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    n = 0
    for f in fonts:
        src = os.path.join(FONTS_DIR, f)
        dst = os.path.join(dest_dir, f)
        shutil.copyfile(src, dst)
        n += 1
    return n


def js_bundle():
    """返回 (katex.min.js, auto-render.min.js)"""
    return read_text(KATEX_JS), read_text(AUTORENDER_JS)


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    css_i, n, _ = css_inline()
    css_m, fonts = css_multifile()
    kjs, ajs = js_bundle()
    print("KaTeX 目录：%s" % KATEX_DIR)
    print("单文件后端：css %d 字符，内联字体 %d 个" % (len(css_i), n))
    print("多文件后端：css %d 字符，需复制字体 %d 个" % (len(css_m), len(fonts)))
    print("katex.min.js %d 字符；auto-render.min.js %d 字符" % (len(kjs), len(ajs)))
    print("字体清单：%s" % ", ".join(fonts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
