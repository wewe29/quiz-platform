# -*- coding: utf-8 -*-
r"""自考《高等数学（工本）》(00023) 真题 → 题库模块。

数据源（已下载到本地缓存，可逐题溯源到具体卷面文件）：
    GitHub: huangnaisheng/zikao-exam-solutions
    路径：00023-高等数学（工本）/YYYY-MM.md
    每份卷面含：试卷结构、考点分布总览表、逐题解析（题目 / 答案 / 考点 / 解析 / 易错提醒）。

体例非常规整，可稳定解析：
    ## 第 N 题
    **题目**：<题干>
    A. …　　B. …　　C. …　　D. …
    **答案**：X
    ### 考点 / ### 解析 / ### 易错提醒

入库规则：
  · 选择题（1–10）→ single，答案取源卷；
  · 计算题与综合题（11–22）→ calc，参考答案取源卷解析，采分点由解析的「第 N 步」拆分而来；
  · 知识点按「考点分布总览」的考点关键词挂到同济第七版节次上，归不上的丢弃。

用法：
    python tools/research/build_zikao_bank.py --report   # 只看统计
    python tools/research/build_zikao_bank.py             # 产出模块
"""
import io
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "_cache")
OUT_DIR = os.path.join(TOOLS, "qa_bank", "exam")

sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from points import make_points   # noqa: E402

REPO = "huangnaisheng/zikao-exam-solutions"
DIR_IN_REPO = "00023-高等数学（工本）"
BLOB = "https://github.com/%s/blob/main/%s/" % (REPO, DIR_IN_REPO)
ZIP = os.path.join(CACHE, "huangnaisheng_zikao-exam-solutions.zip")

PAPERS = [
    ("2022-10", "2022 年 10 月"), ("2023-04", "2023 年 4 月"),
    ("2023-10", "2023 年 10 月"), ("2024-04", "2024 年 4 月"),
    ("2024-10", "2024 年 10 月"), ("2025-04", "2025 年 4 月"),
    ("2025-10", "2025 年 10 月"), ("2026-04", "2026 年 4 月"),
]

# ---------------------------------------------------------------- 知识点映射
# (关键词正则, 同济第七版节次)
KP_RULES = [
    (r"点与坐标面|坐标面|坐标轴|直角坐标系中点", "8.1"),
    (r"向量的数乘|向量的加法|向量的坐标|模长|向量及其线性运算|向量代数", "8.1"),
    (r"数量积|点积|向量积|混合积", "8.2"),
    (r"平面的点法式|平面方程|两平面的夹角|两平面夹角|平面及其方程|平面的方程|点到平面|法向量|方向余弦", "8.3"),
    (r"直线的对称式|空间直线|方向向量|两直线的夹角|两直线夹角|直线与平面", "8.4"),
    (r"旋转曲面|曲面方程|曲面及其方程", "8.5"),
    (r"切线方程|空间曲线|参数方程", "8.6"),
    (r"二元函数求值|二元函数|多元函数的基本概念|多元函数微分学|多元函数极值", "9.1"),
    (r"偏导数|求偏导|二阶偏导", "9.2"),
    (r"全微分", "9.3"),
    (r"隐函数", "9.5"),
    (r"方向导数|梯度", "9.7"),
    (r"驻点|极值|最值|拉格朗日", "9.8"),
    (r"三重积分", "10.3"),
    (r"二重积分|重积分", "10.2"),
    (r"对弧长的曲线积分|对弧长|弧长", "11.1"),
    (r"格林公式", "11.3"),
    (r"对坐标的曲线积分", "11.2"),
    (r"对坐标的曲面积分|曲面积分", "11.5"),
    (r"高斯公式|散度", "11.6"),
    (r"斯托克斯|旋度", "11.7"),
    (r"展开为幂级数|展开成幂级数|函数的幂级数|泰勒级数", "12.5"),
    (r"幂级数", "12.4"),
    (r"傅里叶", "12.7"),
    (r"交错级数|绝对收敛|条件收敛", "12.3"),
    (r"审敛|敛散性|收敛的判别|收敛条件|比较判别|根值|比值|比值判别", "12.2"),
    (r"几何级数|裂项|常数项级数|无穷级数|级数", "12.1"),
    (r"可分离变量", "7.2"),
    (r"齐次微分方程|齐次方程", "7.3"),
    (r"一阶线性|伯努利", "7.4"),
    (r"二阶常系数齐次", "7.6"),
    (r"二阶.*非齐次|二阶线性|特解|通解", "7.7"),
    (r"微分方程", "7.1"),
    (r"投影到.*面|坐标面", "11.5"),
    (r"极限|\\lim", "1.3"),
    (r"数列", "1.2"),
    (r"无穷小|无穷大", "1.4"),
    (r"连续|间断点", "1.8"),
    (r"导数|可导|求导", "2.2"),
    (r"中值定理|罗尔|柯西", "3.1"),
    (r"单调|凹凸|拐点", "3.4"),
    (r"极值|最值", "3.5"),
    (r"不定积分", "4.1"),
    (r"定积分", "5.1"),
    (r"反常积分|广义积分", "5.4"),
    (r"旋转体|侧面积", "6.3"),
    (r"体积|弧长", "6.2"),
    (r"面积", "6.2"),
]

