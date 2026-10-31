# -*- coding: utf-8 -*-
"""答案键 ↔ 解析 **数值** 一致性门禁（audit_choice 的补盲）。

背景（2026-10-31 实测的真事故）：
    q-039「设 A,B 均为 3 阶方阵，|A|=2，|B|=-3，则 |2AB^{-1}|=」，
    答案键写的是 B（-8/3），而解析里自己的推导是
    |2AB^{-1}|=2^3·|A|·|B^{-1}|=8×2×(-1/3)=-16/3（选项 A）。
    **答案键与解析互相矛盾**——学生按解析答对却被判错。
    为什么所有门禁都没抓到：
      · audit_choice 只认「解析里点名字母」（"A 正确"/"B 错"），
        这道题的解析只给了数值推导，一个字母都没点 → 规则②③对它无感；
      · 该题的 verify 字段写的是 `M([[1,2],[3,4]]).det()`——与本题毫无关系的占位算式，
        SymPy 复核自然一路绿灯。
    实测统计：500 题里 250 道客观题，**只有 44 道（17.6%）**的解析点名了答案字母，
    其余 206 道客观题在 audit_choice 的规则②③下是**无保护**的。

本门禁的做法（只管高置信的一小块，宁可漏报不可误报）：
    只检查 **单选题**且 **答案选项是纯数值** 的题，
    要求「答案选项的数值」必须能在解析里读到——读不到就是答案键可疑。
    长陈述型选项（多选为主）解析换个说法就匹配不上，一律不管。

    实测覆盖：500 题里这样的题有 30 道；误报 0 道。
    改之前 q-039 必然被本门禁命中（-8/3 在解析里根本不存在）。

用法：
    python audit_value.py            # 逐条报告
    python audit_value.py --quiet    # 只输出结论行（供构建门禁调用）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_bank import load_bank  # noqa: E402

# 归一化后的「纯数值型选项」形态：只允许 ASCII 数字与数学符号。
# 显式 ASCII —— 否则 Python 的 \w 会匹配中文，q-475 的 "$3\times2$ 矩阵"
# 会被误当成数值型选项（实测踩过：它是 30 道里唯一的假阳性）。
VALUE_PAT = re.compile(r"^[-+()\d\w\^/*\\{}]{2,18}$", re.ASCII)


def norm(s):
    """LaTeX 片段归一化：去 $ / \\left \\right / dfrac→frac / 各类间距命令 / 空白。

    去 `$` 是关键：选项写作 `$-3$`、解析写作 `-3`，不归一化就永远匹配不上。
    """
    s = s or ""
    s = s.replace("$", "")
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = re.sub(r"\\[,;!:]", "", s)
    s = s.replace("\\ ", "")
    s = re.sub(r"\s+", "", s)
    return s


def is_value_like(option_text):
    """该选项是否算「纯数值」——可用于机器核对的短数学量。"""
    no = norm(option_text)
    if not VALUE_PAT.match(no):
        return False
    return bool(re.search(r"\d", no, re.ASCII))


def value_appears(value, haystack):
    """value 是否作为**独立**片段出现在 haystack 里。

    边界检查只看**数字**：前后紧邻数字才算巧合（"135" 撞上 "1350"）。
    不能用 isalnum()——归一化已去掉空格，"k\\neq0" 前面会紧挨着 "\\iff" 的字母 "f"，
    "y_1^2+2y_2^2" 前面会紧挨着中文「为」，两者都会被误判成粘连（实测两处假阳性）。
    """
    if not value:
        return False
    start = 0
    while True:
        i = haystack.find(value, start)
        if i < 0:
            return False
        before = haystack[i - 1] if i > 0 else ""
        after = haystack[i + len(value)] if i + len(value) < len(haystack) else ""
        if not before.isdigit() and not after.isdigit():
            return True
        start = i + 1


def check(questions=None):
    """返回问题清单（空列表 = 通过）。供构建门禁直接调用。"""
    if questions is None:
        questions = load_bank()
    problems = []
    for q in questions:
        if q.get("type") != "single":
            continue
        opts = q.get("options") or []
        if len(opts) < 2:
            continue
        ans = set(q.get("answer") or [])
        expl = norm(q.get("explanation") or "")
        for i, o in enumerate(opts):
            L = "ABCDE"[i]
            if L not in ans or not is_value_like(o):
                continue
            if not value_appears(norm(o), expl):
                problems.append(
                    "%s [single] 答案键 %s 的值 %s 在解析里读不出来——"
                    "答案键与解析可能矛盾（解析若已给出正确数值，答案键应指向它）"
                    % (q.get("id"), L, o))
    return problems


def main():
    quiet = "--quiet" in sys.argv
    problems = check()
    if problems and not quiet:
        for p in problems:
            print("  ⚠ " + p)
    line = "答案键↔解析数值一致性：可疑 %d 处" % len(problems)
    if quiet:
        print(line + (" → 通过" if not problems else " → 不通过"))
    else:
        print("\n" + line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
