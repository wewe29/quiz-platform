# -*- coding: utf-8 -*-
r"""新版高考真题 Typst 源 → 纯文本/LaTeX 抽取器。

源仓库 VincentZyuApps/gaokaomath-typst-page 的 **根目录 `papers/` 树**是
排版管线的新版产物：数学已按 LaTeX 书写，放在 Typst 原始字符串里：

    #mi(`x^{2}+y^{2}=2`)        行内公式
    #mitex(`\frac{1}{2}`)       独立成行的公式
    #align(center)[#mitex(...)] 居中块
    #image("/papers/2024/....png")  插图
    #choices([#mi(`1`)], ...)   选项
    #answer([A])                答案
    #solution[...]              解析
    #part-header("单选题")       分节标题（决定题型）

本模块只做**结构还原**（去指令、取原文），不做任何语义改写；
公式原样保留为 LaTeX 片段，外层加 `$…$` / `$$…$$` 交给 KaTeX 渲染。
"""
import re

# 顶层设置类指令：整体丢弃
TOP_CALLS = {"import", "show", "set", "page", "outline", "part-header"}
# 纯排版类指令：保留其内容
WRAP_CALLS = {"align", "emph", "strong", "box", "block"}

IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_\-]*")


class ExtractError(Exception):
    pass


def _skip_ws(s, i):
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    return i


def _match_close(s, i, open_ch, close_ch):
    """s[i] 是开括号，返回配对闭括号下标（找不到返回 -1）。

    跳过字符串字面量与原始字符串（反引号），避免公式里的 [3] 干扰配对。
    """
    depth = 1
    j = i + 1
    n = len(s)
    while j < n:
        c = s[j]
        if c == '"':
            k = j + 1
            while k < n and s[k] != '"':
                k += 2 if s[k] == "\\" else 1
            j = k + 1
            continue
        if c == "`":
            k = j + 1
            while k < n and s[k] != "`":
                k += 1
            j = k + 1
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def _read_raw(s, i):
    """i 指向反引号；读取 Typst 原始字符串，返回 (内容, 新下标)。"""
    n = 0
    while i + n < len(s) and s[i + n] == "`":
        n += 1
    n = min(n, 3)
    fence = "`" * n
    start = i + n
    j = start
    while j < len(s):
        if s[j] == "`":
            run = 0
            k = j
            while k < len(s) and s[k] == "`":
                run += 1
                k += 1
            if run == n:
                return s[start:j], k
            j = k
            continue
        j += 1
    raise ExtractError("未闭合的原始字符串")


class Parser(object):
    """把一段 Typst 片段还原为纯文本（公式保持 LaTeX）。"""

    def __init__(self):
        self.has_image = False
        self.images = []

    def parse(self, s):
        return self._walk(s, 0, len(s))

    # ---------- 主循环 ----------
    def _walk(self, s, i, end):
        out = []
        while i < end:
            c = s[i]
            if c == "#":
                j = _skip_ws(s, i + 1)
                m = IDENT.match(s, j)
                if not m:
                    out.append(c)
                    i += 1
                    continue
                name = m.group(0)
                nxt, txt = self._call(s, name, m.end(), end)
                if nxt is None:
                    out.append(c)
                    i += 1
                    continue
                out.append(txt)
                i = nxt
                continue
            if c == "`":
                try:
                    raw, k = _read_raw(s, i)
                except ExtractError:
                    out.append(c)
                    i += 1
                    continue
                out.append("$%s$" % raw.strip())
                i = k
                continue
            if c == "\\":
                m = re.match(r"\\[A-Za-z]+", s[i:])
                if m:
                    j = i + m.end()
                    # \texfigure[...]{...} / \FloatBarrier 之类，整体丢弃
                    k = _skip_ws(s, j)
                    if k < end and s[k] == "[":
                        k2 = _match_close(s, k, "[", "]")
                        if k2 >= 0:
                            k = _skip_ws(s, k2 + 1)
                    if k < end and s[k] == "{":
                        k2 = _match_close(s, k, "{", "}")
                        if k2 >= 0:
                            k = k2 + 1
                    i = k
                    continue
                out.append(c)
                i += 1
                continue
            out.append(c)
            i += 1
        return "".join(out)

    # ---------- 指令处理 ----------
    def _call(self, s, name, i, end):
        """返回 (新下标, 文本)；新下标为 None 表示无法解析。"""
        j = _skip_ws(s, i)
        paren = None
        if j < end and s[j] == "(":
            k = _match_close(s, j, "(", ")")
            if k < 0:
                return None, None
            paren = s[j + 1:k]
            j = k + 1
        bracket = None
        j2 = _skip_ws(s, j)
        if j2 < end and s[j2] == "[":
            k2 = _match_close(s, j2, "[", "]")
            if k2 < 0:
                return None, None
            bracket = s[j2 + 1:k2]
            j = k2 + 1

        if name == "mi":
            if paren is None:
                return None, None
            try:
                raw, _ = _read_raw(paren, 0)
            except ExtractError:
                return None, None
            return (j, "$%s$" % raw.strip())

        if name == "mitex":
            if paren is None:
                return None, None
            try:
                raw, _ = _read_raw(paren, 0)
            except ExtractError:
                return None, None
            return (j, "$$\n%s\n$$" % raw.strip())

        if name == "image":
            path = ""
            if paren:
                mm = re.search(r'"([^"]*)"', paren)
                if mm:
                    path = mm.group(1)
            self.has_image = True
            self.images.append(path)
            return (j, "")

        if name in TOP_CALLS:
            return (j, "")

        if name in WRAP_CALLS:
            if bracket is None:
                return (j, "")
            return (j, self._walk(bracket, 0, len(bracket)))

        return (j, "")


