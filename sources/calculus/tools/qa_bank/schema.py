# -*- coding: utf-8 -*-
"""题目数据契约（v2）。

题库从「180 道教材命题」扩到「180 教材题 + 500 道真题」之后，单靠
`common.audit()` 的逐题结构检查已经不够：真题带来三样教材题没有的东西——

    1. 外部可核验来源（年份 / 地区 / 卷别 / 题号 / URL）
    2. 两种溯源级别（原题 / 改编）
    3. 跨知识点覆盖（一道真题常跨多个节次）

所以这里把「一条题目数据必须长什么样」写成可执行的契约，
构建期拦一次，运行期再拦一次（JS 侧 `core/schema.js` 与本文件规则对齐）。

规则分级
--------
    error  构建期直接失败（`validate_bank.py` / `build_*.py` 退出码 1）
    warn   只报告，不阻断

对外接口
--------
QUESTION_KINDS        允许的 source.kind 取值
validate_question(q)  -> [(level, message)]，空列表 = 通过
normalize_question(q) -> dict，补默认值，返回新对象
fingerprint(q)        -> str，题干指纹，用于跨卷去重
"""
import hashlib
import re

from .catalog import SEC

# 允许的出处类型
QUESTION_KINDS = ("textbook", "exam-original", "exam-adapted", "extension")

# 溯源级别
PROV_LEVELS = ("original", "adapted")

# 题型
TYPES = ("single", "multi", "judge", "blank", "term", "short", "calc")

# 难度
DIFFS = ("basic", "medium", "hard")

# 客观题（需要 options + answer 字母）
OBJECTIVE = ("single", "multi", "judge")
# 主观题（需要 answerText + points）
SUBJECTIVE = ("term", "short", "calc")

_ADAPTED_TAG = "真题改编"
_WS_RE = re.compile(r"\s+")


def _err(msg):
    return ("error", msg)


def _warn(msg):
    return ("warn", msg)


# ------------------------------------------------------------------ 逐条规则

def _rule_required(q):
    """必填字段齐全且类型正确。"""
    out = []
    if not isinstance(q, dict):
        return [_err("题目不是 dict")]
    for f in ("id", "type", "difficulty", "chapter", "knowledgePoint", "stem"):
        if f not in q or q[f] in (None, ""):
            out.append(_err("缺必填字段 %s" % f))
    if "id" in q and not isinstance(q["id"], str):
        out.append(_err("id 必须是字符串"))
    if q.get("type") not in TYPES:
        out.append(_err("type 非法：%r" % q.get("type")))
    if q.get("difficulty") not in DIFFS:
        out.append(_err("difficulty 非法：%r" % q.get("difficulty")))
    ch = q.get("chapter")
    if not isinstance(ch, int) or not (1 <= ch <= 12):
        out.append(_err("chapter 必须是 1..12 的整数：%r" % (ch,)))
    if not isinstance(q.get("stem"), str) or not q.get("stem", "").strip():
        out.append(_err("stem 必须是非空字符串"))
    src = q.get("source")
    if not isinstance(src, dict):
        out.append(_err("source 必须是 dict"))
    elif not src.get("text"):
        out.append(_err("source.text 不能为空"))
    return out


def _rule_source_kind(q):
    """source.kind 必须在四态之内。"""
    src = q.get("source") or {}
    kind = src.get("kind")
    if kind not in QUESTION_KINDS:
        return [_err("source.kind 非法：%r（允许 %s）" % (kind, "/".join(QUESTION_KINDS)))]
    return []


def _rule_knowledge_points(q):
    """主知识点与附属知识点都必须存在于 catalog.SEC。"""
    out = []
    kp = q.get("knowledgePoint")
    if kp not in SEC:
        out.append(_err("knowledgePoint %r 不在 catalog.SEC 中" % (kp,)))
    for extra in q.get("knowledgePoints") or []:
        if extra not in SEC:
            out.append(_err("knowledgePoints 含未登记知识点 %r" % (extra,)))
    return out


def _rule_options_answer(q):
    """客观题必须有选项且答案落在选项字母内；主观题必须有答案与采分点。"""
    out = []
    t = q.get("type")
    opts = q.get("options") or []
    ans = q.get("answer") or []
    if t in OBJECTIVE:
        if not opts:
            out.append(_err("客观题缺 options"))
        else:
            letters = "ABCDE"[:len(opts)]
            for a in ans:
                if a not in letters:
                    out.append(_err("答案 %r 不在选项字母 %s 内" % (a, letters)))
        if t in ("single", "judge") and len(ans) != 1:
            out.append(_err("%s 答案数 %d != 1" % (t, len(ans))))
        if t == "multi" and len(ans) < 2:
            out.append(_err("multi 答案数 %d < 2" % len(ans)))
    if t in SUBJECTIVE:
        if not q.get("answerText"):
            out.append(_err("主观题缺 answerText"))
        if not q.get("points"):
            out.append(_err("主观题缺采分点 points"))
    if t == "blank" and not ans:
        out.append(_err("填空题缺答案"))
    return out


