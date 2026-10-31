# -*- coding: utf-8 -*-
r"""考研数学（二 / 三）真题 → 题库模块。

数据源（已下载到本地缓存，可逐条溯源到具体年份卷面文件）：
    GitHub: TsekaLuk/Kaoyan-Math2-Papers
    解析文件：solutions/math2_1987-2019/math2_1987-2019.md
              solutions/<年份>/math2_<年份>/math2_<年份>.md

**与数学一仓库的关键差别**：本仓库的解析文件里**题干与解析在同一文件**，
每道题形如：

    1. 设 $y = \ln (1 + ax)$ ，其中 $a$ 为非零常数，则 $y' =$ ______.
    解. 应填 $\frac{a}{1 + ax}$ .

所以不需要再做「题干文件 ↔ 解析文件」的对齐，只要按题号切块即可。

**可用年份**：1987–2019。2020–2024 三个文件**只有题目、没有答案解析**
（仓库里对应的是原卷 PDF 的版面解析 JSON），没有答案就不能入库——
宁可少收，绝不编答案。

**卷别**：1987–1996 的卷面标题写的是「试卷三」，1997 起是「试卷二」，
一律按源卷面自带的标题记录，不臆造。

用法：
    python tools/research/build_math2_bank.py --report
    python tools/research/build_math2_bank.py
"""
import collections
import io
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
OUT_DIR = os.path.join(TOOLS, "qa_bank", "exam")
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank.schema import fingerprint                                   # noqa: E402
from typst_extract import compose_expl as compose_expl_text              # noqa: E402
from points import make_points                                           # noqa: E402
from kp_rules import classify_full                                       # noqa: E402
from build_kaoyan_bank import (                                          # noqa: E402
    KP_RULES, classify, excluded, damaged, norm_math, CJK, TYPST_LEFT,
)


REPO = "TsekaLuk/Kaoyan-Math2-Papers"
BLOB = "https://github.com/%s/blob/main/solutions/" % REPO
ZIP = os.path.join(HERE, "_cache", "TsekaLuk_Kaoyan-Math2-Papers.zip")
BIG = "math2_1987-2019/math2_1987-2019.md"
MIN_YEAR = 1987
MAX_YEAR = 2019

# ---------------------------------------------------------------- 版式正则
CN_DIGIT = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
YEAR_RE = re.compile(r"^#\s*([〇零一二三四五六七八九]{4})年考研数学试卷([一二三])解答\s*$")
SECTION_RE = re.compile(r"^#\s*([一二三四五六七八九十]+)、\s*(.*)$")
QNUM_DOT = re.compile(r"^(\d{1,2})\s*[.．]\s*(.*)$")
QNUM_PAREN = re.compile(r"^[（(]\s*(\d{1,2})\s*[)）]\s*(.*)$")
OPT_RE = re.compile(r"[（(]\s*([A-D])\s*[)）]\s*")
SOL_RE = re.compile(r"^\s*(?:解|证明|证|解析|答案)\s*[.．、:：]\s*(.*)$")
CHOICE_ANS_RE = re.compile(r"(?:应选|故选|选择|答案为|应取)\s*[（(]?\s*([A-D])\s*[)）]?")
FILL_ANS_RE = re.compile(r"应填\s*(.+?)\s*[.。;；]?\s*$")
BLANK_MARK_RE = re.compile(r"_{2,}|\\underline\s*\{")


def cn_year(s):
    s = s.replace("〇", "零")
    if len(s) != 4:
        return None
    digits = []
    for ch in s:
        if ch not in CN_DIGIT:
            return None
        digits.append(CN_DIGIT[ch])
    return digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]


def section_type(head):
    """由分节标题判断题型。"""
    if "填空" in head:
        return "blank"
    if "选择" in head:
        return "choice"
    if "计算" in head or "证明" in head or "解答" in head:
        return "calc"
    if "满分" in head:
        return "calc"          # 单独一题的分节，如「三、(本题满分7分)」
    return None


def split_years(text):
    """把 1987–2019 合并文件按年份标题切开。"""
    out = []
    cur = None
    for raw in text.split("\n"):
        m = YEAR_RE.match(raw.rstrip())
        if m:
            if cur:
                out.append(cur)
            y = cn_year(m.group(1))
            cur = {"year": y, "paper": "数学%s" % m.group(2), "lines": []}
            continue
        if cur is not None:
            cur["lines"].append(raw)
    if cur:
        out.append(cur)
    return out


