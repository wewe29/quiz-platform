# -*- coding: utf-8 -*-
r"""数据可视化 · 学科产物导出：解析 docx 题库源（章节小测 16 套 + 综合卷 5 套）→ 平台分片。

用法：
    python tools/build_subject.py                # 导出到平台仓 subjects/dataviz
    python tools/build_subject.py --out <dir>
    python tools/build_subject.py --skip-gates   # 仅调试

来源：
    02《数据可视化》章节小测（16套）.docx   8 章 × A/B 卷，各 5 选择 + 5 填空 + 2 简答 = 192 题
    03《数据可视化》综合测试卷（5套）.docx   5 套，各 10 选择 + 5 填空 + 4 简答 + 2 论述 = 105 题
    ⚠ 源材料只有**答案键**，无逐题解析。解析由本脚本生成：
        依据《复习知识文档（图文版）.md》（课件忠实整理）做知识点匹配，
        取最优小节的相关原文摘录作为解析底本（--dump-explanations 可导出人工复核清单）。

映射规则：
    难度：A卷→basic，B卷→medium，综合卷1-2→medium、3-5→hard；章节：综合卷→第 9 章「综合测试卷」
    题型：选择→single，填空→blank，简答/论述→short（论述 id 用 essay）
    简答/论述参考答案 = 答案区原文（含「见知识文档 X.X」的按指针抽取对应小节正文补全）
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))

SUBJECT = {
    "id": "dataviz",
    "name": "数据可视化",
    "textbook": "《数据可视化》课程课件（第 1–8 章，共 490 页）",
    "bankId": "dataviz-course-v1",
    "chapters": 9,
    "chapterLabels": {
        "1": "第1章 数据可视化概述",
        "2": "第2章 数据可视化基础（数据预处理）",
        "3": "第3章 数据可视化（图表类型与绘制）",
        "4": "第4章 时间数据可视化",
        "5": "第5章 比例数据可视化",
        "6": "第6章 关系数据可视化",
        "7": "第7章 文本与高维数据可视化",
        "8": "第8章 数据可视化中的交互",
        "9": "综合测试卷（5 套）",
    },
    "chapterShortLabels": {"9": "综合卷"},
}

SHARD_BUDGET = 200 * 1024
QUIZ_DOCX = os.path.join(PROJECT, "02《数据可视化》章节小测（16套）.docx")
EXAM_DOCX = os.path.join(PROJECT, "03《数据可视化》综合测试卷（5套）.docx")
KNOWLEDGE_MD = os.path.join(PROJECT, "04《数据可视化》复习知识文档（图文版）.md")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
    return ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip() for p in paras]


# ---------------------------------------------------------------- 知识文档索引
def load_knowledge():
    """返回 sections: [{id, title, text}]（按 ### 小节切分）。"""
    with io.open(KNOWLEDGE_MD, encoding="utf-8") as f:
        lines = f.read().splitlines()
    sections = []
    cur_id, cur_title, buf = None, "", []
    for ln in lines:
        mh = re.match(r"^### (\d+\.\d+)\s+(.*)$", ln)
        if mh:
            if cur_id:
                sections.append({"id": cur_id, "title": cur_title, "text": "\n".join(buf)})
            cur_id, cur_title, buf = mh.group(1), mh.group(2).strip(), []
            continue
        mc = re.match(r"^## 第(\d+)章\s+(.*)$", ln)
        if mc:
            if cur_id:
                sections.append({"id": cur_id, "title": cur_title, "text": "\n".join(buf)})
            cur_id, cur_title, buf = mc.group(1) + ".0", mc.group(2).strip(), []
            continue
        if cur_id:
            buf.append(ln)
    if cur_id:
        sections.append({"id": cur_id, "title": cur_title, "text": "\n".join(buf)})
    for s in sections:
        s["body"] = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s["text"])  # 去图片引用
    return sections


