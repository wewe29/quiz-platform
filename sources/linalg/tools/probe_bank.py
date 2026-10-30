"""从成品 HTML 里抽出内联题库 JSON，查看指定题号的原始字段形态。

用途：浏览器行为与源码逻辑对不上时，先看「成品里到底是什么」，
     而不是看 .py 源码里以为的样子（构建环节可能改写字段）。
用法：python probe_bank.py [题号，如 q-010]
"""
import json
import re
import sys

HTML = r"D:\workspace\5-docs\线性代数复习资料\01《线性代数》题库刷题网页.html"

with open(HTML, encoding="utf-8") as f:
    src = f.read()

m = re.search(r"window\.__BANK__\s*=", src)
if not m:
    sys.exit("未找到 window.__BANK__ 赋值")

i = src.index("{", m.end())
depth = 0
for j in range(i, len(src)):
    if src[j] == "{":
        depth += 1
    elif src[j] == "}":
        depth -= 1
        if depth == 0:
            break
bank = json.loads(src[i:j + 1])

qs = bank["questions"] if isinstance(bank, dict) and "questions" in bank else bank
by_id = {q["id"]: q for q in qs}

want = sys.argv[1] if len(sys.argv) > 1 else "q-010"
q = by_id[want]
print("题号 :", q["id"], "| 题型:", q.get("type"))
print("answer        :", repr(q.get("answer")), "->", type(q.get("answer")).__name__)
print("answerText    :", repr(q.get("answerText"))[:120])
print("options       :", repr(q.get("options"))[:200])
print("points        :", repr(q.get("points"))[:200])
print()
print("=== 该题 answer 归一化检查 ===")
ans = q.get("answer")
if isinstance(ans, str):
    print("⚠ answer 是字符串，不是数组 —— multiVerdict 里的 answer.slice().sort() 会抛 TypeError")
elif isinstance(ans, list):
    print("✔ answer 是数组，元素类型:", sorted({type(x).__name__ for x in ans}))
    print("  排序拼接结果:", ",".join(sorted(ans)))
