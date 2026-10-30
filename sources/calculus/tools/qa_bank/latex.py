# -*- coding: utf-8 -*-
r"""LaTeX 排版瑕疵修复（只动排版，不动内容）。

真题源是 PDF / Typst 转写来的 LaTeX，偶有**纯排版层面的瑕疵**——
数学含义没变，但 KaTeX 渲染不了。当前已知的一类：

    \Bigg{|}_{0}^{\frac{\pi}{4}}      ← 源卷面把定界符的「参数」也套上了花括号
    \Bigg|_{0}^{\frac{\pi}{4}}        ← 同一批卷面里的另一种写法，KaTeX 能渲染

`\Bigg{|}` 与 `\Bigg|` 表示的是**同一个**定界符，去掉这对多余的花括号
不改变任何数学内容，只是还原成 KaTeX 认的写法。

纪律：这里**只允许**做「去掉定界符参数外层花括号」这一种改写；
任何会改变公式含义的修补都不在这里做——公式真的坏了就整题丢弃，
由 `check_latex.py` 门禁和 `_latex_bad_ids.json` 黑名单兜底。
"""
import re

# \Big / \Bigg 之类的「有尺寸的定界符」，参数被花括号包住，且参数本身
# 只是一个定界符字符（| ( ) [ ] . /）。
DELIM_BRACE_RE = re.compile(
    r"\\(Big|Bigg|Biggl|Biggm|Bigr|Bigl|big|bigg)\s*\{\s*([|()\[\]./])\s*\}(\s*[_^])")


def fix_delims(text):
    """把 `\\Bigg{|}_{a}` 还原成 `\\Bigg|_{a}`。"""
    if not text:
        return text
    return DELIM_BRACE_RE.sub(lambda m: "\\%s%s%s" % (m.group(1), m.group(2), m.group(3)), text)


def fix_structure(text):
    """题库里所有会被 KaTeX 渲染的文本字段统一过一遍修复。"""
    return fix_delims(text)
