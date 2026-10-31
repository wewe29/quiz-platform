# -*- coding: utf-8 -*-
r"""LaTeX 公式合法性复核（KaTeX 门禁）。

真题公式是从 Typst 转写来的，转写规则可能有漏。
这道门禁把题库里所有 $...$ 公式抠出来，交给本地 KaTeX 逐条渲染，
渲染失败即视为题目损坏——宁可少一道题，不许页面显示一个红叉公式。

用法：
    python tools/research/check_latex.py            # 检查当前题库
    python tools/research/check_latex.py --quiet
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MATH = re.compile(r"\$\$(.+?)\$\$|\$([^$]+)\$", re.S)


def formulas_of(q):
    out = []
    fields = [q.get("stem") or "", q.get("answerText") or "", q.get("explanation") or "",
              q.get("misconception") or ""]
    fields += list(q.get("options") or [])
    fields += [p.get("text", "") if isinstance(p, dict) else str(p) for p in (q.get("points") or [])]
    fields += list(q.get("accept") or [])
    for f in fields:
        if not f:
            continue
        for m in MATH.finditer(f):
            tex = m.group(1) or m.group(2) or ""
            tex = tex.strip()
            if tex:
                out.append(tex)
    return out


def main():
    quiet = "--quiet" in sys.argv
    from qa_bank import load_bank
    questions = load_bank()
    items = []
    for q in questions:
        fs = formulas_of(q)
        if fs:
            items.append({"id": q["id"], "formulas": fs})
    tmp = os.path.join(HERE, "_latex_input.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)

    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        print("[latex] 未找到 node，跳过 KaTeX 复核")
        return 0
    script = os.path.join(HERE, "katex_check.js")
    result_path = os.path.join(HERE, "_latex_result.json")
    r = subprocess.run([node, script, tmp, result_path], capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if not quiet:
        print(out.strip())
        if err.strip():
            print(err.strip())
    # katex_check.js 把 JSON 结果写进 _latex_result.json（stdout 是人类可读摘要），
    # 这里必须读文件，不能去解析 stdout。
    try:
        with open(result_path, encoding="utf-8") as f:
            res = json.load(f)
    except Exception as e:
        print("[latex] 读取 KaTeX 结果失败：%s" % e)
        res = {}
    bad_ids = sorted({b["id"] for b in (res.get("bad") or [])})
    with open(os.path.join(HERE, "_latex_bad_ids.json"), "w", encoding="utf-8") as f:
        json.dump(bad_ids, f, ensure_ascii=False, indent=1)
    if not quiet:
        print("[latex] 涉及题目 %d 道（名单已写入 _latex_bad_ids.json）" % len(bad_ids))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
