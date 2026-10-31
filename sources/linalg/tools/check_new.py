# -*- coding: utf-8 -*-
"""扩写章节（ch1b–ch6b）单章质检器。

用法：
    python check_new.py ch1b
    python check_new.py ch1b ch2b ...

检查项：
    S1  配额核对：题型/难度计数必须等于本文件的 QUOTA 表
    S2  结构自检（audit full=False：选项合法、采分点数、解析、出处）
    S3  B1–B6 内容检查（复用 verify_quiz 的 check_content）
    S4  题干与全库去重（前 60 字键；基准 = current research/existing_stems.txt）
    S5  SymPy 数值复核（verify 项逐条执行）
    S6  客观题答案键 ↔ 解析自洽（audit_choice.check）
    S7  主观题结构（audit_open.check）
    S8  LaTeX 转义扫描（scan_escapes，致命级）
    S9  客观题答案键 ↔ 解析**数值**一致（audit_value.check）——补 S6 的盲区：
        S6 只认「解析里点名字母」，而实测 250 道客观题里只有 44 道点了名，
        其余 206 道在字母规则下无保护（q-039 就漏在这里：答案键 B，
        解析自己算的是 A）。
退出码非 0 即存在 FAIL，扩写未通过。

关于「配额」的两处口径：
    本文件 QUOTA 表      = 每个扩写章**该写多少**（写作计划）
    qa_bank/target.py   = **全库**实际口径（题型×章节矩阵、难度、阈值）——单一事实源
    两者必须自洽：S1 会用 target.py 的 MATRIX 减去基础库实际题数，
    反推出本章该有多少题，与 QUOTA 表逐项对账；对不上直接判 FAIL。
    （难度配额目前只在本表里，target.py 只记全库总量。）
"""
import io
import os
import sys
from collections import Counter, defaultdict

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---------------------------------------------------------------- 配额表（新题，共 320）
QUOTA = {
    "ch1b": {"type": {"single": 9, "multi": 9, "judge": 9, "blank": 9, "short": 8, "calc": 8},
             "diff": {"basic": 26, "medium": 17, "hard": 9}},
    "ch2b": {"type": {"single": 10, "multi": 10, "judge": 10, "blank": 10, "short": 10, "calc": 10},
             "diff": {"basic": 30, "medium": 21, "hard": 9}},
    "ch3b": {"type": {"single": 8, "multi": 8, "judge": 8, "blank": 8, "short": 8, "calc": 8},
             "diff": {"basic": 24, "medium": 15, "hard": 9}},
    "ch4b": {"type": {"single": 10, "multi": 10, "judge": 10, "blank": 10, "short": 10, "calc": 10},
             "diff": {"basic": 28, "medium": 20, "hard": 12}},
    "ch5b": {"type": {"single": 12, "multi": 11, "judge": 11, "blank": 12, "short": 12, "calc": 12},
             "diff": {"basic": 33, "medium": 27, "hard": 10}},
    "ch6b": {"type": {"single": 5, "multi": 5, "judge": 5, "blank": 5, "short": 5, "calc": 5},
             "diff": {"basic": 16, "medium": 10, "hard": 4}},
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    quiet = "--quiet" in sys.argv
    if not args:
        args = ["ch1b", "ch2b", "ch3b", "ch4b", "ch5b", "ch6b"]

    from qa_bank.common import audit, GROUP
    from verify_quiz import check_content, run_sympy_checks
    from audit_choice import check as check_choice
    from audit_open import check as check_open
    from qa_bank import target as T

    # 去重基准（existing_stems.txt）= 当前全库题干的导出，由 tools\export_stems.py 生成。
    # 格式：`题号 | 模块 | 题型 | 题干`。**必须带模块名**：
    #   题号会随章节增删整体重排（加一章，后面的题号全变），
    #   光靠题号认不出「这条基准是不是本章自己的题」——
    #   曾因如此把本章每一道题都误报成「与 q-xxx 重复」。
    #   按模块名剔，既不误报自己，又不放过别的章真撞题干。
    # 注意：这里**不预先 import 基础章**。common.py 的题号由全局计数器按导入顺序分配，
    # 多 import 一次就会把待检章的题号整体顶偏（实测 q-001… 被顶成 q-181…），
    # 报错信息里的题号就全错了。基础库的章节 × 题型计数改从基准文件里数。
    base_by_key = {}
    base_type = Counter()
    stems_path = os.path.join(HERE, "research", "existing_stems.txt")
    with io.open(stems_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split("|", 3)
            if len(parts) >= 4:
                qid, mname, qtype = parts[0].strip(), parts[1].strip(), parts[2].strip()
                key = parts[3].strip()[:60]
                base_by_key.setdefault(key, []).append((mname, qid))
                if not mname.endswith("b"):          # ch1..ch6 = 基础库
                    base_type[(int(mname[2]), GROUP.get(qtype, qtype))] += 1

    grand_fail = 0
    for name in args:
        try:
            mod = __import__("qa_bank." + name, fromlist=["Q"])
        except ImportError:
            print("=" * 72)
            print("%s：模块不存在，跳过（该章还没写）" % name)
            continue
        qs = mod.Q
        err, warn = [], []
        print("=" * 72)
        print("%s：%d 题" % (name, len(qs)))

        # S1 配额
        want = QUOTA[name]
        ch = int(name[2])
        ct = Counter(q["typeGroup"] for q in qs)
        cd = Counter(q["difficulty"] for q in qs)
        for t, n in want["type"].items():
            if ct.get(t, 0) != n:
                err.append("S1 题型 %s = %d，配额 %d" % (t, ct.get(t, 0), n))
        for d, n in want["diff"].items():
            if cd.get(d, 0) != n:
                err.append("S1 难度 %s = %d，配额 %d" % (d, cd.get(d, 0), n))
        # S1b 本表配额 ↔ target.py 的 MATRIX 对账（两处口径不许各说各话）
        for t, n in want["type"].items():
            implied = T.MATRIX[t][ch] - base_type.get((ch, t), 0)
            if implied != n:
                err.append("S1b 配额表与 target.py 不一致：%s %s 本表 %d，"
                           "target.py 矩阵推出 %d" % (name, t, n, implied))
        kp = sorted(set(q["knowledgePoint"] for q in qs))
        print("  题型 %s\n  难度 %s\n  知识点 %s" % (dict(ct), dict(cd), ",".join(kp)))

        # S2/S3/S4
        _, aerr = audit(qs, full=False)
        err.extend(aerr)
        cell = defaultdict(int)
        for q in qs:
            cell[q["chapter"]] += 1
        for ch in cell:
            if ch != int(name[2]):
                err.append("S2 出现非本章题目 chapter=%d（kp 写错？）" % ch)
        check_content(qs, err, warn)
        for q in qs:
            key = (q.get("stem") or "").strip()[:60]
            others = [(m, i) for (m, i) in base_by_key.get(key, []) if m != name]
            if others:
                err.append("S4 %s 题干与 %s 的 %s 重复" % (q["id"], others[0][0], others[0][1]))

        # S5 SymPy
        nver = run_sympy_checks(qs, err, quiet)

        # S6/S7
        for p in check_choice(qs):
            err.append("S6 %s" % p)
        bad_open = check_open(qs)[0]
        for p in bad_open:
            err.append("S7 %s" % p)

        # S8 转义扫描
        from scan_escapes import string_tokens, find_issues
        path = os.path.join(HERE, "qa_bank", name + ".py")
        segs = list(string_tokens(path))
        for row, col, body in segs:
            for idx, level in find_issues(body):
                err.append("S8 %s:%d 转义问题[%s] …%s…" % (name, row, level, body[max(0, idx - 10):idx + 16]))

        # S9 答案键 ↔ 解析数值一致性（S6 只认字母点名，这里补数值这条线）
        from audit_value import check as check_value
        for p in check_value(qs):
            err.append("S9 %s" % p)

        for w in warn:
            print("  [warn] %s" % w)
        print("  SymPy 复核项：%d" % nver)
        if err:
            grand_fail += len(err)
            print("  FAIL %d 项" % len(err))
            for e in err:
                print("    [FAIL] %s" % e)
        else:
            print("  全部通过。")
    print("=" * 72)
    if grand_fail:
        print("共 %d 项失败" % grand_fail)
        return 1
    print("所查章节全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
