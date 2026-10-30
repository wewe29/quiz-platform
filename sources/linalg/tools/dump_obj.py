"""按题型批量导出客观题（题干/选项/答案/解析），供人工逐题核验答案键。

用法：
    python dump_obj.py --type=single --from=1 --to=30
    python dump_obj.py --type=judge --from=1 --to=30
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_bank import load_bank  # noqa: E402


def main():
    args = sys.argv[1:]
    ty = None
    lo = 1
    hi = 999
    for a in args:
        if a.startswith("--type="):
            ty = a.split("=", 1)[1]
        if a.startswith("--from="):
            lo = int(a.split("=", 1)[1])
        if a.startswith("--to="):
            hi = int(a.split("=", 1)[1])
    sel = [q for q in load_bank() if (ty is None or q["type"] == ty)]
    for q in sel[lo - 1:hi]:
        print("-" * 70)
        print("%s [%s/%s]  answer=%s" % (q["id"], q["type"], q["difficulty"], q["answer"]))
        print("题干: %s" % (q["stem"] or "").replace("\n", " "))
        for i, o in enumerate(q.get("options") or []):
            print("   %s. %s" % ("ABCDE"[i], o))
        print("解析: %s" % (q["explanation"] or "").replace("\n", " ⏎ "))


if __name__ == "__main__":
    main()
