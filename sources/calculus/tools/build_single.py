# -*- coding: utf-8 -*-
r"""单文件离线包构建：题库 + KaTeX（含 base64 字体）+ 全部 JS → 一个 HTML。

用法：
    python build_single.py
    python build_single.py --out=D:\path\to\file.html

产物特征：
  * 零外部请求：字体转 base64 data URI，脚本全部内联
  * 双击即用（file:// 可正常工作），断网可用
  * 与多文件站共用同一套 core/ ui/ 源码（普通 <script> 顺序加载，不用 ESM）

与 build_static.py 的关系：同一个题库、同一套代码、两种产物形态。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from qa_bank import load_bank                        # noqa: E402
from qa_bank.export import build_index, catalog      # noqa: E402
from qa_bank.target import TOTAL as TARGET_TOTAL     # noqa: E402  口径单一事实源
import katex_assets                                 # noqa: E402

OUT_DEFAULT = os.path.abspath(
    os.path.join(HERE, "..", "01《高等数学》题库刷题网页 v2.html"))
BANK_ID = "advanced-math-tj7-v2"
BANK_TITLE = "大学《高等数学》题库（同济第七版 + 考研真题）"

CORE_FILES = ["bus.js", "store.js", "judge.js", "schema.js", "bank.js", "session.js",
              "stats.js", "picked.js"]
UI_FILES = ["dom.js", "theme.js", "render.js", "hud.js", "filters.js", "card.js", "drawer.js", "keys.js"]
APP_FILE = "app.js"
CSS_FILES = ["tokens.css", "app.css"]


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    out = OUT_DEFAULT
    for a in sys.argv:
        if a.startswith("--out="):
            out = os.path.abspath(a.split("=", 1)[1])
    allow_partial = "--allow-partial" in sys.argv

    questions = load_bank()
    print("[build] 题库载入：%d 题" % len(questions))
    if len(questions) != TARGET_TOTAL and not allow_partial:
        raise SystemExit("[build] 题量 %d != %d；请补齐题库或加 --allow-partial"
                         % (len(questions), TARGET_TOTAL))

    from build_static import run_gates
    run_gates(questions)

    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("[build] 重复 id：%s" % dup)

    # ---- KaTeX（inline 后端）----
    katex_css, nfonts, _ = katex_assets.css_inline()
    katex_js, autorender_js = katex_assets.js_bundle()
    print("[build] KaTeX 已内联：%d 个 woff2（base64）" % nfonts)

    # ---- CSS ----
    app_css = "\n".join(read_text(os.path.join(HERE, "assets", "css", c)) for c in CSS_FILES)

    # ---- JS ----
    chunks = []
    for f in CORE_FILES:
        chunks.append("/* ===== core/%s ===== */\n%s" % (f, read_text(os.path.join(HERE, "assets", "js", "core", f))))
    for f in UI_FILES:
        chunks.append("/* ===== ui/%s ===== */\n%s" % (f, read_text(os.path.join(HERE, "assets", "js", "ui", f))))
    chunks.append("/* ===== app.js ===== */\n%s" % read_text(os.path.join(HERE, "assets", "js", APP_FILE)))
    app_js = "\n".join(chunks)

    # ---- 题库内联 ----
    idx = build_index(questions, BANK_ID, BANK_TITLE)
    bank = {
        "id": BANK_ID,
        "title": BANK_TITLE,
        "questions": questions,
        "catalog": idx["catalog"],
        "index": {"bank": idx["bank"], "total": idx["total"],
                  "chapters": idx["chapters"], "summary": idx["summary"]},
    }
    bank_js = "window.__BANK__ = " + json.dumps(bank, ensure_ascii=False).replace("</", "<\\/") + ";"

    # ---- 装配 ----
    tpl = read_text(os.path.join(HERE, "template_v2.html"))
    head = ("<style>\n%s\n</style>\n<style>\n%s\n</style>" % (app_css, katex_css))
    html = tpl.replace("/*__HEAD__*/", head)
    html = html.replace("/*__BANK_JS__*/", bank_js)
    # 一个槽位里放两段：katex.min.js + contrib/auto-render.min.js
    html = html.replace("/*__KATEX_JS__*/", katex_js + "\n" + autorender_js)
    html = html.replace("/*__SCRIPTS__*/", app_js)

    for tok in ("__HEAD__", "__BANK_JS__", "__KATEX_JS__", "__SCRIPTS__"):
        if ("/*%s*/" % tok) in html:
            raise SystemExit("[build] 占位符未替换：%s" % tok)

    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)
    if ext:
        raise SystemExit("[build] 发现外部资源引用：%s" % ext[:5])
    if re.search(r"url\(\s*fonts/", html):
        raise SystemExit("[build] 仍有未内联的字体相对路径")

    # 回读校验：抠出内联 JSON 再解析一次，防止装配环节悄悄改字段
    from check_html import extract_bank_json
    raw = extract_bank_json(html)
    if raw is None:
        raise SystemExit("[build] 装配后找不到 window.__BANK__ 赋值块")
    try:
        parsed = json.loads(raw)
    except Exception as e:
        raise SystemExit("[build] 内联题库 JSON 解析失败：%s" % e)
    if len(parsed.get("questions", [])) != len(questions):
        raise SystemExit("[build] 内联题库题数与源不一致")
    src_by = {q["id"]: q for q in questions}
    built_by = {q["id"]: q for q in parsed["questions"]}
    fields = ("type", "difficulty", "stem", "options", "answer", "accept",
              "answerText", "points", "explanation", "misconception", "extension",
              "knowledgePoint", "knowledgePoints", "source", "provenance", "tags")
    diffs = []
    for qid in sorted(set(src_by) & set(built_by)):
        for f in fields:
            if src_by[qid].get(f) != built_by[qid].get(f):
                diffs.append("%s.%s" % (qid, f))
    if diffs:
        raise SystemExit("[build] 成品与源码字段不一致：%s" % diffs[:8])
    print("[build] 成品 ↔ 源码 逐字段一致")

    # script 结构门禁：单文件包把 KaTeX 与题库内联进 <script>。
    # 若模板占位符被错误嵌套，内联的 KaTeX 会退化成普通文本而静默失效，
    # 页面表现为「零报错，但公式全是原文」。
    from check_html import scan_scripts
    scripts, sproblems = scan_scripts(html)
    if sproblems:
        raise SystemExit("[build] 单文件包 script 结构异常：%s" % sproblems[:4])
    bodies = "\n".join(s["body"] for s in scripts if s["src"] is None)
    for label, token in (("KaTeX 主库", "katex"),
                         ("KaTeX auto-render", "renderMathInElement"),
                         ("题库数据", "window.__BANK__")):
        if token not in bodies:
            raise SystemExit("[build] 单文件包内联脚本缺少 %s（关键字 %s）" % (label, token))
    print("[build] 单文件包 script 结构正常：%d 个内联脚本块" % len(scripts))

    # 内联接线门禁：window.__BANK__ 必须真的交给 bank.setInline(...)。
    # 没接线时 hasInline() 恒为 false → 误走 fetch('data/index.json') →
    # 离线双击打开必然 404，页面只剩「题库载入失败」，而且**零报错**。
    # （这个洞曾经真实存在：setInline 定义了却从没被调用，还被登记进悬空导出基线。）
    if not re.search(r"setInline\(\s*window\.__BANK__\s*\)", bodies):
        raise SystemExit("[build] 单文件包没有把 window.__BANK__ 交给 bank.setInline(...)："
                         "内联模式不会生效，页面会去 fetch data/index.json 并 404")
    print("[build] 内联题库接线正常：bank.setInline(window.__BANK__)")

    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    size = os.path.getsize(out)
    print("[build] 输出：%s" % out)
    print("[build] 大小：%.2f MB（%d 字节）" % (size / 1048576.0, size))


if __name__ == "__main__":
    main()