def _rule_explanation(q):
    """解析必须非空且含「答案依据」；$ 分隔符必须成对。"""
    out = []
    expl = q.get("explanation") or ""
    if not expl.strip():
        out.append(_err("缺解析"))
    elif "答案依据" not in expl:
        out.append(_err("解析缺「答案依据」"))
    if len(expl) < 30:
        out.append(_warn("解析过短（%d 字）" % len(expl)))
    for field in ("stem", "explanation", "answerText"):
        txt = q.get(field) or ""
        if txt.count("$") % 2 != 0:
            out.append(_err("%s 中 $ 不成对" % field))
    for i, opt in enumerate(q.get("options") or []):
        if opt.count("$") % 2 != 0:
            out.append(_err("选项 %s 中 $ 不成对" % "ABCDE"[i]))
    return out


def _rule_provenance(q):
    """真题的溯源硬要求：原题必须有 URL；改编必须打标并写明依据。"""
    out = []
    src = q.get("source") or {}
    prov = q.get("provenance") or {}
    kind = src.get("kind")
    if kind in ("exam-original", "exam-adapted"):
        if not isinstance(src.get("year"), int) or not (1980 <= src["year"] <= 2100):
            out.append(_err("真题必须带 4 位年份 source.year：%r" % (src.get("year"),)))
        if not src.get("region"):
            out.append(_err("真题必须带 source.region"))
        if not src.get("paper"):
            out.append(_err("真题必须带 source.paper"))
        if src.get("number") in (None, ""):
            out.append(_err("真题必须带 source.number（卷内题号）"))
    if kind == "exam-original":
        if not src.get("url"):
            out.append(_err("exam-original 必须带 source.url"))
        elif not str(src["url"]).startswith("http"):
            out.append(_err("source.url 必须以 http 开头：%r" % src.get("url")))
        if not prov.get("url"):
            out.append(_err("exam-original 必须带 provenance.url"))
        if prov.get("level") != "original":
            out.append(_err("exam-original 的 provenance.level 必须是 original"))
    if kind == "exam-adapted":
        tags = q.get("tags") or []
        if _ADAPTED_TAG not in tags:
            out.append(_err("exam-adapted 的 tags 必须包含「%s」" % _ADAPTED_TAG))
        if not prov.get("note"):
            out.append(_err("exam-adapted 必须带 provenance.note（改编依据）"))
        if prov.get("level") != "adapted":
            out.append(_err("exam-adapted 的 provenance.level 必须是 adapted"))
    if kind == "extension":
        ext = q.get("extension") or ""
        if ext and not ext.startswith("引申"):
            out.append(_err("引申内容未以「引申」开头"))
    if not q.get("tags"):
        out.append(_warn("无 tags"))
    return out


def _rule_verify(q):
    """计算题必须带 SymPy 可核验项。

    例外：**真题原题**（source.kind == "exam-original"）的参考答案取自已发布的
    「逐题解析」卷面文件，它有外部权威锚点；其可核验性由 audit_provenance.py
    承担——那个脚本会**回到源卷面文件**逐题比对题干 / 选项 / 答案是否与源一致。
    自编题（textbook / extension / exam-adapted）没有这个外部锚点，
    答案必须由 SymPy 独立重算，不许豁免。
    """
    if q.get("type") != "calc" or q.get("verify"):
        return []
    kind = ((q.get("source") or {}).get("kind")) or "textbook"
    if kind == "exam-original":
        prov = q.get("provenance") or {}
        if not prov.get("url"):
            return [_err("真题原题缺 provenance.url，无法做溯源复核")]
        return []
    return [_err("calc 题缺 SymPy 可核验项 verify")]


# ------------------------------------------------------------------ 公共入口

_RULES = (
    _rule_required,
    _rule_source_kind,
    _rule_knowledge_points,
    _rule_options_answer,
    _rule_explanation,
    _rule_provenance,
    _rule_verify,
)


def validate_question(q):
    """返回 [(level, message)]；level ∈ {"error","warn"}。空列表 = 通过。"""
    out = []
    for rule in _RULES:
        out.extend(rule(q))
    return out


def normalize_question(q):
    """补默认值，返回新对象（不改原对象）。"""
    n = dict(q)
    n.setdefault("knowledgePoints", [n.get("knowledgePoint")] if n.get("knowledgePoint") else [])
    prov = dict(n.get("provenance") or {})
    prov.setdefault("level", None)
    prov.setdefault("url", None)
    prov.setdefault("verifiedAt", None)
    prov.setdefault("note", "")
    n["provenance"] = prov
    src = dict(n.get("source") or {})
    for f in ("year", "region", "paper", "number", "url"):
        src.setdefault(f, None)
    n["source"] = src
    n.setdefault("options", [])
    n.setdefault("answer", [])
    n.setdefault("accept", None)
    n.setdefault("answerText", None)
    n.setdefault("points", None)
    n.setdefault("explanation", "")
    n.setdefault("misconception", None)
    n.setdefault("extension", None)
    n.setdefault("tags", [])
    n.setdefault("verify", [])
    return n


def fingerprint(q):
    """题干指纹：归一化空白与 LaTeX 空白后取 SHA-1 前 16 位。

    跨卷去重的依据——同一道真题常被多套汇编收录，题干文字可能只有
    空白与标点差异。
    """
    stem = q.get("stem") or ""
    s = _WS_RE.sub("", stem)
    s = s.replace("\\,", "").replace("\\;", "").replace("\\!", "")
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("（", "(").replace("）", ")")
    s = s.replace("，", ",").replace("。", ".")
    s = s.lower()
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]
