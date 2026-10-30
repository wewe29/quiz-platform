# -*- coding: utf-8 -*-
r"""题库构建脚本：装配题库 + 内联 KaTeX（含 base64 字体）→ 生成单文件 HTML。

用法：
    python build_quiz.py

输入：
    tools/qa_bank/ch*.py   题库数据（每个模块导出 Q 列表）
    tools/template.html    页面骨架（占位符 /*__XXX__*/）
    tools/assets/app.css   页面样式
    tools/assets/app.js    应用逻辑
    <KaTeX 发行版>          dist/katex.min.js, dist/katex.min.css,
                            dist/contrib/auto-render.min.js, dist/fonts/*.woff2

输出：
    ../01《线性代数》题库刷题网页.html

KaTeX 来源（离线，不联网、不装包）：
    D:\workspace\5-docs\exam\数据库\node_modules\katex
"""
import base64
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "01《线性代数》题库刷题网页.html"))


def _katex_dir():
    """KaTeX 发行版定位：环境变量 > 仓库内 vendor（CI/异机用）> 本机 node_modules（历史路径）。
    vendor 进仓库的原因：CI 与其他机器没有 D 盘 node_modules，硬编码路径会让门禁直接跑不起来。"""
    env = os.environ.get("KATEX_DIR")
    if env and os.path.isdir(env):
        return env
    local = os.path.join(HERE, "vendor", "katex", "dist")
    if os.path.isdir(local):
        return local
    return r"D:\workspace\5-docs\exam\数据库\node_modules\katex\dist"


KATEX_DIR = _katex_dir()

sys.path.insert(0, HERE)
from qa_bank import load_bank  # noqa: E402
from qa_bank import target as T  # noqa: E402  口径的单一事实源
from check_html import extract_bank_json  # noqa: E402


def build_summary(questions):
    """按**实际题库**生成页面上的题量文案。

    以前题量文案写死在 template.html 里，加题后忘了改就会印出
    「题库共 500 题」而实际只有 180 题——这种错版在 2026-10-28 真的发生过。
    现在题量、题型/难度配额、判定阈值一律从题库与 target.py 推导，模板里只留占位符。
    """
    from collections import Counter
    c_type = Counter(q["typeGroup"] for q in questions)
    c_diff = Counter(q["difficulty"] for q in questions)
    total = len(questions)
    type_part = " · ".join("%s %d" % (T.TYPE_LABEL[t], c_type.get(t, 0)) for t in T.TYPE_ORDER)
    diff_part = " · ".join("%s %d" % (T.DIFF_LABEL[d], c_diff.get(d, 0)) for d in T.DIFF_ORDER)
    sub = "同济第六版 %d 章 · %d 题 · 六题型 · 三难度" % (T.CHAPTERS, total)
    desc = ("大学线性代数 %d 题单文件刷题网页：六题型、三难度、逐题解析与考点出处，"
            "零外部依赖。" % total)
    footer = "<p>题库共 <b>%d</b> 题：%s；难度 %s。</p>" % (total, type_part, diff_part)

    # 只有真题存在「真题改编」题时才写对应段落——没有就别写，免得说假话
    ext = [q for q in questions if T.EXTENSION_TAG in (q.get("tags") or [])]
    about_extra = footer_extra = ""
    if ext:
        ids = sorted(q["id"] for q in ext)
        about_extra = (
            "<p><b>真题扩写</b>：其中 <b>%d</b> 题（%s 起）的题型改编自公开真题——"
            "中国科学技术大学《线性代数》历年考题汇编、考研数学真题（数一/二/三）、"
            "高校期末卷（浙工大、西电等）；此类题在标签注明「%s」，"
            "出处栏保留教材章节并附真题来源。</p>"
            % (len(ext), ids[0], T.EXTENSION_TAG))
        footer_extra = "<p>其中 %d 题为真题改编（见「题库说明」）。</p>" % len(ext)

    # ---- 第 6 章（选学章）的收录情况：按实际题数生成 ----
    # 原先这里写死「本库仅收录 6 题并标注「选学·引申」」，扩到 36 题后变成假话；
    # 更糟的是 ch6 的 36 题**没有一道带「引申」标记**（引申标记只在 extension 字段里），
    # 原文案等于凭空多宣称了一种标记。两者都改为按实际题库生成。
    ch6 = [q for q in questions if q["chapter"] == 6]
    ch6_note = ""
    if ch6:
        n6 = len(ch6)
        n6_ext = sum(1 for q in ch6 if (q.get("extension") or "").strip())
        ch6_note = ("第 6 章「线性空间与线性变换」为带 * 选学章，本库收录 <b>%d</b> 题，"
                    "出处栏均标注「（选学）」。" % n6)
        if n6_ext:
            ch6_note += "其中 %d 题另附「引申」补充。" % n6_ext
    else:
        ch6_note = "本库未收录第 6 章（选学章）题目。"

    # ---- 「引申」标记说明：只在真有引申题时才写，并给出真实数量 ----
    extq = [q for q in questions if (q.get("extension") or "").strip()]
    ext_note = ""
    if extq:
        ext_note = ("<p>「引申」标记表示超出教材正文、但仍属本课程体系的补充内容，"
                    "不计入答案依据；本库共 <b>%d</b> 题带此标记。</p>" % len(extq))

    return {
        "SUMMARY_SUB": sub,
        "SUMMARY_DESC": desc,
        "SUMMARY_FOOTER": footer,
        "ABOUT_COUNT": str(total),
        "ABOUT_EXTRA": about_extra,
        "FOOTER_EXTRA": footer_extra,
        "CH6_NOTE": ch6_note,
        "EXT_NOTE": ext_note,
    }


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


