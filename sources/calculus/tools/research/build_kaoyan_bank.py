# -*- coding: utf-8 -*-
r"""考研数学（一）真题 → 题库模块。

数据源（已下载到本地缓存，可逐题溯源到具体卷面文件）：
    GitHub: TsekaLuk/Kaoyan-Math1-Papers
    题干：papers/<年份>年考研数学(一)真题.md
    答案解析：solutions/<年份>年解析/<年份>年解析.md

**范围口径**：本题库是《高等数学》题库，只收高等数学范围内的题。
考研数学（一）里的**线性代数**（矩阵/行列式/特征值/二次型/向量组…）与
**概率统计**（概率/分布/期望/方差…）不属于同济《高等数学》，一律丢弃。

用法：
    python tools/research/build_kaoyan_bank.py --report
    python tools/research/build_kaoyan_bank.py
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

from qa_bank.schema import fingerprint                    # noqa: E402
from typst_extract import choice_from_tail, SOURCE_CONFLICT, compose_expl as compose_expl_text  # noqa: E402
from points import make_points                           # noqa: E402
from kp_rules import classify_full                       # noqa: E402

REPO = "TsekaLuk/Kaoyan-Math1-Papers"
BLOB = "https://github.com/%s/blob/main/" % REPO
ZIP = os.path.join(HERE, "_cache", "TsekaLuk_Kaoyan-Math1-Papers.zip")
# 只收 2004 年及以后：更早的卷面文件体例混乱（每字一行、解答题把多小问捆在一起），
# 无法保证「题干 ↔ 答案解析」一一对应，宁可不收。
MIN_YEAR = 2004

# 题号 + 段落标记
NUM_RE = re.compile(r"^\s*[\(（]\s*(\d{1,2})\s*[\)）]\s*(.*)$")
OPT_RE = re.compile(r"^\s*[\(（]\s*([A-D])\s*[\)）]\s*(.*)$")
ANS_MARK = re.compile(r"^\s*[\(（]\s*(\d{1,2})\s*[\)）]\s*【(答案|解|证明)】\s*(.*)$")
SECTION_RE = re.compile(r"^\s*#{0,4}\s*[一二三四五六七八九十]+\s*[、.．]\s*"
                         r"(选择题|填空题|解答题|计算题|证明题)")
IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
FULL_ANS_RE = re.compile(r"^[\(（]\s*(\d{1,2})\s*[\)）]")

# 线性代数 / 概率统计 —— 不属于《高等数学》，整题丢弃
OUT_OF_COURSE = [
    ("线性代数", r"矩阵|行列式|向量组|特征值|特征向量|二次型|正交矩阵|伴随矩阵|"
                 r"过渡矩阵|相似对角|合同变换|正定|标准形|秩为|r\(A\)|r\(A|B|"
                 r"基$\{|一组基|线性无关|线性相关|空间$\\mathbb\{R\}|正交变换|"
                 r"方程组的解|线性方程组|增广矩阵|系数矩阵|初等变换|相似矩阵|"
                 r"单位矩阵|实对称矩阵|对称矩阵|秩"),
    ("概率统计", r"概率|分布律|分布函数|数学期望|方差|随机变量|密度函数|独立事件|"
                 r"条件概率|正态分布|二项分布|样本|总体|置信|估计|检验|统计量|"
                 r"特征函数|数字特征|泊松|超几何|伯努利|似然|大数定律|中心极限定理"),
]

# 高等数学知识点规则（与高考建库共用一套口径）
KP_RULES = [
    (r"二元.*极值|条件极值|拉格朗日乘数|驻点|多元.*极值", "9.8"),
    (r"方向导数|梯度", "9.7"),
    (r"全微分", "9.3"),
    (r"隐函数.*偏导|隐函数.*求导", "9.5"),
    (r"二阶偏导|混合偏导", "9.4"),
    (r"偏导数|求偏导|多元函数|二元函数|重极限|切平面|法平面|方向导数|梯度", "9.2"),
    (r"数量积|向量积|混合积|空间角|夹角|内积|外积", "8.2"),
    (r"向量|\\overrightarrow|\\mathbf|单位向量|线性无关|线性相关|向量组|基底|"
     r"正交|模长|数乘|方向向量|法向量|空间直角坐标系|共线|形心", "8.1"),
    (r"平面方程|点法式|一般式|两平面|点到平面|平面.*法向量", "8.3"),
    (r"直线方程|对称式|两直线|直线与平面|异面直线|直线与直线", "8.4"),
    (r"曲面方程|球面|柱面|旋转曲面|锥面|抛物面", "8.5"),
    (r"空间曲线|螺旋线|空间.*切线|切线.*空间", "8.6"),
    (r"格林公式", "11.3"),
    (r"高斯公式|散度", "11.6"),
    (r"斯托克斯|旋度", "11.7"),
    (r"曲面积分", "11.5"),
    (r"对弧长的曲线积分|第一型曲线积分", "11.1"),
    (r"对坐标的曲线积分|第二型曲线积分", "11.2"),
    (r"三重积分", "10.3"),
    (r"二重积分", "10.2"),
    (r"可分离变量", "7.2"),
    (r"齐次方程", "7.3"),
    (r"一阶线性|伯努利", "7.4"),
    (r"二阶常系数齐次", "7.6"),
    (r"二阶.*非齐次|特解|通解|通解.*微分方程", "7.7"),
    (r"微分方程", "7.1"),
    (r"傅里叶", "12.7"),
    (r"展开为幂级数|展开成幂级数|泰勒级数|和函数|展开为幂级", "12.5"),
    (r"幂级数|收敛半径", "12.4"),
    (r"交错级数|绝对收敛|条件收敛", "12.3"),
    (r"审敛|敛散性|收敛.*判别|比较判别|根值|比值", "12.2"),
    (r"数项级数|几何级数|级数", "12.1"),
    (r"弧长", "6.4"),
    (r"形心|重心|压力|引力|作功|水压", "6.5"),
    (r"旋转体|旋转.*体积|侧面积|表面积", "6.3"),
    (r"面积", "6.2"),
    (r"反常积分|广义积分|瑕积分", "5.4"),
    (r"微积分基本定理|牛顿.*莱布尼茨", "5.2"),
    (r"积分中值", "5.3"),
    (r"定积分", "5.1"),
    (r"不定积分|原函数", "4.1"),
    (r"洛必达", "3.2"),
    (r"泰勒|麦克劳林|余项", "3.3"),
    (r"拉格朗日|罗尔|柯西|中值定理", "3.1"),
    (r"凹凸|拐点|渐近线|图形描绘", "3.4"),
    (r"单调", "3.4"),
    (r"极值|最值|最大值|最小值", "3.5"),
    (r"隐函数|参数方程", "2.4"),
    (r"高阶导数|二阶导", "2.3"),
    (r"求导|可导|导数|切线|切点", "2.2"),
    (r"数列.*极限|极限.*数列|数列.*收敛|数列.*单调|数列极限", "1.2"),
    (r"无穷小|无穷大|极限|\\lim|趋于|夹逼", "1.3"),
    (r"连续|间断点", "1.8"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")
MATH_SEG = re.compile(r"\$\$(.*?)\$\$|\$([^$]*)\$", re.S)
TYPST_LEFT = re.compile(r"(#[A-Za-z])|(`)|"
                         r"(\\(bold|mathbf|mathbb|mathrm|widehat|overline|underline|"
                         r"vec|hat|bar|operatorname|textbf|mathit|cal|bb)\()")
TYPST_MATH = re.compile(
    r"(?<![A-Za-z\\])(sqrt|frac|lim|sum|int|integrate|abs|overline|underline|"
    r"hat|bar|vec|arrow|dots|infty|binom|binomial|matrix|mat|det|root)\s*\("
    r"|(?<![A-Za-z\\])(oo|NN|RR|ZZ|QQ|CC)\b")


def math_segments(txt):
    for m in MATH_SEG.finditer(txt or ""):
        yield m.group(1) if m.group(1) is not None else m.group(2)


def norm_text(t):
    t = re.sub(r"[ \t]+\n", "\n", t or "")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def classify(text, sol=""):
    best, best_score = None, 0
    for pat, key in KP_RULES:
        score = len(re.findall(pat, text)) * 3 + len(re.findall(pat, sol[:400]))
        if score > best_score:
            best, best_score = key, score
    return best if best_score > 0 else None


def excluded(text):
    for label, pat in OUT_OF_COURSE:
        if re.search(pat, text):
            return label
    return None


# ------------------------------------------------------------ 题干解析
HEADER_RE = re.compile(r"^\s*#{1,6}\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.*)$")
TYPE_WORD = {"选择题": "choice", "填空题": "blank", "解答题": "calc",
             "计算题": "calc", "证明题": "calc"}


def parse_papers(text):
    """解析题干文件，返回按分节归类的题目列表（保持文档顺序）。

    考研卷面的编号约定在不同年份三种都有（全卷连续 / 每节重排 / 解答题不编号），
    因此这里**不依赖题号**，只保留顺序与分节类型。
    """
    by_type = {"choice": [], "blank": [], "calc": []}
    cur_type = None
    unnumbered = False          # 当前分节是「# 三、(本题满分5分)」这种无编号分节
    cur = None
    pending = []                # 无编号分节里累积的行

    def flush_unnumbered():
        if pending and cur_type:
            body = norm_text("\n".join(pending))
            body = re.sub(r"^\(本题满分\s*\d+\s*分\)|^(本题满分\s*\d+\s*分)", "",
                          body).strip()
            if body:
                by_type[cur_type].append({"num": None, "type": cur_type,
                                           "stem": body, "options": []})
        del pending[:]

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        mh = HEADER_RE.match(line)
        if mh:
            flush_unnumbered()
            head = mh.group(2).strip()
            cur_type = None
            unnumbered = False
            for word, tp in TYPE_WORD.items():
                if head.startswith(word) or head.startswith("（" + word):
                    cur_type = tp
                    break
            if cur_type is None:
                # 「# 三、(本题满分5分)」——该分节里是一道无编号解答题
                cur_type = "calc"
                unnumbered = True
            continue
        if unnumbered:
            pending.append(line.strip())
            continue
        mopt = OPT_RE.match(line)
        if mopt and cur is not None:
            cur["options"].append([mopt.group(1), mopt.group(2).strip()])
            continue
        mnum = NUM_RE.match(line)
        if mnum:
            num = int(mnum.group(1))
            rest = mnum.group(2).strip()
            if num <= 0:
                continue
            cur = {"num": num, "type": cur_type, "stem": [], "options": []}
            by_type[cur_type or "calc"].append(cur)
            if rest:
                cur["stem"].append(rest)
            continue
        if cur is not None:
            cur["stem"].append(line.strip())
    flush_unnumbered()

    for tp in by_type:
        for q in by_type[tp]:
            q["stem"] = norm_text("\n".join(q["stem"]))
            q["stem"] = re.sub(r"^\(本题满分\s*\d+\s*分\)|^（本题满分\s*\d+\s*分）",
                               "", q["stem"]).strip()
            q["options"] = [o[1] for o in q["options"]]
            if q["options"]:
                q["type"] = "choice"
            elif tp == "blank" or re.search(r"\(\s*\\+quad\s*\)|_{2,}|（\s*）", q["stem"]):
                q["type"] = "blank"
    return by_type


# ------------------------------------------------------------ 答案解析解析
# 解析块起始有两种写法：
#   (11)【答案】 …      /   (11)【解】 …      /   (11)【证明】 …
#   # 五、【解】 方法一  （中文数字分节头同时是解答题块的开头）
#
# 【证明】必须一起认：源卷面的证明题用「（18）【证明】」起头，早先只认
# 【答案】/【解】 会导致这一行不被当作新题块，于是**证明题的正文被并进
# 上一道题**（2017 卷第 19 题的解析里混进了第 20 题的线性代数解答）。
CN_BLOCK = re.compile(r"^\s*#{0,6}\s*([一二三四五六七八九十]+)\s*[、.．]\s*【(答案|解|证明)】\s*(.*)$")

# 题块标记（用于检测「解析里混进了别的题目的正文」）
BLOCK_MARK_RE = re.compile(r"(?m)^\s*[\(（]\s*\d{1,2}\s*[\)）]\s*【(答案|解|证明)】")


def parse_solutions(text):
    """解析答案解析文件，返回按题型归类的块列表（保持文档顺序）。

    题型按**答案形态**判定，不靠分节标题：
      带【答案】且答案是单个字母 → 选择题
      带【答案】且答案是公式/短文本 → 填空题
      只有【解】没有【答案】 → 解答题
    """
    by_type = {"choice": [], "blank": [], "calc": []}
    section_type = None
    cur = None
    for raw in text.split("\n"):
        line = raw.rstrip()
        mh = HEADER_RE.match(line)
        if mh and not CN_BLOCK.match(line):
            head = mh.group(2).strip()
            for word, tp in TYPE_WORD.items():
                if head.startswith(word):
                    section_type = tp
                    break
            continue
        m = ANS_MARK.match(line)
        cn = CN_BLOCK.match(line)
        if m or cn:
            if m:
                num, mark, rest = int(m.group(1)), m.group(2), m.group(3)
            else:
                num, mark, rest = cn.group(1), cn.group(2), cn.group(3)
            cur = {"num": num, "mark": mark, "answer": rest.strip(),
                   "sol": [], "type": None, "section_type": section_type}
            by_type["choice"].append(cur)      # 先占位，下面再归类
            continue
        if cur is not None:
            cur["sol"].append(line)

    # 归类 + 清理
    out = {"choice": [], "blank": [], "calc": []}
    for tp in by_type["choice"]:
        ans = tp["answer"].strip()
        ans = re.split(r"[。\.]\s", ans)[0].strip().strip(" .。")
        ma = re.fullmatch(r"[（(]\s*([A-D])\s*[）)]", ans)
        if ma:
            ans = ma.group(1)
        sol = norm_text("\n".join(tp["sol"]))
        if tp["mark"] in ("解", "证明"):
            sol = norm_text(ans + "\n" + sol) if ans else sol
            ans = ""
        if tp["mark"] == "答案":
            if re.fullmatch(r"[A-D]", ans):
                kind = "choice"
            else:
                kind = "blank"
        else:
            # 只有【解】——按分节标题判；分节没写类型则算解答题
            kind = tp.get("section_type") or "calc"
            if kind in ("choice", "blank") and not ans:
                kind = "calc"
        tp["answer"] = ans
        tp["solution"] = sol
        tp["type"] = kind
        out[kind].append(tp)
    return out


# ---------------------------------------------------- 对齐一致性校验
def tail_choice(solution):
    """解析末尾的「故选 (C)」式答案（与高考建库共用同一实现）。"""
    return choice_from_tail(solution)


def norm_math(s):
    """把公式串归一化，用于「答案是否出现在解析里」的粗比对。"""
    s = re.sub(r"[\s\\{}()$]", "", s or "")
    return s


STOP_BIGRAMS = set(
    "证明 要求 设 已知 其中 如果 那么 以及 或者 并且 不是 没有 可以 应该 需要 "
    "使得 存在 唯一 任意 一定 必须 叫做 称为 记为 设为 对于 关于 由于 因此 "
    "所以 从而 然后 接下来 首先 其次 最后 上面 下面 前面 后面 这个 那个 这些 "
    "那些 一个 两个 三个 一些 一种 一次 函数 方程 方程组 变量 常数 系数 条件 "
    "问题 情况 结果 形式 方式 方法 意思 内容 部分 地方 时候 情况 空间 平面".split()
)


def stem_tokens(stem):
    """从题干里取可用于对齐校验的词元：公式串 + 中文二元词。"""
    toks = set()
    for m in re.finditer(r"\$([^$]{4,200})\$", stem or ""):
        t = norm_math(m.group(1))
        if len(t) >= 6:
            toks.add(t)
    cn = "".join(re.findall(r"[一-鿿]+", stem or ""))
    for i in range(len(cn) - 1):
        bg = cn[i:i + 2]
        if bg not in STOP_BIGRAMS:
            toks.add(bg)
    return toks


def verify_pair(qtype, q, a):
    """校验题干与答案解析是否真的对应；不一致则返回原因。"""
    if qtype == "choice":
        tail = tail_choice(a["solution"])
        if tail and tail != a["answer"]:
            return "答案与解析末尾不一致(%s vs %s)" % (a["answer"], tail)
        return ""
    if qtype == "blank":
        key = norm_math(a["answer"])
        if len(key) >= 2 and key not in norm_math(a["solution"]):
            return "填空答案未出现在解析中"
        return ""
    toks = stem_tokens(q["stem"])
    if not toks:
        return ""
    sol = norm_math(a["solution"])
    math_toks = [t for t in toks if len(t) >= 6 and re.search(r"[\\^_{}=]", t)]
    cn_toks = [t for t in toks if t not in math_toks]
    if math_toks:
        # 题干里有公式时，解析必须命中其中一条公式（只命中中文词太弱，会放过错位）
        if not any(t in sol for t in math_toks[:12]):
            return "题干公式未在解析中出现（疑似错位）"
        return ""
    hit = sum(1 for t in cn_toks[:40] if t and t in sol)
    if hit == 0:
        return "题干与解析无共同词元（疑似错位）"
    return ""


def find_files(z):
    """返回 {年份: (题干条目名, 解析条目名)}。"""
    papers = {}
    sols = {}
    for n in z.namelist():
        m = re.search(r"/papers/(?:(\d{4})年考研数学\(一\)真题\.md|(\d{4})年数学\(一\)真题及参考答案\.md"
                      r"|(\d{4})考研数学一真题\+答案\.md|(\d{4})考研数学一真题\.md|(\d{4})年数学一真题\.md)$", n)
        if m:
            y = next(g for g in m.groups() if g)
            papers.setdefault(int(y), []).append(n)
        m2 = re.search(r"/solutions/(\d{4})年解析/(\d{4})年解析\.md$", n)
        if m2:
            sols.setdefault(int(m2.group(1)), []).append(n)
    return papers, sols


def bad_ids():
    p = os.path.join(HERE, "_latex_bad_ids.json")
    if not os.path.exists(p):
        return set()
    with open(p, encoding="utf-8") as f:
        return set(json.load(f))


def main():
    report = "--report" in sys.argv
    exclude = bad_ids()
    z = zipfile.ZipFile(ZIP)
    papers, sols = find_files(z)
    years = sorted(y for y in (set(papers) & set(sols)) if y >= MIN_YEAR)
    print("[源] 题干 %d 年 / 解析 %d 年，可用配对 %d 年" %
          (len(papers), len(sols), len(years)))

    stats = collections.Counter()
    dropped = collections.Counter()
    by_year = collections.defaultdict(list)
    seen_fp = set()
    kind_stat = collections.Counter()

    for y in years:
        pname = sorted(papers[y], key=lambda s: ("及参考答案" in s, "+答案" in s))[0]
        sname = sorted(sols[y])[0]
        ptext = z.read(pname).decode("utf-8", "replace")
        stext = z.read(sname).decode("utf-8", "replace")
        pq = parse_papers(ptext)
        sq = parse_solutions(stext)

        for qtype in ("choice", "blank", "calc"):
            P = pq.get(qtype) or []
            S = sq.get(qtype) or []
            if not P or not S:
                continue
            # 对齐：优先按题号（解析文件的编号可能是全卷连续号），
            # 题号缺失时按文档顺序兜底；用过的解析块不重复占用。
            smap = {}
            for b in S:
                if isinstance(b["num"], int) and b["num"] not in smap:
                    smap[b["num"]] = b
            pnums = [q["num"] for q in P if isinstance(q["num"], int)]
            snums = [b["num"] for b in S if isinstance(b["num"], int)]
            offset = (min(snums) - min(pnums)) if (pnums and snums) else 0
            used = set()
            pairs = []
            for i, q in enumerate(P):
                a = None
                n = q.get("num")
                if isinstance(n, int):
                    if n in smap and id(smap[n]) not in used:
                        a = smap[n]
                    elif (n + offset) in smap and id(smap[n + offset]) not in used:
                        a = smap[n + offset]
                if a is None and qtype != "calc" and len(P) == len(S):
                    # 选择题/填空题：两边条数一致时按文档顺序兜底
                    for j in range(len(S)):
                        if j not in used:
                            a = S[j]
                            break
                if a is None:
                    pairs.append((q, None))
                    continue
                used.add(id(a))
                pairs.append((q, a))

            for q, a in pairs:
                stats["total"] += 1
                if a is None:
                    dropped["解析文件里缺此题"] += 1
                    continue
                stem = q["stem"]
                opts = [o for o in q["options"] if o]
                answer = (a["answer"] or "").strip()
                sol = (a["solution"] or "").strip()
                if not stem:
                    drop_reason = "题干为空"
                elif IMG_RE.search(stem):
                    drop_reason = "题干含插图（无法内联，丢弃）"
                else:
                    drop_reason = ""
                if drop_reason:
                    dropped[drop_reason] += 1
                    continue

                if qtype == "choice":
                    letters = sorted(set(re.findall(r"[A-D]", answer)))
                    if not letters:
                        dropped["选择题答案无法识别:%r" % answer[:12]] += 1
                        continue
                    answer = "".join(letters)
                    if len(opts) != 4:
                        dropped["选项数不对(%d)" % len(opts)] += 1
                        continue
                elif qtype == "blank":
                    answer = answer.strip()
                    if not answer:
                        dropped["填空题答案为空"] += 1
                        continue
                    if re.search(r"[（(]\s*\d+\s*[）)]", answer):
                        dropped["多空填空题（判题器仅支持单空）"] += 1
                        continue
                else:
                    if not sol:
                        dropped["解答题缺解析"] += 1
                        continue

                why = verify_pair(qtype, q, a)
                if why:
                    dropped["对齐校验不通过：%s" % why] += 1
                    continue

                scope = stem + " " + " ".join(opts)
                hit = excluded(scope)
                if hit:
                    dropped["不属于高等数学范围：%s" % hit] += 1
                    continue
                kp = classify_full(KP_RULES, scope, sol)
                if kp is None:
                    dropped["无法归入高等数学知识点"] += 1
                    continue
                bad, why2 = damaged(stem, opts, answer, sol, qtype)
                if bad:
                    dropped[why2] += 1
                    continue
                fp = fingerprint({"stem": stem})
                if fp in seen_fp:
                    dropped["跨卷重复"] += 1
                    continue
                seen_fp.add(fp)
                num = q.get("num")
                qid = "ky-%d-%s-%s" % (y, num if num else "x", fp[:6])
                if qid in exclude:
                    dropped["KaTeX 复核未通过"] += 1
                    continue
                url = BLOB + pname.split("Kaoyan-Math1-Papers-main/")[-1]
                by_year[y].append({
                    "qid": qid, "stem": stem, "options": opts, "answer": answer,
                    "solution": sol, "kp": kp, "year": y, "num": num, "type": qtype,
                    "url": url, "sol_url": BLOB + sname.split("Kaoyan-Math1-Papers-main/")[-1],
                    "fp": fp,
                })
                stats["kept"] += 1
                kind_stat[qtype] += 1

    print("扫描题目 %d 道，入库 %d 道" % (stats["total"], stats["kept"]))
    print("题型分布：", dict(kind_stat))
    print("丢弃明细：")
    for k, v in dropped.most_common(20):
        print("   %-44s %d" % (k, v))
    print("按年份：", {y: len(v) for y, v in sorted(by_year.items())})
    if report:
        return 0

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    index = []
    for y in sorted(by_year):
        qs = by_year[y]
        name = "ky_%d" % y
        with io.open(os.path.join(OUT_DIR, name + ".py"), "w", encoding="utf-8", newline="\n") as f:
            f.write(build_module(y, qs))
        index.append({"year": y, "module": name, "count": len(qs)})
        print("产出 %s.py：%d 道" % (name, len(qs)))
    with io.open(os.path.join(HERE, "kaoyan_index.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(index, ensure_ascii=False, indent=1))
    return 0


def damaged(stem, opts, ans, expl, qtype):
    for name, txt in [("题干", stem), ("答案", ans), ("解析", expl)] + \
                     [("选项%d" % i, o) for i, o in enumerate(opts)]:
        if not txt:
            continue
        if txt.count("$") % 2:
            return True, "%s 中 $ 不成对" % name
        for seg in math_segments(txt):
            if CJK.search(seg):
                return True, "%s 的公式里混进中文" % name
            if TYPST_MATH.search(seg):
                return True, "%s 的公式里残留 Typst 记号" % name
        if TYPST_LEFT.search(txt):
            return True, "%s 残留 Typst 记号" % name
    if len(stem) < 8:
        return True, "题干过短"
    if SOURCE_CONFLICT.search(expl or ""):
        return True, "源卷面自标与原卷冲突"
    if BLOCK_MARK_RE.search(expl or ""):
        # 解析里还留着别的题目的起头 = 题块没切干净，这道题的解析是串的
        return True, "解析里混进了别的题目的正文"
    return False, ""


def diff_of(qtype, year):
    if qtype == "calc":
        return "hard"
    if qtype == "blank":
        return "medium"
    return "basic" if year <= 2010 else "medium"


def build_module(year, qs):
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""%d 年全国硕士研究生招生考试数学（一）真题（高等数学范围）。' % year,
        "",
        "来源：GitHub 仓库 %s" % REPO,
        "题干文件：papers/…；答案解析：solutions/%d年解析/…" % year,
        "",
        "入库口径：题干 / 选项 / 答案 / 解析取自源卷面文件；",
        "          只收属于同济《高等数学》范围的题，线代与概率统计整题丢弃。",
        '"""',
        "from ..common import Q",
        "",
        "Q = [",
    ]
    for q in qs:
        src = "%d 年考研数学（一）第 %d 题" % (year, q["num"])
        common = [
            "      src=%s," % json.dumps(src, ensure_ascii=False),
            "      kind='exam-original',",
            "      src_year=%d," % year,
            "      src_region='全国',",
            "      src_paper=%s," % json.dumps("%d 年考研数学（一）" % year, ensure_ascii=False),
            "      src_number=%s," % json.dumps(str(q["num"]), ensure_ascii=False),
            "      src_url=%s," % json.dumps(q["url"], ensure_ascii=False),
            "      prov={'level': 'original', 'url': %s," % json.dumps(q["url"], ensure_ascii=False),
            "            'verifiedAt': '2026-10-28',",
            "            'note': '题干、选项、答案与解析取自源卷面 Markdown 文件；"
            "答案解析文件：%s'}," % q["sol_url"],
            "      qid=%s," % json.dumps(q["qid"], ensure_ascii=False),
            "      tags=['考研真题'],",
        ]
        if q["type"] in ("single", "multi"):
            lines.append("    Q(%s, %s, %s," % (
                json.dumps(q["type"]), json.dumps(diff_of(q["type"], year)),
                json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      options=%s," % json.dumps(q["options"], ensure_ascii=False))
            lines.append("      answer=%s," % json.dumps(list(q["answer"]), ensure_ascii=False))
            lines.append("      expl=%s," % json.dumps(compose_expl(q), ensure_ascii=False))
        elif q["type"] == "blank":
            lines.append("    Q('blank', %s, %s," % (
                json.dumps(diff_of(q["type"], year)), json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      answer=[%s]," % json.dumps(q["answer"].strip()))
            lines.append("      expl=%s," % json.dumps(compose_expl(q), ensure_ascii=False))
        else:
            lines.append("    Q('calc', %s, %s," % (
                json.dumps(diff_of(q["type"], year)), json.dumps(q["kp"])))
            lines.append("      stem=%s," % json.dumps(q["stem"], ensure_ascii=False))
            lines.append("      answer_text=%s," % json.dumps(q["solution"], ensure_ascii=False))
            lines.append("      points=[%s]," % ", ".join(
                "{'text': %s, 'partial': 2}" % json.dumps(p, ensure_ascii=False)
                for p in make_points(q["solution"])))
            lines.append("      expl=%s," % json.dumps(compose_expl(q), ensure_ascii=False))
        lines.extend(common)
        lines.append("    ),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def compose_expl(q):
    """解析统一为教材体例：先「答案依据」，再正文。"""
    return compose_expl_text(q.get("answer") or "", q.get("solution") or "")


if __name__ == "__main__":
    raise SystemExit(main())