def extract(text):
    """返回 (还原后的文本, 是否含插图, 插图路径列表)。"""
    p = Parser()
    out = p.parse(text or "")
    return out, p.has_image, p.images


# ---------------------------------------------------------------- 题目块解析

PROBLEM_HEAD = re.compile(r"#problem\s*\(([^)]*)\)\s*\[", re.S)
PART_HEADER = re.compile(r'#part-header\s*\(\s*"([^"]*)"\s*\)')
ANSWER_HEAD = re.compile(r"#answer\s*\(", re.S)
SOLUTION_HEAD = re.compile(r"#solution\s*\[", re.S)
CHOICES_HEAD = re.compile(r"#choices\s*\(", re.S)


def _split_args(s):
    """按顶层逗号切分实参（跳过字符串与原始字符串内部）。"""
    out, depth, cur = [], 0, []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            cur.append(s[i:j + 1])
            i = j + 1
            continue
        if c == "`":
            j = i + 1
            while j < n and s[j] != "`":
                j += 1
            cur.append(s[i:j + 1])
            i = j + 1
            continue
        if c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur))
    return [x.strip() for x in out]


def _strip_bracket(t):
    """去掉最外层的一对方括号（Typst 内容块）。"""
    t = t.strip()
    if t.startswith("[") and t.endswith("]"):
        return t[1:-1].strip()
    return t


def _call_span(text, name, frm=0):
    """定位 `#name(` 的调用区间，返回 (paren_start, paren_end, 整段结束)。

    paren_start 是左括号下标，paren_end 是配对右括号下标。
    """
    pat = re.compile(r"#" + re.escape(name) + r"\s*\(")
    m = pat.search(text, frm)
    if not m:
        return None
    p_open = m.end() - 1
    p_close = _match_close(text, p_open, "(", ")")
    if p_close < 0:
        return None
    return p_open, p_close


# 小问标记：源卷面里 `+ (1)` 表示第 (1) 问
SUBITEM = re.compile(r"^\s*\+\s*(\(\d+\)|\d+[.、)])\s*$", re.M)
# 整段只有一行、没有正文的空小问
DANGLE = re.compile(r"^\s*\+\s*(\(\d+\)|\d+[.、)])\s*$", re.M)


def is_truncated(text):
    """正文是否被源卷面截断（存在没有内容的小问标记）。"""
    return bool(DANGLE.search(text or ""))


# 公式片段（行内与独立成行）：分段时必须整体保护，
# 否则公式里的空行（如 \begin{cases} … \end{cases}）会把题干切碎。
MATH_BLOCK = re.compile(r"\$\$.*?\$\$|\$[^$]*\$", re.S)


