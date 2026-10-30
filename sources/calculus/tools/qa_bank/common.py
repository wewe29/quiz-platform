# -*- coding: utf-8 -*-
"""《高等数学》题库数据公共定义：构造函数、考点出处表、题型常量。

体例说明（沿用本机 线性代数复习资料 题库的标记体系）：
    ⭐重点 📌考点 📖必背 🧗难点 ⚠️易错点 ℹ️了解

每题解析固定三段式：
    1) 答案依据    —— 为什么是这个答案
    2) 考点出处    —— source.text
    3) 辨析 / ⚠️易错点 —— 客观题必须逐项说明其他选项错在哪

内容来源口径：本机不存在《高等数学》课程资料（课件/笔记/作业/真题均已全盘检索），
故题库主体以同济大学《高等数学》第七版（高等教育出版社）章节体系为基准命题，
每题标注教材节次出处；引申内容一律标注「引申」。
"""
import os

from .latex import fix_structure as _fix_latex   # noqa: E402

# ---------------------------------------------------------------- 题型常量
SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC = (
    "single", "multi", "judge", "blank", "term", "short", "calc")

GROUP = {
    SINGLE: SINGLE, MULTI: MULTI, JUDGE: JUDGE,
    BLANK: BLANK, SHORT: SHORT, CALC: CALC,
    # 名词解释与简答合并为同一「简答与名词解释」大组
    TERM: SHORT,
}

TYPE_GROUP_LABEL = {
    SINGLE: "单选", MULTI: "多选", JUDGE: "判断",
    BLANK: "填空", SHORT: "简答与名词解释", CALC: "计算与分析题",
}

# ---------------------------------------------------------------- 章节与知识点出处
# 实体已迁到 `catalog.py`（知识点目录的唯一事实源）。这里做转发，
# 保证 `from .common import SEC` 的既有调用方（ch*.py / verify_quiz.py 等）零改动。
from .catalog import SEC  # noqa: F401,E402

# ---------------------------------------------------------------- 构造函数
_COUNTER = {"n": 0}


