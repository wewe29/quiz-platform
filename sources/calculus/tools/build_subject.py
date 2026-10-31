# -*- coding: utf-8 -*-
r"""高等数学 · 学科产物导出：跑门禁链后把题库导出为平台子站数据分片。

用法：
    python tools/build_subject.py                # 导出到平台仓 subjects/calculus
    python tools/build_subject.py --out <dir>    # 指定导出目录
    python tools/build_subject.py --skip-gates   # 跳过门禁（仅调试）

门禁链（与平台契约对齐，见 quiz-platform/docs/decisions.md）：
    1. scan_escapes            —— LaTeX 转义扫描（fatal 即中止）
    2. audit_choice / audit_open —— 答案键↔解析自洽、主观题结构
    3. validate_bank.py        —— 数据契约门禁（本项目的口径门禁；verify_quiz.py 的
                                  题量/矩阵断言还停留在 180 题旧口径，不在链内）
    4. SymPy 复核              —— 逐题执行 verify 项（93 项，limit/级数/积分等）
    5. 逐题字段校验            —— 平台契约必需字段 + 客观题答案在选项内

导出契约（quiz-platform-subject-v1）与线代侧一致：
    manifest.json（subject/sections/caliber/summary/shards+SHA256）+ chNN[a-c].json。
采分点说明：本库 calc 题采分点 1–6 点不等（partial 均 2 分），平台端主观题满分 =
Σ采分点分值（app.js fullScore），不再按题型写死。
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from qa_bank import load_bank  # noqa: E402
from qa_bank.catalog import CHAPTERS, kp_labels  # noqa: E402

SUBJECT = {
    "id": "calculus",
    "name": "高等数学",
    "textbook": "同济大学《高等数学》第七版（含考研真题 1987–2026）",
    "bankId": "advanced-math-tj7-v2",
    "chapters": 12,
    "chapterLabels": {str(c["n"]): c["label"] for c in CHAPTERS},
}

SHARD_BUDGET = 200 * 1024


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def default_out():
    sibling = os.path.join(os.path.dirname(PROJECT), "quiz-platform", "subjects", SUBJECT["id"])
    if os.path.isdir(os.path.join(os.path.dirname(PROJECT), "quiz-platform")):
        return sibling
    return os.path.join(PROJECT, "platform-dist", SUBJECT["id"])


def _encoded_size(p):
    return len(json.dumps(p, ensure_ascii=False, indent=1).encode("utf-8"))


def shard_questions(questions):
    from collections import OrderedDict
    by_ch = OrderedDict()
    for q in questions:
        by_ch.setdefault(q["chapter"], []).append(q)
    shards = []
    for ch in sorted(by_ch):
        qs = by_ch[ch]
        parts = [{"name": "ch%d.json" % ch, "questions": qs}]
        for _ in range(4):
            if not [p for p in parts if _encoded_size(p) > SHARD_BUDGET]:
                break
            new_parts = []
            for p in parts:
                if _encoded_size(p) > SHARD_BUDGET and len(p["questions"]) > 1:
                    half = len(p["questions"]) // 2
                    new_parts.append({"name": None, "questions": p["questions"][:half]})
                    new_parts.append({"name": None, "questions": p["questions"][half:]})
                else:
                    new_parts.append(p)
            parts = new_parts
        if len(parts) == 1:
            parts[0]["name"] = "ch%d.json" % ch
        else:
            for i, p in enumerate(parts):
                p["name"] = "ch%d%s.json" % (ch, "abcdef"[i])
        for p in parts:
            p["chapter"] = ch
        shards.extend(parts)
    return shards


# ---------------------------------------------------------------- 门禁
def gate_scan_escapes():
    from scan_escapes import string_tokens, find_issues
    fatal = 0
    bank_dir = os.path.join(HERE, "qa_bank")
    for fn in sorted(os.listdir(bank_dir)):
        if not (fn.startswith("ch") and fn.endswith(".py")):
            continue
        for row, col, body in string_tokens(os.path.join(bank_dir, fn)):
            for idx, level in find_issues(body):
                if level == "致命":
                    fatal += 1
                    print("      [escape] %s:%d ..." % (fn, row))
    if fatal:
        raise SystemExit("[gates] scan_escapes：%d 处致命转义" % fatal)
    print("[OK ] scan_escapes：0 处致命转义")


def gate_audits(questions):
    from audit_choice import check as check_choice
    from audit_open import check as check_open
    bad = check_choice(questions)
    if bad:
        for p in bad[:10]:
            print("      [choice] %s" % p)
        raise SystemExit("[gates] audit_choice：%d 处矛盾" % len(bad))
    print("[OK ] audit_choice：答案键↔解析自洽")
    open_bad, _ = check_open(questions)
    if open_bad:
        for p in open_bad[:10]:
            print("      [open] %s" % p)
        raise SystemExit("[gates] audit_open：%d 处问题" % len(open_bad))
    print("[OK ] audit_open：主观题结构合规")


def gate_validate_bank():
    p = subprocess.run([sys.executable, os.path.join(HERE, "validate_bank.py")],
                       cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    if p.returncode != 0:
        for l in out.splitlines()[:40]:
            print("      " + l)
        raise SystemExit("[gates] validate_bank 未通过")
    print("[OK ] validate_bank：数据契约门禁通过")


def _run_code(code, ns):
    import ast
    tree = ast.parse(code, mode="exec")
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = tree.body.pop()
    exec(compile(tree, "<verify>", "exec"), ns)  # noqa: S102 - 受信本地题库
    if last is None:
        return None
    return eval(compile(ast.Expression(last.value), "<verify>", "eval"), ns)


def gate_sympy(questions):
    try:
        import sympy
    except Exception as e:  # pragma: no cover
        print("[warn] sympy 不可用（%s），跳过数值复核" % e)
        return 0
    base_ns = {k: getattr(sympy, k) for k in dir(sympy) if not k.startswith("_")}
    base_ns["M"] = sympy.Matrix
    # 高数核验代码大量使用裸符号（x/y/z/t…）未声明——预注入 sympy.abc 常用符号
    try:
        import sympy.abc as _abc
        base_ns.update({k: v for k, v in vars(_abc).items() if not k.startswith("_")})
    except Exception:
        pass
    # ⚠ abc 的 greek 字母会把 pi/E/I 变成「同名符号」，覆盖掉 sympy 常量——
    # cos(2*pi) 永不求值、积分结果恒带 sin(pi)。注入后必须把常量恢复回来。
    for const in ("pi", "E", "I", "oo", "zoo", "nan", "S", "N", "Q"):
        if hasattr(sympy, const):
            base_ns[const] = getattr(sympy, const)
    base_ns["M"] = sympy.Matrix  # 确保矩阵别名不被覆盖
    total = bad = 0
    for q in questions:
        for item in (q.get("verify") or []):
            total += 1
            code, expected, desc = item.get("code", ""), str(item.get("expected", "")), item.get("desc", "")
            # 每项独立命名空间：核验项里的赋值（z=…; y=…）不得泄漏到后续项——
            # 否则前一项把 y 赋成表达式，后一项 diff/integrate 会拿到「变量位置上是表达式」的错参数
            ns = dict(base_ns)
            try:
                val = _run_code(code, ns)
                got = str(val).strip()
            except Exception as e:
                bad += 1
                print("      [verify] %s[%s] 执行失败：%s" % (q["id"], desc, e))
                continue
            ok = got == expected.strip()
            if not ok:
                try:
                    ok = abs(float(got) - float(expected)) <= 1e-9
                except Exception:
                    ok = False
            if not ok and val is not None:
                # 数学等价回退：sin(pi)**2 这类未化简形态与 0/1/8 等期望值相等
                try:
                    d = sympy.simplify(sympy.sympify(val) - sympy.sympify(expected))
                    ok = (d == 0)
                except Exception:
                    ok = False
            if not ok:
                bad += 1
                print("      [verify] %s[%s] 得到 %r，题库写 %r" % (q["id"], desc, got, expected))
    if bad:
        raise SystemExit("[gates] SymPy 复核 %d/%d 项不符" % (bad, total))
    print("[OK ] SymPy 复核：%d 项全部通过" % total)
    return total


def gate_fields(questions):
    from collections import Counter
    ids = [q["id"] for q in questions]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit("[gates] 重复题号：%s" % sorted(dup)[:8])
    bad = 0
    for q in questions:
        for k in ("id", "type", "typeGroup", "difficulty", "chapter", "stem", "explanation"):
            if not q.get(k):
                print("      [field] %s 缺 %s" % (q.get("id", "?"), k))
                bad += 1
        if q["type"] in ("single", "multi", "judge"):
            letters = "ABCDE"[:len(q.get("options") or [])]
            for a in q.get("answer") or []:
                if a not in letters:
                    print("      [field] %s 答案 %s 不在选项内" % (q["id"], a))
                    bad += 1
        if q["type"] in ("term", "short", "calc") and not q.get("answerText"):
            print("      [field] %s 主观题缺参考答案" % q["id"])
            bad += 1
    if bad:
        raise SystemExit("[gates] 逐题字段校验 %d 处失败" % bad)
    print("[OK ] 逐题字段校验通过")


# ---------------------------------------------------------------- 文案
def compose_about_html(questions):
    from collections import Counter
    c_kind = Counter((q["source"] or {}).get("kind", "textbook") for q in questions)
    exam_n = c_kind.get("exam-original", 0) + c_kind.get("exam-adapted", 0)
    c_type = Counter(q["typeGroup"] for q in questions)
    type_part = " · ".join("%s %d" % (lbl, c_type.get(t, 0))
                           for t, lbl in [("single", "单选"), ("multi", "多选"), ("judge", "判断"),
                                          ("blank", "填空"), ("short", "简答与名词解释"), ("calc", "计算与分析")])
    return "".join([
        "<p><b>内容来源</b>：以同济大学《高等数学》第七版章节体系为骨架出题；其中 <b>%d</b> 题"
        "取自 1987–2026 年考研数学真题（原题或数据改编），出处栏标明年份与题号。</p>" % exam_n,
        "<p><b>题型分布</b>：%s；难度分基础 / 中等 / 困难三档。</p>" % type_part,
        "<p><b>判分口径</b>：客观题自动判分（多选少选、错选均 0 分）；简答与计算题<b>按采分点自评</b>"
        "（勾选「得到 / 未得到」），主观题满分 = 采分点分值之和。</p>",
        "<p><b>多选计分</b>：全对得满分；<b>少选、错选均 0 分</b>。</p>",
        "<p><b>自托管说明</b>：全站资源（题库数据、公式渲染库、字体）均自托管于本站，"
        "无任何第三方依赖；进度数据保存在浏览器本地。</p>",
    ])


def compose_footer_html(questions):
    total = len(questions)
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    lbl = [("single", "单选"), ("multi", "多选"), ("judge", "判断"),
           ("blank", "填空"), ("short", "简答与名词解释"), ("calc", "计算与分析")]
    type_part = " · ".join("%s %d" % (l, c_type.get(t, 0)) for t, l in lbl)
    return ("<p>题库共 <b>%d</b> 题：%s；难度 基础 / 中等 / 困难 三档。</p>"
            "<p>内容基准：同济大学《高等数学》第七版；真题题目标注年份与卷种。</p>" % (total, type_part))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-gates", action="store_true")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    print("[subject] 步骤 1/3：门禁链")
    questions = load_bank()
    print("      题库载入：%d 题" % len(questions))
    if not args.skip_gates:
        gate_scan_escapes()
        gate_audits(questions)
        gate_validate_bank()
        gate_sympy(questions)
        gate_fields(questions)
    else:
        print("[subject] ⚠ --skip-gates：门禁被跳过（仅限调试）")

    print("[subject] 步骤 2/3：生成分片")
    shards = shard_questions(questions)
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    exam_n = sum(1 for q in questions
                 if (q["source"] or {}).get("kind", "textbook").startswith("exam"))

    # 答案位置阈值：按实测分布 ±35% 记录（本库未做位置均衡，仅作面板参照）
    single_pos = Counter(q["answer"][0] for q in questions
                         if q["type"] == "single" and q.get("answer"))
    n_single = sum(single_pos.values()) or 1
    exp = n_single / 4.0
    lo, hi = int(exp * 0.65), int(exp * 1.35) + 1
    for L in "ABCD":
        v = single_pos.get(L, 0)
        if not (lo <= v <= hi):
            print("      [warn] 单选答案 %s 出现 %d 次，超出参考区间 [%d,%d]" % (L, v, lo, hi))
    multi_pos = Counter()
    for q in questions:
        if q["type"] == "multi":
            for a in q.get("answer") or []:
                multi_pos[a] += 1
    multi_vals = [multi_pos.get(L, 0) for L in "ABCD"]
    multi_range = (max(multi_vals) - min(multi_vals)) if multi_vals else 0

    print("[subject] 步骤 3/3：写出产物")
    os.makedirs(data_dir, exist_ok=True)
    # 写前清理：上一版构建的陈旧分片必须删除，否则 dist 里新旧并存
    import glob as _glob
    for old in _glob.glob(os.path.join(data_dir, "ch*.json")):
        os.remove(old)
    shard_entries = []
    for p in shards:
        path = os.path.join(data_dir, p["name"])
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"chapter": p["chapter"], "questions": p["questions"]},
                      f, ensure_ascii=False, indent=1)
        size = os.path.getsize(path)
        print("      %-12s %3d 题  %6.1f KB" % (p["name"], len(p["questions"]), size / 1024.0))
        if size > SHARD_BUDGET:
            raise SystemExit("[subject] 分片 %s 超预算" % p["name"])
        shard_entries.append({"file": p["name"], "chapter": p["chapter"],
                              "count": len(p["questions"]), "sha256": sha256(path)})

    sections = {kp: label for kp, label in kp_labels()}
    manifest = {
        "schema": "quiz-platform-subject-v1",
        "subject": SUBJECT,
        "sections": sections,
        "caliber": {
            "total": len(questions),
            "byType": {t: c_type.get(t, 0) for t in
                       ("single", "multi", "judge", "blank", "short", "calc")},
            "byDifficulty": {d: c_diff.get(d, 0) for d in ("basic", "medium", "hard")},
            "byChapter": {str(k): c_ch[k] for k in sorted(c_ch)},
            "limits": {"singleMin": lo, "singleMax": hi, "multiRange": multi_range},
        },
        "summary": {
            "sub": "同济第七版 %d 章 · %d 题 · 含考研真题 %d 题" % (SUBJECT["chapters"], len(questions), exam_n),
            "desc": "高等数学 %d 题刷题子站：12 章、三难度、逐题解析与考点出处，考研真题标注年份卷种。" % len(questions),
            "aboutHtml": compose_about_html(questions),
            "footerHtml": compose_footer_html(questions),
            "realExamTagged": exam_n,
        },
        "shards": shard_entries,
    }
    with io.open(os.path.join(data_dir, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("[OK ] manifest.json（%d 分片，共 %d 题，真题 %d 题）" % (len(shard_entries), len(questions), exam_n))
    print("[subject] 导出完成：%s" % data_dir)


if __name__ == "__main__":
    main()