def split_sections(lines):
    """把一年的正文按分节标题切开。"""
    out = []
    head = None
    body = []
    for raw in lines:
        m = SECTION_RE.match(raw.rstrip())
        if m:
            if head is not None:
                out.append((head, body))
            head = "%s、%s" % (m.group(1), m.group(2))
            body = []
            continue
        if head is None:
            continue
        body.append(raw)
    if head is not None:
        out.append((head, body))
    return out


def parse_items(body, sec_type):
    """把一节正文切成若干题：{num, stem_lines, opt_lines, sol_lines}。"""
    items = []
    cur = None
    state = "stem"
    for raw in body:
        line = raw.rstrip()
        if not line.strip():
            continue
        m = QNUM_DOT.match(line) or QNUM_PAREN.match(line)
        if m:
            n = int(m.group(1))
            # 题号递增才算新题，避免把解答里的「1.」当成新题
            if cur is None or state == "stem" or n > (cur.get("num") or 0):
                cur = {"num": n, "stem_lines": [m.group(2)], "opt_lines": [], "sol_lines": []}
                items.append(cur)
                state = "stem"
                continue
        if cur is None:
            continue
        ms = SOL_RE.match(line)
        if ms and state == "stem":
            state = "sol"
            cur["sol_lines"].append(ms.group(1))
            continue
        if state == "stem":
            if sec_type == "choice" and OPT_RE.search(line):
                cur["opt_lines"].append(line)
            else:
                cur["stem_lines"].append(line)
        else:
            cur["sol_lines"].append(line)

    if not items:
        # 整节就是一道题（早期卷的「三、(本题满分7分)」式分节）
        stem_lines, sol_lines, state = [], [], "stem"
        for raw in body:
            line = raw.rstrip()
            if not line.strip():
                continue
            ms = SOL_RE.match(line)
            if ms and state == "stem":
                state = "sol"
                sol_lines.append(ms.group(1))
                continue
            (sol_lines if state == "sol" else stem_lines).append(line)
        if stem_lines or sol_lines:
            items.append({"num": None, "stem_lines": stem_lines,
                          "opt_lines": [], "sol_lines": sol_lines})
    return items


def extract_options(lines):
    """从正文里按 (A)(B)(C)(D) 切出四个选项；返回 (题干剩余, {字母: 选项文本})。"""
    text = "\n".join(lines)
    ms = list(OPT_RE.finditer(text))
    if not ms:
        return text, {}
    stem = text[:ms[0].start()].strip()
    opts = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        val = text[m.end():end].strip()
        val = val.strip().strip(".").strip("。").strip()
        val = re.sub(r"\s+", " ", val)
        if letter_ok(m.group(1)) and m.group(1) not in opts:
            opts[m.group(1)] = val
    return stem, opts


def letter_ok(l):
    return l in ("A", "B", "C", "D")


def choice_answer(sol):
    """选择题答案：解析开头的「应选 (A)」或结尾的「故选 (B)」。"""
    head = sol[:120]
    m = CHOICE_ANS_RE.search(head)
    if m:
        return m.group(1)
    tail = sol[-60:]
    m = CHOICE_ANS_RE.search(tail)
    if m:
        return m.group(1)
    return None


def fill_answer(sol):
    """填空题答案：解析里的「应填 X」。"""
    for line in sol.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = FILL_ANS_RE.search(line)
        if m:
            v = m.group(1).strip()
            v = v.strip().strip(".").strip("。").strip()
            return v
        if line:
            break
    return None


def diff_of(qtype, year):
    if qtype == "calc":
        return "hard"
    if qtype == "blank":
        return "medium"
    return "basic" if year <= 2010 else "medium"


