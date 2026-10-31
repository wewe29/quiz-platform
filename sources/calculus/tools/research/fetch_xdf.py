# -*- coding: utf-8 -*-
r"""考研数学真题素材抓取器（xdf 题型整合页）。

用途：把「真题（年份 卷别）」条目连同所属模块/题型抽成结构化锚点，
      供 (1) 素材摘要文档 与 (2) 真题改编题的出处登记使用。

重要口径（不可放宽）：
    该站正文的公式是 MathJax 的**线性化输出**，上下标与分式被压平，
    例如 "x3ex−1" 到底是 $x^3e^x-1$ 还是 $x\cdot 3e^x$ 存在歧义。
    因此本脚本**只抽结构与考点锚点，不把公式当题干直接采用**——
    真题正文的落地方式见 tools/research/真题素材摘要.md 的「落地口径」。

用法：
    python tools/research/fetch_xdf.py            # 抓取并写入 xdf_items.json
"""
import gzip
import io
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "xdf_items.json")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

# 已实测可访问、且正文含「真题（年 卷别）」的页面
PAGES = [
    "https://kaoyan.xdf.cn/202606/15252944.html",
    "https://kaoyan.xdf.cn/202606/15252931.html",
]

# HTML 实体 → LaTeX（仅覆盖抓取样本里出现过的；未覆盖的保持原样并标记）
ENT2TEX = {
    "rarr": r"\to", "minus": "-", "infin": r"\infty", "int": r"\int",
    "pi": r"\pi", "sdot": r"\cdot", "prime": "'", "lambda": r"\lambda",
    "ge": r"\ge", "le": r"\le", "ne": r"\ne", "isin": r"\in",
    "notin": r"\notin", "times": r"\times", "Delta": r"\Delta",
    "sum": r"\sum", "prod": r"\prod", "part": r"\partial",
    "radic": r"\sqrt", "cap": r"\cap", "cup": r"\cup",
    "alpha": r"\alpha", "beta": r"\beta", "theta": r"\theta",
    "omega": r"\omega", "rho": r"\rho", "sigma": r"\sigma",
    "mu": r"\mu", "epsilon": r"\varepsilon", "varphi": r"\varphi",
    "rightarrow": r"\rightarrow", "Rightarrow": r"\Rightarrow",
    "ldots": r"\ldots", "cdots": r"\cdots", "sim": r"\sim",
    "equiv": r"\equiv", "approx": r"\approx", "langle": r"\langle",
    "rangle": r"\rangle", "lfloor": r"\lfloor", "rfloor": r"\rfloor",
    "quad": r"\quad", "qquad": r"\qquad", "circ": r"\circ",
    "perp": r"\perp", "parallel": r"\parallel", "degree": r"^\circ",
    "sqrt": r"\sqrt", "dArr": r"\Downarrow", "uArr": r"\Uparrow",
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    m = re.search(rb'charset=["\']?([A-Za-z0-9_\-]+)', raw[:4000])
    enc = m.group(1).decode("ascii") if m else "utf-8"
    if enc.lower() in ("gb2312", "gbk"):
        enc = "gb18030"
    return raw.decode(enc, "replace")


def body_of(html):
    """取文章正文容器。结束标记取 copyright 之前——xdf_content_line 会出现在正文中间。"""
    i = html.find('<div class="xdf_content_detail"')
    if i < 0:
        i = html.find('xdf_content_detail')
    if i < 0:
        return ""
    j = html.find('xdf_content_copyright', i)
    if j < 0:
        j = len(html)
    return html[i:j]


def title_of(html):
    m = re.search(r'<div class="xdf_content_title[^"]*"[^>]*>(.*?)</div>', html, re.S)
    if not m:
        return ""
    t = re.sub(r"(?s)<[^>]+>", " ", m.group(1))
    return re.sub(r"\s+", " ", t).strip()


def ent2tex(s):
    """把 HTML 实体转成 LaTeX 记号；未覆盖的实体保留并加标记。"""
    def rep(m):
        name = m.group(1)
        if name in ENT2TEX:
            return ENT2TEX[name]
        return "\\text{%s?}" % name
    s = re.sub(r"&([A-Za-z]+);", rep, s)
    return s


def clean(s):
    s = s.replace("", "")        # 零宽空格（MathJax 线性化的分隔符）
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


LABEL_PATTERNS = [
    re.compile(r"真题（\s*(\d{4})\s*([^）]*?)\s*）"),                 # 真题（2021 数二）
    re.compile(r"【\s*(\d{4})\s*([^】]*?)\s*真题"),                    # 【2021 数二真题原题】
    re.compile(r"【\s*(\d{4})\s*([^】]*?)\s*】"),                      # 【2021 数二真题节选】
    re.compile(r"（\s*(\d{4})\s*([^）]*?真题[^）]*)\s*）"),             # （2024 数三真题）
]

SPLIT_MARKERS = ["真题解析", "解析", "详解"]


def paper_of(raw):
    """把「数二」「数学二」「数二真题原题」统一成「数学二」。"""
    t = re.sub(r"(真题|原题|节选|改编|精选|真题节选|经典|完整|详细)", "", raw)
    t = re.sub(r"[（(）)【】\s]", "", t)
    if t in ("数一", "一"): return "数学一"
    if t in ("数二", "二"): return "数学二"
    if t in ("数三", "三"): return "数学三"
    return t or "未标注"


def parse(body):
    """扫出「真题（…）」/「【…真题…】」条目。

    每个条目的正文形如：<题干> <strong>真题解析</strong> <解析正文>
    """
    tokens = re.findall(r"<h([1-4])[^>]*>(.*?)</h\1>|<p[^>]*>(.*?)</p>", body, re.S)
    items = []
    ctx = {"h1": "", "h2": "", "h3": ""}
    pending = None
    for lvl, htxt, phtml in tokens:
        if htxt:
            level = int(lvl)
            text = clean(ent2tex(re.sub(r"(?s)<[^>]+>", " ", htxt)))
            if level == 1:
                ctx["h1"] = text
            elif level == 2:
                ctx["h2"] = text
            elif level == 3:
                ctx["h3"] = text
            else:
                year, praw = None, None
                for pat in LABEL_PATTERNS:
                    m = pat.search(text)
                    if m:
                        year, praw = m.group(1), m.group(2)
                        break
                if year:
                    pending = (int(year), paper_of(praw), text)
            continue
        if pending and phtml:
            year, paper, label = pending
            # 在「解析」标记处切分
            cut = -1
            marker = None
            for mk in SPLIT_MARKERS:
                i = phtml.find(mk)
                if i >= 0 and (cut < 0 or i < cut):
                    cut, marker = i, mk
            if cut >= 0:
                stem_html = phtml[:cut]
                expl_html = phtml[cut + len(marker):]
            else:
                stem_html, expl_html = phtml, ""
            stem = clean(ent2tex(re.sub(r"(?s)<[^>]+>", " ", stem_html)))
            expl = clean(ent2tex(re.sub(r"(?s)<[^>]+>", " ", expl_html)))
            items.append({
                "year": year,
                "paper": paper,
                "label": label,
                "module": ctx["h2"],
                "topic": ctx["h3"],
                "stemRaw": stem,
                "explainRaw": expl,
            })
            pending = None
    return items


def main():
    all_items = []
    sources = []
    for url in PAGES:
        try:
            html = fetch(url)
        except Exception as e:
            print("[xdf] 抓取失败 %s：%s" % (url, e))
            continue
        body = body_of(html)
        title = title_of(html)
        items = parse(body)
        print("[xdf] %s  标题=%s  条目=%d" % (url, title[:40], len(items)))
        for it in items:
            it["sourceUrl"] = url
            it["sourceTitle"] = title
        all_items.extend(items)
        sources.append({"url": url, "title": title, "items": len(items)})

    data = {"sources": sources, "items": all_items}
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1))
    print("[xdf] 合计 %d 条锚点 → %s" % (len(all_items), OUT_JSON))

    by_year = {}
    for it in all_items:
        k = (it["year"], it["paper"])
        by_year[k] = by_year.get(k, 0) + 1
    for k in sorted(by_year):
        print("   %s %s：%d 条" % (k[0], k[1], by_year[k]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
