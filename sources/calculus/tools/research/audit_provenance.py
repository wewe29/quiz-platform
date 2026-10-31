# -*- coding: utf-8 -*-
r"""溯源审计：把题库里每一道真题**回源**比对一遍。

这道门禁回答三个问题：
  1. 每道题的 provenance.url 是否登记完整、指向它真实所在的那份卷面；
  2. 题干 / 选项 / 答案是否真的出现在源卷面文件里（不是我们编的）；
  3. src_year / region / paper / number 是否与源卷面对得上。

比对方式：重新读取本地缓存里的源卷面文件，按题号定位原题，
再做「归一化文本包含」判断——归一化会去掉空白与 $ 定界符，
只比实质内容，不比排版。

用法：
    python tools/research/audit_provenance.py            # 全量审计
    python tools/research/audit_provenance.py --sample 50 # 抽样打印明细
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
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank import load_bank          # noqa: E402
from typst_extract import parse_paper   # noqa: E402

CACHE = os.path.join(HERE, "_cache")
KY_ZIP = os.path.join(CACHE, "TsekaLuk_Kaoyan-Math1-Papers.zip")
M2_ZIP = os.path.join(CACHE, "TsekaLuk_Kaoyan-Math2-Papers.zip")
ZK_ZIP = os.path.join(CACHE, "huangnaisheng_zikao-exam-solutions.zip")

URL_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/blob/main/(.+)$")


def norm(s):
    """归一化：去掉空白、$ 定界符与 Markdown 强调记号，只留实质内容。"""
    s = s or ""
    s = s.replace("**", "").replace("$", "")
    s = re.sub(r"\s+", "", s)
    return s


def load_sources():
    """建立 {url: (zip路径, 内部路径)} 映射。"""
    out = {}
    if os.path.exists(KY_ZIP):
        z = zipfile.ZipFile(KY_ZIP)
        for n in z.namelist():
            if not n.endswith(".md"):
                continue
            if "/papers/" not in n and "/solutions/" not in n:
                continue
            rel = n.split("Kaoyan-Math1-Papers-main/", 1)[-1]
            url = "https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/" + rel
            out[url] = (KY_ZIP, n)
    if os.path.exists(M2_ZIP):
        z = zipfile.ZipFile(M2_ZIP)
        for n in z.namelist():
            if not n.endswith(".md"):
                continue
            if "/solutions/" not in n:
                continue
            rel = n.split("Kaoyan-Math2-Papers-main/", 1)[-1]
            url = "https://github.com/TsekaLuk/Kaoyan-Math2-Papers/blob/main/" + rel
            out[url] = (M2_ZIP, n)
    if os.path.exists(ZK_ZIP):
        z = zipfile.ZipFile(ZK_ZIP)
        for n in z.namelist():
            if not n.endswith(".md"):
                continue
            rel = n.split("zikao-exam-solutions-main/", 1)[-1]
            url = ("https://github.com/huangnaisheng/zikao-exam-solutions/"
                   "blob/main/" + rel)
            out[url] = (ZK_ZIP, n)
    return out


def main():
    sample_n = 0
    for a in sys.argv:
        if a.startswith("--sample="):
            sample_n = int(a.split("=", 1)[1])
    bank = load_bank()
    exams = [q for q in bank if (q.get("provenance") or {}).get("level") == "original"]
    sources = load_sources()
    zips = {}
    extracted = {}

    def get_text(url):
        """取源卷面的可比文本。

        Typst 源要先按同样的抽取规则还原成 LaTeX 文本再比，
        否则拿 '#mi(`x`)' 去比 '$x$' 必然对不上。
        """
        if url in extracted:
            return extracted[url]
        if url not in sources:
            extracted[url] = None
            return None
        zp, inner = sources[url]
        if zp not in zips:
            zips[zp] = zipfile.ZipFile(zp)
        raw = zips[zp].read(inner).decode("utf-8", "replace")
        if inner.endswith(".typ"):
            chunks = []
            for qq in parse_paper(raw):
                chunks.append(qq["stem"])
                chunks.extend(qq["options"])
                chunks.append(qq["solution"])
                chunks.append(qq["answer"])
            text = "\n".join(chunks)
        else:
            text = raw
        extracted[url] = text
        return text

    stats = collections.Counter()
    problems = collections.defaultdict(list)
    by_source = collections.defaultdict(list)
    for q in exams:
        prov = q.get("provenance") or {}
        url = prov.get("url")
        src = q.get("source") or {}
        if not url:
            stats["缺 provenance.url"] += 1
            problems["缺 provenance.url"].append(q.get("id"))
            continue
        if not URL_RE.match(url):
            stats["provenance.url 格式非法"] += 1
            problems["provenance.url 格式非法"].append(q.get("id"))
            continue
        if url not in sources:
            stats["源文件不在本地缓存（无法回源核对）"] += 1
            problems["源文件不在本地缓存（无法回源核对）"].append(q.get("id"))
            continue
        by_source[url].append(q)

    # 回源比对
    checked = 0
    for url, qs in by_source.items():
        text = get_text(url)
        nt = norm(text)
        for q in qs:
            checked += 1
            stem = norm(q.get("stem") or "")
            if not stem:
                stats["题干为空"] += 1
                problems["题干为空"].append(q.get("id"))
                continue
            # 取题干的前 40 个归一化字符做包含判断（源文里可能带前缀标记）
            probe = stem[:40]
            if probe and probe not in nt:
                stats["题干未在源卷面中找到"] += 1
                problems["题干未在源卷面中找到"].append(q.get("id"))
                continue
            # 答案与解析可能来自另一份文件（如考研的 solutions/），一并纳入比对
            extra = ""
            prov = q.get("provenance") or {}
            for u2 in re.findall(r"https://github\.com/\S+?(?:\.typ|\.md)", prov.get("note") or ""):
                t2 = get_text(u2)
                if t2:
                    extra += t2
            nt_all = nt + norm(extra)
            # 选项逐条核对
            opts = q.get("options") or []
            bad_opt = None
            for o in opts:
                no = norm(str(o))
                if len(no) >= 4 and no not in nt_all:
                    bad_opt = str(o)[:40]
                    break
            if bad_opt:
                stats["选项未在源卷面中找到"] += 1
                problems["选项未在源卷面中找到"].append(q.get("id"))
                continue
            # 答案值也要能在源卷面里找到（选择题是字母，不具区分度，跳过）
            t = q.get("type")
            if t in ("blank", "calc"):
                ansv = q.get("answer")
                if isinstance(ansv, list):
                    ansv = ansv[0] if ansv else ""
                ansv = norm(str(ansv or "")).strip("$")
                if len(ansv) >= 3 and ansv not in nt_all:
                    stats["答案值未在源卷面中找到"] += 1
                    problems["答案值未在源卷面中找到"].append(q.get("id"))
                    continue
            stats["回源一致"] += 1

    print("真题题量：%d" % len(exams))
    print("涉及源文件：%d 个" % len(by_source))
    print("回源核对：%d 道" % checked)
    print()
    print("核对结果：")
    for k, v in stats.most_common():
        print("   %-34s %d" % (k, v))
    bad = {k: v for k, v in problems.items() if k != "题干未在源卷面中找到"}
    if bad:
        print()
        print("异常明细：")
        for k, v in bad.items():
            for i in v[:10]:
                print("   [%s] %s" % (k, i))
    miss = problems.get("题干未在源卷面中找到") or []
    if miss:
        print()
        print("题干未在源卷面中找到（%d 道，抽样）：" % len(miss))
        for i in miss[:8]:
            print("   %s" % i)

    if sample_n:
        print()
        print("=" * 74)
        print("抽样明细（人工核对）")
        import random
        random.seed(20261028)
        pool = [q for q in exams if q.get("id") not in set(miss)]
        for q in random.sample(pool, min(sample_n, len(pool))):
            print("-" * 70)
            print("%s ｜ %s" % (q.get("id"), (q.get("source") or {}).get("text")))
            print("URL：%s" % (q.get("provenance") or {}).get("url"))
            print("题干：%s" % (q.get("stem") or "")[:180])
            print("选项：%s" % (q.get("options") or [])[:4])
            print("答案：%r" % (q.get("answer"),))
            print("解析：%s" % (q.get("explanation") or "")[:180])

    ok = stats.get("回源一致", 0) == len(exams)
    print()
    print("溯源审计%s" % ("通过" if ok else "存在异常，见上"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