def _split_paras(t):
    """按空行分段，但公式内部不切分。"""
    store = []

    def rep(m):
        store.append(m.group(0))
        return "\x00%d\x00" % (len(store) - 1)

    protected = MATH_BLOCK.sub(rep, t or "")
    raw = [p.strip() for p in re.split(r"\n{2,}", protected) if p.strip()]
    out = []
    for p in raw:
        p = re.sub(r"\x00(\d+)\x00",
                   lambda m: store[int(m.group(1))], p)
        if p.strip():
            out.append(p.strip())
    return out


LETTER_ANS = re.compile(r"[A-D]{1,4}")
BARE_ANS = re.compile(r"\$[^$\n]+\$|-?\d+(?:\.\d+)?")
# 填空位：\underline{\hspace{2.5em}} 或 ____
# 注意：**不能**把「（ ）」算作填空位——那是选择题的答题括号，
# 会把「源卷面漏了选项的选择题」误判成填空题。
BLANK_MARK = re.compile(r"\\underline\{|_{3,}")
# 解析末尾的「故选 B.」式答案（排除「不选 D」这类否定表述）
TAIL_CHOICE = re.compile(
    r"(?<![不未非没勿])选\s*((?:[（(]?\s*[A-D]\s*[）)]?\s*[,、，和]?\s*){1,4})")
# 源卷面自己标注了与原卷冲突（如「原 PDF …应选 D」）——这类题整题丢弃
SOURCE_CONFLICT = re.compile(r"原\s*PDF|现稿|以此为准|原题|原卷|题面应选|原文应选")


def compose_expl(answer, solution):
    """解析统一为教材体例：先「答案依据」，再正文。

    - 裸 LaTeX 答案（形如 \\frac{1}{3}）要补上 $…$ 才能渲染成公式；
    - 解析正文开头常常把答案重复一遍，去掉这一次重复。
    """
    ans = (answer or "").strip()
    if ans and "$" not in ans and re.search(r"[\\^_{}]", ans):
        ans = "$%s$" % ans
    sol = (solution or "").strip()
    if ans and sol:
        bare = ans.strip("$")
        lines = sol.split("\n")
        if lines and lines[0].strip() == bare:
            sol = "\n".join(lines[1:]).strip()
    head = "**答案依据**：%s" % ans if ans else "**答案依据**：见解析"
    if not sol:
        head += "（源卷面未收录解析）"
    return (head + "\n" + sol).strip()


def choice_from_tail(solution):
    """从解析末尾回捞选项答案（如「……故选 B.」）。

    只认**结尾附近**的表述，避免把解析里讨论「选项 A」误当答案；
    「不选 D」这类否定表述不算答案。
    """
    s = (solution or "").strip()
    if not s:
        return ""
    hits = list(TAIL_CHOICE.finditer(s))
    if not hits:
        return ""
    m = hits[-1]
    if len(s) - m.end() > 12:          # 答案必须在结尾 12 个字符内
        return ""
    letters = sorted(set(re.findall(r"[A-D]", m.group(1))))
    return "".join(letters)


def pick_answer(leftover, kind):
    """从题干之后的段落里取出答案行。

    版式 B（答案直接写在小问里）里，答案紧跟在题干之后：
      选择题 → 单行字母（如 C、ACD）
      填空题 → 单行公式（如 $27$）或纯数字
    返回 (答案文本, 剩余段落=解析)。
    """
    if not leftover:
        return "", []
    if kind in ("choice", "single", "multi"):
        for i, p in enumerate(leftover[:2]):
            t = p.strip()
            if re.fullmatch(r"[A-D]{1,4}", t):
                return t, leftover[i + 1:]
        return "", leftover
    if kind == "blank":
        for i, p in enumerate(leftover[:2]):
            t = p.strip()
            if re.fullmatch(r"\$[^$\n]+\$", t) or re.fullmatch(r"-?\d+(?:\.\d+)?", t):
                return t, leftover[i + 1:]
        return "", leftover
    return "", leftover


