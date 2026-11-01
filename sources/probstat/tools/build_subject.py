# -*- coding: utf-8 -*-
r"""概率论与数理统计 —— 学科产物导出：跑完内容门禁后，导出平台子站数据分片。

用法：
    python tools/build_subject.py                # 导出到默认平台仓（自动探测）
    python tools/build_subject.py --out <dir>    # 指定导出目录（subjects/probstat）
    python tools/build_subject.py --skip-gates   # 跳过门禁（仅供调试；正式导出禁止）

流程：
    1. load_bank()   —— 装载 qa_prob 全部章节（ch1-ch4 + ch58 + special），顺序即导出顺序。
    2. 内容门禁      —— 10 道检查（ID/答案键/选项重复/题型口径/变体组/裸中文/控制字符等），
                        任何一道失败即中止；门禁不降级。
    3. 导出 data/：
       manifest.json —— subject 元数据 / sections / caliber / summary / 分片清单 / SHA256
       chNN[a-c].json —— 按章分片；单分片 > 200KB 自动对半拆分（预算门禁约束）

契约（quiz-platform-subject-v1）与字段说明见平台仓 docs/decisions.md。
"""
import argparse
import hashlib
import io
import json
import os
import re
import string
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

# ---------------------------------------------------------------- 学科元数据（平台子站的唯一配置源）
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

SEC = {
    "1.1": "随机试验与样本空间",
    "1.2": "概率的定义与性质",
    "1.3": "等可能概型（古典概型）",
    "1.4": "条件概率与乘法公式",
    "1.5": "全概率公式与贝叶斯公式",
    "1.6": "独立性",
    "2.1": "离散型随机变量",
    "2.2": "分布函数",
    "2.3": "连续型随机变量与概率密度",
    "2.4": "常见分布（二项/泊松/指数/正态）",
    "2.5": "随机变量函数的分布",
    "3.1": "二维随机变量与联合分布",
    "3.2": "边缘分布",
    "3.3": "条件分布",
    "3.4": "随机变量的独立性",
    "4.1": "数学期望",
    "4.2": "方差",
    "4.3": "协方差与相关系数",
    "4.4": "矩与切比雪夫不等式",
    "5.1": "依概率收敛",
    "5.2": "大数定律",
    "5.3": "中心极限定理",
    "6.1": "总体与样本",
    "6.2": "统计量与抽样分布",
    "6.3": "三大分布（χ²/t/F）",
    "7.1": "点估计（矩估计与极大似然）",
    "7.2": "估计量的评价标准",
    "7.3": "区间估计",
    "8.1": "假设检验的基本思想",
    "8.2": "正态总体参数的假设检验",
}

TYPE_ORDER = ("single", "multi", "judge", "blank", "short", "calc")
TYPE_LABEL = {"single": "单选", "multi": "多选", "judge": "判断",
              "blank": "填空", "short": "简答", "calc": "计算"}
DIFF_ORDER = ("basic", "medium", "hard")

SHARD_BUDGET = 200 * 1024  # 单分片字节上限（平台预算门禁约束，见实施方案 §5）

_MODULES = ("qa_prob.ch1", "qa_prob.ch2", "qa_prob.ch3", "qa_prob.ch4",
            "qa_prob.ch58", "qa_prob.special")


def load_bank():
    """装载全部题库模块；顺序 = ch1 → ch2 → ch3 → ch4 → ch58 → special。"""
    import importlib
    from qa_prob import common
    for mod in _MODULES:
        importlib.import_module(mod)
    return common.ALL_QUESTIONS


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), f.read(0) or b""):
            h.update(chunk)
    return h.hexdigest().upper()


def default_out():
    """默认导出位置：优先同级平台仓 subjects/probstat；否则项目内 platform-dist/。"""
    sibling = os.path.join(os.path.dirname(PROJECT), "quiz-platform", "subjects", SUBJECT["id"])
    if os.path.isdir(os.path.join(os.path.dirname(PROJECT), "quiz-platform")):
        return sibling
    return os.path.join(PROJECT, "platform-dist", SUBJECT["id"])


