# -*- coding: utf-8 -*-
r"""采分点切分 —— 高考 / 考研 / 自考三套建库脚本共用。

**为什么单独抽出来**：三套脚本各自复制了一份 `make_points`，都带同一个缺陷——
步骤数不够时用 `pts.append(pts[-1])` 复制上一段来凑数，结果 950 道主观题里
有 586 道的采分点完全重复。重复的采分点会让「采分点自评」变成假选择：
学生勾一个就等于勾了四个。

**纪律**（宁可少收不可收错）：
  · 绝不复制同一段来凑数——点不够就少给点
  · 绝不把 `$$` 这类空壳当采分点
  · 绝不把别的题目的内容并进来
  · 切分只依据源卷面自己的结构（步骤标记 / 空行 / 句末标点），不臆造

用法：
    from points import make_points
    pts = make_points(solution_text, n=6)
"""
import re

# ---------------------------------------------------------------- 显示公式保护
DISPLAY_RE = re.compile(r"\$\$.*?\$\$", re.S)

# ---------------------------------------------------------------- 步骤头
# 源卷面里出现过的步骤标记：
#   高考 Typst：行首 "解：" / "(1)" / "1."
#   考研：行首 "（1）" / "（Ⅰ）" / "（I）" / "第1步："
#   自考：**第1步：…**
HEAD_RE = re.compile(
    r"(?:^|\n)[ \t]*"
    r"(?:"
    r"\*\*第[一二三四五六七八九十\d]+步[：:][ \t]*\*\*"
    r"|第[一二三四五六七八九十\d]+步[：:]"
    r"|\(\d{1,2}\)(?!\d)"
    r"|（(?:[IVXivx]{1,3}|[Ⅰ-Ⅻ]{1,3}|\d{1,2})）(?!\d)"
    r"|\d{1,2}[.、)）](?!\d)"
    r"|解[：:]"
    r")",
    re.M)

# 句子切分：先按空行，再按句末标点
SENT_SPLIT = re.compile(r"(?<=[。；！？])")


def _mask_display(text):
    """把 $$…$$ 整块换成占位符，免得被空行切成碎片。"""
    disp = []

    def _sub(m):
        disp.append(m.group(0))
        return "\x00D%d\x00" % (len(disp) - 1)

    return DISPLAY_RE.sub(_sub, text or ""), disp


def _restore(s, disp):
    if not disp:
        return s
    return re.sub(r"\x00D(\d+)\x00", lambda m: disp[int(m.group(1))], s)


def split_steps(text):
    """把解析正文切成「有意义的步骤」。

    有显式步骤标记时，每一步 = 从该标记到下一个标记之间的全部正文
    （多行内容不会被截断）；没有标记时，按空行分段。
    """
    text = (text or "").strip()
    if not text:
        return []
    masked, disp = _mask_display(text)
    masked = re.sub(r"\*\*", "", masked)

    heads = list(HEAD_RE.finditer(masked))
    steps = []
    if heads:
        pre = masked[:heads[0].start()].strip()
        if pre:
            steps.append(pre)
        for i, m in enumerate(heads):
            start = m.end()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(masked)
            body = masked[start:end].strip()
            if body:
                steps.append(body)
    else:
        steps = [b.strip() for b in re.split(r"\n\s*\n", masked) if b.strip()]

    out = []
    for s in steps:
        s = _restore(s, disp).strip()
        if not s:
            continue
        # 空壳：只有 $$ 或只有空白
        if re.fullmatch(r"\$\$(\s*)\$\$", s):
            continue
        out.append(s)
    return out


def _split_pieces(text):
    """把一段拆成更小的片：先按空行，再按句末标点。"""
    parts = []
    for blk in re.split(r"\n\s*\n", text):
        blk = blk.strip()
        if not blk:
            continue
        sents = [s.strip() for s in SENT_SPLIT.split(blk) if s.strip()]
        parts.extend(sents if sents else [blk])
    return parts


def make_points(text, n=6):
    """从解析正文生成采分点（最多 n 个）。

    · 步骤数多于 n：把尾部合并进最后一点，不丢内容
    · 步骤数少于 n：从最长的一段里继续拆（按空行 → 句末标点）
    · 任何情况下都不复制、不填空壳
    """
    steps = split_steps(text)
    if not steps:
        return []

    guard = 0
    while len(steps) < n and guard < 80:
        guard += 1
        idx = max(range(len(steps)), key=lambda i: len(steps[i]))
        pieces = _split_pieces(steps[idx])
        if len(pieces) < 2:
            break
        steps[idx:idx + 1] = pieces

    seen = set()
    uniq = []
    for s in steps:
        k = s.strip()
        if not k or k in seen:
            continue
        seen.add(k)
        uniq.append(k)

    if len(uniq) > n:
        uniq = uniq[:n - 1] + ["；".join(uniq[n - 1:])]
    return uniq


# ---------------------------------------------------------------- LaTeX 感知检查
DELIM_RE = re.compile(r"\\(?:left|right)\s*[\{\}\(\).]")


def latex_braces_unbalanced(text):
    """LaTeX 感知的花括号配对检查。

    朴素 `count("{") != count("}")` 会把
        $\\left\\{ \\begin{array}{ll} … \\end{array} \\right.$
    判成「不配对」——`\\left\\{` 由 `\\right.` 闭合，源码里本来就少一个 `}`。
    这里把定界符指令（\\left. / \\right{ 等）与转义字面量（\\{ \\}）排除后再数。
    """
    s = DELIM_RE.sub("", text or "")
    depth = 0
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2          # 跳过转义序列（\{ \} \\ \, …）
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return True
        i += 1
    return depth != 0


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    demo = ("（I）由 $\\left\\{ \\begin{array}{l} z = \\sqrt{x^2 + y^2}, \\\\ z^2 = 2x, "
            "\\end{array} \\right.$ 得 $x^2 + y^2 = 2x$\n"
            "故 $C$ 在 $xOy$ 平面上的投影曲线为 $L:\\left\\{ … \\right.$\n\n"
            "（Ⅱ） $M = \\iint_{S} 9\\sqrt{x^2 + y^2 + z^2} \\, \\mathrm{d}S$\n\n"
            "由 $z_x' = \\frac{x}{\\sqrt{x^2+y^2}}$ 得 $\\mathrm{d}S = \\sqrt{2}\\mathrm{d}x\\mathrm{d}y$")
    for i, p in enumerate(make_points(demo)):
        print("[%d] %s" % (i + 1, p))
    print("花括号不配对（LaTeX 感知）：", latex_braces_unbalanced(demo))
