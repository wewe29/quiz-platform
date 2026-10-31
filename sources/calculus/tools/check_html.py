# -*- coding: utf-8 -*-
"""成品 HTML 自检：解析内联题库 JSON + 检查结构 + 定位可疑片段。

用法：
    python tools/check_html.py "<html 路径>"            # 单文件离线包
    python tools/check_html.py "<站点目录>"              # 多文件站点（目录）
    python tools/check_html.py --site "<站点目录>"
    python tools/check_html.py "<html 路径>" --line 332 --col 34468
"""
import io
import json
import os
import re
import sys


def scan_scripts(src):
    """按 HTML 规则解析 <script> 元素，返回 (scripts, problems)。

    scripts: [{'src': str|None, 'body': str}]，按文档顺序
    problems: 结构性问题列表

    为什么必须真正解析、不能数标签：
      HTML 解析器把 <script> 的内容当作 CDATA **纯文本**，
      所以 `<script><script src="x.js"></script>` 这种嵌套写法
      不会触发任何语法错误——外层 script 的内容被当成 JS 源码，
      内层外链**永远不会被加载**。页面表现为「零报错，但公式全是原文」。
      而开闭标签个数是相等的（3 开 3 闭），数个数也看不出问题。

    历史上真实踩过：多文件站构建器把 `<script src=...>` 标签塞进了
    模板里已有的 `<script>/*__SCRIPTS__*/</script>` 内部，
    katex.min.js 从未加载 → 全站公式退化成 LaTeX 源码。
    """
    from html.parser import HTMLParser

    class _Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.scripts = []
            self.problems = []
            self._cur = None

        def handle_starttag(self, tag, attrs):
            if tag != "script":
                return
            if self._cur is not None:
                self.problems.append("<script> 还没闭合就又开了一个（嵌套脚本标签）")
            self._cur = {"src": dict(attrs).get("src"), "body": ""}

        def handle_endtag(self, tag):
            if tag != "script":
                return
            if self._cur is None:
                self.problems.append("多余的 </script>")
                return
            s = self._cur
            self._cur = None
            self.scripts.append(s)

        def handle_data(self, data):
            if self._cur is not None:
                self._cur["body"] += data

    p = _Parser()
    try:
        p.feed(src)
        p.close()
    except Exception as e:
        p.problems.append("HTML 解析失败：%s" % e)
    if p._cur is not None:
        p.problems.append("未闭合的 <script>（缺少 </script>）")
    for s in p.scripts:
        if s["src"] is None and re.search(r"<\s*script[\s>/]", s["body"], re.I):
            p.problems.append("script 元素内容里出现字面量 <script>（嵌套脚本标签）")
    return p.scripts, p.problems