# ---------------------------------------------------------------- 内容门禁
def run_gates(questions):
    """10 道内容门禁；返回错误列表（空 = 通过）。"""
    errs = []
    seen_ids = set()
    vg_members = {}

    for q in questions:
        qid = q["id"]
        # G1 ID 唯一 + 格式
        if qid in seen_ids:
            errs.append("G1 重复 ID：%s" % qid)
        seen_ids.add(qid)
        if not re.match(r"^ps-\d{3,4}$", qid):
            errs.append("G1 ID 格式非法：%s" % qid)

        # G2 口径字段
        if q["typeGroup"] not in TYPE_ORDER:
            errs.append("G2 %s 非法题型组：%s" % (qid, q["typeGroup"]))
        if q["difficulty"] not in DIFF_ORDER:
            errs.append("G2 %s 非法难度：%s" % (qid, q["difficulty"]))
        if not 1 <= q["chapter"] <= 8:
            errs.append("G2 %s 章节越界：%s" % (qid, q["chapter"]))
        if q["knowledgePoint"] not in SEC:
            errs.append("G2 %s 考点不在 SEC：%s" % (qid, q["knowledgePoint"]))

        # G3 答案键（字母口径：A/B/C… 对应 options 下标）
        opts = q["options"] or []
        ans = q["answer"] or []
        if q["type"] in ("single", "multi", "judge"):
            letters = string.ascii_uppercase[:len(opts)]
            if not ans:
                errs.append("G3 %s 答案为空" % qid)
            for a in ans:
                if a not in letters:
                    errs.append("G3 %s 答案越界：%r（%d 个选项）" % (qid, a, len(opts)))
            if q["type"] == "single" and len(ans) != 1:
                errs.append("G3 %s 单选答案数 != 1：%r" % (qid, ans))
            if q["type"] == "multi" and len(ans) < 2:
                errs.append("G3 %s 多选答案数 < 2：%r" % (qid, ans))
            if q["type"] == "judge" and ans not in (["A"], ["B"]):
                errs.append("G3 %s 判断答案必须 A/B：%r" % (qid, ans))

        # G4 选项：仅客观选择题（单选/多选）受选项规则约束；判断题选项固定；
        #          填空/简答/计算无选项，用答案字段承载
        if q["type"] == "judge":
            if opts != ["正确", "错误"]:
                errs.append("G4 %s 判断题选项必须是 正确/错误：%r" % (qid, opts))
        elif q["type"] in ("single", "multi"):
            if not (2 <= len(opts) <= 8):
                errs.append("G4 %s 选项数量非法：%d" % (qid, len(opts)))
            seen_opt = set()
            for o in opts:
                if not isinstance(o, str) or not o.strip():
                    errs.append("G4 %s 存在空选项" % qid)
                    break
                if o.strip() in seen_opt:
                    errs.append("G4 %s 选项重复：%r" % (qid, o.strip()[:30]))
                    break
                seen_opt.add(o.strip())

        # G5 控制字符 + 数学模式内裸中文（未包 \text{}）
        for field in ("stem", "explanation", "answerText", "misconception"):
            text = q.get(field) or ""
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text):
                errs.append("G5 %s.%s 含控制字符" % (qid, field))
            for m in re.finditer(r"\$([^$]+)\$", text):
                inner = m.group(1)
                stripped = re.sub(r"\\text\{[^}]*\}", "", inner)
                if re.search(r"[\u4e00-\u9fff]", stripped):
                    errs.append("G5 %s.%s 数学模式内裸中文：%s…" % (qid, field, inner[:24]))

        # G7 解析必填 / G8 题干长度
        if not (q.get("explanation") or "").strip():
            errs.append("G7 %s 缺解析" % qid)
        if len((q.get("stem") or "").strip()) < 8:
            errs.append("G8 %s 题干过短" % qid)

        # G9 主观题（简答/计算）须有采分点 + 参考答案
        if q["typeGroup"] in ("short", "calc"):
            pts = q.get("points") or []
            if len(pts) < 2:
                errs.append("G9 %s 采分点 < 2" % qid)
            if any((p.get("partial") or 0) <= 0 for p in pts):
                errs.append("G9 %s 存在非正分值采分点" % qid)
            if not (q.get("answerText") or "").strip():
                errs.append("G9 %s 缺参考答案" % qid)

        # G10 verify 结构
        for v in (q.get("verify") or []):
            if not all(isinstance(v.get(k), str) and v[k] for k in ("desc", "code", "expected")):
                errs.append("G10 %s verify 结构不完整" % qid)
                break

        # 变体组登记（G6 在装载后统一查规模）
        vg = q.get("variantGroup")
        if vg:
            vg_members.setdefault(vg, []).append(qid)

    # G6 变体组：格式 + 至少 2 题（举一反三语义）
    for vg, members in vg_members.items():
        if not re.match(r"^vg-[a-z0-9-]+$", vg):
            errs.append("G6 变体组 ID 非法：%s" % vg)
        if len(members) < 2:
            errs.append("G6 变体组 %s 只有 %d 题（举一反三至少 2 题）：%s"
                        % (vg, len(members), ",".join(members)))
    return errs


def _encoded_size(p):
    """分片落盘尺寸：必须与 json.dump 的写盘口径一致（indent=1），否则预算测量失真。"""
    return len(json.dumps(p, ensure_ascii=False, indent=1).encode("utf-8"))