def pick_section(sections, keywords, chapter_hint=None):
    """按关键词覆盖度选最优小节；chapter_hint 优先同章。
    章级伞节（N.0，仅章标题）不参与匹配——它们会靠标题关键词抢占真实小节。"""
    best, best_score = None, -1
    for s in sections:
        if s["id"].endswith(".0"):
            continue
        score = 0
        for kw in keywords:
            if kw and kw in s["title"]:
                score += 3
            if kw and kw in s["body"]:
                score += 1
        if chapter_hint and s["id"].split(".")[0] == str(chapter_hint):
            score += 2
        if score > best_score:
            best, best_score = s, score
    return best if best_score > 0 else None


def excerpt_for(section, keywords, limit=180):
    """从Section 正文挑含关键词的句子，拼成不超过 limit 字的摘录。"""
    body = re.sub(r"[#*`>\[\]]", "", section["body"])
    sents = [s.strip() for s in re.split(r"(?<=[。；！？])", body) if s.strip()]
    scored = []
    for s in sents:
        sc = sum(1 for kw in keywords if kw and kw in s)
        if sc:
            scored.append((sc, s))
    scored.sort(key=lambda x: -x[0])
    out, used = [], 0
    for _, s in scored:
        if used + len(s) > limit and out:
            break
        out.append(s)
        used += len(s)
        if len(out) >= 2:
            break
    if not out:
        out = [s for s in sents if s][:1]
    return "／".join(out)[:limit + 40]


def keywords_of(text, answer=None):
    """中文 2-gram + 英数词，过滤通用停用词。"""
    text = re.sub(r"[（）()　\s_。，、；：？》《「」$\\]|A[.、]|B[.、]|C[.、]|D[.、]|E[.、]", "", text)
    if answer:
        text += re.sub(r"[（）()　\s]", "", str(answer))
    grams = set()
    i = 0
    while i < len(text):
        ch = text[i]
        if re.match(r"[A-Za-z0-9]", ch):
            m = re.match(r"[A-Za-z0-9_\.]+", text[i:])
            grams.add(m.group(0).lower())
            i += len(m.group(0))
            continue
        if i + 1 < len(text) and re.match(r"[\u4e00-\u9fff]", text[i + 1]):
            grams.add(text[i:i + 2])
        i += 1
    stop = {"下列", "不包括", "包括", "常用", "属于", "可以", "通过", "使用", "进行", "称为",
            "数据可视化", "可视化", "一种", "三个", "方面", "信息", "最早", "追溯", "时期",
            "选项", "正确", "说法", "关于", "分别", "哪些", "什么", "如何", "以及"}
    return [g for g in grams if g not in stop and len(g) >= 2]


# ---------------------------------------------------------------- 题目解析
SET_HEAD = re.compile(r"^第(\d+)章 .+ · 小测 ([AB]) 卷$")
EXAM_HEAD = re.compile(r"^(?:总体知识测试卷|试卷)?（([一二三四五])）")
SEC_HEAD = re.compile(r"^[一二三四]、(选择题|填空题|简答题|论述题)")
TYPE_MAP = {"选择题": "single", "填空题": "blank", "简答题": "short", "论述题": "short"}
SEC_ID = {"选择题": "single", "填空题": "blank", "简答题": "short", "论述题": "essay"}
NUM_START = re.compile(r"^(\d+)[\.、]\s*(.*)$")
OPT_SPLIT = re.compile(r"([A-E])[\.、]\s*")


def split_options(text):
    """行内选项：`A. xxx　　B. yyyC. zzz` → ['xxx','yyy','zzz']。"""
    marks = list(OPT_SPLIT.finditer(text))
    if not marks:
        return None
    opts = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        opts.append(text[start:end].strip().rstrip("。").strip())
    return opts


