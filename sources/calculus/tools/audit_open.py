"""主观题（简答/计算/名词解释）结构审计 + SymPy 复核覆盖率统计。

检查项：
  · 采分点个数是否符合约定
      —— 教材题：固定表（short 3 点 / calc 4 点 / term 2 点），满分 6/8/4
      —— 真题（exam-original）：按解析实际步骤数取 1–6 点，每点 2 分，
         满分 = 2 × 点数（前端 judge.fullScore 就是按 partial 求和，口径自洽）
  · 每点分值合计是否等于该题满分
  · 采分点文本、参考答案文本是否为空
  · 采分点里是否残留 LaTeX 定界符 $ 或未闭合的花括号
  · 采分点是否出现重复（复制同一段来凑数会让「采分点自评」变成假选择）
  · verify 条目按题型的覆盖分布（回答「哪些数字结论被机器重算过」）

用法：python audit_open.py
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "research"))
from qa_bank import load_bank  # noqa: E402
from points import latex_braces_unbalanced  # noqa: E402

WANT_POINTS = {"short": 3, "calc": 4, "term": 2}
FULL = {"short": 6, "calc": 8, "term": 4}
# 真题主观题：采分点数按解析实际步骤数，上限 6；每点 2 分
EXAM_MAX_POINTS = 6
EXAM_PARTIAL = 2


def check(questions=None):
    """返回 (问题清单, 统计)。供构建门禁直接调用。"""
    if questions is None:
        questions = load_bank()
    errs = []
    vc = Counter()
    types = Counter()
    for q in questions:
        t = q["type"]
        if t not in WANT_POINTS:
            continue
        types[t] += 1
        pts = q.get("points") or []
        is_exam = (q.get("source") or {}).get("kind") == "exam-original"
        if is_exam:
            if not (1 <= len(pts) <= EXAM_MAX_POINTS):
                errs.append("%s 采分点数 %d，应为 1–%d" % (q["id"], len(pts), EXAM_MAX_POINTS))
            want_full = EXAM_PARTIAL * len(pts)
        else:
            if len(pts) != WANT_POINTS[t]:
                errs.append("%s 采分点数 %d，应为 %d" % (q["id"], len(pts), WANT_POINTS[t]))
            want_full = FULL[t]
        total = 0
        texts = []
        for i, p in enumerate(pts):
            text = p.get("text") if isinstance(p, dict) else str(p)
            texts.append((text or "").strip())
            if not (text or "").strip():
                errs.append("%s 第 %d 个采分点文本为空" % (q["id"], i + 1))
            partial = p.get("partial", 2) if isinstance(p, dict) else 2
            total += partial
            # 注意：采分点里的 $…$ 是**正确的**（页面上会交给 KaTeX 渲染），
            # 这里只查「$ 个数为奇数」和「花括号不配对」这两类真损坏。
            if (text or "").count("$") % 2:
                errs.append("%s 第 %d 个采分点的 $ 定界符个数为奇数" % (q["id"], i + 1))
            # LaTeX 感知的花括号检查：\left\{ … \right. 这类定界符指令
            # 在源码里本来就少一个 }，朴素计数会误报。
            if latex_braces_unbalanced(text):
                errs.append("%s 第 %d 个采分点花括号不配对" % (q["id"], i + 1))
            # 复制同一段来凑数 → 采分点自评会变成假选择
            if re.fullmatch(r"\$\$(\s*)\$\$", (text or "").strip()):
                errs.append("%s 第 %d 个采分点是空壳" % (q["id"], i + 1))
        if len(set(texts)) != len(texts):
            errs.append("%s 采分点里有重复（复制凑数）" % q["id"])
        if total != want_full:
            errs.append("%s 采分点合计 %d 分，该题满分 %d 分" % (q["id"], total, want_full))
        if not (q.get("answerText") or "").strip():
            errs.append("%s 参考答案为空" % q["id"])
        v = q.get("verify") or []
        vc[t] += len(v)
        if v:
            vc["_q_with_verify"] += 1
    return errs, {"types": dict(types), "verify": {k: v for k, v in vc.items() if not k.startswith("_")}}


def main():
    errs, stats = check()
    print("主观题统计：", stats["types"])
    print("SymPy 复核条目按题型：", stats["verify"])
    print()
    if errs:
        print("发现问题 %d 处：" % len(errs))
        for e in errs[:60]:
            print("  ⚠ " + e)
        if len(errs) > 60:
            print("  …（其余 %d 处省略）" % (len(errs) - 60))
        return 1
    print("✅ 主观题结构全部合规（采分点数/分值合计/文本非空/无重复/无残留定界符）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
