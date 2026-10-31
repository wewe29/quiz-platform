# -*- coding: utf-8 -*-
r"""多文件站点构建：题库分章 JSON + 静态资源 + index.html。

用法：
    python build_static.py
    python build_static.py --out=D:\path\to\site

输出结构：
    <out>/index.html
    <out>/data/index.json
    <out>/data/ch01.json … ch12.json
    <out>/assets/css/tokens.css, app.css
    <out>/assets/js/core/*.js
    <out>/assets/js/ui/*.js
    <out>/assets/js/app.js
    <out>/assets/vendor/katex/katex.min.css, katex.min.js, contrib/auto-render.min.js, fonts/*.woff2

与单文件离线包（build_single.py）共用同一套源码：
core/ 与 ui/ 用普通 <script> 标签顺序加载，不用 ESM——
ESM 在 file:// 下被 CORS 拦截，两套产物就无法共用源码。
"""
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from qa_bank import load_bank                      # noqa: E402
from qa_bank.export import build_index, split_by_chapter   # noqa: E402
from qa_bank.target import TOTAL as TARGET_TOTAL   # noqa: E402  口径单一事实源
import katex_assets                               # noqa: E402

OUT_DEFAULT = os.path.abspath(os.path.join(HERE, "..", "_site_v2"))
BANK_ID = "advanced-math-tj7-v2"
BANK_TITLE = "大学《高等数学》题库（同济第七版 + 考研真题）"

CORE_FILES = ["bus.js", "store.js", "judge.js", "schema.js", "bank.js", "session.js",
              "stats.js", "picked.js"]
UI_FILES = ["dom.js", "theme.js", "render.js", "hud.js", "filters.js", "card.js", "drawer.js", "keys.js"]
APP_FILE = "app.js"

CSS_FILES = [("tokens.css", "assets/css/tokens.css"), ("app.css", "assets/css/app.css")]


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_json(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1))


def run_gates(questions):
    """内容门禁：与单文件构建同一条链，不能因为换了产物形态就放松。"""
    from scan_escapes import string_tokens, find_issues
    bank_dir = os.path.join(HERE, "qa_bank")
    fatal = 0
    for fn in sorted(os.listdir(bank_dir)):
        if not (fn.startswith("ch") and fn.endswith(".py")):
            continue
        p = os.path.join(bank_dir, fn)
        for row, col, body in string_tokens(p):
            for idx, level in find_issues(body):
                if level == "致命":
                    fatal += 1
                    print("[build] 转义损坏 %s:%d" % (fn, row))
    if fatal:
        raise SystemExit("[build] 发现 %d 处 LaTeX 转义会被 Python 吃掉" % fatal)
    print("[build] LaTeX 转义扫描通过")

    from audit_choice import check as check_choice
    from audit_open import check as check_open
    bad = check_choice(questions)
    if bad:
        for p in bad:
            print("[build] 答案键自洽性问题：%s" % p)
        raise SystemExit("[build] 答案键 ↔ 解析 自洽性审计未通过")
    print("[build] 答案键 ↔ 解析 自洽性审计通过")
    bad = check_open(questions)[0]
    if bad:
        for p in bad:
            print("[build] 主观题结构问题：%s" % p)
        raise SystemExit("[build] 主观题结构审计未通过")
    print("[build] 主观题结构审计通过")

    run_render_coverage(questions)
    run_filter_keys(questions)
    run_keyboard_contract()

    # 「导出了却从没被调用」门禁：这类缺陷让整块功能是死的
    # （card.setBadge → 答题卡计数恒为 0；stats.recompute → 统计面板全空），
    # 单测与数据门禁都测不出来，只有静态扫描能抓。
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_unwired.py")],
                       capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    for line in out.splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        raise SystemExit("[build] 出现新的悬空导出（导出了却从没被调用）")


