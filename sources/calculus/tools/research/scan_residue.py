# -*- coding: utf-8 -*-
r"""扫描已生成题库模块里的 Typst/LaTeX 残留记号，统计分布。"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)

from qa_bank.common import load_bank  # noqa: E402

PATTERNS = [
    ("mi()", r"#mi\("),
    ("mitex()", r"#mitex\("),
    ("align()", r"#align\("),
    ("emoji/other call", r"#(?!problem|choices|answer|solution|blank)[a-zA-Z]+\("),
    ("hash generic", r"#[a-zA-Z]"),
    ("\\bold(", r"\\bold\("),
    ("\\mathbf no-brace", r"\\mathbf\s+[A-Za-z]"),
    ("\\triangleA", r"\\triangle[A-Za-z]"),
    ("angleA", r"\\angle[A-Za-z]"),
    ("brace-word", r"_\{\s*[A-Za-z]+[A-Za-z]"),
    ("bracket-wrapped", r"^\s*\[.+\]\s*$"),
    ("backtick", r"`"),
    ("dollar odd", r"(?<!\\)\$"),
    ("mat/paren func", r"\\(mat|det|vec|abs|sqrt|frac|binom)\("),
    ("tilde~", r"~"),
]


def main():
    bank = load_bank()
    cnt = collections.Counter()
    samples = collections.defaultdict(list)
    for q in bank:
        parts = {
            "stem": q.get("stem") or "",
            "expl": q.get("expl") or "",
            "answer_text": q.get("answer_text") or "",
        }
        for i, o in enumerate(q.get("options") or []):
            parts["opt%d" % i] = o
        for name, txt in parts.items():
            for label, pat in PATTERNS:
                if label == "dollar odd":
                    if txt.count("$") % 2:
                        cnt[label] += 1
                        if len(samples[label]) < 6:
                            samples[label].append((q.get("id"), name, txt[:110]))
                    continue
                if label == "bracket-wrapped":
                    continue
                if re.search(pat, txt):
                    cnt[label] += 1
                    if len(samples[label]) < 6:
                        samples[label].append((q.get("id"), name, txt[:110]))
    print("题库总量：%d" % len(bank))
    for label, _ in PATTERNS:
        print("  %-18s %d" % (label, cnt.get(label, 0)))
    print()
    for label in [l for l, _ in PATTERNS if cnt.get(l)]:
        print("== %s ==" % label)
        for qid, where, txt in samples[label]:
            print("   %s [%s] %s" % (qid, where, txt.replace("\n", "\\n")))
        print()


if __name__ == "__main__":
    raise SystemExit(main())
