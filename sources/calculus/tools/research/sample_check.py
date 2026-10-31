# -*- coding: utf-8 -*-
"""抽检：从题库里随机抽几道真题，打印生成结果，用于人工对照源文件。"""
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank import load_bank


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    qs = load_bank()
    exam = [q for q in qs if q["source"]["kind"] != "textbook"]
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    picks = random.sample(exam, min(n, len(exam)))
    for q in picks:
        print("=" * 72)
        print("id       :", q["id"])
        print("知识点  :", q["knowledgePoint"], "|", q["source"]["text"])
        print("出处    :", q["source"]["year"], q["source"]["region"], q["source"]["paper"], "第", q["source"]["number"], "题")
        print("链接    :", q["source"]["url"])
        print("题型    :", q["type"], "| 难度:", q["difficulty"])
        print("题干    :", q["stem"][:400])
        if q["options"]:
            for i, o in enumerate(q["options"]):
                print("   %s. %s" % ("ABCD"[i], o[:150]))
        print("答案    :", q["answer"])
        if q.get("answerText"):
            print("参考    :", q["answerText"][:220].replace("\n", " / "))
        print("解析    :", (q["explanation"] or "")[:260].replace("\n", " / "))


if __name__ == "__main__":
    main()