def parse_paper(text):
    """解析一份卷面，返回题目列表。

    每题：{num, stem, options, answer, solution, section, has_image, truncated}
    section 取自 #part-header（单选题 / 多选题 / 填空题 / 解答题 …）。
    """
    events = []
    i, n = 0, len(text)
    while i < n:
        if text[i] != "#":
            i += 1
            continue
        j = _skip_ws(text, i + 1)
        m = IDENT.match(text, j)
        if not m:
            i += 1
            continue
        name = m.group(0)
        if name == "part-header":
            mm = PART_HEADER.match(text, i)
            if mm:
                events.append(("part", mm.group(1), i, mm.end()))
                i = mm.end()
                continue
        if name == "problem":
            mm = PROBLEM_HEAD.match(text, i)
            if not mm:
                i = m.end()
                continue
            b_open = mm.end() - 1
            b_close = _match_close(text, b_open, "[", "]")
            if b_close < 0:
                i = mm.end()
                continue
            events.append(("problem", mm.group(1).strip(), i, b_close + 1,
                           text[b_open + 1:b_close]))
            i = b_close + 1
            continue
        if name == "answer":
            mm = ANSWER_HEAD.match(text, i)
            if not mm:
                i = m.end()
                continue
            a_open = mm.end() - 1
            a_close = _match_close(text, a_open, "(", ")")
            if a_close < 0:
                i = mm.end()
                continue
            events.append(("answer", text[a_open + 1:a_close], i, a_close + 1))
            i = a_close + 1
            continue
        if name == "solution":
            mm = SOLUTION_HEAD.match(text, i)
            if not mm:
                i = m.end()
                continue
            b_open = mm.end() - 1
            b_close = _match_close(text, b_open, "[", "]")
            if b_close < 0:
                i = mm.end()
                continue
            events.append(("solution", text[b_open + 1:b_close], i, b_close + 1))
            i = b_close + 1
            continue
        i = m.end()

    # 按 problem 事件分组，把紧随其后的 answer / solution 归给它
    groups = []
    cur = None
    section0 = ""
    for ev in events:
        if ev[0] == "part":
            if cur is not None:
                cur["section"] = ev[1]
            else:
                section0 = ev[1]
            continue
        if ev[0] == "problem":
            cur = {"num": ev[1], "body": ev[4], "section": section0,
                   "answer_raw": None, "solution_raw": None}
            groups.append(cur)
            continue
        if cur is None:
            continue
        if ev[0] == "answer" and cur["answer_raw"] is None:
            cur["answer_raw"] = ev[1]
        elif ev[0] == "solution" and cur["solution_raw"] is None:
            cur["solution_raw"] = ev[1]

    questions = []
    for g in groups:
        body = g["body"]
        opts = []
        has_img = False
        rest = body
        span = _call_span(body, "choices")
        if span:
            p_open, p_close = span
            for raw in _split_args(body[p_open + 1:p_close]):
                if not raw or raw.startswith("cols"):
                    continue
                o_txt, o_img, _ = extract(_strip_bracket(raw))
                if o_img:
                    has_img = True
                opts.append(o_txt)
            rest = body[:p_open] + body[p_close + 1:]
        stem_txt, r_img, imgs = extract(rest)
        if r_img:
            has_img = True

        answer = ""
        solution = ""
        if g["answer_raw"] is not None:
            a_txt, _, _ = extract(_strip_bracket(g["answer_raw"]))
            answer = a_txt.strip()
        if g["solution_raw"] is not None:
            s_txt, s_img, _ = extract(g["solution_raw"])
            solution = s_txt
            if s_img:
                has_img = True

        paras = _split_paras(stem_txt)
        stem = paras[0] if paras else ""
        leftover = paras[1:]

        # 题型按**结构**判定，不依赖分节标题（源卷面存在标题错标）：
        #   有选项 → 选择题；无选项但题干含填空位 → 填空题；否则 → 解答题
        if len(opts) >= 2:
            kind = "choice"
        elif BLANK_MARK.search(stem):
            kind = "blank"
        else:
            kind = "calc"

        if not answer:
            answer, leftover = pick_answer(leftover, kind)
        if not solution:
            solution = "\n\n".join(leftover)
        if not answer and kind == "choice":
            answer = choice_from_tail(solution)

        questions.append({
            "num": g["num"], "stem": stem, "options": opts,
            "answer": answer, "solution": solution, "section": g["section"],
            "kind": kind,
            "has_image": has_img, "images": imgs,
            "truncated": is_truncated(stem) or is_truncated(solution),
        })
    return questions


def section_kind(section):
    """分节标题 → 题型关键词（供答案行识别使用）。"""
    s = section or ""
    if "多选" in s:
        return "multi"
    if "单选" in s or "选择" in s:
        return "single"
    if "填空" in s:
        return "blank"
    return "calc"
