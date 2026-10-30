# -*- coding: utf-8 -*-
"""题库数据门禁（Task 4）。

在既有五道门禁（scan_escapes / audit_choice / audit_open / verify_quiz /
check_html）之外补一道**数据契约门禁**：题目从 180 道教材题扩到 680 道
（教材 + 真题）之后，「结构对不对」已经不能只靠 `common.audit()` 兜住，
还需要验证来源字段、溯源级别、知识点归属与跨卷去重。

用法:
    python tools/validate_bank.py            # 人读报告
    python tools/validate_bank.py --json     # 机读 JSON
退出码: 0 = 通过；1 = 有 error。

输出包含题型 / 难度 / 章节 / 知识点四维分布，以及 provenance 级别分布
（原题 / 改编 / 教材）——最后一栏是给「题库是否真的接上了真题」看的。
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(errors="replace")
    except Exception:
        pass

from qa_bank.common import load_bank          # noqa: E402
from qa_bank.schema import (                    # noqa: E402
    validate_question, normalize_question, fingerprint,
)

# 题量目标：180 教材题 + 500 真题 = 680。
# 放宽到下限：真题按批补齐，分批构建时不必每次都失败。
TOTAL_TARGET = 680
TOTAL_MIN = 180


def main():
    args = sys.argv[1:]
    as_json = "--json" in args

    questions = load_bank()
    errors, warns = [], []
    for q in questions:
        for level, msg in validate_question(q):
            (errors if level == "error" else warns).append("%s: %s" % (q.get("id", "?"), msg))

    # --- id 唯一 ---
    ids = [q.get("id") for q in questions]
    dup = sorted({i for i, c in Counter(ids).items() if c > 1})
    for d in dup:
        errors.append("重复 id：%s" % d)

    # --- 跨卷题干指纹去重 ---
    fp_map = defaultdict(list)
    for q in questions:
        fp_map[fingerprint(q)].append(q.get("id"))
    dup_fp = {k: v for k, v in fp_map.items() if len(v) > 1}
    for k, v in sorted(dup_fp.items()):
        errors.append("题干重复（指纹 %s）：%s" % (k, " / ".join(v)))

    # --- 分布统计 ---
    by_type = Counter(q.get("typeGroup") for q in questions)
    by_diff = Counter(q.get("difficulty") for q in questions)
    by_ch = Counter(q.get("chapter") for q in questions)
    by_kp = Counter()
    for q in questions:
        for kp in (q.get("knowledgePoints") or [q.get("knowledgePoint")]):
            by_kp[kp] += 1
    by_prov = Counter()
    by_kind = Counter()
    for q in questions:
        src = q.get("source") or {}
        by_kind[src.get("kind")] += 1
        by_prov[(q.get("provenance") or {}).get("level")] += 1

    # --- 题量门禁 ---
    if len(questions) < TOTAL_MIN:
        errors.append("题量 %d < 下限 %d" % (len(questions), TOTAL_MIN))
    elif len(questions) < TOTAL_TARGET:
        warns.append("题量 %d < 目标 %d（真题尚未补齐）" % (len(questions), TOTAL_TARGET))

    report = {
        "total": len(questions),
        "target": TOTAL_TARGET,
        "byTypeGroup": dict(by_type),
        "byDifficulty": dict(by_diff),
        "byChapter": {str(k): v for k, v in sorted(by_ch.items(), key=lambda x: (x[0] is None, x[0]))},
        "bySourceKind": dict(by_kind),
        "byProvenance": {str(k): v for k, v in by_prov.items()},
        "knowledgePointCoverage": len(by_kp),
        "duplicateIds": dup,
        "duplicateFingerprints": len(dup_fp),
        "errors": errors,
        "warnings": warns,
    }

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=" * 66)
        print("题量：%d（目标 %d）" % (len(questions), TOTAL_TARGET))
        print("题型分布：%s" % dict(by_type))
        print("难度分布：%s" % dict(by_diff))
        print("章节分布：%s" % report["byChapter"])
        print("出处类型：%s" % dict(by_kind))
        print("溯源级别：%s" % report["byProvenance"])
        print("覆盖知识点：%d 个" % len(by_kp))
        print("-" * 66)
        for w in warns:
            print("  [warn] %s" % w)
        if errors:
            print("失败：%d 项 error" % len(errors))
            for e in errors[:60]:
                print("  [FAIL] %s" % e)
            if len(errors) > 60:
                print("  ... 另有 %d 项" % (len(errors) - 60))
        else:
            print("数据契约门禁通过。")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
