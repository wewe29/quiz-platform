# -*- coding: utf-8 -*-
"""成品 HTML 自检：解析内联题库 JSON + 检查结构 + 定位可疑片段。

用法：
    python tools/check_html.py "<html 路径>"
    python tools/check_html.py "<html 路径>" --line 332 --col 34468
"""
import io
import json
import os
import re
import sys


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


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
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

    # ---- 5) base64 字体数量 ----
    fonts = re.findall(r"url\(data:font/woff2;base64,", src)
    print("内联 woff2 字体：%d 个" % len(fonts))

    # ---- 6) 占位符残留 ----
    for tok in ("__APP_CSS__", "__KATEX_CSS__", "__BANK__", "__KATEX_JS__",
                "__AUTORENDER_JS__", "__APP_JS__"):
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