def parse_quiz(lines):
    """章节小测：16 套。返回 sets。"""
    sets = []
    cur = None
    cur_type = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = SET_HEAD.match(line)
        if m:
            cur = {"kind": "set", "chapter": int(m.group(1)), "set": m.group(2), "types": {}}
            sets.append(cur)
            cur_type = None
            cur_sec = None
            continue
        if cur is None:
            continue
        ms = SEC_HEAD.match(line)
        if ms:
            cur_type = TYPE_MAP[ms.group(1)]
            cur_sec = SEC_ID[ms.group(1)]
            cur["types"].setdefault(cur_type, [])
            continue
        if line.startswith("参考答案") or line.startswith("（满分"):
            cur_type = None
            continue
        if cur_type is None:
            continue
        mq = NUM_START.match(line)
        if mq:
            no = int(mq.group(1))
            rest = mq.group(2)
            if cur_type == "single":
                srch = OPT_SPLIT.search(rest)
                opts = split_options(rest)
                stem = rest[:srch.start()].strip() if srch else rest
            else:
                opts = None
                stem = rest
            item = {"no": no, "stem": stem, "options": opts}
            if cur_sec:
                item["sec"] = cur_sec
            cur["types"][cur_type].append(item)
        elif cur["types"][cur_type]:
            # 题干折行续接
            cur["types"][cur_type][-1]["stem"] += line
    return sets


def parse_exam(lines):
    """综合卷：5 套。"""
    sets = []
    cur = None
    cur_type = None
    cn = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = EXAM_HEAD.match(line)
        if m:
            cur = {"kind": "exam", "chapter": 9, "set": cn[m.group(1)], "types": {}}
            sets.append(cur)
            cur_type = None
            cur_sec = None
            continue
        if cur is None:
            continue
        ms = SEC_HEAD.match(line)
        if ms:
            cur_type = TYPE_MAP[ms.group(1)]
            cur_sec = SEC_ID[ms.group(1)]
            cur["types"].setdefault(cur_type, [])
            continue
        if line.startswith("参考答案") or line.startswith("（满分"):
            cur_type = None
            continue
        if cur_type is None:
            continue
        mq = NUM_START.match(line)
        if mq:
            no = int(mq.group(1))
            rest = mq.group(2)
            if cur_type == "single":
                srch = OPT_SPLIT.search(rest)
                opts = split_options(rest)
                stem = rest[:srch.start()].strip() if srch else rest
            else:
                opts = None
                stem = rest
            item = {"no": no, "stem": stem, "options": opts}
            if cur_sec:
                item["sec"] = cur_sec
            cur["types"][cur_type].append(item)
        elif cur["types"][cur_type]:
            cur["types"][cur_type][-1]["stem"] += line
    return sets


ANS_SET = re.compile(r"^第(\d+)章 · ([AB])卷$")
ANS_EXAM = re.compile(r"^试卷（([一二三四五])）$")
ANS_LINE = re.compile(r"^(选择|填空|简答|论述)[:：]\s*(.*)$")


def parse_answers(lines):
    """答案区：紧凑行。返回 {(kind, ch, set): {atype: {no: text}}}。

    注意：_ingest_compact 直接写 results，这里**没有** flush 机制——
    旧版 flush 用 cur_val=[1,""] 回写桶会把「1.A」覆盖成空值（真实踩过）。"""
    results = {}
    cur_key = None
    cur_atype = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        ms = ANS_SET.match(line)
        if ms:
            cur_key = ("set", int(ms.group(1)), ms.group(2))
            results.setdefault(cur_key, {})
            cur_atype = None
            continue
        me = ANS_EXAM.match(line)
        if me:
            idx = ["一", "二", "三", "四", "五"].index(me.group(1)) + 1
            cur_key = ("exam", 9, idx)
            results.setdefault(cur_key, {})
            cur_atype = None
            continue
        ma = ANS_LINE.match(line)
        if ma:
            cur_atype = {"选择": "single", "填空": "blank", "简答": "short", "论述": "essay"}[ma.group(1)]
            _ingest_compact(results, cur_key, cur_atype, None, ma.group(2))
            continue
        if cur_key and cur_atype:
            # 答案折行续接
            _ingest_compact(results, cur_key, cur_atype, None, line)
    return results


