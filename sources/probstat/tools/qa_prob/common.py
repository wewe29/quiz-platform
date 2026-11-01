# -*- coding: utf-8 -*-
"""qa_prob/common.py —— 概率论题库公共定义（Q 构造函数 + 常量）。"""

SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC = (
    "single", "multi", "judge", "blank", "short", "calc")

ALL_QUESTIONS = []


def _clean(text):
    """清除控制字符 + 修复数学模式内裸中文（用 \\text{} 包裹）+ 收敛重复包裹。"""
    import re
    if not text:
        return text
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
    def _wrap(m):
        inner = m.group(1)
        if not any("\u4e00" <= c <= "\u9fff" for c in inner):
            return m.group(0)
        parts = re.split(r"([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+)", inner)
        out = ""
        for p in parts:
            if p and any("\u4e00" <= c <= "\u9fff" for c in p):
                out += "\\text{" + p + "}"
            elif p:
                out += p
        return "$" + out + "$"
    text = re.sub(r"\$([^$]+)\$", _wrap, text)
    # 收敛嵌套包裹：题面已写 \\text{其他} 时，上面会再包一层变成 \\text{\\text{其他}}
    return re.sub(r"\\text\{\\text\{([^{}]*)\}\}", r"\\text{\1}", text)


def Q(qtype, diff, kp, stem, answer=None, options=None, answer_text=None,
      points=None, expl="", mis=None, tags=None, variant_group=None,
      verify=None, qid=None, accept=None):
    chapter = int(kp.split(".")[0])
    if qtype == "judge" and not options:
        options = ["正确", "错误"]
    pts = None
    if points:
        pts = [{"text": p["text"] if isinstance(p, dict) else p,
                "partial": p.get("partial", 2) if isinstance(p, dict) else 2}
               for p in points]
    qid = qid or "ps-%03d" % (len(ALL_QUESTIONS) + 1)
    q = {
        "id": qid,
        "type": qtype,
        "typeGroup": {"single": "single", "multi": "multi", "judge": "judge",
                      "blank": "blank", "term": "short", "short": "short",
                      "calc": "calc"}.get(qtype, qtype),
        "difficulty": diff,
        "chapter": chapter,
        "knowledgePoint": kp,
        "source": {"text": "", "kind": "textbook"},
        "stem": _clean(stem),
        "options": [_clean(o) if isinstance(o, str) else o for o in (options or [])] or options,
        "answer": answer or [],
        "accept": accept,
        "answerText": _clean(answer_text),
        "points": pts,
        "explanation": _clean(expl),
        "misconception": mis,
        "extension": None,
        "tags": tags or [],
        "verify": verify or [],
        "variantGroup": variant_group,
    }
    ALL_QUESTIONS.append(q)
    return q
