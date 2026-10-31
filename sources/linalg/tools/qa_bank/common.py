# -*- coding: utf-8 -*-
"""题库数据公共定义：构造函数、考点出处表、题型常量。

体例说明（沿用本机 D:\\workspace\\5-docs\\机器学习复习资料\\01《机器学习》知识点清单.md 的标记体系）：
    ⭐重点 📌考点 📖必背 🧗难点 ⚠️易错点 ℹ️了解

每题解析固定三段式：
    1) 答案依据    —— 为什么是这个答案
    2) 考点出处    —— source.text
    3) 辨析 / ⚠️易错点 —— 客观题必须逐项说明其他选项错在哪
"""
import os
import re

# 口径的单一事实源：题量/配额/阈值一律从这里读，不在本文件写死数字。
# （以前题量门禁在本文件、构建脚本、verify_quiz.py 各写一份，改一处忘一处就出错版。）
try:
    from . import target
except ImportError:  # 兼容把 common.py 当顶层模块直接导入的场合
    import target

# ---------------------------------------------------------------- 题型常量
SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC = (
    "single", "multi", "judge", "blank", "term", "short", "calc")

GROUP = {
    SINGLE: SINGLE, MULTI: MULTI, JUDGE: JUDGE,
    BLANK: BLANK, SHORT: SHORT, CALC: CALC,
    # 名词解释与简答合并为同一「简答与名词解释」大组：该组共 30 题
    TERM: SHORT,
}

TYPE_GROUP_LABEL = {
    SINGLE: "单选", MULTI: "多选", JUDGE: "判断",
    BLANK: "填空", SHORT: "简答与名词解释", CALC: "计算与分析题",
}

# ---------------------------------------------------------------- 章节与知识点出处
# key = "章节.知识点"，value = 教材节次出处文本
SEC = {
    "1.1": "同济《线性代数》第六版 §1.1 二阶与三阶行列式",
    "1.2": "同济《线性代数》第六版 §1.2 全排列和对换",
    "1.3": "同济《线性代数》第六版 §1.3 n 阶行列式的定义",
    "1.4": "同济《线性代数》第六版 §1.4 行列式的性质",
    "1.5": "同济《线性代数》第六版 §1.5 行列式按行(列)展开",
    "2.1": "同济《线性代数》第六版 §2.1 线性方程组和矩阵",
    "2.2": "同济《线性代数》第六版 §2.2 矩阵的运算",
    "2.3": "同济《线性代数》第六版 §2.3 逆矩阵",
    "2.4": "同济《线性代数》第六版 §2.4 克拉默法则",
    "2.5": "同济《线性代数》第六版 §2.5 矩阵分块法",
    "3.1": "同济《线性代数》第六版 §3.1 矩阵的初等变换",
    "3.2": "同济《线性代数》第六版 §3.2 矩阵的秩",
    "3.3": "同济《线性代数》第六版 §3.3 线性方程组的解",
    "4.1": "同济《线性代数》第六版 §4.1 向量组及其线性组合",
    "4.2": "同济《线性代数》第六版 §4.2 向量组的线性相关性",
    "4.3": "同济《线性代数》第六版 §4.3 向量组的秩",
    "4.4": "同济《线性代数》第六版 §4.4 线性方程组的解的结构",
    "4.5": "同济《线性代数》第六版 §4.5 向量空间",
    "5.1": "同济《线性代数》第六版 §5.1 向量的内积、长度及正交性",
    "5.2": "同济《线性代数》第六版 §5.2 方阵的特征值与特征向量",
    "5.3": "同济《线性代数》第六版 §5.3 相似矩阵",
    "5.4": "同济《线性代数》第六版 §5.4 对称矩阵的对角化",
    "5.5": "同济《线性代数》第六版 §5.5 二次型及其标准形",
    "5.6": "同济《线性代数》第六版 §5.6 用配方法化二次型成标准形",
    "5.7": "同济《线性代数》第六版 §5.7 正定二次型",
    "6.1": "同济《线性代数》第六版 §6.1 线性空间的定义与性质（选学）",
    "6.2": "同济《线性代数》第六版 §6.2 维数、基与坐标（选学）",
    "6.3": "同济《线性代数》第六版 §6.3 基变换与坐标变换（选学）",
    "6.4": "同济《线性代数》第六版 §6.4 线性变换（选学）",
    "6.5": "同济《线性代数》第六版 §6.5 线性变换的矩阵表示式（选学）",
}

LOCAL_ML = "本机《机器学习》课件 01机器学习-引言.pptx slide %s（仅作对照，非题目主体）"

# ---------------------------------------------------------------- 构造函数
_COUNTER = {"n": 0}


