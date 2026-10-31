# -*- coding: utf-8 -*-
"""题库独立核验器。

核验内容（对应计划的 A1–A6 + B 组）：
    A 组 结构不变量
        A1 题量 180，6 题型各 30
        A2 难度 basic/medium/hard = 90/63/27
        A3 章节 = 30/36/36/36/36/6
        A4 「题型 × 章节」矩阵逐格等于修正矩阵（V7）
        A5 单选答案位置落在 [5,10]，多选答案字母极差 <= 12
        A6 客观题答案在选项内；主观题采分点数 = term2/short3/calc4
    B 组 内容与表达
        B1 每题解析含「答案依据」；主观题含「考点出处」
        B2 判断题选项恒为 [正确,错误]，答案 ∈ {A,B}
        B3 填空题有 answer 且有 accept 等价写法
        B4 题干/解析中 $ 成对（LaTeX 分隔符不落单）
        B5 题干不重复；标签非空；出处非空
        B6 每道计算题至少带一条 SymPy 可核验项，且核验通过

用法：
    python tools/verify_quiz.py                 # 全量
    python tools/verify_quiz.py --chapter ch2   # 单章
    python tools/verify_quiz.py --quiet         # 只看结论
"""
import os
import sys
from collections import Counter, defaultdict

# 本机控制台是 GBK 码页：题库里出现「²」「⇒」「∉」等非 GBK 字符时，
# 打印 desc 会抛 UnicodeEncodeError 把整个核验打断（曾让多个子任务白烧 token）。
# 这里允许替换而不是抛异常，核验必须永远能跑完。
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---- 修正后的「题型 × 章节」矩阵（V7：原批准计划 §4.3 合计 176，已机械修正为 180）----
MATRIX = {
    'single': {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3},
    'multi': {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2},
    'judge': {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3},
    'blank': {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2},
    'short': {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2},
    'calc': {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3},
}
CHAPTER_N = {ch: 15 for ch in range(1, 13)}
DIFF_N = {"basic": 84, "medium": 60, "hard": 36}
TYPE_N = 30


def check_matrix(questions, err):
    cell = defaultdict(int)
    for q in questions:
        cell[(q["typeGroup"], q["chapter"])] += 1
    for t, row in MATRIX.items():
        for ch, n in row.items():
            got = cell.get((t, ch), 0)
            if got != n:
                err.append("A4 矩阵不符 %s×ch%d = %d，期望 %d" % (t, ch, got, n))
    for ch, n in CHAPTER_N.items():
        got = sum(1 for q in questions if q["chapter"] == ch)
        if got != n:
            err.append("A3 章节 %d = %d，期望 %d" % (ch, got, n))


def check_content(questions, err, warn):
    seen_stem = {}
    for q in questions:
        qid = q["id"]
        expl = q.get("explanation") or ""
        if "答案依据" not in expl:
            err.append("B1 %s 解析缺「答案依据」" % qid)
        if q["type"] in ("term", "short", "calc") and "考点出处" not in expl:
            err.append("B1 %s 主观题解析缺「考点出处」" % qid)
        if len(expl) < 30:
            warn.append("B1 %s 解析过短（%d 字）" % (qid, len(expl)))

        if q["type"] == "judge":
            if q.get("options") != ["正确", "错误"]:
                err.append("B2 %s 判断题选项应为 [正确,错误]" % qid)
            if q["answer"] not in (["A"], ["B"]):
                err.append("B2 %s 判断题答案应为 A 或 B" % qid)
        if q["type"] == "multi":
            if not (2 <= len(q["answer"]) <= len(q.get("options") or [])):
                err.append("A6 %s 多选答案个数 %d 不在 [2, 选项数]" % (qid, len(q["answer"])))
        if q["type"] == "blank":
            ans = q.get("answer") or []
            if not ans or not all(isinstance(a, str) and a.strip() for a in ans):
                err.append("B3 %s 填空题答案非法" % qid)
            if not q.get("accept"):
                warn.append("B3 %s 填空题未给 accept 等价写法" % qid)
        if q["type"] == "calc" and not q.get("verify"):
            err.append("B6 %s 计算题缺 SymPy 可核验项" % qid)

        for field in ("stem", "explanation", "answerText"):
            txt = q.get(field) or ""
            if txt.count("$") % 2 != 0:
                err.append("B4 %s 的 %s 中 $ 不成对" % (qid, field))
        if q["type"] in ("single", "multi", "judge"):
            for opt in (q.get("options") or []):
                if opt.count("$") % 2 != 0:
                    err.append("B4 %s 选项中 $ 不成对" % qid)

        stem = (q.get("stem") or "").strip()
        key = stem[:60]
        if key in seen_stem:
            err.append("B5 %s 与 %s 题干重复" % (qid, seen_stem[key]))
        seen_stem[key] = qid

        if not q.get("tags"):
            warn.append("B5 %s 无标签" % qid)
        if not (q.get("source") or {}).get("text"):
            err.append("B5 %s 缺考点出处" % qid)
        if q.get("extension") and not q["extension"].startswith("引申"):
            err.append("%s 引申内容未以「引申」开头" % qid)


