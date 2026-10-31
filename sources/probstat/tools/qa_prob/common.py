# -*- coding: utf-8 -*-
"""qa_prob/common.py —— 概率论题库公共定义（Q 构造函数 + 常量）。"""

SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC = (
    "single", "multi", "judge", "blank", "short", "calc")

ALL_QUESTIONS = []


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
    ALL_QUESTIONS.append(q)
    return q
