"""逐字段对比「源码题库」与「成品 HTML 内联题库」。

为什么要这个脚本：浏览器里判分与源码逻辑对不上时，必须先回答
「成品里到底是什么」，而不是相信 .py 源码或自己的记忆。
任何差异都会打印出来——构建环节最容易悄悄改字段。

用法：python diff_bank.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_bank import load_bank  # noqa: E402

# 成品路径相对脚本定位（脚本在 tools/ 内，成品在其上一级）——
# 不写绝对路径，CI/异机也能跑。可用环境变量覆盖（平台构建复用时指到别处）。
HTML = os.environ.get("QUIZ_HTML") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "01《线性代数》题库刷题网页.html"))

FIELDS = ["type", "difficulty", "knowledgePoint", "stem", "options", "answer",
          "accept", "answerText", "points", "explanation", "misconception", "extension"]


def extract_built(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.__BANK__\s*=", src)
    if not m:
        sys.exit("未找到 window.__BANK__")
    i = src.index("{", m.end())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                break
    return json.loads(src[i:j + 1])


def main():
    src_qs = load_bank()
    built = extract_built(HTML)
    built_qs = built["questions"] if isinstance(built, dict) and "questions" in built else built

    src_by = {q["id"]: q for q in src_qs}
    built_by = {q["id"]: q for q in built_qs}

    print("源码题数 :", len(src_by))
    print("成品题数 :", len(built_by))
    only_src = sorted(set(src_by) - set(built_by))
    only_built = sorted(set(built_by) - set(src_by))
    if only_src:
        print("!! 只在源码中:", only_src)
    if only_built:
        print("!! 只在成品中:", only_built)

    diffs = 0
    for qid in sorted(set(src_by) & set(built_by)):
        s, b = src_by[qid], built_by[qid]
        for f in FIELDS:
            sv, bv = s.get(f), b.get(f)
            if sv == bv:
                continue
            diffs += 1
            print("\n--- 差异 %s . %s" % (qid, f))
            print("  源码:", repr(sv)[:220])
            print("  成品:", repr(bv)[:220])
    print("\n" + "=" * 60)
    print("字段差异总数：", diffs)
    if diffs == 0:
        print("✅ 源码与成品逐字段完全一致")
        return 0
    print("❌ 存在差异，见上")
    return 1


if __name__ == "__main__":
    sys.exit(main())