# ---------------------------------------------------------------- 解析

Q_SPLIT = re.compile(r"^## 第 (\d+) 题\s*$", re.M)
OPTION_LINE = re.compile(r"^([A-D])\.\s*(.+?)(?=\s*[　]{2,}\s*[A-D]\.\s|\s*$)")
ANS_PATTERNS = [
    re.compile(r"\*\*答案\*\*\s*[：:]\s*(.+?)(?:\n|$)"),
    re.compile(r"\*\*答案[：:]\s*(.+?)\*\*(?:\n|$)"),
    re.compile(r"\*\*答案\*\*\s*[：:]\s*(.+?)(?:\n|$)"),
]
KP_LINE = re.compile(r"\*\*题目\*\*[：:]\s*(.*)")
STEP_RE = re.compile(r"\*\*第[一二三四五六七八九十]+步[：:]\s*(.*?)\*\*", re.S)

# 源卷面自己标注的转写问题（勘误/残缺/印错）——这类题直接丢弃，
# 不能因为「考点栏写的是勘误说明」就把它当成考点。
BAD_KP = re.compile(r"印成|漏写|残缺|勘误|应为|误写|排版|无法辨认|不清楚")


def read_paper(name):
    with zipfile.ZipFile(ZIP) as z:
        raw = z.read("zikao-exam-solutions-main/%s/%s.md" % (DIR_IN_REPO, name)).decode("utf-8", "replace")
    return raw


