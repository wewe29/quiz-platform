# -*- coding: utf-8 -*-
r"""机器学习 · 学科产物导出：解析 md 题库源（章节小测 14 套 + 综合卷 5 套）→ 平台分片。

用法：
    python tools/build_subject.py                # 导出到平台仓 subjects/ml
    python tools/build_subject.py --out <dir>
    python tools/build_subject.py --skip-gates   # 仅调试

来源与体例：
    02《机器学习》章节小测（14套）.md   7 章 × A/B 卷，各 5 单选 + 3 多选 + 2 简答 = 140 题
    03《机器学习》综合测试卷（5套）.md   5 套难度递增，各 10 单选 + 5 填空 + 4 简答 + 2 论述 = 105 题
    每套卷后紧跟「参考答案与解析」，逐题含解析/答案要点——满足「无解析不入库」。

映射规则：
    难度：A卷→basic，B卷→medium，综合卷1-2→medium、3-5→hard（难度依次递增）
    章节：小测 1–7 章；综合卷→第 8 章「综合测试卷」
    题型：单选/多选/填空/简答/论述（论述并入 short 组）
    采分点：章节小测简答按 ①②③ 拆分（每点 3 分，合计 9 分与原卷一致）；
            综合卷简答/论述按「总起/分述（N分）」标记解析出每点分值（合计=原卷满分）
    评分提示与易错提醒 → misconception；答案中的括号注释自动派生填空可接受写法
本文件自包含（不 import qa_bank）：镜像到平台 sources/ml/tools 即可独立构建。
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))

SUBJECT = {
    "id": "ml",
    "name": "机器学习",
    "textbook": "《机器学习》课程课件（001–006）· 7 章体系",
    "bankId": "ml-course-v1",
    "chapters": 8,
    "chapterLabels": {
        "1": "第1章 人工智能与机器学习导论",
        "2": "第2章 机器学习概述与背景知识",
        "3": "第3章 回归",
        "4": "第4章 逻辑回归",
        "5": "第5章 朴素贝叶斯",
        "6": "第6章 机器学习实践",
        "7": "第7章 Scikit-learn 机器学习库",
        "8": "综合测试卷（5 套）",
    },
    "chapterShortLabels": {"8": "综合卷"},
    "chapterShortLabels": {"8": "综合卷"},
}

SHARD_BUDGET = 200 * 1024
SET_SECTION = re.compile(r"^## 第(\d+)章 ([AB])卷")
EXAM_SECTION = re.compile(r"^## 第(\d+)套 · ")
QSECTION = re.compile(r"^### [一二三四]、(单选题|多选题|填空题|简答题|论述题)")
TYPE_MAP = {"单选题": "single", "多选题": "multi", "填空题": "blank",
            "简答题": "short", "论述题": "short"}
DIFF_MAP_A = "basic"
DIFF_MAP_B = "medium"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def read_lines(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read().splitlines()


# ---------------------------------------------------------------- 解析
def parse_questions(lines):
    """题干/选项段。返回 sets[(kind, chapter, setno, {type: [ {no, stem, options} ]})]。"""
    sets = []
    cur = None
    cur_type = None
    for raw in lines:
        line = raw.rstrip()
        m = SET_SECTION.match(line)
        if m:
            cur = {"kind": "set", "chapter": int(m.group(1)), "set": m.group(2), "types": {}}
            sets.append(cur)
            cur_type = None
            cur_sec = None
            continue
        m = EXAM_SECTION.match(line)
        if m:
            cur = {"kind": "exam", "chapter": 8, "set": int(m.group(1)), "types": {}}
            sets.append(cur)
            cur_type = None
            cur_sec = None
            continue
        if cur is None:
            continue
        if "参考答案与解析" in line:
            # 本套卷的答案段开始：停止收集题干（答案段里的编号行不是题目）
            cur_type = None
            continue
        mq = QSECTION.match(line)
        if mq:
            sec_name = mq.group(1)
            cur_type = TYPE_MAP[sec_name]
            cur_sec = {"单选题": "single", "多选题": "multi", "填空题": "blank",
                       "简答题": "short", "论述题": "essay"}[sec_name]  # id 用，论述与简答分空间
            cur["types"].setdefault(cur_type, [])
            for it in cur["types"][cur_type]:
                it.setdefault("sec", cur_sec)
            continue
        if line.startswith("# "):
            cur_type = None
            continue
        if cur_type is None:
            continue
        qm = re.match(r"^(\d+)\.\s+(.*)$", line)
        if qm:
            item = {"no": int(qm.group(1)), "stem": qm.group(2).strip(), "options": []}
            if cur_sec:
                item["sec"] = cur_sec
            cur["types"][cur_type].append(item)
            continue
        om = re.match(r"^\s*[-·]?\s*([A-E])[\.、]\s*(.*)$", line)
        if om and cur["types"][cur_type]:
            cur["types"][cur_type][-1]["options"].append(om.group(2).strip())
    return sets


def parse_answers(lines):
    """答案段。返回 sets 的答案映射 {(kind, chapter, set): {type: {no: {...}}}}。"""
    results = {}
    cur_key = None
    cur_type = None
    cur_item = None

    def flush():
        if cur_item is not None and cur_key and cur_type:
            results[cur_key].setdefault(cur_type, {})[cur_item["no"]] = cur_item

    for raw in lines:
        line = raw.rstrip()
        m = SET_SECTION.match(line)
        if m:
            flush(); cur_item = None; cur_type = None
            cur_key = ("set", int(m.group(1)), m.group(2))
            results.setdefault(cur_key, {})
            continue
        m = EXAM_SECTION.match(line)
        if m and "参考答案" not in line:
            flush(); cur_item = None; cur_type = None
            cur_key = ("exam", 8, int(m.group(1)))
            results.setdefault(cur_key, {})
            continue
        if "参考答案与解析" in line:
            continue
        if cur_key is None:
            continue
        mq = re.match(r"^\*\*[一二三四]、(单选题|多选题|填空题|简答题|论述题)\*\*", line)
        if mq:
            flush(); cur_item = None
            cur_type = TYPE_MAP[mq.group(1)]
            results[cur_key].setdefault(cur_type, {})
            continue
        # 单选/多选/填空答案：N. **答案：XXX**（后随缩进解析行）
        ma = re.match(r"^(\d+)\.\s+\*\*答案[:：]\s*\*\*\s*(.*)$", line) or \
             re.match(r"^(\d+)\.\s+\*\*答案[:：]\s*([A-E]+)\*\*", line)
        if ma and cur_type:
            flush()
            no = int(ma.group(1))
            rest = (ma.group(2) or "").strip().rstrip("*").strip()
            cur_item = {"no": no, "answer": rest, "explanation": "", "points": [],
                        "misconception": "", "is_points": False}
            continue
        # 综合卷简答/论述：N. **总起（N分）：** / N. **分述…（N分）：**（无「答案要点」标记）
        mg = re.match(r"^(\d+)\.\s+\*\*(总起|分述[^*（]*?)（(\d+)分）[:：]\*\*\s*(.*)$", line)
        if mg and cur_type:
            flush()
            cur_item = {"no": int(mg.group(1)), "answer": "", "explanation": "",
                        "points": [{"text": (mg.group(2) + "：" + mg.group(4)).strip(),
                                    "partial": int(mg.group(3))}],
                        "misconception": "", "is_points": True}
            continue
        # 简答/论述答案要点（允许标记后带课件出处等后缀：**答案要点**（02 P30、P31）：）
        mp = re.match(r"^(\d+)\.\s+\*\*答案要点\*\*[^*]*[:：]\s*(.*)$", line)
        if mp and cur_type:
            flush()
            cur_item = {"no": int(mp.group(1)), "answer": "", "explanation": "",
                        "points": [], "misconception": "", "is_points": True}
            _ingest_point_line(cur_item, mp.group(2))
            continue
        if cur_item is None:
            continue
        # 评分提示/评分说明 → misconception
        mm = re.match(r"^\s*\*?\*?(评分提示与易错提醒|评分说明)[:：]", line)
        if mm:
            cur_item["misconception"] = re.sub(r"^\s*\*?\*?[^：]*[:：]\s*", "", line).strip()
            continue
        # 总起/分述（N分）→ 新采分点（label 可含自由文本，如「分述①归纳与推测的对应」）
        ms = re.match(r"^\s*\*\*(总起|分述[^*（]*?)（(\d+)分）[:：]\*\*\s*(.*)$", line)
        if ms and cur_item.get("is_points"):
            cur_item["points"].append({"text": (ms.group(1) + "：" + ms.group(3)).strip(),
                                       "partial": int(ms.group(2))})
            continue
        # 条目激活期的续行（缩进解析行、顶层 $$ 公式块等）：宽收——
        # 结束条件是上面各「新条目/新标记」分支，或下方非本套内容的行
        if not re.match(r"^(\d+)\.\s", line):
            body = line.strip()
            if not body:
                continue
            if cur_item.get("is_points"):
                m1 = re.match(r"([①②③④⑤⑥⑦⑧⑨⑩])\s*(.*)$", body)
                if m1:
                    # 章节小测简答的 ①②③ 续行：新采分点（分值由导出时按原卷每题分值回填）
                    cur_item["points"].append({"text": m1.group(2).strip(), "partial": 0})
                elif cur_item["points"]:
                    cur_item["points"][-1]["text"] += "\n" + body
                else:
                    cur_item["answer"] += ("\n" if cur_item["answer"] else "") + body
            else:
                body = re.sub(r"^解析[:：]\s*", "", body)
                if cur_item["explanation"]:
                    cur_item["explanation"] += "\n" + body
                else:
                    cur_item["explanation"] = body
        # 非缩进行：可能是下一大题的标题行（已被上方分支处理），忽略
    flush()
    return results


def _ingest_point_line(item, text):
    """答案要点首行：可能是 ①…（无分值标记）或 总起（N分）：…"""
    ms = re.match(r"\*\*(总起|分述[①-⑩]?)（(\d+)分）[:：]\*\*\s*(.*)$", text)
    if ms:
        item["points"].append({"text": (ms.group(1) + "：" + ms.group(3)).strip(),
                               "partial": int(ms.group(2))})
        return
    m1 = re.match(r"([①②③④⑤⑥⑦⑧⑨⑩])\s*(.*)$", text)
    if m1:
        item["points"].append({"text": m1.group(2).strip(), "partial": 0})
    elif text:
        item["answer"] += text


# ---------------------------------------------------------------- 组装
def build_questions():
    sets_q = parse_questions(read_lines(os.path.join(PROJECT, "02《机器学习》章节小测（14套）.md")))
    exams_q = parse_questions(read_lines(os.path.join(PROJECT, "03《机器学习》综合测试卷（5套）.md")))
    sets_a = parse_answers(read_lines(os.path.join(PROJECT, "02《机器学习》章节小测（14套）.md")))
    exams_a = parse_answers(read_lines(os.path.join(PROJECT, "03《机器学习》综合测试卷（5套）.md")))
    all_answers = {}
    all_answers.update(sets_a)
    all_answers.update(exams_a)

    questions = []
    missing_expl = []
    seen_stems = {}
    dropped_dup = []
    for coll in (sets_q, exams_q):
        for s in coll:
            key = ("set", s["chapter"], s["set"]) if s["kind"] == "set" else ("exam", 8, s["set"])
            answers = all_answers.get(key, {})
            diff = DIFF_MAP_A if s["kind"] == "set" and s["set"] == "A" else (
                DIFF_MAP_B if s["kind"] == "set" else ("medium" if s["set"] <= 2 else "hard"))
            for qtype, items in s["types"].items():
                for it in items:
                    ans = answers.get(qtype, {}).get(it["no"])
                    # 题型前缀必须进 id：单选/多选/简答在各套内独立编号（都从 1 起），不加前缀必然冲突
                    # id 中的题型段用原始小节名（论述=essay）：简答与论述在综合卷内独立编号，
                    # 都映射到 short 行为组，不加区分必然撞号
                    qid = ("ml-c%d%s-%s-%d" % (s["chapter"], s["set"], it.get("sec") or qtype, it["no"])
                           if s["kind"] == "set" else "ml-s%d-%s-%d" % (s["set"], it.get("sec") or qtype, it["no"]))
                    if qtype == "single" or qtype == "multi":
                        letters = sorted((ans or {}).get("answer", "").replace(" ", ""))
                        explanation = (ans or {}).get("explanation", "")
                    elif qtype == "blank":
                        letters = []
                        explanation = (ans or {}).get("explanation", "")
                    else:
                        letters = []
                        explanation = (ans or {}).get("explanation", "")
                    q = {
                        "id": qid, "type": qtype,
                        "typeGroup": "short" if qtype in ("short",) else qtype,
                        "difficulty": diff, "chapter": s["chapter"],
                        "knowledgePoint": str(s["chapter"]),
                        "source": {"text": _source_text(s, qtype), "kind": "textbook"},
                        "stem": it["stem"], "options": it["options"] or None,
                        "answer": letters if qtype in ("single", "multi") else
                                  _blank_answer(ans) if qtype == "blank" else [],
                        "answerText": _answer_text(ans, qtype),
                        "points": _points(ans, qtype, s["kind"]),
                        "explanation": explanation,
                        "misconception": (ans or {}).get("misconception") or None,
                        "extension": None,
                        "tags": ["第%d章" % s["chapter"],
                                 "综合卷" if s["kind"] == "exam" else (s["set"] + "卷")],
                        "verify": [],
                        "accept": _blank_accepts(ans) if qtype == "blank" else None,
                    }
                    if not explanation and qtype in ("single", "multi"):
                        missing_expl.append(qid)
                    # 综合卷与小测偶有原题重复（源材料如此）：保留先出现者，弃后出现者
                    skey = it["stem"][:50]
                    if skey in seen_stems:
                        dropped_dup.append("%s(=%s)" % (qid, seen_stems[skey]))
                        continue
                    seen_stems[skey] = qid
                    questions.append(q)
    if dropped_dup:
        print("[assemble] 丢弃源材料内重复题干 %d 题：%s" % (len(dropped_dup), dropped_dup[:4]))
    return questions, missing_expl


def _source_text(s, qtype):
    if s["kind"] == "set":
        return "《机器学习》章节小测 第%d章 %s卷（依据课程课件 00%d 系列）" % (
            s["chapter"], s["set"], s["chapter"])
    return "《机器学习》综合测试卷 第%d套（难度递增，满分 100 分）" % s["set"]


def _blank_answer(ans):
    v = (ans or {}).get("answer", "").strip()
    return [v] if v else []


def _blank_accepts(ans):
    v = (ans or {}).get("answer", "").strip()
    if not v:
        return None
    accepts = [v]
    stripped = re.sub(r"[（(][^）)]*[）)]", "", v).strip()
    if stripped and stripped != v:
        accepts.append(stripped)
    head = re.split(r"[（(，,]", v)[0].strip()
    if head and head not in accepts:
        accepts.append(head)
    return accepts


def _answer_text(ans, qtype):
    if qtype not in ("short",):
        return None
    a = ans or {}
    if a.get("points"):
        return "\n".join(p["text"] for p in a["points"])
    return a.get("answer", "") or a.get("explanation", "")


def _points(ans, qtype, kind):
    a = ans or {}
    pts = a.get("points") or []
    if not pts:
        # 兜底：答案要点无 ① 分点（如整段公式推导）→ 整体作为单一采分点，
        # 分值取原卷该题满分（章节小测简答 9 分 / 综合卷简答 10 分 / 论述 15 分）
        txt = a.get("answer", "") or a.get("explanation", "")
        if txt and qtype == "short":
            total = {"set": 9}.get(kind, 10)
            return [{"text": txt.strip(), "partial": total}]
        return None
    out = []
    # 章节小测简答：①②③ 无分值标记 → 每点 3 分（原卷每题 9 分 / 3 点）
    fallback = 3 if kind == "set" else 2
    for p in pts:
        partial = p["partial"] or fallback
        out.append({"text": p["text"], "partial": partial})
    return out


# ---------------------------------------------------------------- 门禁
def gates(questions):
    ids = [q["id"] for q in questions]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit("[gates] 重复题号：%s" % dup[:8])
    stems = {}
    bad = 0
    for q in questions:
        if not q["stem"]:
            print("      [gate] %s 缺题干" % q["id"])
            bad += 1
        if q["type"] in ("single", "multi", "blank") and not q["explanation"]:
            print("      [gate] %s 客观/填空题缺解析" % q["id"]); bad += 1
        if q["type"] == "short" and not (q["answerText"] and q["points"]):
            print("      [gate] %s 主观题缺参考答案/采分点" % q["id"]); bad += 1
        if q["type"] in ("single", "multi"):
            letters = "ABCDE"[:len(q["options"] or [])]
            if not q["options"]:
                print("      [gate] %s 客观题缺选项" % q["id"]); bad += 1
            if q["type"] == "single" and len(q["answer"]) != 1:
                print("      [gate] %s 单选答案数 %d != 1" % (q["id"], len(q["answer"]))); bad += 1
            if q["type"] == "multi" and len(q["answer"]) < 2:
                print("      [gate] %s 多选答案数 %d < 2" % (q["id"], len(q["answer"]))); bad += 1
            for a in q["answer"]:
                if a not in letters:
                    print("      [gate] %s 答案 %s 不在选项内" % (q["id"], a)); bad += 1
        if q["type"] == "blank" and not q["answer"]:
            print("      [gate] %s 填空缺答案" % q["id"]); bad += 1
        if q["type"] == "short":
            if not q["answerText"]:
                print("      [gate] %s 主观题缺参考答案" % q["id"]); bad += 1
            if not q["points"] or sum(p["partial"] for p in q["points"]) <= 0:
                print("      [gate] %s 主观题缺采分点" % q["id"]); bad += 1
        key = q["stem"][:50]
        if key in stems:
            print("      [gate] %s 与 %s 题干重复" % (q["id"], stems[key])); bad += 1
        stems[key] = q["id"]
    if bad:
        raise SystemExit("[gates] %d 处问题，拒绝导出" % bad)
    print("[OK ] 门禁：题号唯一 / 解析齐备 / 答案在选项内 / 采分点齐备 / 无重复题干")


# ---------------------------------------------------------------- 导出
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
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    print("[subject] 步骤 1/3：解析 md 题库源")
    questions, missing_expl = build_questions()
    from collections import Counter
    c_type = Counter(q["type"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    print("      解析出 %d 题：%s；难度 %s" % (
        len(questions), dict(c_type), dict(c_diff)))
    if missing_expl:
        print("[gates] 无解析的客观题（不允许入库）：%s" % missing_expl[:10])
        raise SystemExit("[gates] %d 题缺解析——先补解析再出包" % len(missing_expl))
    if not args.skip_gates:
        gates(questions)

    print("[subject] 步骤 2/3：生成分片")
    shards = shard_questions(questions)
    exam_n = c_ch.get(8, 0)

    print("[subject] 步骤 3/3：写出产物")
    os.makedirs(data_dir, exist_ok=True)
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
            "sub": "7 章体系 + 综合卷 · %d 题 · 含考研级综合测试" % len(questions),
            "desc": "机器学习 %d 题刷题子站：章节小测 A/B 卷 + 5 套综合卷，逐题解析与课件出处，进度保存在本地。" % len(questions),
            "aboutHtml": "".join([
                "<p><b>内容来源</b>：《机器学习》课程课件（001–006）体系；章节小测 14 套（A 卷基础巩固、"
                "B 卷理解运用）+ 综合测试卷 5 套（难度递增），共 <b>%d</b> 题，逐题配解析/答案要点。</p>" % len(questions),
                "<p><b>题型说明</b>：单选 %d · 多选 %d · 填空 %d · 简答与论述 %d；"
                "综合卷归入「综合卷」章节。</p>" % (c_type.get("single", 0), c_type.get("multi", 0),
                                                 c_type.get("blank", 0), c_type.get("short", 0)),
                "<p><b>判分口径</b>：客观题自动判分（多选少选、错选均 0 分）；简答与论述题<b>按采分点自评</b>，"
                "主观题满分 = 采分点分值之和（与原卷每题满分一致）。</p>",
                "<p><b>自托管说明</b>：全站资源自托管，无任何第三方依赖；进度数据保存在浏览器本地。</p>",
            ]),
            "footerHtml": "<p>题库共 <b>%d</b> 题：单选 %d · 多选 %d · 填空 %d · 简答与论述 %d；"
                          "综合卷 %d 题归入「综合卷」章节。</p>" % (
                              len(questions), c_type.get("single", 0), c_type.get("multi", 0),
                              c_type.get("blank", 0), c_type.get("short", 0), exam_n),
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
