# -*- coding: utf-8 -*-
r"""扫描题库源码里的「LaTeX 转义被 Python 吃掉」问题。

背景：题库用普通字符串（非 raw string）存 LaTeX，源码里必须把反斜杠写成两个。
一旦漏写，Python 会按自己的转义规则解释：
    "\\neq"  -> \neq   （正确）
    "\neq"   -> 换行 + "eq"（静默损坏：公式里凭空多一个换行，网页上显示错乱）
后者多数不报错、只给 SyntaxWarning，极难发现。

两类问题：
    [致命] 反斜杠 + 会被 Python 解释成别的字符（b/t/r/f/v/a/x/N/u/U/0），
           或 + "n" 且后面紧跟 LaTeX 命令字母 → 该命令被吃掉，公式损坏。
    [无害] 反斜杠 + Python 不认识的符号（如 \;、\,）→ Python 原样保留，
           LaTeX 正确，只是会打印 SyntaxWarning。

实现说明：不用 ast——隐式拼接的相邻字符串在 AST 里是**一个跨行节点**，
会被整体跳过。改用 tokenize：它逐个给出字符串 token，且列号是**字符**下标。

用法：
    python tools/scan_escapes.py            # 只报告
    python tools/scan_escapes.py --fix      # 自动加倍该反斜杠
"""
import io
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "qa_bank")

CTRL = set("btrfvaxNuU0")
NL = "n"
_STR_RE = re.compile(r"^([A-Za-z]*)(\"\"\"|'''|\"|')", re.S)


def string_tokens(path):
    """产出 (行号, 该行内起始字符列, 字面量正文)。只处理非 raw 的普通字符串。"""
    with open(path, "rb") as f:
        for tok in tokenize.tokenize(f.readline):
            if tok.type != tokenize.STRING:
                continue
            s = tok.string
            m = _STR_RE.match(s)
            if not m:
                continue
            prefix = m.group(1).lower()
            if "r" in prefix or "b" in prefix:
                continue          # raw 字符串不解释转义；bytes 与本项目无关
            quote = m.group(2)
            body = s[len(m.group(0)):-len(quote)]
            row, col = tok.start
            if "\n" in body:
                # 多行字面量：逐行给出各自的起始列
                for k, ln in enumerate(body.split("\n")):
                    yield (row + k, col if k == 0 else 0, ln)
            else:
                yield (row, col + len(m.group(0)), body)


def find_issues(body):
    """在字面量正文里找可疑反斜杠，返回 [(字符下标, 级别)]。"""
    hits = []
    i = 0
    while i < len(body) - 1:
        if body[i] != "\\":
            i += 1
            continue
        nxt = body[i + 1]
        if nxt == "\\":
            i += 2                    # 已正确成对
            continue
        if nxt in CTRL:
            hits.append((i, "致命"))
        elif nxt == NL and i + 2 < len(body) and body[i + 2].isascii() and body[i + 2].isalpha():
            # 仅当后面紧跟 **ASCII** 字母才算 LaTeX 命令被吃掉。
            # 刻意写的 \n（换行）后面常跟中文，中文不是 ASCII，不能误判。
            hits.append((i, "致命"))  # 例如 \neq 被当成 换行 + "eq"
        elif not nxt.isalnum():
            hits.append((i, "无害"))  # Python 不认识的转义：原样保留，仅消警告
        i += 2
    return hits


def main():
    fix = "--fix" in sys.argv
    files = sorted(f for f in os.listdir(BANK) if f.startswith("ch") and f.endswith(".py"))
    total = fatal = 0
    edits = {}

    for fn in files:
        path = os.path.join(BANK, fn)
        src = io.open(path, encoding="utf-8").read()
        per_line = {}
        for row, col, body in string_tokens(path):
            for idx, level in find_issues(body):
                total += 1
                if level == "致命":
                    fatal += 1
                per_line.setdefault(row, []).append(col + idx)
                print("%s:%d  [%s]  ...%s..." %
                      (fn, row, level, body[max(0, idx - 14):idx + 20].replace("\n", "\\n")))
        if per_line:
            edits[fn] = per_line

    print("-" * 60)
    print("共 %d 处，其中致命（公式会被损坏）%d 处" % (total, fatal))

    if fix and edits:
        for fn, per_line in edits.items():
            path = os.path.join(BANK, fn)
            lines = io.open(path, encoding="utf-8").read().split("\n")
            n = 0
            for row, idxs in per_line.items():
                L = list(lines[row - 1])
                for pos in sorted(idxs, reverse=True):
                    L.insert(pos, "\\")
                    n += 1
                lines[row - 1] = "".join(L)
            io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
            print("已修复 %s：%d 处" % (fn, n))
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
