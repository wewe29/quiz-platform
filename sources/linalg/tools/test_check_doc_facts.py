# -*- coding: utf-8 -*-
r"""check_doc_facts 的反向测试：**造错必须报错**，好的时候不得误报。

用法：python tools/test_check_doc_facts.py      （失败时退出码非 0）

为什么要有这道测试：
    交付文档的数字一旦和产物对不上，托管方照着文档去核对就会得到错误结论。
    这道门禁自己也得证明**它真的会红**——否则就是又一个「看着很严、其实没牙」的检查。

**造错必须落在门禁真正读的那一节里**（同一串数字在 §0 渠道表与 §1 现状速查里都出现，
改错地方等于没改 —— 2026-11-13 写这道测试时就被这个绊了一次：改的是 §0 的字节数，
门禁读的是 §1 的行，于是「没报错」，是**测试写错了**，不是门禁不灵）。
"""
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_doc_facts as cdf  # noqa: E402

ROOT = os.path.dirname(HERE)
DOC = os.path.join(ROOT, cdf.DOC_NAME)
S0 = "## 0. 部署渠道"
S1 = "## 1. 现状速查"

failures = []


def check(name, ok, detail=""):
    if ok:
        print("  [PASS] %s" % name)
    else:
        print("  [FAIL] %s%s" % (name, ("  ← " + detail) if detail else ""))
        failures.append(name)


def _product():
    for name in cdf.PRODUCT_CANDIDATES:
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            return p
    raise SystemExit("[test] 找不到成品")


def _bank():
    from qa_bank import load_bank
    return load_bank()


def _mutate_in(text, section, old, new):
    """只在该小节内替换第一处 old→new。"""
    i = text.find(section)
    if i < 0:
        raise SystemExit("[test] 找不到小节 %r" % section)
    j = text.find("\n## ", i + len(section))
    end = j if j > 0 else len(text)
    scope = text[i:end]
    if old not in scope:
        raise SystemExit("[test] 造错失败：%s 里找不到 %r" % (section, old))
    return text[:i] + scope.replace(old, new, 1) + text[end:]


def _run(tmp, name, text, product, bank):
    p = os.path.join(tmp, name)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return cdf.check(p, product, bank)


def main():
    print("[test] 交付文档事实门禁 · 反向测试")
    product = _product()
    bank = _bank()
    with io.open(DOC, encoding="utf-8") as f:
        good = f.read()
    real_size = format(os.path.getsize(product), ",")

    tmp = tempfile.mkdtemp(prefix="docfacts-")
    try:
        # T0 正例：原文档不得误报
        errs = cdf.check(DOC, product, bank)
        check("T0 正确的文档不误报", not errs, "errors=%r" % errs[:3])

        # T1 §1 本地成品字节数写错
        errs = _run(tmp, "t1.md", _mutate_in(good, S1, real_size + " 字节", "1,000,000 字节"), product, bank)
        check("T1 §1 字节数写错被拦下", any("字节" in e for e in errs), "errors=%r" % errs[:3])

        # T2 §1 SHA256 写错
        errs = _run(tmp, "t2.md", _mutate_in(good, S1, "ED06E78B0AC2C7FC", "DEADBEEFDEADBEEF"), product, bank)
        check("T2 §1 SHA256 写错被拦下", any("SHA256" in e for e in errs), "errors=%r" % errs[:3])

        # T3 §1 题量写错
        errs = _run(tmp, "t3.md", _mutate_in(good, S1, "**528 题**", "**530 题**"), product, bank)
        check("T3 §1 题量写错被拦下", any("题量" in e for e in errs), "errors=%r" % errs[:3])

        # T4 §1 难度分布写错
        errs = _run(tmp, "t4.md", _mutate_in(good, S1, "基础 247 / 中等 179 / 困难 102",
                                              "基础 247 / 中等 180 / 困难 102"), product, bank)
        check("T4 §1 难度分布写错被拦下", any("难度分布" in e for e in errs), "errors=%r" % errs[:3])

        # T5 §1 题型分布写错
        errs = _run(tmp, "t5.md", _mutate_in(good, S1, "单选 89 / 多选 83", "单选 88 / 多选 83"), product, bank)
        check("T5 §1 题型分布写错被拦下", any("题型分布" in e for e in errs), "errors=%r" % errs[:3])

        # T6 §1 mcode 埋块数与「多 N 字节」不自洽
        errs = _run(tmp, "t6.md", _mutate_in(good, S1, "（多 1,523＝宿主埋点）", "（多 9,999＝宿主埋点）"),
                    product, bank)
        check("T6 §1 埋块数不自洽被拦下", any("不自洽" in e for e in errs), "errors=%r" % errs[:3])

        # T7 §1 整行删掉（不允许「找不到就默认通过」）
        i = good.find(S1)
        j = good.find("\n## ", i + len(S1))
        scope = good[i:j]
        stripped = good[:i] + "\n".join(l for l in scope.splitlines()
                                         if "本地成品大小" not in l) + good[j:]
        errs = _run(tmp, "t7.md", stripped, product, bank)
        check("T7 §1 断言行缺失被拦下", any("找不到" in e for e in errs), "errors=%r" % errs[:3])

        # T8 §1 Pages 线上字节与本地产物不一致
        errs = _run(tmp, "t8.md", _mutate_in(good, S1, "GitHub Pages 线上 **%s 字节" % real_size,
                                              "GitHub Pages 线上 **1,600,000 字节"), product, bank)
        check("T8 §1 Pages 字节不符被拦下", any("Pages" in e for e in errs), "errors=%r" % errs[:3])

        # T9 §0 Pages 线上字节写错
        errs = _run(tmp, "t9.md", _mutate_in(good, S0, "%s 字节" % real_size, "1,111,111 字节"),
                    product, bank)
        check("T9 §0 Pages 字节写错被拦下", any("§0" in e for e in errs), "errors=%r" % errs[:3])

        # T10 §0 mcode 行内部不自洽（线上 − 本地 ≠ 文中埋块）
        errs = _run(tmp, "t10.md", _mutate_in(good, S0, "+ **1,523**", "+ **9,999**"), product, bank)
        check("T10 §0 埋块数不自洽被拦下", any("不自洽" in e for e in errs), "errors=%r" % errs[:3])

        # T11 §0 mcode 行写的本地成品字节不对
        errs = _run(tmp, "t11.md", _mutate_in(good, S0, "本地成品 %s" % real_size, "本地成品 1,000,000"),
                    product, bank)
        check("T11 §0 本地成品字节写错被拦下", any("§0" in e for e in errs), "errors=%r" % errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 60)
    if failures:
        print("文档事实门禁自检 FAIL：%d 项 -> %s" % (len(failures), ", ".join(failures)))
        return 1
    print("文档事实门禁自检全绿。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