def _ingest_compact(results, key, atype, cur, text):
    """紧凑答案行：`1.A　2.D　…` 或 `1.记录信息　2.pyecharts　…`。

    分项边界：句号/分号/全角空格之后跟「数字.」且点后不是数字（排除 3.1415、3.1.2 这类小数）；
    编号按出现顺序回填（源材料编号偶有跳号）。"""
    bucket = results[key].setdefault(atype, {})
    if atype == "single":
        for m in re.finditer(r"(\d+)\s*[\.、]\s*([A-E])", text):
            bucket[int(m.group(1))] = m.group(2)
        return
    parts = re.split(r"(?<=[。；\u3000])\s*(?=\d+[\.、])", text)
    seq = 1
    for p in parts:
        m = re.match(r"^(\d+)[\.、]\s*(.*)$", p.strip())
        if not m:
            if bucket.get(seq):
                bucket[seq] += p.strip()   # 无编号的续行并入上一项
            continue
        bucket[seq] = m.group(2).strip()
        seq += 1


# ---------------------------------------------------------------- 组装
def build_questions():
    knowledge = load_knowledge()
    sets_q = parse_quiz(docx_text(QUIZ_DOCX))
    exams_q = parse_exam(docx_text(EXAM_DOCX))
    ans_all = parse_answers(docx_text(QUIZ_DOCX))
    ans_all.update(parse_answers(docx_text(EXAM_DOCX)))

    questions = []
    empty_opts = []
    seen_stems = {}
    dropped_dup = []
    no_answer = []
    for coll in (sets_q, exams_q):
        for s in coll:
            key = ("set", s["chapter"], s["set"]) if s["kind"] == "set" else ("exam", 9, s["set"])
            answers = ans_all.get(key, {})
            diff = ("basic" if s["kind"] == "set" and s["set"] == "A"
                    else "medium" if s["kind"] == "set"
                    else ("medium" if s["set"] <= 2 else "hard"))
            for qtype, items in s["types"].items():
                for it in items:
                    sec_tag = it.get("sec") or qtype
                    qid = ("dv-c%d%s-%s-%d" % (s["chapter"], s["set"], sec_tag, it["no"])
                           if s["kind"] == "set"
                           else "dv-s%d-%s-%d" % (s["set"], sec_tag, it["no"]))
                    if qtype == "single":
                        letters = [answers.get("single", {}).get(it["no"], "")]
                        if not letters[0]:
                            no_answer.append(qid)
                            continue
                        # 空文本选项补位
                        opts = [o if o else "（源文档此选项文本缺失）" for o in it["options"]]
                        if any("缺失" in o for o in opts):
                            empty_opts.append(qid)
                        answer = letters
                        q_accept = None
                    elif qtype == "blank":
                        val = answers.get("blank", {}).get(it["no"])
                        if not val:
                            no_answer.append(qid)
                            continue
                        opts = None
                        accepts = [val]
                        stripped = re.sub(r"[（(][^）)]*[）)]", "", val).strip()
                        if stripped and stripped != val:
                            accepts.append(stripped)
                        answer = [val]
                        q_accept = accepts
                    else:
                        val = answers.get("short", {}).get(it["no"]) or answers.get("essay", {}).get(it["no"])
                        if not val:
                            no_answer.append(qid)
                            continue
                        opts = None
                        answer = []
                        q_accept = None
                    kws = keywords_of(it["stem"], (answer[0] if qtype != "short" else it["stem"]))
                    sec = pick_section(knowledge, kws, s["chapter"])
                    answer_text = points = None
                    if qtype != "short":
                        expl = ""
                        if sec:
                            expl = "依据《复习知识文档》%s %s：%s" % (
                                sec["id"], sec["title"].split(" ")[0], excerpt_for(sec, kws))
                    else:
                        # 简答/论述：答案区原文即参考答案；指针型（见知识文档X.X）抽取正文补全
                        answer_text = val
                        pointer = re.search(r"见知识文档\s*([\d\.]+)", val)
                        extra = ""
                        if pointer:
                            sid = pointer.group(1)
                            for sec in knowledge:
                                if sec["id"] == sid:
                                    extra = excerpt_for(sec, kws, limit=220)
                                    break
                        answer_text = val + (("　◆ " + extra) if extra else "")
                        expl = ""
                        points = _short_points(val, qtype, s["kind"])
                    q = {
                        "id": qid, "type": qtype,
                        "typeGroup": "short" if qtype == "short" else qtype,
                        "difficulty": diff, "chapter": s["chapter"],
                        "knowledgePoint": str(s["chapter"]),
                        "source": {"text": _source_text(s), "kind": "textbook"},
                        "stem": it["stem"], "options": opts,
                        "answer": answer,
                        "answerText": answer_text,
                        "points": points,
                        "explanation": expl,
                        "misconception": None,
                        "extension": None,
                        "tags": ["第%d章" % s["chapter"],
                                 "综合卷" if s["kind"] == "exam" else (s["set"] + "卷")],
                        "verify": [],
                        "accept": q_accept,
                    }
                    skey = it["stem"][:50]
                    if skey in seen_stems:
                        dropped_dup.append("%s(=%s)" % (qid, seen_stems[skey]))
                        continue
                    seen_stems[skey] = qid
                    questions.append(q)
    if no_answer:
        print("[assemble] 无答案可用的题（不入库）：%d 道：%s" % (len(no_answer), no_answer[:6]))
    if dropped_dup:
        print("[assemble] 丢弃源材料内重复题干 %d 题：%s" % (len(dropped_dup), dropped_dup[:4]))
    if empty_opts:
        print("[assemble] 选项文本在源文档中缺失（已补占位）：%s" % empty_opts[:6])
    return questions