def Q(qtype, diff, kp, stem, answer=None, options=None, answer_text=None,
      points=None, expl="", mis=None, ext=None, tags=None, src=None,
      kind="textbook", accept=None, verify=None, qid=None,
      src_year=None, src_region=None, src_paper=None, src_number=None,
      src_url=None, prov=None, kps=None):
    """构造一道题。

    qtype      : single/multi/judge/blank/term/short/calc
    diff       : basic/medium/hard
    kp         : 知识点 key，如 "1.7"
    stem       : 题干（可含 $LaTeX$）
    answer     : 客观题答案字母数组；填空题答案字符串数组
    options    : 客观题选项数组
    answer_text: 主观题参考答案全文
    points     : 主观题采分点 list[str] 或 list[dict]
    expl       : 解析正文（含答案依据 + 辨析）
    mis        : 本题专属易错点
    ext        : 引申补充（必须以「引申」开头）
    src        : 覆盖默认出处文本
    kind       : textbook/exam-original/exam-adapted/extension
    accept     : 填空题可接受的其他写法
    verify     : 可核验项 list[dict{desc,code,expected}]（SymPy 复核用）

    --- 真题接入（v2 新增）---
    src_year   : 试卷年份，如 2024（真题必填）
    src_region : 地区，如「全国」或省份名（真题必填）
    src_paper  : 卷别，如「数学一」（真题必填）
    src_number : 卷内题号（真题必填）
    src_url    : 可点开的来源 URL（exam-original 必填）
    prov       : dict，provenance 覆盖值，如 {"level":"original","url":...,"note":...}
    kps        : 附属知识点 list[str]（真题常跨节次）
    """
    _COUNTER["n"] += 1
    qid = qid or ("q-%03d" % _COUNTER["n"])
    chapter = int(kp.split(".")[0])
    # 判断题固定两个选项：A=正确，B=错误。由构造器统一注入，
    # 避免出现「判断题无 options → 页面渲染不出任何作答控件」的死题。
    if qtype == JUDGE and not options:
        options = ["正确", "错误"]
    is_exam = kind in ("exam-original", "exam-adapted")
    if is_exam and not src:
        raise ValueError("真题必须给出 src 出处文本（例：2024 考研数学一 第 12 题）")
    if kind == "exam-original" and not src_url:
        # 把错误拦在「写题那一刻」，而不是构建那一刻——构建期才发现要回改源码。
        raise ValueError("exam-original 必须给出 src_url（可点开的来源链接）")
    if src is None:
        src = SEC.get(kp, kp)
    if kind == "extension":
        src = src + "　〔引申〕"
    if points:
        pts = []
        for p in points:
            if isinstance(p, dict):
                pts.append({"text": _fix_latex(p["text"]), "partial": p.get("partial", 2)})
            else:
                pts.append({"text": _fix_latex(p), "partial": 2})
    else:
        pts = None
    prov = dict(prov or {})
    prov.setdefault("level", ("original" if kind == "exam-original" else "adapted")
                    if is_exam else None)
    prov.setdefault("url", src_url if kind == "exam-original" else None)
    prov.setdefault("verifiedAt", None)
    prov.setdefault("note", "")
    return {
        "id": qid,
        "type": qtype,
        "typeGroup": GROUP[qtype],
        "difficulty": diff,
        "chapter": chapter,
        "knowledgePoint": kp,
        "knowledgePoints": list(kps) if kps else [kp],
        "source": {
            "text": src,
            "kind": kind,
            "year": src_year,
            "region": src_region,
            "paper": src_paper,
            "number": src_number,
            "url": src_url,
        },
        "provenance": prov,
        "stem": _fix_latex(stem),
        "options": [_fix_latex(o) for o in options] if options else options,
        "answer": ([_fix_latex(a) for a in answer] if isinstance(answer, list)
                   else _fix_latex(answer) if isinstance(answer, str) else answer)
        if answer is not None else [],
        "accept": [_fix_latex(a) for a in accept] if accept else accept,
        "answerText": _fix_latex(answer_text) if answer_text else answer_text,
        "points": pts,
        "explanation": _fix_latex(expl),
        "misconception": _fix_latex(mis) if mis else mis,
        "extension": _fix_latex(ext) if ext else ext,
        "tags": tags or [],
        "verify": verify or [],
    }