def parse_overview(text):
    """考点分布总览表 → {题号: (考点, 所属章节)}"""
    out = {}
    m = re.search(r"## 二、考点分布总览(.*?)(?=\n## )", text, re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if not cells[0].isdigit():
            continue
        out[int(cells[0])] = (cells[1], cells[2])
    return out


def split_sections(text):
    parts = Q_SPLIT.split(text)
    secs = []
    for i in range(1, len(parts), 2):
        secs.append((int(parts[i]), parts[i + 1]))
    return secs


def clean_md(text):
    """把 Markdown 表格压成行内文字，保留公式与加粗。"""
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            cells = [c for c in cells if c and not set(c) <= set("-: ")]
            if cells:
                lines.append("· " + " / ".join(cells))
            continue
        lines.append(ln)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def parse_options(block):
    """从题块里抽出 A/B/C/D 四个选项。"""
    lines = [l.rstrip() for l in block.splitlines()]
    opts = {}
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("**"):
            continue
        if not re.match(r"^[A-D]\.\s", s):
            continue
        for m in re.finditer(r"([A-D])\.\s*(.*?)(?=\s*[　]{2,}\s*[A-D]\.\s|$)", s):
            opts[m.group(1)] = m.group(2).strip()
    return opts


def section_of(block, title):
    m = re.search(r"###\s*%s\s*\n(.*?)(?=\n###\s|\n##\s|\Z)" % title, block, re.S)
    return clean_md(m.group(1)) if m else ""


def classify(kp_text, chapter_text):
    text = (kp_text or "") + " " + (chapter_text or "")
    best, hits = None, 0
    for pat, key in KP_RULES:
        c = len(re.findall(pat, text))
        if c > hits:
            best, hits = key, c
    return best


def parse_paper(key, label):
    text = read_paper(key)
    ov = parse_overview(text)
    url = BLOB + "%s.md" % key
    out = []
    for num, block in split_sections(text):
        kp_text, chapter_text = ov.get(num, ("", ""))
        km = KP_LINE.search(block)
        stem = km.group(1).strip() if km else ""
        opts = parse_options(block)
        am = None
        for pat in ANS_PATTERNS:
            am = pat.search(block)
            if am:
                break
        ans = am.group(1).strip() if am else ""
        ans = ans.replace("**", "").strip()
        expl = section_of(block, "解析")
        mis = section_of(block, "易错提醒")
        kptxt = section_of(block, "考点")
        out.append({
            "paper": key, "paperLabel": label, "num": num, "url": url,
            "stem": stem, "options": opts, "answer": ans,
            "kaoDian": kp_text, "chapter": chapter_text,
            "kpSection": kptxt, "expl": expl, "mis": mis,
            "kind": "选择" if num <= 10 else ("计算" if num <= 20 else "综合"),
        })
    return out


# ---------------------------------------------------------------- 产出

def pyrepr(s):
    return json.dumps(s, ensure_ascii=False)


def build_module(paper_key, label, questions, url):
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""%s 全国高等教育自学考试统一命题考试《高等数学（工本）》(00023) 真题。' % label,
        "",
        "来源：GitHub 仓库 %s（逐题解析版），路径 %s/%s.md" % (REPO, DIR_IN_REPO, paper_key),
        "原始链接：%s" % url,
        "",
        "入库口径：题干、选项、答案、解析、易错提醒均取自该卷面文件；",
        "          采分点由解析正文的「第 N 步」拆分而成；知识点按考点关键词归到同济第七版节次。",
        '"""',
        "from ..common import Q",
        "",
        "URL = %s" % pyrepr(url),
        "PAPER = %s" % pyrepr("自考 00023 高等数学（工本）"),
        "LABEL = %s" % pyrepr(label),
        "",
        "Q = [",
    ]
    for q in questions:
        stem = q["stem"]
        expl = q["expl"]
        mis = q["mis"]
        if q["kind"] == "选择":
            opts = [q["options"].get(L, "") for L in "ABCD"]
            answer = q["answer"] if q["answer"] in ("A", "B", "C", "D") else "A"
            lines.append("    Q('single', %s, %s," % (pyrepr(diff_of(q)), pyrepr(q["kp"])))
            lines.append("      stem=%s," % pyrepr(stem))
            lines.append("      options=%s," % pyrepr(opts))
            lines.append("      answer=[%s]," % pyrepr(answer))
            lines.append("      expl=%s," % pyrepr(compose_choice_expl(q)))
            lines.append("      mis=%s," % pyrepr(mis))
        else:
            lines.append("    Q('calc', %s, %s," % (pyrepr(diff_of(q)), pyrepr(q["kp"])))
            lines.append("      stem=%s," % pyrepr(stem))
            lines.append("      answer_text=%s," % pyrepr(expl))
            lines.append("      points=[%s]," % ", ".join(
                "{'text': %s, 'partial': 2}" % pyrepr(p) for p in make_points(expl)))
            lines.append("      expl=%s," % pyrepr(compose_open_expl(q)))
            lines.append("      mis=%s," % pyrepr(mis))
        lines.append("      src=%s," % pyrepr("%s 自考 00023 高等数学（工本）第 %d 题" % (label, q["num"])))
        lines.append("      kind='exam-original',")
        lines.append("      src_year=%d, src_region='全国', src_paper=PAPER, src_number=%d," % (
            int(q["paper"].split("-")[0]), q["num"]))
        lines.append("      src_url=URL,")
        lines.append("      prov={'level': 'original', 'url': URL, 'verifiedAt': '2026-10-28',")
        lines.append("            'note': '题干、选项、答案与解析取自源卷面文件；采分点由解析的「第 N 步」拆分。'},")
        lines.append("      qid='zk-%s-%02d'," % (q["paper"].replace("-", ""), q["num"]))
        lines.append("      tags=['自考真题'],")
        lines.append("    ),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def diff_of(q):
    if q["kind"] == "选择":
        return "basic" if q["num"] <= 5 else "medium"
    return "medium" if q["num"] <= 17 else "hard"


def compose_choice_expl(q):
    head = "**答案依据**：%s\n**考点出处**：%s（%s）" % (
        (q["kpSection"] or q["kaoDian"] or "").strip(),
        (q["kaoDian"] or "").strip(),
        (q["chapter"] or "").strip())
    return (head + "\n" + (q["expl"] or "")).strip()


def compose_open_expl(q):
    head = "**答案依据**：%s\n**考点出处**：%s（%s）" % (
        (q["kpSection"] or q["kaoDian"] or "").strip(),
        (q["kaoDian"] or "").strip(),
        (q["chapter"] or "").strip())
    return (head + "\n" + (q["expl"] or "")).strip()


def main():
    report = "--report" in sys.argv
    exclude = set()
    _p = os.path.join(HERE, "_latex_bad_ids.json")
    if os.path.exists(_p):
        with open(_p, encoding="utf-8") as f:
            exclude = set(json.load(f))
        if exclude:
            print("[gate] 剔除 KaTeX 复核失败的题目 %d 道" % len(exclude))
    all_q = []
    for key, label in PAPERS:
        qs = parse_paper(key, label)
        for q in qs:
            q["kp"] = classify(q["kaoDian"], q["chapter"])
        all_q.extend(qs)

    kept = [q for q in all_q if q["kp"] and not BAD_KP.search(q["kaoDian"] or "")]
    unmapped = [q for q in all_q if not q["kp"] or BAD_KP.search(q["kaoDian"] or "")]
    kept = [q for q in kept if ("zk-%s-%02d" % (q["paper"].replace("-", ""), q["num"])) not in exclude]
    # 主观题必须有参考答案（解析为空 → 无法作答，直接丢）
    no_ref = [q for q in kept if q["kind"] != "选择" and not (q["expl"] or "").strip()]
    kept = [q for q in kept if not (q["kind"] != "选择" and not (q["expl"] or "").strip())]

    # 自考同一道题会在多期卷面重复出现（命题组沿用题源），按题干指纹去重，
    # 保留最早出现的那一期；重复题的答案与解析一致，保留一份即可。
    from qa_bank.schema import fingerprint
    seen_fp = {}
    dedup = []
    dupes = []
    for q in sorted(kept, key=lambda x: (x["paper"], x["num"])):
        fp = fingerprint({"stem": q["stem"]})
        if fp in seen_fp:
            dupes.append((q["paper"], q["num"], seen_fp[fp]))
            continue
        seen_fp[fp] = "%s-%d" % (q["paper"], q["num"])
        dedup.append(q)
    kept = dedup
    print("解析无参考答��丢弃 %d 道；跨卷重复丢弃 %d 道" % (len(no_ref), len(dupes)))
    noopt = [q for q in kept if q["kind"] == "选择" and len(q["options"]) < 4]
    noans = [q for q in kept if q["kind"] == "选择" and q["answer"] not in ("A", "B", "C", "D")]
    print("解析到题目 %d 道" % len(all_q))
    print("知识点归不上 %d 道：" % len(unmapped))
    seen = set()
    for q in unmapped:
        if q["kaoDian"] in seen:
            continue
        seen.add(q["kaoDian"])
        print("   %s" % q["kaoDian"])
    print("选项缺失 %d 道，答案非法 %d 道" % (len(noopt), len(noans)))
    for q in noopt[:6]:
        print("   缺选项 %s-%d：%s" % (q["paper"], q["num"], q["stem"][:50]))
    ok = [q for q in kept if not (q["kind"] == "选择" and (len(q["options"]) < 4 or q["answer"] not in ("A", "B", "C", "D")))]
    print("可用真题 %d 道" % len(ok))
    by_kp = {}
    for q in ok:
        by_kp.setdefault(q["kp"], 0)
        by_kp[q["kp"]] += 1
    for k in sorted(by_kp):
        print("   %s：%d 道" % (k, by_kp[k]))
    if report:
        return 0

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    index = []
    for key, label in PAPERS:
        qs = [q for q in ok if q["paper"] == key]
        if not qs:
            continue
        name = "zikao_%s" % key.replace("-", "")
        src = build_module(key, label, qs, qs[0]["url"])
        with io.open(os.path.join(OUT_DIR, name + ".py"), "w", encoding="utf-8", newline="\n") as f:
            f.write(src)
        index.append({"paper": key, "label": label, "module": name,
                      "count": len(qs), "url": qs[0]["url"]})
        print("产出 %s.py：%d 题" % (name, len(qs)))
    with io.open(os.path.join(HERE, "zikao_index.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(index, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