def shard_questions(questions):
    """按章分组，组内保持 load_bank 的排序（已排序）；超预算的章再对半拆。"""
    from collections import OrderedDict
    by_ch = OrderedDict()
    for q in questions:
        by_ch.setdefault(q["chapter"], []).append(q)
    shards = []
    for ch in sorted(by_ch):
        qs = by_ch[ch]
        parts = [{"name": "ch%d.json" % ch, "questions": qs}]
        # 拆分：按落盘口径量尺寸，超预算就对半，最多拆 4 份
        for _ in range(3):
            big = [p for p in parts if _encoded_size(p) > SHARD_BUDGET]
            if not big:
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
        # 命名：ch1.json / ch5a.json / ch5b.json …
        if len(parts) == 1:
            parts[0]["name"] = "ch%d.json" % ch
        else:
            for i, p in enumerate(parts):
                p["name"] = "ch%d%s.json" % (ch, "abcdef"[i])
        for p in parts:
            p["chapter"] = ch
        shards.extend(parts)
    return shards


def compose_about_html(questions):
    """平台版「题库说明」：题型分布 + 判分口径 + 自托管说明。"""
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    type_part = " · ".join("%s %d" % (TYPE_LABEL[t], c_type.get(t, 0)) for t in TYPE_ORDER)
    about = []
    about.append("<p><b>内容来源</b>：以浙江大学《概率论与数理统计》第四版为基准出题，每题标注考点出处。</p>")
    about.append("<p><b>题型分布</b>：%s；难度分基础 / 中等 / 困难三档。</p>" % type_part)
    about.append("<p><b>判分口径</b>：客观题自动判分；简答与计算题<b>按采分点自评</b>。</p>")
    about.append("<p><b>自托管说明</b>：全站资源自托管，无第三方依赖；进度保存在浏览器本地。</p>")
    return "".join(x for x in about if x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="导出目录（subjects/probstat）")
    ap.add_argument("--skip-gates", action="store_true", help="跳过门禁（仅调试）")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    # 1) 装载题库（与构建同源同序）
    print("[subject] 步骤 1/3：装载题库")
    questions = load_bank()
    print("      装载 %d 题（%s）" % (len(questions), " + ".join(m.split(".")[1] for m in _MODULES)))

    # 2) 内容门禁
    if args.skip_gates:
        print("[subject] ⚠ --skip-gates：门禁被跳过（仅限调试，禁止用于发布）")
    else:
        print("[subject] 步骤 2/3：跑内容门禁（10 道）")
        errs = run_gates(questions)
        if errs:
            for e in errs[:30]:
                print("  [FAIL] " + e)
            raise SystemExit("[subject] 门禁未通过（%d 处），拒绝导出平台产物。" % len(errs))
        print("      全部通过")

    # 3) 写分片 → 计哈希 → 写 manifest
    print("[subject] 步骤 3/3：写出产物")
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    tagged = sum(1 for q in questions if any("真题" in t for t in (q.get("tags") or [])))
    vg_count = len(set(q["variantGroup"] for q in questions if q.get("variantGroup")))

    shards = shard_questions(questions)

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
            raise SystemExit("[subject] 分片 %s（%d 字节）超出预算 %d——请人工检查" %
                             (p["name"], size, SHARD_BUDGET))
        shard_entries.append({"file": p["name"], "chapter": p["chapter"],
                              "count": len(p["questions"]), "sha256": sha256(path)})

    total = len(questions)
    manifest = {
        "schema": "quiz-platform-subject-v1",
        "subject": SUBJECT,
        "sections": SEC,
        "caliber": {
            "total": total,
            "byType": {t: c_type.get(t, 0) for t in TYPE_ORDER},
            "byDifficulty": {d: c_diff.get(d, 0) for d in DIFF_ORDER},
            "byChapter": {str(k): c_ch[k] for k in sorted(c_ch)},
            "limits": {"singleMin": 0, "singleMax": 9999, "multiRange": 9999},
        },
        "summary": {
            "sub": "8 章 · %d 题 · 章节小测 + 综合测试" % total,
            "desc": "概率论与数理统计 %d 题刷题子站：8 章、三难度、逐题解析与考点出处。" % total,
            "aboutHtml": compose_about_html(questions),
            "footerHtml": "<p>题库共 <b>%d</b> 题（浙大第四版 §1–§8）。</p>" % total,
            "realExamTagged": tagged,
        },
        "shards": shard_entries,
    }
    manifest_path = os.path.join(data_dir, "manifest.json")
    with io.open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print("[OK ] manifest.json（%d 分片，共 %d 题，变体组 %d 组，真题改编 %d 题）"
          % (len(shard_entries), total, vg_count, tagged))
    print("[subject] 导出完成：%s" % data_dir)


if __name__ == "__main__":
    main()
