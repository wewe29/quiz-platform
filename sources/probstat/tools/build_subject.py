# -*- coding: utf-8 -*-
"""概率论与数理统计 · 学科产物导出（自包含，不 import qa_bank）。

用法：
    python tools/build_subject.py                # 导出到平台仓 subjects/probstat
    python tools/build_subject.py --out <dir>
    python tools/build_subject.py --skip-gates   # 仅调试

题库结构（8 章，首版 ~100 题）：
    ch1 随机事件与概率 (14)
    ch2 一维随机变量及其分布 (16)
    ch3 多维随机变量及其分布 (14)
    ch4 随机变量的数字特征 (14)
    ch5 大数定律与中心极限定理 (9)
    ch6 数理统计的基本概念 (12)
    ch7 参数估计 (12)
    ch8 假设检验 (9)
采分点口径：CALC 4 点×2 分；SHORT 3 点×2 分。
所有概率/期望/方差计算均可用 sympy.stats 核验。
"""
import argparse
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))

SUBJECT = {
    "id": "probstat",
    "name": "概率论与数理统计",
    "textbook": "浙江大学《概率论与数理统计》第四版（高等教育出版社）",
    "bankId": "probstat-zjuda-v1",
    "chapters": 8,
    "chapterLabels": {
        "1": "第1章 随机事件与概率",
        "2": "第2章 一维随机变量及其分布",
        "3": "第3章 多维随机变量及其分布",
        "4": "第4章 随机变量的数字特征",
        "5": "第5章 大数定律与中心极限定理",
        "6": "第6章 数理统计的基本概念",
        "7": "第7章 参数估计",
        "8": "第8章 假设检验",
    },
}

SHARD_BUDGET = 200 * 1024
SEC = {
    "1.1": "随机试验与样本空间", "1.2": "概率的定义与性质",
    "1.3": "等可能概型（古典概型）", "1.4": "条件概率与乘法公式",
    "1.5": "全概率公式与贝叶斯公式", "1.6": "独立性",
    "2.1": "离散型随机变量", "2.2": "分布函数",
    "2.3": "连续型随机变量与概率密度", "2.4": "常见分布（二项/泊松/指数/正态）",
    "2.5": "随机变量函数的分布",
    "3.1": "二维随机变量与联合分布", "3.2": "边缘分布",
    "3.3": "条件分布", "3.4": "随机变量的独立性",
    "4.1": "数学期望", "4.2": "方差",
    "4.3": "协方差与相关系数", "4.4": "矩与切比雪夫不等式",
    "5.1": "依概率收敛", "5.2": "大数定律",
    "5.3": "中心极限定理",
    "6.1": "总体与样本", "6.2": "统计量与抽样分布",
    "6.3": "三大分布（χ²/t/F）",
    "7.1": "点估计（矩估计与极大似然）", "7.2": "估计量的评价标准",
    "7.3": "区间估计",
    "8.1": "假设检验的基本思想", "8.2": "正态总体参数的假设检验",
}


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


def Q(qtype, diff, kp, stem, answer=None, options=None, answer_text=None,
      points=None, expl="", mis=None, tags=None, variant_group=None,
      verify=None, qid=None, accept=None):
    chapter = int(kp.split(".")[0])
    if qtype == "judge" and not options:
        options = ["正确", "错误"]
    if points:
        pts = [{"text": p["text"] if isinstance(p, dict) else p,
                "partial": p.get("partial", 2) if isinstance(p, dict) else 2}
               for p in points]
    else:
        pts = None
    return {
        "id": qid or "ps-%03d" % (len(ALL_QUESTIONS) + 1),
        "type": qtype,
        "typeGroup": {"single": "single", "multi": "multi", "judge": "judge",
                      "blank": "blank", "term": "short", "short": "short", "calc": "calc"}.get(qtype, qtype),
        "difficulty": diff,
        "chapter": chapter,
        "knowledgePoint": kp,
        "source": {"text": SUBJECT["textbook"] + " §" + kp, "kind": "textbook"},
        "stem": stem,
        "options": options,
        "answer": answer or [],
        "accept": accept,
        "answerText": answer_text,
        "points": pts,
        "explanation": expl,
        "misconception": mis,
        "extension": None,
        "tags": tags or [],
        "verify": verify or [],
        "variantGroup": variant_group,
    }


ALL_QUESTIONS = []


def add(q):
    ALL_QUESTIONS.append(q)


# ================================================================ 内容导入
def load_content():
    """从分章模块载入题目。模块自本目录 qa_prob/ 导入。"""
    prob_dir = os.path.join(HERE, "qa_prob")
    if prob_dir not in sys.path:
        sys.path.insert(0, os.path.dirname(prob_dir))
    for mod_name in ("qa_prob.ch1", "qa_prob.ch2", "qa_prob.ch3", "qa_prob.ch4", "qa_prob.ch58"):
        try:
            mod = __import__(mod_name, fromlist=["Q"])
            for q in mod.Q:
                ALL_QUESTIONS.append(q)
        except ImportError as e:
            print("[bank] 跳过缺失章节 ch%d：%s" % (ch, e))


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


