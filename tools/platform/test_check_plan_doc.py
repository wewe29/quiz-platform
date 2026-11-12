# -*- coding: utf-8 -*-
r"""check_plan_doc 的反向测试：**造错必须报错**，好的时候不得误报。

用法：python tools/platform/test_check_plan_doc.py      （失败时退出码非 0）

为什么要有这道测试：
    方案文档是交付说明的正本，它写着题量与 dist 体积。
    门禁自己也得证明**它真的会红**、且**不误报历史陈述**——
    「三学科 170 题渲染截断（线代 108 / 高数 53 / 概率论 9）」是历史，
    不是现状断言，门禁必须放它过去。
"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import check_plan_doc as cpd  # noqa: E402

DOC = os.path.join(PLATFORM, cpd.DOC_REL)
REGISTRY = os.path.join(PLATFORM, "subjects", "registry.json")
DIST = os.path.join(PLATFORM, "dist")

failures = []


def check(name, ok, detail=""):
    if ok:
        print("  [PASS] %s" % name)
    else:
        print("  [FAIL] %s%s" % (name, ("  ← " + detail) if detail else ""))
        failures.append(name)


def _mutate(text, old, new):
    if old not in text:
        raise SystemExit("[test] 造错失败：找不到 %r" % old)
    return text.replace(old, new, 1)


def _run(tmp, name, text):
    p = os.path.join(tmp, name)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return cpd.check(p, REGISTRY, DIST)


def main():
    print("[test] 方案文档事实门禁 · 反向测试")
    if not os.path.isfile(REGISTRY):
        print("[FAIL] 缺 registry.json，先跑 build_all.py")
        return 1
    with io.open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    total = sum(int(s["total"]) for s in reg["subjects"])
    with io.open(DOC, encoding="utf-8") as f:
        good = f.read()

    tmp = tempfile.mkdtemp(prefix="plandoc-")
    try:
        # T0 正例
        errs = cpd.check(DOC, REGISTRY, DIST)
        check("T0 正确的文档不误报", not errs, "errors=%r" % errs[:3])

        # T1 总题数写错
        errs = _run(tmp, "t1.md", _mutate(good, "%d 题" % total, "%d 题" % (total + 7)))
        check("T1 总题数写错被拦下", any("题" in e for e in errs), "errors=%r" % errs[:3])

        # T2 逐学科题量写错（概率统计 156 → 100，正是 2026-11-13 实测到的那处腐烂）
        errs = _run(tmp, "t2.md", _mutate(good, "概率统计 156", "概率统计 100"))
        check("T2 逐学科题量写错被拦下", any("概率统计" in e for e in errs), "errors=%r" % errs[:3])

        # T3 dist 文件数写错
        n_real = sum(len(f) for _, _, f in os.walk(DIST))
        errs = _run(tmp, "t3.md", _mutate(good, "%d 文件" % n_real, "%d 文件" % (n_real + 3)))
        check("T3 dist 文件数写错被拦下", any("文件" in e for e in errs), "errors=%r" % errs[:3])

        # T4 dist 体积写错
        errs = _run(tmp, "t4.md", _mutate(good, "MB；题量见", "MB；题量见"))
        # 体积数字用正则定位更稳：直接把 "8.15 MB" 改成 "9.99 MB"
        import re
        mb = re.search(r"([\d.]+) MB；题量见", good)
        if mb:
            errs = _run(tmp, "t4.md", _mutate(good, mb.group(1) + " MB；题量见", "9.99 MB；题量见"))
            check("T4 dist 体积写错被拦下", any("MB" in e for e in errs), "errors=%r" % errs[:3])
        else:
            check("T4 dist 体积写错被拦下", False, "文档里找不到体积断言")

        # T5 断言整体消失 → 必须报错（不允许「找不到就默认通过」）
        #    把全文的「学科」换成「科目」：所有「N 学科 … M 题」断言一起消失
        stripped = good.replace("学科", "科目")
        errs = _run(tmp, "t5.md", stripped)
        check("T5 断言缺失被拦下", any("找不到" in e for e in errs), "errors=%r" % errs[:3])

        # T6 历史陈述的括号（只列 3 学科）不得误报
        errs = cpd.check(DOC, REGISTRY, DIST)
        check("T6 历史括号不误报", not any("线代 108" in e for e in errs), "errors=%r" % errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 60)
    if failures:
        print("方案文档门禁自检 FAIL：%d 项 -> %s" % (len(failures), ", ".join(failures)))
        return 1
    print("方案文档门禁自检全绿。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
