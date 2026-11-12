# -*- coding: utf-8 -*-
r"""tools/platform/check_plan_doc.py — 方案文档里的数字必须与真实产物一致。

**为什么需要这道门禁（2026-11-13 实测）**
《应用化实施方案与迭代计划.md》是这个项目的**方案与交付说明正本**，它写着
「当前全量：221 文件 / 8.11 MB；题量见 registry.json（高数 905 / 线代 528 / **概率统计 100** / …）」。
一查：概率统计早就从 100 题扩到 156 题，dist 体积也早已不是 8.11 MB ——
**文档停在了扩题之前**。而内容门禁只看题库与产物、字节门禁只看「线上 == HEAD」，
**文档这一层在整个项目里没有任何门禁**，数字静默腐烂。

这道门禁把方案文档钉在事实源上：
  ① 文档里「N 学科 / M 题」的断言 == `subjects/registry.json`（题量与学科数的唯一事实源）；
  ② 文档里逐学科题量括号 == registry 里各学科的题量；
  ③ 文档里「dist 文件数 / 体积」== 真实 `dist/`（构建产物；不存在就跳过并说明）。

**解析不到就报红**：句式被改 ⇒ 直接失败并说明「没找到该断言」——
不允许「找不到就默认通过」，那正是让这类腐烂静默下去的写法。

用法：
    python tools/platform/check_plan_doc.py                # 检查默认文档
    python tools/platform/check_plan_doc.py --doc X --dist Y
退出码：0 = 一致；1 = 有对不上的地方（或断言解析不到）。
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
DOC_REL = os.path.join("docs", "应用化实施方案与迭代计划.md")

# 文档里用的**简称** → registry 的学科 id（registry 里的 name 是全称）。
# 认不出的标签 ⇒ 报红（文档句式变了，别让它悄悄失去校验）。
LABEL_TO_ID = {
    "高数": "calculus", "高等数学": "calculus",
    "线代": "linalg", "线性代数": "linalg",
    "机器学习": "ml",
    "数可视": "dataviz", "数据可视化": "dataviz",
    "概率统计": "probstat", "概率论": "probstat", "概率论与数理统计": "probstat",
}


def _cn_num(text):
    """中文数字 → 整数（只需支持「五」这种量词场景）。"""
    digits = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    if text in digits:
        return digits[text]
    if len(text) == 2 and text[0] == "十":
        return 10 + digits.get(text[1], 0)
    if len(text) == 2 and text[1] == "十":
        return digits.get(text[0], 0) * 10
    return -1


def _read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def _dist_stats(dist):
    n = 0
    total = 0
    for root, dirs, files in os.walk(dist):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            n += 1
            total += os.path.getsize(os.path.join(root, fn))
    return n, total


def check(doc_path, registry_path=None, dist=None):
    """返回问题清单（空列表 = 全部对得上）。"""
    problems = []
    if not os.path.isfile(doc_path):
        return ["找不到文档：%s" % doc_path]
    registry_path = registry_path or os.path.join(PLATFORM, "subjects", "registry.json")
    if not os.path.isfile(registry_path):
        return ["找不到 registry.json：%s" % registry_path]
    with open(registry_path, encoding="utf-8") as f:
        reg = json.load(f)
    subs = reg.get("subjects") or []
    by_id = {s["id"]: int(s.get("total") or 0) for s in subs}
    total = sum(by_id.values())
    doc = _read(doc_path)

    # ① 「N 学科 … M 题」断言
    #    只认**全学科口径**（N == registry 的学科数）：文档里也有历史陈述的
    #    「三学科 170 题渲染截断（线代 108 / 高数 53 / 概率论 9）」——
    #    那是修复前的截断题数，不是现状。全学科口径的才是「当前全站多少题」。
    found_total = False
    for m in re.finditer(r"(\d+|[一二三四五六七八九十]+)\s*学科", doc):
        raw = m.group(1)
        n_sub = int(raw) if raw.isdigit() else _cn_num(raw)
        if n_sub != len(subs):
            continue
        tail = doc[m.end():m.end() + 240]
        mm = re.search(r"([\d,]+)\s*题", tail)
        if not mm:
            continue                      # 只是提到「五学科 --restamp」之类，没有题量断言
        found_total = True
        said = int(mm.group(1).replace(",", ""))
        if said != total:
            ctx = doc[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            problems.append("文档写「%d 题」!= registry 实际 %d 题（%s）" % (said, total, ctx))
    if not found_total:
        problems.append("文档里找不到「N 学科 … M 题」的断言（句式被改了？）")

    # ② 逐学科题量括号
    #    只认**列全学科**的括号（覆盖 registry 的大部分学科才算「现状断言」）。
    #    为什么不逐个认：文档里也有**历史**陈述的括号，例如
    #    「三学科 170 题渲染截断（线代 108 / 高数 53 / 概率论 9）」——
    #    那是修复前的截断题数，不是现状。宁可少查，也不能让门禁满地误报。
    found_list = False
    for m in re.finditer(r"（([^（）]*)）", doc):
        scope = m.group(1)
        pairs = re.findall(r"([一-龥]+)\s*(\d+)", scope)
        known = [(lab, int(n)) for lab, n in pairs if lab in LABEL_TO_ID]
        if len({LABEL_TO_ID[lab] for lab, _ in known}) < max(2, len(subs) - 1):
            continue
        found_list = True
        for lab, n in known:
            sid = LABEL_TO_ID[lab]
            if by_id.get(sid) != n:
                problems.append("文档写 %s %d 题 != registry 实际 %d 题" % (lab, n, by_id.get(sid, -1)))
        unknown = [lab for lab, _ in pairs if lab not in LABEL_TO_ID]
        if unknown:
            problems.append("括号里有认不出的学科标签 %r（文档句式变了？）" % unknown)
    if not found_list:
        problems.append("文档里找不到逐学科题量的括号清单（句式被改了？）")

    # ③ dist 文件数 / 体积
    m = re.search(r"([\d,]+)\s*文件\s*/\s*([\d.]+)\s*MB", doc)
    if not m:
        problems.append("文档里找不到「N 文件 / X MB」的 dist 断言")
    else:
        said_n = int(m.group(1).replace(",", ""))
        said_mb = float(m.group(2))
        if dist and os.path.isdir(dist):
            n, total_b = _dist_stats(dist)
            if said_n != n:
                problems.append("文档写 dist %d 文件 != 真实 %d 文件" % (said_n, n))
            real_mb = round(total_b / 1000000.0, 2)
            if abs(said_mb - real_mb) > 0.005:
                problems.append("文档写 dist %.2f MB != 真实 %.2f MB（%d 字节）"
                                % (said_mb, real_mb, total_b))
        else:
            problems.append("没有 dist/ 可核对（先跑 build_all.py --dist）")
    return problems


def main():
    ap = argparse.ArgumentParser(description="方案文档里的数字必须与真实产物一致")
    ap.add_argument("--doc", default=os.path.join(PLATFORM, DOC_REL))
    ap.add_argument("--registry", default=None)
    ap.add_argument("--dist", default=os.path.join(PLATFORM, "dist"))
    args = ap.parse_args()

    problems = check(args.doc, args.registry, args.dist)
    if problems:
        print("[FAIL] 方案文档与产物对不上 %d 处：" % len(problems))
        for p in problems:
            print("   ⚠ " + p)
        print("修法：改文档（数字要跟产物一致），别改产物去迁就文档。")
        return 1
    print("[OK ] 方案文档里的学科数 / 题量 / dist 体积与真实产物一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
