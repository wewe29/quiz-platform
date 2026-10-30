# -*- coding: utf-8 -*-
"""题库导出：把 Python 题库转成前端要的目录 + 分章 JSON。

两份产物：
  index.json   —— 题库元信息 + 目录（章节 / 知识点 / 题型 / 难度 / 出处类型）
  chNN.json    —— 单章题目数组

多文件站按需加载靠的是这两份；单文件离线包由 build_quiz.py 直接
把全量题目内联进 window.__BANK__，并复用本模块的 catalog。
"""
from collections import OrderedDict

from .catalog import CHAPTERS, KP_INDEX, SEC
from .common import GROUP, TYPE_GROUP_LABEL

TYPE_GROUPS = [
    ("single", "单选"),
    ("multi", "多选"),
    ("judge", "判断"),
    ("blank", "填空"),
    ("short", "简答与名词解释"),
    ("calc", "计算与分析题"),
]

DIFFS = [("basic", "基础"), ("medium", "中等"), ("hard", "困难")]

KINDS = ["textbook", "exam-original", "exam-adapted", "extension"]

KIND_LABEL = {
    "textbook": "教材命题",
    "exam-original": "真题原题",
    "exam-adapted": "真题改编",
    "extension": "引申",
}


def catalog():
    """前端用的完整目录。"""
    chapters = []
    for c in CHAPTERS:
        chapters.append({
            "n": c["n"],
            "label": c["label"],
            "title": c.get("title") or c["label"],
            "secs": list(c["secs"]),
        })
    kps = []
    kp_label = {}
    for key in sorted(SEC.keys()):
        meta = KP_INDEX.get(key, {})
        kps.append({
            "key": key,
            "label": meta.get("label", key),
            "section": meta.get("section", ""),
            "chapter": meta.get("chapter", int(key.split(".")[0])),
        })
        kp_label[key] = meta.get("label", key)
    return {
        "chapters": chapters,
        "secKeys": sorted(SEC.keys()),
        "knowledgePoints": kps,
        "kpLabel": kp_label,
        "typeGroups": [{"key": k, "label": l, "rank": i}
                       for i, (k, l) in enumerate(TYPE_GROUPS)],
        "diffs": [{"key": k, "label": l, "rank": i}
                  for i, (k, l) in enumerate(DIFFS)],
        "kinds": list(KINDS),
        "kindLabel": dict(KIND_LABEL),
    }


def split_by_chapter(questions):
    """按章切分，返回 {章号: [题目…]}（章号升序）。"""
    out = OrderedDict()
    for q in questions:
        out.setdefault(int(q["chapter"]), []).append(q)
    return OrderedDict(sorted(out.items()))


def build_summary(questions):
    """题库概览：题型 / 难度 / 出处类型 / 章节计数，供页脚与说明区使用。"""
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_kind = Counter((q.get("source") or {}).get("kind") or "textbook" for q in questions)
    c_ch = Counter(int(q["chapter"]) for q in questions)
    return {
        "total": len(questions),
        "byTypeGroup": dict(c_type),
        "byDifficulty": dict(c_diff),
        "byKind": dict(c_kind),
        "byChapter": dict(sorted(c_ch.items())),
        "typeLabel": dict(TYPE_GROUP_LABEL),
        "kindLabel": dict(KIND_LABEL),
    }


def build_index(questions, bank_id, title, extra=None):
    """生成 index.json 内容。"""
    per = split_by_chapter(questions)
    chapters = []
    for n, qs in per.items():
        chapters.append({
            "n": n,
            "count": len(qs),
            "file": "ch%02d.json" % n,
        })
    idx = {
        "bank": {"id": bank_id, "title": title},
        "total": len(questions),
        "catalog": catalog(),
        "summary": build_summary(questions),
        "chapters": chapters,
    }
    if extra:
        idx.update(extra)
    return idx