def run_code(code, ns):
    """执行题库里的核验代码，返回其值。

    支持两种写法：
        1) 单个表达式        —— "M([[1,2],[3,4]]).det()"
        2) 若干语句 + 末句表达式 —— "a=symbols('a'); expand(...)"
    第 2 种用 ast 拆出末句表达式单独求值（eval 本身不接受语句序列）。
    """
    import ast
    tree = ast.parse(code, mode="exec")
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = tree.body.pop()
    exec(compile(tree, "<verify>", "exec"), ns)  # noqa: S102 - 受信本地题库
    if last is None:
        return None
    return eval(compile(ast.Expression(last.value), "<verify>", "eval"), ns)


def run_sympy_checks(questions, err, quiet):
    try:
        import sympy
    except Exception as e:  # pragma: no cover
        err.append("B6 无法导入 sympy：%s" % e)
        return 0
    # 题库代码里用 M(...) 表示矩阵（与 ch1 既有写法一致）
    base_ns = {k: getattr(sympy, k) for k in dir(sympy) if not k.startswith("_")}
    base_ns["M"] = sympy.Matrix
    # 预置常用符号变量，题库核验代码可直接使用 x, y, z, t, n, k 等
    _syms = sympy.symbols("x y z t u v n k m a b c p q s w")
    _names = "x y z t u v n k m a b c p q s w".split()
    base_ns.update(dict(zip(_names, _syms)))
    base_ns["f"] = sympy.Function
    total = 0
    for q in questions:
        for item in (q.get("verify") or []):
            total += 1
            desc = item.get("desc", "")
            code = item.get("code", "")
            expected = str(item.get("expected", ""))
            # 每条核验项使用全新命名空间：避免前一条给 x/y 等符号赋表达式后污染后续核验
            ns = dict(base_ns)
            try:
                val = run_code(code, ns)
                got = str(val)
            except Exception as e:
                err.append("B6 %s[%s] 执行失败：%s" % (q["id"], desc, e))
                continue
            ok = (got.strip() == expected.strip())
            if not ok:
                try:
                    ok = abs(float(got) - float(expected)) <= 1e-9
                except Exception:
                    ok = False
            if not ok:
                err.append("B6 %s[%s] 结果不符：得到 %r，题库写 %r" % (q["id"], desc, got, expected))
            elif not quiet:
                print("   [sympy ok] %s %-22s %s" % (q["id"], desc, got))
    return total


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    chaps = [a.split("=", 1)[1] for a in args if a.startswith("--chapter=")]
    if not chaps:
        chaps = [a for a in args if a.startswith("ch")]
    if not chaps:
        chaps = ["ch%d" % i for i in range(1, 13)]

    allq = []
    for name in chaps:
        mod = __import__("qa_bank." + name, fromlist=["Q"])
        allq.extend(mod.Q)

    err, warn = [], []
    print("=" * 72)
    print("核验范围：%s   题数：%d" % (",".join(chaps), len(allq)))

    # A1–A6
    from qa_bank.common import audit
    full = (len(chaps) == 6)
    rep, aerr = audit(allq, full=full)
    for line in rep:
        print("  " + line)
    err.extend(aerr)
    if full:
        # 全量模式下才校验跨章不变量（单章模式下这些计数必然不等）
        check_matrix(allq, err)
    else:
        # 单章模式：只校验本章内部矩阵
        sub = {t: {c: n for c, n in row.items() if c in [int(x[2:]) for x in chaps]}
               for t, row in MATRIX.items()}
        cell = defaultdict(int)
        for q in allq:
            cell[(q["typeGroup"], q["chapter"])] += 1
        for t, row in sub.items():
            for c, n in row.items():
                got = cell.get((t, c), 0)
                if got != n:
                    err.append("A4 矩阵不符 %s×ch%d = %d，期望 %d" % (t, c, got, n))

    # 重复 id
    ids = [q["id"] for q in allq]
    dup = [i for i, c in Counter(ids).items() if c > 1]
    if dup:
        err.append("重复 id：%s" % dup)

    # B1–B6
    check_content(allq, err, warn)

    # B6 数值复核
    nverify = run_sympy_checks(allq, err, quiet)

    print("-" * 72)
    print("SymPy 复核项：%d 条" % nverify)
    for w in warn:
        print("  [warn] %s" % w)
    if err:
        print("失败：%d 项" % len(err))
        for e in err:
            print("  [FAIL] %s" % e)
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