def Q(qtype, diff, kp, stem, answer=None, options=None, answer_text=None,
      points=None, expl="", mis=None, ext=None, tags=None, src=None,
      kind="textbook", accept=None, verify=None, qid=None, variant_group=None):
    """构造一道题。

    qtype      : single/multi/judge/blank/term/short/calc
    diff       : basic/medium/hard
    kp         : 知识点 key，如 "3.2"
    stem       : 题干（可含 $LaTeX$）
    answer     : 客观题答案字母数组；填空题答案字符串数组
    options    : 客观题选项数组
    answer_text: 主观题参考答案全文
    points     : 主观题采分点 list[str] 或 list[dict]
    expl       : 解析正文（含答案依据 + 辨析）
    mis        : 本题专属易错点
    ext        : 引申补充（必须以「引申」开头）
    src        : 覆盖默认出处文本
    kind       : textbook/local/extension
    accept     : 填空题可接受的其他写法
    verify     : 可核验项 list[dict{desc,code,expected}]（SymPy 复核用）
    variant_group: 举一反三变式族 id（同族题在子站组成模块）
    """
    _COUNTER["n"] += 1
    qid = qid or ("q-%03d" % _COUNTER["n"])
    chapter = int(kp.split(".")[0])
    # 判断题固定两个选项：A=正确，B=错误。由构造器统一注入，
    # 避免出现「判断题无 options → 页面渲染不出任何作答控件」的死题。
    if qtype == JUDGE and not options:
        options = ["正确", "错误"]
    if src is None:
        src = SEC.get(kp, kp)
    if kind == "extension":
        src = src + "　〔引申〕"
    if points:
        pts = []
        for p in points:
            if isinstance(p, dict):
                pts.append({"text": p["text"], "partial": p.get("partial", 2)})
            else:
                pts.append({"text": p, "partial": 2})
    else:
        pts = None
    return {
        "id": qid,
        "type": qtype,
        "typeGroup": GROUP[qtype],
        "difficulty": diff,
        "chapter": chapter,
        "knowledgePoint": kp,
        "source": {"text": src, "kind": kind},
        "stem": stem,
        "options": options,
        "answer": answer if answer is not None else [],
        "accept": accept,
        "answerText": answer_text,
        "points": pts,
        "explanation": expl,
        "misconception": mis,
        "extension": ext,
        "tags": tags or [],
        "verify": verify or [],
        "variantGroup": variant_group,
    }


def load_bank(chapters=None):
    """载入 ch1..ch6 全部题目，按 (章节, 题型, 难度, 知识点) 稳定排序并分配 idx。

    chapters 为 None 时载入全部六章；缺失的章会被跳过并打印提示，
    便于分章写作期间做「部分构建」预览（正式构建仍要求题量等于 target.TOTAL）。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    order = ["ch1", "ch1b", "ch2", "ch2b", "ch3", "ch3b",
             "ch4", "ch4b", "ch5", "ch5b", "ch6", "ch6b", "chx"]
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

    type_rank = {SINGLE: 0, MULTI: 1, JUDGE: 2, BLANK: 3, TERM: 4, SHORT: 5, CALC: 6}
    diff_rank = {"basic": 0, "medium": 1, "hard": 2}
    allq.sort(key=lambda q: (q["chapter"], type_rank[q["type"]], diff_rank[q["difficulty"]]))
    for i, q in enumerate(allq):
        q["idx"] = i
    return allq


# ---------------------------------------------------------------- 自检（可在构建时开启）
def audit(questions, full=True):
    """返回 (报告字符串列表, 错误列表)。

    full=True  校验全局不变量：题量、题型/难度/章节配额、答案位置均衡——
                期望值一律取自 target.py（单一事实源），不在此处写死。
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
        if len(questions) != target.TOTAL:
            err.append("题量 %d != %d" % (len(questions), target.TOTAL))
        for t in target.TYPE_ORDER:
            n = target.BY_TYPE[t]
            if c_type.get(t, 0) != n:
                err.append("题型 %s = %d != %d" % (t, c_type.get(t, 0), n))
        for d in target.DIFF_ORDER:
            n = target.BY_DIFFICULTY[d]
            if c_diff.get(d, 0) != n:
                err.append("难度 %s = %d != %d" % (d, c_diff.get(d, 0), n))
        for ch in sorted(target.BY_CHAPTER):
            n = target.BY_CHAPTER[ch]
            if c_ch.get(ch, 0) != n:
                err.append("章节 %d = %d != %d" % (ch, c_ch.get(ch, 0), n))

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
            if not (target.SINGLE_LETTER_MIN <= single_pos.get(L, 0) <= target.SINGLE_LETTER_MAX):
                err.append("单选答案 %s 出现 %d 次，超出 [%d,%d]" % (
                    L, single_pos.get(L, 0), target.SINGLE_LETTER_MIN, target.SINGLE_LETTER_MAX))
        multi_pos = Counter()
        for q in questions:
            if q["type"] == "multi":
                for a in q["answer"]:
                    multi_pos[a] += 1
        rep.append("多选答案字母：%s" % dict(multi_pos))
        if multi_pos:
            vals = [multi_pos.get(L, 0) for L in "ABCD"]
            if max(vals) - min(vals) > target.MULTI_LETTER_RANGE:
                err.append("多选答案字母极差 %d > %d" % (
                    max(vals) - min(vals), target.MULTI_LETTER_RANGE))
    return rep, err