def run_render_coverage(questions):
    """渲染层内容覆盖门禁：用**真实的 render.js** 跑一遍全库。

    数据门禁全绿 ≠ 渲染时内容没被丢掉。真实踩过：解析里的「答案依据」
    被摘出来后挂在「其它段落」上渲染，而整篇解析只有
    「答案依据 + 逐项错因」时其它段落为空 → 依据整段丢弃（856 题中 103 题）。
    数据层面解析字段一直存在且非空，所以纯数据门禁查不出来。
    """
    import shutil
    import subprocess
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        print("[build] 未找到 node，跳过渲染层覆盖检查")
        return
    script = os.path.join(HERE, "render_coverage.js")
    payload = json.dumps(questions, ensure_ascii=False).encode("utf-8")
    r = subprocess.run([node, script], input=payload, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    for line in (out + err).splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        raise SystemExit("[build] 渲染层内容覆盖检查未通过")


def run_filter_keys(questions):
    """筛选键契约门禁：chip 上写的题数，必须等于点它真能选出的题数。

    真实踩过（用户实机发现）：章节 chip 写着「函数与极限(154)」，点下去却是
    「当前筛选命中 0 题」。根因是 chip 的 key 是字符串 "1"、题目里 chapter 是数字 1，
    session.passes 用 indexOf(q.chapter) 比 → 永远失配。
    数据层完全正确（题数、字段、章节分布都在），只有「界面计数」与「界面筛选」
    用了两套 key 空间 —— 单测与数据门禁都覆盖不到，只有把真实 UI 的 key 生成逻辑
    和真实 session.passes 放在一起跑才抓得到。
    """
    import shutil
    import subprocess
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        print("[build] 未找到 node，跳过筛选键契约检查")
        return
    idx = build_index(questions, BANK_ID, BANK_TITLE)
    payload = json.dumps({"questions": questions, "catalog": idx["catalog"]},
                         ensure_ascii=False).encode("utf-8")
    script = os.path.join(HERE, "check_filter_keys.js")
    r = subprocess.run([node, script], input=payload, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    for line in (out + err).splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        raise SystemExit("[build] 筛选键契约检查未通过")


def run_keyboard_contract():
    """键盘快捷键契约门禁：Enter 必须真的能提交答案。

    真实踩过（2026-10-31，线上复验时浏览器实测发现）：
        多选题选好答案后按 Enter **提交不了**，而点「提交答案（Enter）」按钮完全正常。
    根因是选项元素自己绑了 keydown（Enter → onPick），和全局「Enter = 提交答案」抢键：
        事件先落到选项 → 多选题的 onPick 是 toggle → 刚选的答案被自己取消；
        事件再冒泡到全局 → 缓冲区已空 → 弹「还没作答，先选一个选项」。
    单选题不受影响（onPick 是赋值），所以只有多选题坏、且鼠标路径正常，
    自测与数据门禁全都照不到 —— 只有把真实 render.js + 真实 keys.js 跑一遍真实按键路径才抓得到。
    """
    import shutil
    import subprocess
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        print("[build] 未找到 node，跳过键盘快捷键契约检查")
        return
    script = os.path.join(HERE, "check_keyboard_contract.js")
    r = subprocess.run([node, script], capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    for line in (out + err).splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        raise SystemExit("[build] 键盘快捷键契约检查未通过")


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
    run_gates(questions)

    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("[build] 重复 id：%s" % dup)

    # ---- 数据 ----
    per = split_by_chapter(questions)
    idx = build_index(questions, BANK_ID, BANK_TITLE)
    write_json(os.path.join(out, "data", "index.json"), idx)
    for n, qs in per.items():
        write_json(os.path.join(out, "data", "ch%02d.json" % n), {"chapter": n, "questions": qs})
    print("[build] 数据：index.json + %d 个分章文件" % len(per))

    # ---- 静态资源 ----
    for src_name, dst_rel in CSS_FILES:
        write_text(os.path.join(out, dst_rel.replace("/", os.sep)),
                   read_text(os.path.join(HERE, "assets", "css", src_name)))
    for f in CORE_FILES:
        write_text(os.path.join(out, "assets", "js", "core", f),
                   read_text(os.path.join(HERE, "assets", "js", "core", f)))
    for f in UI_FILES:
        write_text(os.path.join(out, "assets", "js", "ui", f),
                   read_text(os.path.join(HERE, "assets", "js", "ui", f)))
    write_text(os.path.join(out, "assets", "js", APP_FILE),
               read_text(os.path.join(HERE, "assets", "js", APP_FILE)))

    # ---- KaTeX ----
    css_m, fonts = katex_assets.css_multifile()
    write_text(os.path.join(out, "assets", "vendor", "katex", "katex.min.css"), css_m)
    kjs, ajs = katex_assets.js_bundle()
    write_text(os.path.join(out, "assets", "vendor", "katex", "katex.min.js"), kjs)
    write_text(os.path.join(out, "assets", "vendor", "katex", "contrib", "auto-render.min.js"), ajs)
    katex_assets.copy_fonts(os.path.join(out, "assets", "vendor", "katex", "fonts"))
    print("[build] KaTeX：%d 个 woff2 字体" % len(fonts))

    # ---- index.html ----
    tpl = read_text(os.path.join(HERE, "template_v2.html"))
    head = "\n".join(
        ['<link rel="stylesheet" href="assets/css/%s">' % name for name, _ in CSS_FILES] +
        ['<link rel="stylesheet" href="assets/vendor/katex/katex.min.css">'])
    scripts = ["assets/vendor/katex/katex.min.js",
               "assets/vendor/katex/contrib/auto-render.min.js"]
    scripts += ["assets/js/core/%s" % f for f in CORE_FILES]
    scripts += ["assets/js/ui/%s" % f for f in UI_FILES]
    scripts += ["assets/js/%s" % APP_FILE]
    script_tags = "\n".join('<script src="%s"></script>' % s for s in scripts)

    html = tpl.replace("/*__HEAD__*/", head)

    # 模板里占位符是被 <script> 包住的。多文件站要塞的是**外链 <script src> 标签**，
    # 若只替换占位符注释，就会拼出 `<script><script src=...></script>`——
    # HTML 解析器把外层 script 的内容当纯文本，内层外链**永远不会被加载**
    # （katex.min.js 就此消失，页面零报错但全站公式退化成 LaTeX 源码）。
    # 所以这里整块替换掉 <script> 元素本身。
    def put_block(token, payload):
        pat = re.compile(r"<script>\s*/\*%s\*/\s*</script>" % re.escape(token))
        out, n = pat.subn(lambda m: payload, html)
        if n != 1:
            raise SystemExit("[build] 模板中 <script>/*%s*/</script> 命中 %d 次，期望 1 次"
                             % (token, n))
        return out

    html = put_block("__BANK_JS__", "")
    html = put_block("__KATEX_JS__", "")      # katex 两个外链已在 script_tags 里
    html = put_block("__SCRIPTS__", script_tags)

    for tok in ("__HEAD__", "__BANK_JS__", "__KATEX_JS__", "__SCRIPTS__"):
        if ("/*%s*/" % tok) in html:
            raise SystemExit("[build] 占位符未替换：%s" % tok)

    # 多文件站允许**同源相对路径**引用，但不允许任何外部 http(s) 资源。
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)
    if ext:
        raise SystemExit("[build] index.html 含外部资源引用：%s" % ext[:5])

    # script 元素结构门禁：嵌套脚本标签会让外链静默失效（见 put_block 的注释）。
    # 这条门禁是事故的直接拦路虎——历史上多文件站就是靠它才没把坏产物发出去，
    # 而当时**没有**这道门禁，于是 katex.min.js 丢失却「全绿」。
    from check_html import scan_scripts
    scripts, sproblems = scan_scripts(html)
    if sproblems:
        raise SystemExit("[build] index.html script 结构异常：%s" % sproblems[:4])
    ext_scripts = [s for s in scripts if s["src"]]
    lost = []
    for s in ext_scripts:
        p = os.path.normpath(os.path.join(out, s["src"].split("?")[0]))
        if not os.path.isfile(p):
            lost.append(s["src"])
    if lost:
        raise SystemExit("[build] index.html 引用了不存在的脚本文件：%s" % lost[:8])
    must = ["assets/vendor/katex/katex.min.js",
            "assets/vendor/katex/contrib/auto-render.min.js",
            "assets/js/app.js"]
    srcs = [s["src"] for s in ext_scripts]
    missing_must = [m for m in must if m not in srcs]
    if missing_must:
        raise SystemExit("[build] index.html 未引用必需脚本：%s" % missing_must)
    print("[build] index.html script 结构正常：%d 个外链脚本全部落地"
          % len(ext_scripts))

    write_text(os.path.join(out, "index.html"), html)
    print("[build] 输出目录：%s" % out)

    # ---- 自检：产物里不能有外部引用 ----
    bad_ext = []
    for root, dirs, files in os.walk(out):
        for fn in files:
            if not fn.endswith((".html", ".css", ".js", ".json")):
                continue
            p = os.path.join(root, fn)
            with io.open(p, "r", encoding="utf-8", errors="replace") as f:
                src = f.read()
            for u in re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', src):
                if "mcode.cn" not in u:      # 平台部署后会注入埋点，属宿主行为
                    bad_ext.append("%s -> %s" % (os.path.relpath(p, out), u))
    if bad_ext:
        raise SystemExit("[build] 产物含外部资源引用：%s" % bad_ext[:5])
    print("[build] 产物外部资源引用检查通过（零外部请求）")

    total = 0
    for root, dirs, files in os.walk(out):
        for fn in files:
            total += os.path.getsize(os.path.join(root, fn))
    print("[build] 站点体积：%.2f MB" % (total / 1048576.0))


if __name__ == "__main__":
    main()