def inline_katex_css(css, fonts_dir):
    """把 @font-face 的 src 改写为 base64 data URI。

    这是本项目相对本机先例 Day1速测卷_今天复习范围.html 的关键修正：
    先例引用相对路径 fonts/，而同级并无 fonts/ 目录，导致字体 404、公式降级。

    KaTeX 的每条 @font-face 声明了 woff2 / woff / truetype 三种候选源。
    离线单文件场景下只需保留 woff2（现代浏览器全部支持，体积也最小），
    其余两种候选源一并去掉，避免产生指向不存在文件的引用。
    """
    cache = {}
    missing = []

    def data_uri(fname):
        if fname in cache:
            return cache[fname]
        path = os.path.join(fonts_dir, fname)
        if not os.path.exists(path):
            missing.append(fname)
            return None
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        ext = fname.rsplit(".", 1)[1].lower()
        mime = {"woff2": "font/woff2", "woff": "font/woff", "ttf": "font/ttf"}[ext]
        fmt = {"woff2": "woff2", "woff": "woff", "ttf": "truetype"}[ext]
        cache[fname] = 'url(data:%s;base64,%s) format("%s")' % (mime, b64, fmt)
        return cache[fname]

    # 1) 完整的三候选 src 列表 → 只留 woff2
    src_pat = re.compile(
        r'url\(fonts/([A-Za-z0-9_\-]+\.woff2)\)\s*format\("woff2"\),'
        r'url\(fonts/[A-Za-z0-9_\-]+\.woff\)\s*format\("woff"\),'
        r'url\(fonts/[A-Za-z0-9_\-]+\.ttf\)\s*format\("truetype"\)')
    out = src_pat.sub(lambda m: data_uri(m.group(1)) or m.group(0), css)

    # 2) 兜底：其它形态的单一 url(fonts/xxx)
    single_pat = re.compile(r'url\(fonts/([A-Za-z0-9_\-]+\.(?:woff2|woff|ttf))\)')
    out = single_pat.sub(lambda m: data_uri(m.group(1)) or m.group(0), out)

    return out, len(cache), missing


