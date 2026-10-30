"""客观题答案 ↔ 解析 自洽性交叉审计（高置信版）。

背景：题库用统一体例写解析——错误选项写成 "X 错：…"，正确选项在
      「答案依据」里被点名。若 `answer` 与解析互相矛盾，学生按解析答对
      却被判错（页面还会把它标成「错选」）。本题库曾真实出现过这类缺陷。

高置信判据（宁可漏报，不可误报；漏报靠人工全量复核兜底）：
  ① 题干在「选错误项」（含 错误/不属于/不正确/不能/不是）时，
     解析里的 "X 错" 是在解释**正确答案为什么错**，不算矛盾 → 排除。
  ② 解析用 "**成立**" / "X 正确" 明确断言 X 为对项，但 answer 里没有 X → 矛盾。
  ③ answer 里有 X，但解析把 X 断言为错项（且题目不是「选错误项」）→ 矛盾。
  ④ 多选题中，既不在 answer 里、解析也完全没提的选项 → 需人工确认。

用法：
    python audit_choice.py              # 报告矛盾
    python audit_choice.py --quiet      # 只输出结论行（供构建门禁调用）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_bank import load_bank  # noqa: E402

# 题目在「选错误项」时，解析里的「X 错」是解释答案为何错
NEGATIVE_STEM = ("错误", "不属于", "不正确", "不能", "不是", "不包括",
                 "不成立", "不真", "是错", "错误的", "不恰当")

# 解析断言 X 为错项
WRONG_PAT = [
    r'(?:^|[^A-Za-z0-9]){L}\s*错',
    r'(?:^|[^A-Za-z0-9]){L}\s*不对',
    r'(?:^|[^A-Za-z0-9]){L}\s*不成立',
    r'(?:^|[^A-Za-z0-9]){L}\s*不能成立',
    r'(?:^|[^A-Za-z0-9]){L}\s*是错的',
]
# 解析断言 X 为对项（只收高置信写法）
RIGHT_PAT = [
    r'{L}[^。\n]{0,60}\*\*成立\*\*',
    r'(?:^|[^A-Za-z0-9]){L}\s*正确',
    r'(?:^|[^A-Za-z0-9]){L}\s*是对的',
    r'(?:^|[^A-Za-z0-9]){L}\s*成立',
]


def analyse(q):
    expl = q.get("explanation") or ""
    segs = [s for s in expl.split("\n") if s.strip()]
    wrong, right = set(), set()
    for L in "ABCD":
        for s in segs:
            if any(re.search(p.replace("{L}", L), s) for p in WRONG_PAT):
                wrong.add(L)
                break
        for s in segs:
            if L in wrong:
                continue
            if any(re.search(p.replace("{L}", L), s) for p in RIGHT_PAT):
                right.add(L)
                break
    return right, wrong


def check(questions=None):
    """返回自洽性问题清单（空列表 = 通过）。供构建门禁直接调用。"""
    if questions is None:
        questions = load_bank()
    types = ["single", "multi", "judge"]
    problems = []
    for q in questions:
        if q["type"] not in types:
            continue
        expl = q.get("explanation") or ""
        # 源卷面本身没收录解析的题：答案直接取自源卷面答案块，
        # 没有解析可供交叉核对，不参与本项审计（另行统计）。
        if "源卷面未收录解析" in expl:
            continue
        ans = set(q["answer"])
        stem = q.get("stem") or ""
        picks_wrong = any(k in stem for k in NEGATIVE_STEM)
        right, wrong = analyse(q)

        if picks_wrong:
            # 「选错误项」题型：answer 就该是解析断言为错的那一项；
            # 解析断言「A/B/D 正确」是正常的，不算矛盾。
            if wrong and not (ans & wrong):
                problems.append("%s [%s] 题干在选错误项，但解析断言 %s 错，而 answer 里没有"
                                % (q["id"], q["type"], "/".join(sorted(wrong))))
        else:
            for L in sorted(ans & wrong):
                problems.append("%s [%s] answer 含 %s，但解析断言 %s 错" % (q["id"], q["type"], L, L))
            for L in sorted(right - ans):
                problems.append("%s [%s] 解析断言 %s 成立，但 answer 里没有" % (q["id"], q["type"], L))
        if q["type"] == "multi":
            for i, o in enumerate(q.get("options") or []):
                L = "ABCDE"[i]
                if L not in ans and L not in wrong and L not in right:
                    problems.append("%s [multi] 选项 %s 未被答案或解析交代，需人工确认" % (q["id"], L))

    return problems


def main():
    quiet = "--quiet" in sys.argv
    problems = check()
    if problems and not quiet:
        for p in problems:
            print("  ⚠ " + p)
    line = "客观题自洽性审计：矛盾 %d 处" % len(problems)
    if quiet:
        print(line + (" → 通过" if not problems else " → 不通过"))
    else:
        print("\n" + line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