def extract_bank_json(src):
    """从成品 HTML 中抠出 window.__BANK__ 的 JSON 字面量。

    不能用正则：JSON 字符串里含有括号（如 "str(M([...]).inv())"），
    且贪婪匹配会跨过后续 <script> 块。这里按大括号深度扫描，
    同时正确跳过字符串字面量与转义。
    """
    anchor = src.find("window.__BANK__")
    if anchor < 0:
        return None
    i = src.find("{", anchor)
    if i < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(src)):
        c = src[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return None


def check_site(root):
    """多文件站点自检：结构、引用可达性、数据 JSON、外部请求、JS 语法。

    单文件模式只验「一个 HTML 里内联了什么」；多文件站真正的失败模式是
    **引用指不到文件**（相对路径写错、文件漏拷），静态扫不出来，必须逐个解析。
    """
    import shutil
    import subprocess

    errs = []
    index = os.path.join(root, "index.html")
    if not os.path.exists(index):
        return ["站点缺少 index.html：%s" % index]
    src = io.open(index, encoding="utf-8").read()
    print("站点：%s" % root)
    print("index.html：%d 字节" % len(src.encode("utf-8")))

    # 1) 引用可达性
    refs = re.findall(r'(?:src|href)\s*=\s*["\']([^"\'#][^"\']*)["\']', src)
    missing = []
    for r in refs:
        if r.startswith(("http://", "https://", "//", "data:", "mailto:")):
            continue
        p = os.path.normpath(os.path.join(root, r.split("?")[0]))
        if not os.path.exists(p):
            missing.append(r)
    if missing:
        errs.append("引用指不到文件：%s" % missing[:8])
    else:
        print("相对引用全部可达：%d 条" % len(refs))

    # 2) 外部资源引用（零外部请求是硬要求）
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?:)?//[^"\']+', src)
    if ext:
        errs.append("存在外部资源引用：%s" % ext[:5])
    else:
        print("外部资源引用：无")

    # 2b) script 元素结构（嵌套脚本标签会让外链静默失效）
    scripts, sproblems = scan_scripts(src)
    if sproblems:
        errs.append("script 元素结构异常：%s" % sproblems[:4])
    else:
        ext_scripts = [s for s in scripts if s["src"]]
        missing_src = []
        for s in ext_scripts:
            p = os.path.normpath(os.path.join(root, s["src"].split("?")[0]))
            if not os.path.isfile(p):
                missing_src.append(s["src"])
        if missing_src:
            errs.append("script src 指向的文件不存在：%s" % missing_src[:8])
        else:
            print("script 结构：%d 个元素（外链 %d / 内联 %d），全部可达"
                  % (len(scripts), len(ext_scripts), len(scripts) - len(ext_scripts)))

    # 3) 数据 JSON
    data_dir = os.path.join(root, "data")
    idx_path = os.path.join(data_dir, "index.json")
    if not os.path.exists(idx_path):
        errs.append("缺少 data/index.json")
    else:
        idx = json.load(io.open(idx_path, encoding="utf-8"))
        total = 0
        print("index.json：%d 题，%d 章" % (idx.get("total", 0), len(idx.get("chapters", []))))
        if idx.get("total") != sum(c["count"] for c in idx.get("chapters", [])):
            errs.append("index.json 题数与分章计数之和不一致")
        for c in idx.get("chapters", []):
            p = os.path.join(data_dir, c["file"])
            if not os.path.exists(p):
                errs.append("缺分章文件：%s" % c["file"])
                continue
            d = json.load(io.open(p, encoding="utf-8"))
            n = len(d.get("questions", []))
            total += n
            if n != c["count"]:
                errs.append("%s 实际 %d 题 ≠ index 记录 %d 题" % (c["file"], n, c["count"]))
        if total != idx.get("total"):
            errs.append("分章题数之和 %d ≠ index.total %d" % (total, idx.get("total")))
        else:
            print("分章题数核对通过：%d 题" % total)

    # 4) 字体相对路径必须是真存在的文件
    katex_css = os.path.join(root, "assets", "vendor", "katex", "katex.min.css")
    if os.path.exists(katex_css):
        css = io.open(katex_css, encoding="utf-8").read()
        fonts = set(re.findall(r"url\(fonts/([^)]+)\)", css))
        fdir = os.path.join(root, "assets", "vendor", "katex", "fonts")
        gone = [f for f in sorted(fonts) if not os.path.exists(os.path.join(fdir, f))]
        if gone:
            errs.append("KaTeX CSS 引用了不存在的字体：%s" % gone[:5])
        else:
            print("KaTeX 字体引用全部可达：%d 个" % len(fonts))

    # 5) JS 语法
    node = shutil.which("node") or shutil.which("node.exe")
    if node:
        bad = 0
        checked = 0
        for root_dir, dirs, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".js"):
                    continue
                p = os.path.join(root_dir, fn)
                rel = os.path.relpath(p, root)
                if rel.startswith("assets\\vendor") or rel.startswith("assets/vendor"):
                    continue    # 第三方压缩产物不重复检查
                checked += 1
                r = subprocess.run([node, "--check", p], capture_output=True)
                if r.returncode != 0:
                    bad += 1
                    err = r.stderr.decode("utf-8", "replace").strip().splitlines()
                    msg = next((x for x in err if "Error" in x), err[-1] if err else "?")
                    errs.append("JS 语法错误 %s：%s" % (rel, msg.strip()))
        print("自研 JS：%d 个文件，语法错误 %d" % (checked, bad))
    else:
        print("未找到 node，跳过 JS 语法检查")

    print("-" * 60)
    if errs:
        print("发现 %d 个问题：" % len(errs))
        for e in errs:
            print("  [FAIL] %s" % e)
        return errs
    print("站点自检通过。")
    return errs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    if os.path.isdir(path) or "--site" in sys.argv:
        target = path if os.path.isdir(path) else sys.argv[sys.argv.index("--site") + 1]
        errs = check_site(target)
        return 1 if errs else 0
    if not os.path.exists(path):
        print("文件不存在：%s" % path)
        return 2
    src = io.open(path, encoding="utf-8").read()
    print("文件：%s" % path)
    print("大小：%d 字节（%.2f MB）" % (len(src.encode("utf-8")), len(src.encode("utf-8")) / 1048576.0))
    print("行数：%d" % (src.count("\n") + 1))

    errs = []

    # ---- 1) 内联题库 JSON ----
    raw = extract_bank_json(src)
    if raw is None:
        errs.append("未找到 window.__BANK__ 赋值块")
    else:
        # 除了 JSON 本身合法，还必须检查它后面的 JS 收尾是否合法。
        # 只验 JSON 会漏掉「{json}{}」这类多出一段字面量的情况——
        # 那种情况下 JSON 本身能解析，但整段脚本是 SyntaxError，页面静默变成 0 题。
        tail_start = src.find(raw, src.find("window.__BANK__")) + len(raw)
        tail = src[tail_start:src.find("</script>", tail_start)]
        if not re.fullmatch(r"\s*\)?\s*;\s*", tail):
            errs.append("题库赋值块尾部不是合法 JS（应只剩 `;` 或 `);`），实际为：%r" % tail[:80])
        else:
            print("题库赋值块尾部：%r" % tail.strip())
        print("题库 JSON 片段长度：%d" % len(raw))
        try:
            bank = json.loads(raw)
            qs = bank.get("questions", [])
            print("JSON 解析成功：id=%s，题目 %d 道" % (bank.get("id"), len(qs)))
            types = {}
            for q in qs:
                types[q["typeGroup"]] = types.get(q["typeGroup"], 0) + 1
            print("题型分布：%s" % types)
        except Exception as e:
            errs.append("题库 JSON 解析失败：%s" % e)
            # 定位出错位置
            try:
                json.loads(raw)
            except json.JSONDecodeError as je:
                pos = je.pos
                print("JSON 错误位置 %d（行 %d 列 %d）" % (pos, raw.count("\n", 0, pos) + 1, pos))
                print("上下文：%r" % raw[max(0, pos - 160):pos + 160])

    # ---- 2) 外部资源引用 ----
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?:)?//[^"\']+', src)
    if ext:
        errs.append("存在外部资源引用：%s" % ext[:5])
    else:
        print("外部资源引用：无")

    # ---- 3) 残留相对路径字体 ----
    if re.search(r"url\(\s*fonts/", src):
        errs.append("仍有未内联的 fonts/ 相对路径")
    else:
        print("fonts/ 相对路径：无")

    # ---- 4) script/style 配对 ----
    ns = len(re.findall(r"<script\b", src))
    ne = len(re.findall(r"</script>", src))
    nstyle = len(re.findall(r"<style\b", src))
    nstylee = len(re.findall(r"</style>", src))
    print("<script>：%d 开 / %d 闭" % (ns, ne))
    print("<style>：%d 开 / %d 闭" % (nstyle, nstylee))
    if ns != ne:
        errs.append("script 标签未配对")
    if nstyle != nstylee:
        errs.append("style 标签未配对")

    # ---- 4b) script 元素结构 + 关键库是否真的在页面里 ----
    scripts, sproblems = scan_scripts(src)
    if sproblems:
        errs.append("script 元素结构异常：%s" % sproblems[:4])
    else:
        bodies = "\n".join(s["body"] for s in scripts if s["src"] is None)
        need = {
            "KaTeX 主库": "katex",
            "KaTeX auto-render": "renderMathInElement",
            "题库数据": "window.__BANK__",
        }
        for label, token in need.items():
            if token not in bodies:
                errs.append("内联脚本里找不到 %s（关键字 %s）" % (label, token))
        if not any(s["src"] is None and "window.__BANK__" in s["body"] for s in scripts):
            errs.append("没有独立的 window.__BANK__ 赋值脚本块")
        print("script 元素：%d 个（内联 %d），关键库齐全"
              % (len(scripts), len([s for s in scripts if s["src"] is None])))

    # ---- 4c. 单文件包必须把内联题库交给 bank ----
    # 没接线时 hasInline() 恒为 false → 误走 fetch('data/index.json') →
    # 离线双击打开必然 404，页面只剩「题库载入失败」，而且零报错。
    wired = any(s["src"] is None
                and re.search(r"setInline\(\s*window\.__BANK__\s*\)", s["body"])
                for s in scripts)
    if not wired:
        errs.append("单文件包没有把 window.__BANK__ 交给 bank.setInline(...)："
                    "内联模式不生效，页面会去 fetch data/index.json 并 404")
    else:
        print("内联题库接线：已找到 bank.setInline(window.__BANK__)")

    # ---- 5) base64 字体数量 ----
    fonts = re.findall(r"url\(data:font/woff2;base64,", src)
    print("内联 woff2 字体：%d 个" % len(fonts))

    # ---- 6) 占位符残留 ----
    for tok in ("__APP_CSS__", "__KATEX_CSS__", "__BANK__", "__KATEX_JS__",
                "__AUTORENDER_JS__", "__APP_JS__", "__HEAD__", "__BANK_JS__",
                "__SCRIPTS__"):
        if ("/*%s*/" % tok) in src:
            errs.append("占位符未替换：%s" % tok)

    # ---- 7) 可选：按行列定位片段 ----
    if "--line" in sys.argv:
        li = int(sys.argv[sys.argv.index("--line") + 1])
        col = int(sys.argv[sys.argv.index("--col") + 1]) if "--col" in sys.argv else 0
        lines = src.split("\n")
        if 1 <= li <= len(lines):
            L = lines[li - 1]
            print("--- line %d (len=%d) around col %d ---" % (li, len(L), col))
            print(repr(L[max(0, col - 200):col + 200]))

    # ---- 8) 内联 JS 语法检查（node --check，只解析不执行）----
    import shutil
    import subprocess
    node = shutil.which("node") or shutil.which("node.exe")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", src, re.S)
    if node:
        bad = 0
        for i, body in enumerate(scripts):
            if not body.strip():
                continue
            r = subprocess.run([node, "--check", "-"], input=body.encode("utf-8"),
                               capture_output=True)
            if r.returncode != 0:
                bad += 1
                err = r.stderr.decode("utf-8", "replace").strip().splitlines()
                msg = next((x for x in err if "Error" in x), err[-1] if err else "?")
                errs.append("内联脚本 #%d JS 语法错误：%s" % (i + 1, msg.strip()))
        print("内联 JS 脚本：%d 段，语法错误 %d" % (len(scripts), bad))
    else:
        print("未找到 node，跳过 JS 语法检查")

    print("-" * 60)
    if errs:
        print("发现 %d 个问题：" % len(errs))
        for e in errs:
            print("  [FAIL] %s" % e)
        return 1
    print("成品自检通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
