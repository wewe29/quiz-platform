# -*- coding: utf-8 -*-
r"""全库内容 CLI —— 跨四科题库的统计 / 查重 / 检索 / 导出工具（维护者用，零依赖）。

用法（在平台仓根目录）：
    python tools/platform/content_cli.py stats                 # 各科总览：题量/题型/难度/解析覆盖率
    python tools/platform/content_cli.py matrix [--subject ml] # 章节 × 题型矩阵
    python tools/platform/content_cli.py dupes                 # 全库题干指纹查重（跨科）
    python tools/platform/content_cli.py find 关键词            # 全库检索（题干/解析/答案）
    python tools/platform/content_cli.py export [--subject ml] [--chapter 3] [--type single]
                                               [--limit 20] [--out 审校.md]
    python tools/platform/content_cli.py stats --json          # 机读输出

数据源：subjects/<id>/data/*.json（构建产物，先跑 build_all 保证最新）。
定位：给维护者的内容管理工具——与运行时无关，不引任何依赖。
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
SUBJECTS_DIR = os.path.join(PLATFORM, "subjects")

TYPE_LABEL = {"single": "单选", "multi": "多选", "judge": "判断", "blank": "填空",
              "term": "名词解释", "short": "简答", "calc": "计算", "essay": "论述"}


def load_all():
    """读取全部学科分片。返回 {subject: {"manifest": …, "questions": […]}}。"""
    out = {}
    for mpath in sorted(glob.glob(os.path.join(SUBJECTS_DIR, "*", "data", "manifest.json"))):
        sid = os.path.basename(os.path.dirname(os.path.dirname(mpath)))
        with open(mpath, encoding="utf-8") as f:
            manifest = json.load(f)
        questions = []
        for s in manifest.get("shards", []):
            sp = os.path.join(os.path.dirname(mpath), s["file"])
            if os.path.isfile(sp):
                with open(sp, encoding="utf-8") as f:
                    questions.extend(json.load(f).get("questions", []))
        out[sid] = {"manifest": manifest, "questions": questions}
    return out


def fp(stem):
    """题干指纹：去空白与标点，**保留**字母数字——
    「2x+1」与「2x-1」是不同的题，剥掉字母数字会把它们误判成重复。"""
    return re.sub(r"[\s　。，、；：？。（）“”\"'‘’$\\]", "", stem)[:60]


def cmd_stats(args):
    banks = load_all()
    report = []
    grand = 0
    for sid, b in sorted(banks.items()):
        qs = b["questions"]
        grand += len(qs)
        from collections import Counter
        c_type = Counter(q["type"] for q in qs)
        c_diff = Counter(q["difficulty"] for q in qs)
        n_expl = sum(1 for q in qs if (q.get("explanation") or q.get("answerText")))
        subjective = [q for q in qs if q["type"] in ("term", "short", "calc")]
        n_pts = sum(1 for q in subjective if q.get("points"))
        n_mis = sum(1 for q in qs if q.get("misconception"))
        avg_stem = sum(len(q.get("stem") or "") for q in qs) // max(len(qs), 1)
        avg_expl = sum(len(q.get("explanation") or "") for q in qs) // max(len(qs), 1)
        report.append({
            "subject": sid, "name": b["manifest"]["subject"]["name"], "total": len(qs),
            "byType": dict(c_type), "byDifficulty": dict(c_diff),
            "explanationCoverage": round(n_expl / max(len(qs), 1) * 100, 1),
            "pointsCoverage": round(n_pts / max(len(subjective), 1) * 100, 1),
            "subjectiveCount": len(subjective),
            "misconceptionCoverage": round(n_mis / max(len(qs), 1) * 100, 1),
            "avgStemLen": avg_stem, "avgExplLen": avg_expl,
        })
    if args.json:
        print(json.dumps({"grandTotal": grand, "subjects": report}, ensure_ascii=False, indent=1))
        return 0
    print("全库总题量：%d（%d 科）\n" % (grand, len(report)))
    for r in report:
        print("◆ %s（%s）— %d 题" % (r["name"], r["subject"], r["total"]))
        print("  题型  :", " · ".join("%s %d" % (TYPE_LABEL.get(k, k), v) for k, v in sorted(r["byType"].items())))
        print("  难度  :", " · ".join("%s %d" % (k, v) for k, v in sorted(r["byDifficulty"].items())))
        print("  覆盖  : 解析 %s%% · 采分点 %s%% · 易错点 %s%%" % (
            r["explanationCoverage"], r["pointsCoverage"], r["misconceptionCoverage"]))
        print("  体量  : 题干均 %d 字 · 解析均 %d 字" % (r["avgStemLen"], r["avgExplLen"]))
    return 0


def cmd_matrix(args):
    banks = load_all()
    if args.subject:
        banks = {k: v for k, v in banks.items() if k == args.subject}
    for sid, b in sorted(banks.items()):
        qs = b["questions"]
        chapters = sorted({q["chapter"] for q in qs})
        types = sorted({q["type"] for q in qs})
        print("◆ %s（%s）章节 × 题型" % (b["manifest"]["subject"]["name"], sid))
        head = "  章节    | " + " | ".join("%-6s" % TYPE_LABEL.get(t, t) for t in types)
        print(head)
        print("  " + "-" * (len(head) - 2))
        for ch in chapters:
            row = [str(sum(1 for q in qs if q["chapter"] == ch and q["type"] == t)) for t in types]
            label = b["manifest"]["subject"]["chapterLabels"].get(str(ch), "第%d章" % ch)
            print("  %-8s | %s" % (label[:8], " | ".join("%-6s" % x for x in row)))
        total_row = [str(sum(1 for q in qs if q["type"] == t)) for t in types]
        print("  %-8s | %s" % ("合计", " | ".join("%-6s" % x for x in total_row)))
        print()
    return 0


def cmd_dupes(args):
    banks = load_all()
    seen = {}
    dupes = []
    for sid, b in sorted(banks.items()):
        for q in b["questions"]:
            key = fp(q.get("stem") or "")
            if not key:
                continue
            if key in seen and seen[key][0] != sid:
                dupes.append((seen[key], (sid, q["id"]), q.get("stem") or ""))
            elif key in seen:
                dupes.append((seen[key], (sid, q["id"]), q.get("stem") or ""))
            else:
                seen[key] = (sid, q["id"])
    if not dupes:
        print("全库指纹查重：无重复题干 ✓")
        return 0
    print("全库指纹查重：%d 组疑似重复\n" % len(dupes))
    for a, b_, stem in dupes:
        print("  %s/%s  ↔  %s/%s" % (a[0], a[1], b_[0], b_[1]))
        print("    %s" % stem[:70])
    return 0


def cmd_find(args):
    keyword = args.keyword.lower()
    banks = load_all()
    hits = 0
    for sid, b in sorted(banks.items()):
        for q in b["questions"]:
            hay = ((q.get("stem") or "") + (q.get("explanation") or "") +
                   json.dumps(q.get("answer") or [], ensure_ascii=False) +
                   (q.get("answerText") or "")).lower()
            if keyword in hay:
                hits += 1
                ans = q.get("answer")
                ans_s = "/".join(ans) if isinstance(ans, list) else str(ans)
                print("%s/%s [%s] %s" % (sid, q["id"], TYPE_LABEL.get(q["type"], q["type"]),
                                         (q.get("stem") or "")[:60]))
                print("    答案：%s" % ans_s[:60])
                if hits >= getattr(args, "limit", 30):
                    print("（已达 %d 条上限，可用 --limit 放宽）" % args.limit)
                    return 0
    print("共 %d 处命中「%s」" % (hits, keyword))
    return 0


def cmd_export(args):
    banks = load_all()
    if args.subject:
        banks = {k: v for k, v in banks.items() if k == args.subject}
    rows = []
    for sid, b in sorted(banks.items()):
        for q in b["questions"]:
            if args.chapter and q["chapter"] != args.chapter:
                continue
            if args.type and q["type"] != args.type:
                continue
            if args.difficulty and q["difficulty"] != args.difficulty:
                continue
            rows.append((sid, q))
    if args.limit:
        rows = rows[:args.limit]
    lines = ["# 题库审校清单（%d 题）\n" % len(rows)]
    for sid, q in rows:
        ans = q.get("answer")
        ans_s = "/".join(ans) if isinstance(ans, list) else str(ans or "")
        lines.append("## %s/%s [%s·%s] 第%d章 知识点%s" % (
            sid, q["id"], TYPE_LABEL.get(q["type"], q["type"]), q.get("difficulty", "?"),
            q.get("chapter", 0), q.get("knowledgePoint", "")))
        lines.append("")
        lines.append("**题干**：%s" % (q.get("stem") or ""))
        if q.get("options"):
            letters = "ABCDE"
            for i, o in enumerate(q["options"]):
                lines.append("- %s. %s" % (letters[i], o))
        lines.append("")
        lines.append("**答案**：%s" % ans_s)
        if q.get("answerText"):
            lines.append("")
            lines.append("**参考答案**：%s" % q["answerText"])
        lines.append("")
        lines.append("**解析**：%s" % (q.get("explanation") or ""))
        lines.append("")
    out = args.out or "题库审校清单.md"
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("已导出 %d 题到 %s" % (len(rows), os.path.abspath(out)))
    return 0


def main():
    ap = argparse.ArgumentParser(description="全库内容 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("stats", help="各科总览统计")
    s1.add_argument("--json", action="store_true")
    s2 = sub.add_parser("matrix", help="章节 × 题型矩阵")
    s2.add_argument("--subject")
    s3 = sub.add_parser("dupes", help="全库题干指纹查重")
    s4 = sub.add_parser("find", help="全库检索")
    s4.add_argument("keyword")
    s4.add_argument("--limit", type=int, default=30)
    s5 = sub.add_parser("export", help="导出审校清单（Markdown）")
    s5.add_argument("--subject")
    s5.add_argument("--chapter", type=int)
    s5.add_argument("--type")
    s5.add_argument("--difficulty")
    s5.add_argument("--limit", type=int)
    s5.add_argument("--out")
    args = ap.parse_args()
    return {"stats": cmd_stats, "matrix": cmd_matrix, "dupes": cmd_dupes,
            "find": cmd_find, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