def _source_text(s):
    if s["kind"] == "set":
        return "《数据可视化》章节小测 第%d章 %s卷（依据第%d章课件）" % (s["chapter"], s["set"], s["chapter"])
    return "《数据可视化》综合测试卷 第%d套（满分 100 分）" % s["set"]


def _short_points(val, qtype, kind):
    """简答/论述采分点：按 ；/。/①② 拆分为 2–5 点，分值合计 = 原卷该题满分。"""
    total = 10 if kind == "set" or True else 10
    if qtype == "short":
        total = 10
    text = re.sub(r"^见知识文档[\d\.]+[:：]?", "", val).strip()
    segs = [x for x in re.split(r"[；;]", text) if x.strip()]
    if len(segs) < 2:
        segs = [x for x in re.split(r"(?<=[。])", text) if x.strip()]
    if len(segs) < 2:
        segs = [text.strip()]
    segs = segs[:5]
    per = max(2, round(total / len(segs)))
    pts = [{"text": s.strip(), "partial": per} for s in segs]
    # 分值微调到合计=total
    diff = total - sum(p["partial"] for p in pts)
    if diff:
        pts[-1]["partial"] += diff
    return pts


# ---------------------------------------------------------------- 门禁与导出（同平台契约）
def gates(questions):
    ids = [q["id"] for q in questions]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit("[gates] 重复题号：%s" % dup[:8])
    bad = 0
    stems = {}
    for q in questions:
        if not q["stem"]:
            print("      [gate] %s 缺题干" % q["id"]); bad += 1
        if q["type"] in ("single", "multi", "blank") and not q["explanation"]:
            print("      [gate] %s 缺解析" % q["id"]); bad += 1
        if q["type"] == "short" and not (q["answerText"] and q["points"]):
            print("      [gate] %s 主观题缺参考答案/采分点" % q["id"]); bad += 1
        if q["type"] == "single":
            letters = "ABCDE"[:len(q["options"] or [])]
            if len(q["answer"]) != 1 or q["answer"][0] not in letters:
                print("      [gate] %s 答案 %s 不在选项内" % (q["id"], q["answer"])); bad += 1
        if q["type"] == "blank" and not q["answer"][0]:
            print("      [gate] %s 填空缺答案" % q["id"]); bad += 1
        skey = q["stem"][:50]
        if skey in stems:
            print("      [gate] %s 与 %s 题干重复" % (q["id"], stems[skey])); bad += 1
        stems[skey] = q["id"]
    if bad:
        raise SystemExit("[gates] %d 处问题，拒绝导出" % bad)
    print("[OK ] 门禁：题号唯一 / 解析齐备 / 答案在选项内 / 无重复题干")


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