def gates(questions):
    ids = [q["id"] for q in questions]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit("[gates] 重复题号：%s" % dup[:8])
    bad = 0
    stems = {}
    for q in questions:
        if not q.get("stem") or not q.get("explanation"):
            print("      [gate] %s 缺题干或解析" % q["id"]); bad += 1
        if q["type"] in ("single", "multi"):
            letters = "ABCDE"[:len(q.get("options") or [])]
            for a in q.get("answer") or []:
                if a not in letters:
                    print("      [gate] %s 答案 %s 不在选项内" % (q["id"], a)); bad += 1
            if q["type"] == "single" and len(q.get("answer") or []) != 1:
                print("      [gate] %s 单选答案数 != 1" % q["id"]); bad += 1
        if q["type"] in ("short", "calc") and not (q.get("answerText") and q.get("points")):
            print("      [gate] %s 主观题缺参考答案/采分点" % q["id"]); bad += 1
        skey = (q.get("stem") or "")[:50]
        if skey in stems:
            print("      [gate] %s 与 %s 题干重复" % (q["id"], stems[skey])); bad += 1
        stems[skey] = q["id"]
    if bad:
        raise SystemExit("[gates] %d 处问题，拒绝导出" % bad)
    print("[OK ] 门禁：题号唯一 / 解析齐备 / 答案在选项内 / 无重复题干")


def compose_about_html(questions):
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    type_part = " · ".join(
        "%s %d" % (lbl, c_type.get(t, 0))
        for t, lbl in [("single", "单选"), ("multi", "多选"), ("judge", "判断"),
                       ("blank", "填空"), ("short", "简答"), ("calc", "计算")])
    return "".join([
        "<p><b>内容来源</b>：以浙江大学《概率论与数理统计》第四版为基准出题，每题标注考点出处。</p>",
        "<p><b>题型分布</b>：%s；难度分基础 / 中等 / 困难三档。</p>" % type_part,
        "<p><b>判分口径</b>：客观题自动判分；简答与计算题<b>按采分点自评</b>。</p>",
        "<p><b>自托管说明</b>：全站资源自托管，无第三方依赖；进度保存在浏览器本地。</p>",
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-gates", action="store_true")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    if args.skip_gates:
        print("[subject] ⚠ --skip-gates")
    load_content()
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in ALL_QUESTIONS)
    c_diff = Counter(q["difficulty"] for q in ALL_QUESTIONS)
    c_ch = Counter(q["chapter"] for q in ALL_QUESTIONS)
    print("      题库载入：%d 题" % len(ALL_QUESTIONS))

    if not args.skip_gates:
        gates(ALL_QUESTIONS)

    shards = shard_questions(ALL_QUESTIONS)
    os.makedirs(data_dir, exist_ok=True)
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
            raise SystemExit("[subject] 分片超预算")
        shard_entries.append({"file": p["name"], "chapter": p["chapter"],
                              "count": len(p["questions"]), "sha256": sha256(path)})

    manifest = {
        "schema": "quiz-platform-subject-v1",
        "subject": SUBJECT,
        "sections": SEC,
        "caliber": {
            "total": len(ALL_QUESTIONS),
            "byType": {t: c_type.get(t, 0) for t in ("single", "multi", "judge", "blank", "short", "calc")},
            "byDifficulty": {d: c_diff.get(d, 0) for d in ("basic", "medium", "hard")},
            "byChapter": {str(k): c_ch[k] for k in sorted(c_ch)},
            "limits": {"singleMin": 0, "singleMax": 9999, "multiRange": 9999},
        },
        "summary": {
            "sub": "8 章 · %d 题 · 章节小测 + 综合测试" % len(ALL_QUESTIONS),
            "desc": "概率论与数理统计 %d 题刷题子站：8 章、三难度、逐题解析与考点出处。" % len(ALL_QUESTIONS),
            "aboutHtml": compose_about_html(ALL_QUESTIONS),
            "footerHtml": "<p>题库共 <b>%d</b> 题（浙大第四版 §1–§8）。</p>" % len(ALL_QUESTIONS),
            "realExamTagged": 0,
        },
        "shards": shard_entries,
    }
    with io.open(os.path.join(data_dir, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("[OK ] manifest.json（%d 分片，共 %d 题）" % (len(shard_entries), len(ALL_QUESTIONS)))
    print("[subject] 导出完成：%s" % data_dir)


if __name__ == "__main__":
    main()