def load_bank(chapters=None):
    """载入 ch1..ch12 全部题目，按 (章节, 题型, 难度, 知识点) 稳定排序并分配 idx。

    chapters 为 None 时载入全部十二章；缺失的章会被跳过并打印提示，
    便于分章写作期间做「部分构建」预览（正式构建仍要求 180 题）。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    order = ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7",
             "ch8", "ch9", "ch10", "ch11", "ch12"]
    if chapters is not None:
        order = [c for c in order if c in set(chapters)]
    allq = []
    for name in order:
        try:
            mod = __import__("qa_bank." + name, fromlist=["Q"])
        except ImportError:
            print("[bank] 跳过缺失章节：%s" % name)
            continue
        allq.extend(mod.Q)

    # 真题模块（按「卷 × 年份」分模块，见 qa_bank/exam/）。
    # 分章预览构建（chapters 指定了具体章）时默认不并入真题——
    # 真题横跨全部 12 章，混进单章预览会破坏「本章矩阵」的自检口径。
    if chapters is None or "exam" in set(chapters):
        try:
            from .exam import load_exam
            allq.extend(load_exam())
        except ImportError:
            print("[bank] 未找到真题包 qa_bank.exam，跳过真题模块")

    type_rank = {SINGLE: 0, MULTI: 1, JUDGE: 2, BLANK: 3, TERM: 4, SHORT: 5, CALC: 6}
    diff_rank = {"basic": 0, "medium": 1, "hard": 2}
    allq.sort(key=lambda q: (q["chapter"], type_rank[q["type"]], diff_rank[q["difficulty"]]))
    for i, q in enumerate(allq):
        q["idx"] = i
    return allq


# ---------------------------------------------------------------- 自检（可在构建时开启）
def audit(questions, full=True):
    """返回 (报告字符串列表, 错误列表)。

    full=True  校验全局不变量：题量 180、题型 36/24/36/24/24/36、难度 84/60/36、
                章节 12 章各 15、单选/多选答案位置均衡。
    full=False 只校验逐题结构（选项合法性、采分点数、解析、出处等），
                供单章自检使用——单章下全局计数必然不成立，不应报为错误。
    """
    rep, err = [], []
    from collections import Counter, defaultdict
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    cell = defaultdict(Counter)
    for q in questions:
        cell[q["typeGroup"]][q["chapter"]] += 1

    rep.append("题型分布：%s" % dict(c_type))
    rep.append("难度分布：%s" % dict(c_diff))
    rep.append("章节分布：%s" % dict(sorted(c_ch.items())))

    if full:
        if len(questions) != 180:
            err.append("题量 %d != 180" % len(questions))
        for t, n in (("single", 36), ("multi", 24), ("judge", 36),
                     ("blank", 24), ("short", 24), ("calc", 36)):
            if c_type.get(t, 0) != n:
                err.append("题型 %s = %d != %d" % (t, c_type.get(t, 0), n))
        for d, n in (("basic", 84), ("medium", 60), ("hard", 36)):
            if c_diff.get(d, 0) != n:
                err.append("难度 %s = %d != %d" % (d, c_diff.get(d, 0), n))
        for ch in range(1, 13):
            if c_ch.get(ch, 0) != 15:
                err.append("章节 %d = %d != 15" % (ch, c_ch.get(ch, 0)))

    # 客观题答案必须在选项内
    for q in questions:
        if q["options"]:
            letters = "ABCDE"[:len(q["options"])]
            if q["type"] in ("single", "judge") and len(q["answer"]) != 1:
                err.append("%s 单选/判断答案数 != 1" % q["id"])
            if q["type"] == "multi" and len(q["answer"]) < 2:
                err.append("%s 多选答案数 < 2" % q["id"])
            for a in q["answer"]:
                if a not in letters:
                    err.append("%s 答案 %s 不在选项内" % (q["id"], a))
        else:
            if q["type"] in ("single", "multi", "judge"):
                err.append("%s 客观题缺少 options" % q["id"])
        if q["type"] in ("term", "short", "calc"):
            if not q["answerText"]:
                err.append("%s 主观题缺少 answerText" % q["id"])
            if not q["points"]:
                err.append("%s 主观题缺少采分点" % q["id"])
            else:
                want = {"term": 2, "short": 3, "calc": 4}[q["type"]]
                if len(q["points"]) != want:
                    err.append("%s 采分点数 %d != %d" % (q["id"], len(q["points"]), want))
        if not q["explanation"]:
            err.append("%s 缺少解析" % q["id"])
        if q["source"]["kind"] == "extension" and not (q.get("extension") or "").startswith("引申"):
            err.append("%s 引申题未以「引申」开头" % q["id"])

    # 答案位置均衡（全局口径，仅全量模式下有意义）
    if full:
        single_pos = Counter(q["answer"][0] for q in questions if q["type"] == "single")
        rep.append("单选答案位置：%s" % dict(single_pos))
        for L in "ABCD":
            if not (5 <= single_pos.get(L, 0) <= 10):
                err.append("单选答案 %s 出现 %d 次，超出 [5,10]" % (L, single_pos.get(L, 0)))
        multi_pos = Counter()
        for q in questions:
            if q["type"] == "multi":
                for a in q["answer"]:
                    multi_pos[a] += 1
        rep.append("多选答案字母：%s" % dict(multi_pos))
        if multi_pos:
            vals = [multi_pos.get(L, 0) for L in "ABCD"]
            if max(vals) - min(vals) > 12:
                err.append("多选答案字母极差 %d > 12" % (max(vals) - min(vals)))
    return rep, err
