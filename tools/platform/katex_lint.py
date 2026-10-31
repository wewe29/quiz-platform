# -*- coding: utf-8 -*-
"""KaTeX 严格模式体检：找出「数学模式里塞了裸中文」以及「LaTeX 转义被吃成控制字符」。

为什么要有这个门禁
------------------
KaTeX 在 strict 模式下对「数学模式里的裸中文」会打 `unicodeTextInMathMode` 警告，
控制台立刻变脏——而本站的验收基线是**子站与门户控制台 0 error / 0 warning**。

真实踩坑记录（2026-10-31，概率论与数理统计并入时）：

1. 解析里写成 `$P(阳)=...$`、`$P(病|阳)=...$`——中文直接躺在数学模式里，
   KaTeX 每次渲染都报 `unicodeTextInMathMode: Unicode text character "阳" used in math mode`。
   正确写法：`$P(\\text{阳})=...$`、`$P(\\text{病}\\mid\\text{阳})=...$`。

2. 更隐蔽的一种：在 **Python 源码**里写 `"$P(\\text{阳})=...$"`（反斜杠只写一个），
   Python 会把 `\\t` 解析成 **TAB**，`\text` 变成「制表符 + ext」——
   页面照样渲染，但公式里凭空多一个空白，且 KaTeX 仍报警。
   源码里 LaTeX 的反斜杠必须**双写**。

本模块只做**静态扫描**（不依赖浏览器），产出问题清单，交给调用方决定是警告还是阻断。

判据口径
--------
* 只看**真正处于数学模式**的片段：按 `$...$` / `$$...$$` **顺序配对**解析。
  非配对的正则会把「两个数学段之间的散文」误判成数学段——
  2026-10-31 就用错方法误报过线代的 `「$N$ 的列都是齐次方程 $(A-E)y=0$」`。
* `\\text{}` / `\\mathrm{}` 等**显式文本命令**里的中文不算问题（KaTeX 支持）。
* 中日韩标点（，。、）在数学模式里**不触发** KaTeX 警告，不算问题。
"""
import re

CJK_IDEOGRAPH = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\u3005\u3007]")
CJK_PUNCT = re.compile(r"[\u3000-\u303f\uff00-\uffef]")
TEXT_COMMAND = re.compile(r"\\(?:text|mathrm|mathbf|mathbb|textit|textbf|textrm|operatorname|mbox|mathsf|mathtt)\s*\{")


def math_segments(text):
    """按顺序配对解析 `$...$` 与 `$$...$$`，返回数学模式内的原文片段列表。

    必须是顺序配对而不是非贪婪正则：只有顺序配对才能正确区分
    「数学段」与「两个数学段之间的散文」。
    """
    segs = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            i += 2                      # 跳过转义符与其后一个字符
            continue
        if text.startswith("$$", i):
            j = text.find("$$", i + 2)
            if j < 0:
                break
            segs.append(text[i + 2:j])
            i = j + 2
            continue
        if ch == "$":
            j = i + 1
            buf = []
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                if text[j] == "$":
                    break
                buf.append(text[j])
                j += 1
            if j < n:
                segs.append("".join(buf))
                i = j + 1
                continue
            i += 1
            continue
        i += 1
    return segs


def strip_text_commands(seg):
    """去掉 \\text{...} 之类显式文本命令及其内容。"""
    out = []
    i = 0
    n = len(seg)
    while i < n:
        m = TEXT_COMMAND.match(seg, i)
        if m:
            depth = 0
            j = m.end() - 1
            while j < n:
                if seg[j] == "{":
                    depth += 1
                elif seg[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            i = j + 1
            continue
        out.append(seg[i])
        i += 1
    return "".join(out)


def scan_math(text):
    """返回 (问题类型, 片段) 列表；问题类型 ∈ {cjk_in_math, control_char}。

    control_char 只认 **除 \\n / \\r 以外**的 C0 控制符：
    多行显示公式（`$$...$$` 里带换行）是正常写法，不能误杀；
    而 TAB 几乎总是 `\\text` 少写一个反斜杠被 Python 解析出来的残留。
    """
    problems = []
    for seg in math_segments(text):
        bad = [c for c in seg if (ord(c) < 0x20 and c not in "\n\r") or ord(c) == 0x7f]
        if bad:
            problems.append(("control_char", seg))
        bare = strip_text_commands(seg)
        if CJK_IDEOGRAPH.search(bare):
            problems.append(("cjk_in_math", seg))
    return problems


def scan_value(value):
    """递归扫描任意 JSON 值，返回 [(路径, 类型, 片段)]。"""
    found = []
    if isinstance(value, str):
        for kind, seg in scan_math(value):
            found.append(("", kind, seg))
    elif isinstance(value, dict):
        for k, v in value.items():
            for path, kind, seg in scan_value(v):
                found.append((("%s.%s" % (path, k) if path else str(k)), kind, seg))
    elif isinstance(value, list):
        for idx, v in enumerate(value):
            for path, kind, seg in scan_value(v):
                found.append(("%s[%d]" % (path, idx) if path else "[%d]" % idx, kind, seg))
    return found


def is_cjk_punct_only(seg):
    """整段只有中日韩标点（KaTeX 不报警）→ True。"""
    rest = strip_text_commands(seg)
    rest = CJK_PUNCT.sub("", rest)
    return not CJK_IDEOGRAPH.search(rest)


if __name__ == "__main__":
    import sys
    src = sys.stdin.read()
    probs = scan_math(src)
    if not probs:
        print("OK")
    for kind, seg in probs:
        print("[%s] %r" % (kind, seg))
    sys.exit(1 if probs else 0)
