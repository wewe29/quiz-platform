# -*- coding: utf-8 -*-
r"""考研数学真题 → 题库模块（解析 + 过滤 + 归类 + 产出）。

数据源（已下载到本地缓存，可逐条溯源到具体年份卷面文件）：
    GitHub: TsekaLuk/Kaoyan-Math1-Papers
    仓库内容为「考研数学一真题（1987–2025）」的社区转写版（Markdown + LaTeX）。
    每一道题在页面上都能点开对应的 .md 原文件核对。

本脚本做四件事：
  1) 解析：按「一、选择题 / 二、填空题 / 三、解答题」分区，按【N】切题，
     抽出题干、选项、答案。
  2) 过滤：识别转写残损（数学式里混进中文、$ 不配对、花括号不配对、
     选项缺失、答案不在选项内等）。**宁可少收，不可收错**——
     收错的题会让页面给出错误答案，比没有这道题更糟。
  3) 归类：按关键词规则表把题挂到同济第七版的节次（知识点）上；
     归不上的直接丢弃，不瞎归。
  4) 产出：生成 tools/qa_bank/exam/ky1_<年份>.py 模块（Q() 列表）。

用法：
    python tools/research/build_exam_bank.py --report     # 只看统计，不产出
    python tools/research/build_exam_bank.py               # 产出模块
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
PAPER_DIR = os.path.join(HERE, "_cache", "papers")
OUT_DIR = os.path.join(TOOLS, "qa_bank", "exam")

sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = "TsekaLuk/Kaoyan-Math1-Papers"
BLOB = "https://github.com/%s/blob/main/papers/" % REPO

# ---------------------------------------------------------------- 解析

SEC_RE = re.compile(r"^#{1,6}\s*.*?(选择题|填空题|解答题).*$", re.M)
Q_RE = re.compile(r"^[ \t]*(?:^|\s)*【\s*(\d{1,2})\s*】", re.M)
OPT_RE = re.compile(r"[（(]\s*(?:\$[^$]{0,40}\$\s*)?([A-D])\s*[）)]")
ANS_RE = re.compile(r"【\s*(?:答案|参考答案|答案与解析)\s*】\s*([^\n]{0,40})")


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8", "gb18030", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def section_of(text, pos):
    """返回 pos 之前最近的分区名。"""
    kind = "解答"
    for m in SEC_RE.finditer(text):
        if m.start() <= pos:
            kind = m.group(1)
        else:
            break
    return kind


def strip_math_noise(s):
    """把 $...$ 之外的多余空白压掉，并去掉 KaTeX 友好的空格。"""
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def balanced_math(s):
    """检查 $ 与花括号是否配对。"""
    if s.count("$") % 2 != 0:
        return False
    depth = 0
    for ch in s:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


CJK = re.compile(r"[\u4e00-\u9fff]")


def math_segments(s):
    """取所有 $...$ 内的内容（只看非 display 的）。"""
    segs = []
    for m in re.finditer(r"\$(.+?)\$", s, re.S):
        segs.append(m.group(1))
    return segs


def damaged(stem, options, answer, kind):
    """返回 (是否损坏, 原因)。"""
    if not stem or len(stem) < 6:
        return True, "题干过短"
    if not balanced_math(stem):
        return True, "$ 或花括号不配对"
    for seg in math_segments(stem):
        if CJK.search(seg):
            return True, "数学式里混进中文（转写残损）"
    if kind == "选择题":
        if len(options) < 4:
            return True, "选项不足 4 个"
        for letter, txt in options:
            if not txt.strip():
                return True, "选项 %s 为空" % letter
            if not balanced_math(txt):
                return True, "选项 %s 数学式不配对" % letter
            for seg in math_segments(txt):
                if CJK.search(seg):
                    return True, "选项 %s 里混进中文" % letter
        if answer not in ("A", "B", "C", "D"):
            return True, "答案不在选项内：%s" % answer
    if "【" in stem or "】" in stem:
        return True, "题干残留标记"
    return False, ""


def parse_paper(path):
    """把一份卷子解析成题目列表。"""
    text = read_text(path)
    name = os.path.basename(path)
    m = re.search(r"(\d{4})", name)
    year = int(m.group(1)) if m else 0
    # 2024/2025 目录里有重复文件，只取信息最全的一份
    marks = list(Q_RE.finditer(text))
    out = []
    for i, mk in enumerate(marks):
        num = int(mk.group(1))
        start = mk.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        chunk = text[start:end]
        kind = section_of(text, mk.start())
        # 答案
        am = ANS_RE.search(chunk)
        ans_raw = am.group(1) if am else ""
        ans_letters = re.findall(r"[A-D]", ans_raw)
        # 选项：从「答案」之前切
        head = chunk[:am.start()] if am else chunk
        opts = []
        om = list(OPT_RE.finditer(head))
        for j, o in enumerate(om):
            ostart = o.end()
            oend = om[j + 1].start() if j + 1 < len(om) else len(head)
            opts.append((o.group(1), strip_math_noise(head[ostart:oend])))
        stem = strip_math_noise(head[:om[0].start()] if om else head)
        out.append({
            "year": year, "number": num, "kind": kind,
            "stem": stem, "options": opts,
            "answer": "".join(sorted(set(ans_letters))) if ans_letters else "",
            "ansRaw": ans_raw.strip(),
            "file": name,
            "url": BLOB + name,
        })
    return year, out


# ---------------------------------------------------------------- 归类规则

# (正则, 节次 key) —— 命中即取；都命中时取匹配数最多的那条。
RULES = [
    (r"极限|趋于|\\lim", "1.3"),
    (r"数列.*(收敛|极限)|通项", "1.2"),
    (r"无穷小|无穷大|等价无穷小", "1.4"),
    (r"泰勒|麦克劳林|展开为幂级数|展开成幂级数", "1.5"),
    (r"洛必达|未定式", "1.5"),
    (r"间断点|连续性|连续函数|连续区间", "1.8"),
    (r"闭区间.*(最大|最小|介值|零点)", "1.10"),
    (r"导数|可导|求导|微分", "2.4"),
    (r"隐函数.*导|参数方程", "2.3"),
    (r"高阶导数|莱布尼茨|麦克劳林公式", "2.5"),
    (r"洛必达法则|泰勒公式.*求", "2.6"),
    (r"中值定理|拉格朗日|罗尔|柯西|泰勒.*定理", "3.1"),
    (r"单调|极值|最值", "3.3"),
    (r"凹凸|拐点", "3.4"),
    (r"渐近线|渐近", "3.5"),
    (r"不定积分|原函数|积分公式", "4.1"),
    (r"换元积分|分部积分", "4.2"),
    (r"定积分|微积分基本定理", "5.1"),
    (r"反常积分|广义积分", "5.3"),
    (r"定积分.*(几何|应用)|面积|体积|弧长|侧面积|功|压力", "6.1"),
    (r"旋转体", "6.3"),
    (r"形心|重心|物理", "6.4"),
    (r"微分方程", "7.1"),
    (r"可分离变量|齐次方程", "7.2"),
    (r"一阶线性|伯努利", "7.3"),
    (r"二阶常系数|特征方程", "7.7"),
    (r"欧拉方程|不因式分解", "7.9"),
    (r"空间解析几何|向量积|混合积", "8.1"),
    (r"偏导数|全微分", "9.2"),
    (r"复合函数.*求导|链式法则", "9.3"),
    (r"隐函数.*偏导", "9.5"),
    (r"极值|条件极值|拉格朗日乘数", "9.8"),
    (r"方向导数|梯度", "9.6"),
    (r"二重积分", "10.2"),
    (r"三重积分", "10.3"),
    (r"曲线积分", "11.2"),
    (r"格林公式", "11.3"),
    (r"曲面积分", "11.5"),
    (r"高斯公式|散度", "11.6"),
    (r"斯托克斯|旋度", "11.7"),
    (r"常数项级数|级数.*收敛|审敛", "12.2"),
    (r"交错级数|绝对收敛|条件收敛", "12.3"),
    (r"幂级数", "12.4"),
    (r"傅里叶级数", "12.7"),
]


def classify(text):
    """把题干文本归到一个节次；归不上返回 None。"""
    best, best_hits = None, 0
    for pat, key in RULES:
        hits = len(re.findall(pat, text))
        if hits > best_hits:
            best, best_hits = key, hits
    return best if best_hits > 0 else None


# ---------------------------------------------------------------- 主流程

def main():
    report_only = "--report" in sys.argv
    files = []
    for fn in sorted(os.listdir(PAPER_DIR)):
        if fn.endswith(".md") and fn != "README.md":
            files.append(os.path.join(PAPER_DIR, fn))
    # 同年多文件时保留题目最多的一份
    by_year = {}
    for p in files:
        year, qs = parse_paper(p)
        if year == 0:
            continue
        if year not in by_year or len(qs) > len(by_year[year][1]):
            by_year[year] = (p, qs)
    print("卷子年份：%s" % sorted(by_year))

    total = kept = 0
    drop = {}
    unmapped = 0
    per_year = {}
    for year in sorted(by_year):
        path, qs = by_year[year]
        ykept = 0
        for q in qs:
            total += 1
            bad, why = damaged(q["stem"], q["options"], q["answer"], q["kind"])
            if bad:
                drop[why.split("：")[0]] = drop.get(why.split("：")[0], 0) + 1
                continue
            kp = classify(q["stem"] + " " + " ".join(t for _, t in q["options"]))
            if kp is None:
                unmapped += 1
                continue
            q["kp"] = kp
            kept += 1
            ykept += 1
        per_year[year] = (path, [q for q in qs if q.get("kp") and not damaged(
            q["stem"], q["options"], q["answer"], q["kind"])[0]])

    print("解析题目 %d 道" % total)
    print("损坏丢弃 %d 道：" % sum(drop.values()))
    for k, v in sorted(drop.items(), key=lambda x: -x[1]):
        print("   %-28s %d" % (k, v))
    print("知识点归不上丢弃 %d 道" % unmapped)
    print("可用真题 %d 道" % kept)
    for year in sorted(per_year):
        path, qs = per_year[year]
        print("   %d：%s（%d 道）  %s" % (year, os.path.basename(path), len(qs), qs[0]["url"] if qs else ""))

    if report_only:
        return 0

    # ---- 产出模块 ----
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    index = []
    for year in sorted(per_year):
        path, qs = per_year[year]
        if not qs:
            continue
        mod = write_module(year, os.path.basename(path), qs)
        index.append({"year": year, "module": mod, "count": len(qs),
                      "url": qs[0]["url"]})
    with io.open(os.path.join(HERE, "exam_index.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(index, ensure_ascii=False, indent=1))
    print("产出模块 %d 个 → %s" % (len(index), OUT_DIR))
    return 0


def write_module(year, src_name, qs):
    name = "ky1_%d" % year
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""%d 年全国硕士研究生入学统一考试《数学（一）》真题（高数部分）。' % year,
        "",
        "来源：GitHub 仓库 %s 的社区转写版 papers/%s" % (REPO, src_name),
        "原始链接：%s" % (qs[0]["url"] if qs else ""),
        "",
        "入库规则：",
        "  1) 只收转写完好（数学式无残损、选项齐全、答案在选项内）的题；",
        "  2) 只收高等数学部分（线代 / 概率已剔除）；",
        "  3) 知识点按关键词规则表挂到同济第七版节次上。",
        '"""',
        "from ..common import Q",
        "",
        "SRC = %r" % (qs[0]["url"] if qs else ""),
        "",
        "Q = [",
    ]
    for q in qs:
        lines.append("    _q(%r, %r)," % (q, q["kp"]))
    lines.append("]")
    lines.append("")
    src = "\n".join(lines)
    dst = os.path.join(OUT_DIR, name + ".py")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    return name


if __name__ == "__main__":
    raise SystemExit(main())