def main():
    allow_partial = "--allow-partial" in sys.argv
    chapters = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--chapter=")]
    out_path = OUT
    for a in sys.argv:
        if a.startswith("--out="):
            out_path = os.path.abspath(a.split("=", 1)[1])

    # 构建前先扫 LaTeX 转义：源码里漏写的反斜杠会被 Python 吃掉，
    # 造成公式静默损坏（\\neq -> 换行+"eq"）。必须挡住。
    from scan_escapes import string_tokens, find_issues
    fatal = 0
    bank_dir = os.path.join(HERE, "qa_bank")
    for fn in sorted(os.listdir(bank_dir)):
        if not (fn.startswith("ch") and fn.endswith(".py")):
            continue
        p = os.path.join(bank_dir, fn)
        try:
            segs = list(string_tokens(p))
        except Exception as e:
            raise SystemExit("[build] 扫描 %s 失败：%s" % (fn, e))
        for row, col, body in segs:
            for idx, level in find_issues(body):
                if level == "致命":
                    fatal += 1
                    print("[build] 转义损坏 %s:%d  ...%s..." %
                          (fn, row, body[max(0, idx - 12):idx + 18]))
    if fatal:
        raise SystemExit("[build] 发现 %d 处 LaTeX 转义会被 Python 吃掉，请先跑 scan_escapes.py --fix" % fatal)
    print("[build] LaTeX 转义扫描通过")

    questions = load_bank(chapters) if chapters else load_bank()
    print("[build] 题库载入：%d 题" % len(questions))
    if len(questions) != T.TOTAL and not allow_partial:
        raise SystemExit(
            "[build] 题量 %d != %d（口径见 qa_bank/target.py）。\n"
            "        题库变了 → 口径要同步更新，否则门禁会一直拦：\n"
            "          python tools/tally.py --emit-target   # 打印可粘贴的新口径块\n"
            "        确认无误后粘贴进 qa_bank/target.py，再重跑本脚本。\n"
            "        （分章写作期想要预览构建可加 --allow-partial）" % (len(questions), T.TOTAL))

    # 校验：每题必须有 id，且 id 唯一
    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("[build] 重复 id：%s" % dup)

    # ---- 内容门禁：答案键 ↔ 解析自洽 + 主观题结构 ----
    # 曾经真实出现过 answer 与 explanation 互相矛盾（q-003/q-008/q-010），
    # 学生按解析答对却被判错。「核验通过」不等于「答案键是对的」。
    from audit_choice import check as check_choice
    from audit_open import check as check_open
    bad = check_choice(questions)
    if bad:
        for p in bad:
            print("[build] 答案键自洽性问题：%s" % p)
        raise SystemExit("[build] 答案键与解析自洽性审计未通过")
    print("[build] 答案键 ↔ 解析 自洽性审计通过")
    bad = check_open(questions)[0]
    if bad:
        for p in bad:
            print("[build] 主观题结构问题：%s" % p)
        raise SystemExit("[build] 主观题结构审计未通过")
    print("[build] 主观题结构审计通过")

    # ---- KaTeX ----
    katex_js = read_text(os.path.join(KATEX_DIR, "katex.min.js"))
    katex_css = read_text(os.path.join(KATEX_DIR, "katex.min.css"))
    autorender_js = read_text(os.path.join(KATEX_DIR, "contrib", "auto-render.min.js"))
    fonts_dir = os.path.join(KATEX_DIR, "fonts")
    katex_css, nfonts, missing = inline_katex_css(katex_css, fonts_dir)
    if missing:
        raise SystemExit("[build] 缺少字体文件：%s" % missing)
    print("[build] KaTeX 已内联：css %d 字体（base64）" % nfonts)

    # ---- 装配 ----
    app_css = read_text(os.path.join(HERE, "assets", "app.css"))
    app_js = read_text(os.path.join(HERE, "assets", "app.js"))
    tpl = read_text(os.path.join(HERE, "template.html"))

    bank = {
        "id": "linear-algebra-tj6-v1",
        "title": "大学《线性代数》题库（同济第六版）",
        # 判定阈值随题库一起下发，页面不写死数字
        "limits": T.limits(),
        "questions": questions,
    }
    bank_js = json.dumps(bank, ensure_ascii=False).replace("</", "<\\/")

    def put(html, token, value):
        ph = "/*__%s__*/" % token
        if ph not in html:
            raise SystemExit("[build] 模板缺少占位符：%s" % ph)
        return html.replace(ph, value)

    html = tpl
    html = put(html, "APP_CSS", app_css)
    html = put(html, "KATEX_CSS", katex_css)
    html = put(html, "BANK", bank_js)
    html = put(html, "KATEX_JS", katex_js)
    html = put(html, "AUTORENDER_JS", autorender_js)
    html = put(html, "APP_JS", app_js)
    summary = build_summary(questions)
    for token in ("SUMMARY_SUB", "SUMMARY_DESC", "SUMMARY_FOOTER",
                  "ABOUT_COUNT", "ABOUT_EXTRA", "FOOTER_EXTRA",
                  "CH6_NOTE", "EXT_NOTE"):
        html = put(html, token, summary[token])
    print("[build] 题量文案已按实际题库生成：%s" % summary["SUMMARY_SUB"])

    # 自检：不得残留占位符 / 不得存在外部资源引用
    # 注意要匹配占位符本体 /*__X__*/，而不是裸 token——
    # 模板里的 window.__BANK__ 是全局变量名，不是待替换占位符。
    for bad in ("__APP_CSS__", "__KATEX_CSS__", "__BANK__", "__KATEX_JS__",
                "__AUTORENDER_JS__", "__APP_JS__", "__SUMMARY_SUB__",
                "__SUMMARY_DESC__", "__SUMMARY_FOOTER__", "__ABOUT_COUNT__",
                "__ABOUT_EXTRA__", "__FOOTER_EXTRA__", "__CH6_NOTE__",
                "__EXT_NOTE__"):
        if ("/*%s*/" % bad) in html:
            raise SystemExit("[build] 占位符未替换：%s" % bad)
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)
    if ext:
        raise SystemExit("[build] 发现外部资源引用：%s" % ext[:5])
    if re.search(r"url\(\s*fonts/", html):
        raise SystemExit("[build] 仍有未内联的字体相对路径")

    # 装配后自检：把内联题库抠出来重新解析一次。
    # 只看「构建成功」是不够的——曾经因为模板多了一个 {}，
    # 产出 {json}{} 这种非法 JS，页面静默变成 0 题。
    m = extract_bank_json(html)
    if m is None:
        raise SystemExit("[build] 装配后找不到 window.__BANK__ 赋值块")
    raw = m
    try:
        parsed = json.loads(raw)
    except Exception as e:
        raise SystemExit("[build] 内联题库 JSON 解析失败：%s" % e)
    if len(parsed.get("questions", [])) != len(questions):
        raise SystemExit("[build] 内联题库题数与源不一致")
    print("[build] 内联题库回读校验通过（%d 题）" % len(parsed["questions"]))

    # 回读后还要逐字段比对：构建环节可能悄悄改写字段
    # （曾经出现过成品 JSON 与源码 answer 不一致的情况）。
    src_by = {q["id"]: q for q in questions}
    built_by = {q["id"]: q for q in parsed["questions"]}
    field_diffs = []
    for qid in sorted(set(src_by) & set(built_by)):
        for f in ("type", "difficulty", "stem", "options", "answer", "accept",
                  "answerText", "points", "explanation", "misconception", "extension"):
            if src_by[qid].get(f) != built_by[qid].get(f):
                field_diffs.append("%s.%s" % (qid, f))
    if field_diffs:
        raise SystemExit("[build] 成品与源码字段不一致：%s" % field_diffs[:8])
    print("[build] 成品 ↔ 源码 逐字段一致")

    with io.open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    size = os.path.getsize(out_path)
    print("[build] 输出：%s" % out_path)
    print("[build] 大小：%.2f MB（%d 字节）" % (size / 1048576.0, size))


if __name__ == "__main__":
    main()