def default_out():
    sibling = os.path.join(os.path.dirname(PROJECT), "quiz-platform", "subjects", SUBJECT["id"])
    if os.path.isdir(os.path.join(os.path.dirname(PROJECT), "quiz-platform")):
        return sibling
    return os.path.join(PROJECT, "platform-dist", SUBJECT["id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-gates", action="store_true")
    ap.add_argument("--dump-explanations", default=None,
                    help="把生成的解析导出为 JSON 供人工复核")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    print("[subject] 步骤 1/3：解析 docx 题库源 + 知识文档匹配")
    questions = build_questions()
    from collections import Counter
    c_type = Counter(q["type"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    print("      解析出 %d 题：%s；难度 %s" % (len(questions), dict(c_type), dict(c_diff)))
    if not args.skip_gates:
        gates(questions)

    if args.dump_explanations:
        with io.open(args.dump_explanations, "w", encoding="utf-8", newline="\n") as f:
            json.dump([{k: q[k] for k in ("id", "stem", "answer", "explanation")}
                       for q in questions if q["type"] != "short"],
                      f, ensure_ascii=False, indent=1)
        print("[OK ] 解析复核清单：%s" % args.dump_explanations)

    print("[subject] 步骤 2/3：生成分片")
    shards = shard_questions(questions)
    exam_n = c_ch.get(9, 0)

    print("[subject] 步骤 3/3：写出产物")
    os.makedirs(data_dir, exist_ok=True)
    # 写前清理：上一版构建的陈旧分片必须删除，否则 dist 里新旧并存
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
            raise SystemExit("[subject] 分片 %s 超预算" % p["name"])
        shard_entries.append({"file": p["name"], "chapter": p["chapter"],
                              "count": len(p["questions"]), "sha256": sha256(path)})

    sections = {str(n): SUBJECT["chapterLabels"][str(n)].split(" ", 1)[-1]
                for n in range(1, SUBJECT["chapters"] + 1)}
    manifest = {
        "schema": "quiz-platform-subject-v1",
        "subject": SUBJECT,
        "sections": sections,
        "caliber": {
            "total": len(questions),
            "byType": {t: c_type.get(t, 0) for t in ("single", "multi", "judge", "blank", "short")},
            "byDifficulty": {d: c_diff.get(d, 0) for d in ("basic", "medium", "hard")},
            "byChapter": {str(k): c_ch[k] for k in sorted(c_ch)},
            "limits": {"singleMin": 0, "singleMax": 9999, "multiRange": 9999},
        },
        "summary": {
            "sub": "8 章体系 + 综合卷 · %d 题 · 章节小测 A/B + 综合测试" % len(questions),
            "desc": "数据可视化 %d 题刷题子站：章节小测 A/B 卷 + 5 套综合卷，逐题解析（依据课件整理的知识文档）与考点出处。" % len(questions),
            "aboutHtml": "".join([
                "<p><b>内容来源</b>：《数据可视化》课程课件（第 1–8 章，490 页）体系；"
                "章节小测 16 套（A/B 卷）+ 综合测试卷 5 套，共 <b>%d</b> 题。</p>" % len(questions),
                "<p><b>解析说明</b>：源材料仅提供答案键，本站解析由《复习知识文档》（课件忠实整理版）"
                "按知识点匹配生成——每题标注依据小节，学习时请对照原文。</p>",
                "<p><b>判分口径</b>：客观题自动判分；简答与论述题<b>按采分点自评</b>，"
                "主观题满分 = 采分点分值之和（与原卷每题满分一致）。</p>",
                "<p><b>自托管说明</b>：全站资源自托管，无任何第三方依赖；进度数据保存在浏览器本地。</p>",
            ]),
            "footerHtml": "<p>题库共 <b>%d</b> 题：选择 %d · 填空 %d · 简答与论述 %d；"
                          "综合卷 %d 题归入「综合卷」章节。</p>" % (
                              len(questions), c_type.get("single", 0), c_type.get("blank", 0),
                              c_type.get("short", 0), exam_n),
            "realExamTagged": 0,
        },
        "shards": shard_entries,
    }
    with io.open(os.path.join(data_dir, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("[OK ] manifest.json（%d 分片，共 %d 题）" % (len(shard_entries), len(questions)))
    print("[subject] 导出完成：%s" % data_dir)


if __name__ == "__main__":
    main()