def build_module(year, paper, qs):
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""%d 年全国硕士研究生招生考试%s真题（高等数学范围）。' % (year, paper),
        "",
        "来源：GitHub 仓库 %s" % REPO,
        "答案解析文件：solutions/%s" % BIG,
        "",
        "入库口径：题干 / 选项 / 答案 / 解析取自源卷面文件；",
        "          只收属于同济《高等数学》范围的题，线代与概率统计整题丢弃。",
        '"""',
        "from ..common import Q",
        "",
        "Q = [",
    ]
    for q in qs:
        src = "%d 年考研%s第 %s 题" % (year, paper, q["num"] if q["num"] else "—")
        common = [
            "      src=%s," % json.dumps(src, ensure_ascii=False),
            "      kind='exam-original',",
            "      src_year=%d," % year,
            "      src_region='全国',",
            "      src_paper=%s," % json.dumps("%d 年考研%s" % (year, paper), ensure_ascii=False),
            "      src_number=%s," % json.dumps(str(q["num"]), ensure_ascii=False),
            "      src_url=%s," % json.dumps(q["url"], ensure_ascii=False),
            "      prov={'level': 'original', 'url': %s," % json.dumps(q["url"], ensure_ascii=False),
            "            'verifiedAt': '2026-10-28',",
            "            'note': '题干、选项、答案与解析取自源卷面 Markdown 文件；"
            "答案解析文件：%s'}," % (BLOB + BIG),
            "      qid=%s," % json.dumps(q["qid"], ensure_ascii=False),
            "      tags=['考研真题', '考研%s']," % paper,
        ]
        if q["type"] == "choice":
            lines.append("    Q('single', %s, %s," % (
                json.dumps(diff_of("choice", year)), json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      options=%s," % json.dumps(q["options"], ensure_ascii=False))
            lines.append("      answer=%s," % json.dumps(list(q["answer"]), ensure_ascii=False))
            lines.append("      expl=%s," % json.dumps(compose_expl_text(
                q["answer"], q["solution"]), ensure_ascii=False))
        elif q["type"] == "blank":
            lines.append("    Q('blank', %s, %s," % (
                json.dumps(diff_of("blank", year)), json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      answer=[%s]," % json.dumps(q["answer"]))
            lines.append("      expl=%s," % json.dumps(compose_expl_text(
                q["answer"], q["solution"]), ensure_ascii=False))
        else:
            lines.append("    Q('calc', %s, %s," % (
                json.dumps(diff_of("calc", year)), json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      answer_text=%s," % json.dumps(q["solution"], ensure_ascii=False))
            lines.append("      points=[%s]," % ", ".join(
                "{'text': %s, 'partial': 2}" % json.dumps(p, ensure_ascii=False)
                for p in make_points(q["solution"])))
            lines.append("      expl=%s," % json.dumps(compose_expl_text(
                "", q["solution"]), ensure_ascii=False))
        lines.extend(common)
        lines.append("    ),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def bad_ids():
    """KaTeX 复核失败的题号黑名单（由 check_latex.py 写出）。"""
    p = os.path.join(HERE, "_latex_bad_ids.json")
    if not os.path.exists(p):
        return set()
    with io.open(p, encoding="utf-8") as f:
        return set(json.load(f))


def main():
    report = "--report" in sys.argv
    exclude = bad_ids()
    dump = None
    for a in sys.argv:
        if a.startswith("--dump="):
            dump = a.split("=", 1)[1]
    drops = []
    z = zipfile.ZipFile(ZIP)
    name = None
    for n in z.namelist():
        if n.endswith(BIG):
            name = n
            break
    if not name:
        print("找不到 %s" % BIG)
        return 1
    text = z.read(name).decode("utf-8", "replace")

    stats = collections.Counter()
    dropped = collections.Counter()
    by_year = collections.defaultdict(list)
    seen_fp = set()
    kind_stat = collections.Counter()
    url = BLOB + BIG

    years = split_years(text)
    print("[源] 年份段 %d 个：%s" % (
        len(years), "%s–%s" % (years[0]["year"], years[-1]["year"])))

    for yinfo in years:
        year = yinfo["year"]
        paper = yinfo["paper"]
        if year < MIN_YEAR or year > MAX_YEAR:
            continue
        for head, body in split_sections(yinfo["lines"]):
            sec_type = section_type(head)
            if sec_type is None:
                dropped["分节标题认不出题型：%s" % head[:20]] += 1
                continue
            for it in parse_items(body, sec_type):
                stats["total"] += 1
                stem_raw = "\n".join(it["stem_lines"]).strip()
                sol = "\n".join(it["sol_lines"]).strip()
                stem = re.sub(r"[ \t]+", " ", stem_raw).strip()
                stem = re.sub(r"\n{2,}", "\n", stem)

                if not stem:
                    dropped["题干为空"] += 1
                    continue
                if "同试卷" in stem or "同第" in stem and "题" in stem:
                    dropped["源卷面写的是「同试卷X第Y题」（无题干）"] += 1
                    continue
                if re.search(r"如图|下图|图中|见图|图\s*\d|!\[[^\]]*\]\([^)]*\)", stem):
                    dropped["题干含图（无法内联）"] += 1
                    continue

                qtype = sec_type
                options = []
                answer = ""
                if qtype == "choice":
                    stem2, opts = extract_options(it["stem_lines"] + it["opt_lines"])
                    stem2 = re.sub(r"[ \t]+", " ", stem2).strip()
                    if not opts:
                        dropped["选择题没有识别出选项"] += 1
                        continue
                    if len(opts) != 4:
                        dropped["选项数不对(%d)" % len(opts)] += 1
                        continue
                    stem = stem2
                    options = [opts["A"], opts["B"], opts["C"], opts["D"]]
                    if not sol:
                        dropped["选择题缺解析"] += 1
                        continue
                    a = choice_answer(sol)
                    if not a:
                        dropped["选择题答案识别不出"] += 1
                        continue
                    answer = a
                elif qtype == "blank":
                    n_blank = len(BLANK_MARK_RE.findall(stem))
                    if n_blank >= 2:
                        dropped["多空填空题（判题器仅支持单空）"] += 1
                        continue
                    if not sol:
                        dropped["填空题缺解析"] += 1
                        continue
                    a = fill_answer(sol)
                    if not a:
                        dropped["填空题答案识别不出"] += 1
                        continue
                    if len(a) > 80:
                        dropped["填空题答案过长（疑似多空）"] += 1
                        continue
                    if "，" in a or "," in a:
                        dropped["填空题答案含多段（疑似多空）"] += 1
                        continue
                    answer = a
                else:
                    if not sol:
                        dropped["解答题缺解析"] += 1
                        continue
                    if len(stem) < 8:
                        dropped["题干过短"] += 1
                        continue

                scope = stem + " " + " ".join(options)
                hit = excluded(scope)
                if hit:
                    dropped["不属于高等数学范围：%s" % hit] += 1
                    continue
                kp = classify_full(KP_RULES, scope, sol)
                if kp is None:
                    dropped["无法归入高等数学知识点"] += 1
                    if dump:
                        drops.append({"year": year, "num": it["num"], "type": qtype,
                                      "stem": stem, "reason": "无法归类"})
                    continue
                bad, why2 = damaged(stem, options, answer, sol, qtype)
                if bad:
                    dropped[why2] += 1
                    continue
                fp = fingerprint({"stem": stem})
                if fp in seen_fp:
                    dropped["跨卷重复"] += 1
                    continue
                seen_fp.add(fp)
                num = it["num"]
                qid = "ky2-%d-%s-%s" % (year, num if num else "x", fp[:6])
                if qid in exclude:
                    dropped["KaTeX 复核未通过"] += 1
                    continue
                by_year[year].append({
                    "qid": qid, "stem": stem, "options": options, "answer": answer,
                    "solution": sol, "kp": kp, "year": year, "num": num,
                    "type": qtype, "url": url, "fp": fp,
                })
                stats["kept"] += 1
                kind_stat[qtype] += 1

    print("扫描题目 %d 道，入库 %d 道" % (stats["total"], stats["kept"]))
    print("题型分布：", dict(kind_stat))
    print("丢弃明细：")
    for k, v in dropped.most_common(25):
        print("   %-46s %d" % (k, v))
    print("按年份：", {y: len(v) for y, v in sorted(by_year.items())})
    if dump:
        with io.open(dump, "w", encoding="utf-8", newline="\n") as f:
            for d in drops:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        print("丢弃样本已写出：%s（%d 条）" % (dump, len(drops)))
    if report:
        return 0

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    index = []
    for y in sorted(by_year):
        qs = by_year[y]
        paper = "数学三" if y <= 1996 else "数学二"
        name = "ky2_%d" % y
        with io.open(os.path.join(OUT_DIR, name + ".py"), "w", encoding="utf-8", newline="\n") as f:
            f.write(build_module(y, paper, qs))
        index.append({"year": y, "module": name, "count": len(qs)})
        print("产出 %s.py：%d 道" % (name, len(qs)))
    with io.open(os.path.join(HERE, "math2_index.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(index, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
