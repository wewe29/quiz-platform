# -*- coding: utf-8 -*-
r"""学科产物导出：跑完全部内容门禁后，把题库导出为平台子站的数据分片。

用法：
    python tools/build_subject.py                # 导出到默认平台仓（自动探测）
    python tools/build_subject.py --out <dir>    # 指定导出目录（subjects/<id>）
    python tools/build_subject.py --skip-gates   # 跳过门禁（仅供调试；正式导出禁止）

流程：
    1. update_site.py --no-stage   —— 完整门禁链（构建 + 6 道验证），任何一步失败即中止；
                                      门禁不降级：平台产物必须与单文件版出自同一套检查。
    2. load_bank()                 —— 与构建完全一致的题库装载（同一排序、同一 idx 语义）。
    3. 导出 data/：
       manifest.json               —— subject 元数据 / sections / caliber / summary / 分片清单 / SHA256
       chNN[a-c].json              —— 按章分片；单分片 > 200KB 自动对半拆分（预算门禁约束）
    4. 打印产物清单。

契约（quiz-platform-subject-v1）与字段说明见平台仓 docs/decisions.md。
"""
import argparse
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from qa_bank import load_bank  # noqa: E402
from qa_bank.common import SEC  # noqa: E402
from qa_bank import target as T  # noqa: E402
import build_quiz  # noqa: E402  复用 build_summary 的文案生成

# ---------------------------------------------------------------- 学科元数据（平台子站的唯一配置源）
SUBJECT = {
    "id": "linalg",
    "name": "线性代数",
    "textbook": "同济大学《工程数学·线性代数》第六版",
    "bankId": "linear-algebra-tj6-v1",
    "chapters": 6,
    "chapterLabels": {
        "1": "第1章 行列式",
        "2": "第2章 矩阵及其运算",
        "3": "第3章 初等变换与线性方程组",
        "4": "第4章 向量组的线性相关性",
        "5": "第5章 相似矩阵及二次型",
        "6": "第6章 线性空间与线性变换（选学）",
    },
}

SHARD_BUDGET = 200 * 1024  # 单分片字节上限（平台预算门禁约束，见实施方案 §5）


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), f.read(0) or b""):
            h.update(chunk)
    return h.hexdigest().upper()


def default_out():
    """默认导出位置：优先同级平台仓 subjects/<id>；否则项目内 platform-dist/。"""
    sibling = os.path.join(os.path.dirname(PROJECT), "quiz-platform", "subjects", SUBJECT["id"])
    if os.path.isdir(os.path.join(os.path.dirname(sibling), os.pardir)) or os.path.isdir(
            os.path.join(os.path.dirname(PROJECT), "quiz-platform")):
        return sibling
    return os.path.join(PROJECT, "platform-dist", SUBJECT["id"])


def compose_about_html(questions, summary):
    """平台版「题库说明」：复用单文件文案，但把离线条款改写为平台事实。"""
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    type_part = " · ".join("%s %d" % (T.TYPE_LABEL[t], c_type.get(t, 0)) for t in T.TYPE_ORDER)
    diff_part = " · ".join("%s %d" % (T.DIFF_LABEL[d], c_diff.get(d, 0)) for d in T.DIFF_ORDER)
    about = []
    about.append("<p><b>内容来源</b>：以同济大学《工程数学·线性代数》第六版（高等教育出版社，2014）为基准出题，"
                 "每题标注考点出处。</p>")
    about.append("<p><b>素材盘点</b>：本机<b>不存在</b>《线性代数》课程资料；全部线性代数内容仅以机器学习课程内嵌的 "
                 "5 页课件与 4 份笔记形式存在。故本库 %d 题按公开教材出题，磁盘资料仅作对照与「引申」。</p>"
                 % len(questions))
    about.append(summary["ABOUT_EXTRA"])
    about.append("<p><b>判分口径</b>：客观题自动判分；简答与计算题<b>由你按采分点自评</b>"
                 "（勾选「得到 / 未得到」），不伪装成自动判分。</p>")
    about.append("<p><b>多选计分</b>：全对得满分；<b>少选、错选均 0 分</b>。</p>")
    about.append("<p><b>自托管说明</b>：全站资源（题库数据、公式渲染库、字体）均自托管于本站，"
                 "无任何第三方依赖；进度数据保存在浏览器本地。</p>")
    about.append("<p>题型 %s；难度 %s。</p>" % (type_part, diff_part))
    return "".join(x for x in about if x)


def compose_footer_html(summary):
    parts = [summary["SUMMARY_FOOTER"], summary["FOOTER_EXTRA"],
             "<p>内容基准：同济大学数学系《工程数学·线性代数》第六版（ISBN 978-7-04-039661-4）。%s</p>"
             % summary["CH6_NOTE"], summary["EXT_NOTE"]]
    return "".join(x for x in parts if x)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="导出目录（subjects/<id>）")
    ap.add_argument("--skip-gates", action="store_true", help="跳过门禁（仅调试）")
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out or default_out())
    data_dir = os.path.join(out_dir, "data")
    print("[subject] 导出目标：%s" % out_dir)

    # 1) 完整门禁链（与单文件版完全同一套，不降级）
    if args.skip_gates:
        print("[subject] ⚠ --skip-gates：门禁被跳过（仅限调试，禁止用于发布）")
    else:
        import subprocess
        print("[subject] 步骤 1/3：跑完整门禁链（update_site.py --no-stage）")
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, os.path.join(HERE, "update_site.py"), "--no-stage"],
                           cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        tail = [l for l in out.splitlines() if l.strip()][-12:]
        for l in tail:
            print("      " + l)
        if p.returncode != 0:
            raise SystemExit("[subject] 门禁未通过，拒绝导出平台产物。")

    # 2) 装载题库（与构建同源同序）
    print("[subject] 步骤 2/3：装载题库并生成分片")
    questions = load_bank()

    summary = build_quiz.build_summary(questions)
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    c_ch = Counter(q["chapter"] for q in questions)
    tagged = sum(1 for q in questions if T.EXTENSION_TAG in (q.get("tags") or []))

    shards = shard_questions(questions)

    # 3) 写分片 → 计哈希 → 写 manifest
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
            raise SystemExit("[subject] 分片 %s（%d 字节）超出预算 %d——请人工检查" %
                             (p["name"], size, SHARD_BUDGET))
        shard_entries.append({"file": p["name"], "chapter": p["chapter"],
                              "count": len(p["questions"]), "sha256": sha256(path)})

    manifest = {
        "schema": "quiz-platform-subject-v1",
        "subject": SUBJECT,
        "sections": SEC,
        "caliber": {
            "total": len(questions),
            "byType": {t: c_type.get(t, 0) for t in T.TYPE_ORDER},
            "byDifficulty": {d: c_diff.get(d, 0) for d in T.DIFF_ORDER},
            "byChapter": {str(k): c_ch[k] for k in sorted(c_ch)},
            "limits": T.limits(),
        },
        "summary": {
            "sub": summary["SUMMARY_SUB"],
            "desc": summary["SUMMARY_DESC"],
            "aboutHtml": compose_about_html(questions, summary),
            "footerHtml": compose_footer_html(summary),
            "realExamTagged": tagged,
        },
        "shards": shard_entries,
    }
    manifest_path = os.path.join(data_dir, "manifest.json")
    with io.open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print("[OK ] manifest.json（%d 分片，共 %d 题，真题改编 %d 题）"
          % (len(shard_entries), len(questions), tagged))
    print("[subject] 导出完成：%s" % data_dir)


if __name__ == "__main__":
    main()
