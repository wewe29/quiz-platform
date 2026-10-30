"""主观题（简答/计算/名词解释）结构审计 + SymPy 复核覆盖率统计。

检查项：
  · 采分点个数是否符合题型约定（short 3 点、calc 4 点、term 2 点）
  · 每点分值合计是否等于该题满分（short 6、calc 8、term 4）
  · 采分点文本、参考答案文本是否为空
  · 采分点里是否残留 LaTeX 定界符 $ 或未闭合的花括号
  · verify 条目按题型的覆盖分布（回答「哪些数字结论被机器重算过」）

用法：python audit_open.py
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_bank import load_bank  # noqa: E402

WANT_POINTS = {"short": 3, "calc": 4, "term": 2}
FULL = {"short": 6, "calc": 8, "term": 4}


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
        if len(pts) != WANT_POINTS[t]:
            errs.append("%s 采分点数 %d，应为 %d" % (q["id"], len(pts), WANT_POINTS[t]))
        total = 0
        for i, p in enumerate(pts):
            text = p.get("text") if isinstance(p, dict) else str(p)
            if not (text or "").strip():
                errs.append("%s 第 %d 个采分点文本为空" % (q["id"], i + 1))
            partial = p.get("partial", 2) if isinstance(p, dict) else 2
            total += partial
            # 注意：采分点里的 $…$ 是**正确的**（页面上会交给 KaTeX 渲染），
            # 这里只查「$ 个数为奇数」和「花括号不配对」这两类真损坏。
            if (text or "").count("$") % 2:
                errs.append("%s 第 %d 个采分点的 $ 定界符个数为奇数" % (q["id"], i + 1))
            if (text or "").count("{") != (text or "").count("}"):
                errs.append("%s 第 %d 个采分点花括号不配对" % (q["id"], i + 1))
        if total != FULL[t]:
            errs.append("%s 采分点合计 %d 分，该题满分 %d 分" % (q["id"], total, FULL[t]))
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
        for e in errs:
            print("  ⚠ " + e)
        return 1
    print("✅ 主观题结构全部合规（采分点数/分值合计/文本非空/无残留定界符）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
