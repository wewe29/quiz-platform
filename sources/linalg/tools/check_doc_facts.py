# -*- coding: utf-8 -*-
r"""《更新指南.md》里的事实必须与真实产物一致（交付文档的「数字不许过期」门禁）。

**为什么需要这道门禁（2026-11-13 实测）**
《更新指南.md》是**交付给使用者/托管方的那份文档**。它的「现状速查」表里写着
本地成品字节数、SHA256、线上字节数、题量与题型/难度分布 —— 全是会被改动的数字。
2026-11-13 一查：那张表里的字节数与 SHA256 还是 **2026-10-31 的旧值**
（1,658,279 B / `0E67F233…`），而真值早已变成 1,658,628 B / `ED06E78B…`；
同一份文件 §0 与 §1 还**互相矛盾**（§0 说 mcode 线上 1,660,151 B，§1 说 1,664,809 B）。

**为什么别的门禁没抓到**
- 内容门禁只管题库与产物（题号、答案键、题型配额）—— 不看文档；
- 字节门禁只管「线上 == HEAD 成品」—— 不看文档；
- 于是**文档这一层是整个项目里唯一没有门禁的一层**，数字静默腐烂，直到有人手点。

所以把交付文档的数字钉在真实产物上：
  ① 本地成品大小 / SHA256 == 真实文件；
  ② GitHub Pages 线上字节数 == 本地成品字节数（Pages 与本地产物**逐字节相同**是不变量）；
  ③ mcode 线上字节数 − 本地字节数 == 文档自称的「多 N 字节」（内部自洽）；
  ④ 题量、题型分布、难度分布 == 实际题库（`qa_bank.load_bank()` 现算）。

**解析不到就报红**：表格行被改名、句式被改 ⇒ 门禁直接失败并说明「没找到该断言」，
**不允许「找不到就默认通过」**——那正是让这类腐烂静默下去的写法。

用法：
    python tools/check_doc_facts.py                 # 检查默认文档与默认成品
    python tools/check_doc_facts.py --doc X --product Y
退出码：0 = 文档里的事实与产物一致；1 = 有对不上的地方（或断言解析不到）。
"""
import argparse
import hashlib
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

DOC_NAME = "更新指南.md"
PRODUCT_CANDIDATES = ["01《线性代数》题库刷题网页.html", "index.html"]

# 文档里用的**简称**（与 target.py 的 TYPE_LABEL 全称不同：简答 / 计算）。
# 顺序必须与 qa_bank.target.TYPE_ORDER 一致 —— 门禁按位置对，顺序错位也会报出来。
TYPE_SHORT = {
    "single": "单选",
    "multi": "多选",
    "judge": "判断",
    "blank": "填空",
    "short": "简答",
    "calc": "计算",
}
DIFF_SHORT = {"basic": "基础", "medium": "中等", "hard": "困难"}


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _section(doc, heading):
    """截出某一小节的文本（从 heading 到下一个 '## '）；找不到返回空串。"""
    i = doc.find(heading)
    if i < 0:
        return ""
    j = doc.find("\n## ", i + len(heading))
    return doc[i:j if j > 0 else len(doc)]


def _row(doc, key, section=None):
    """取含 key 的那一**整行**（渠道表是 3 列：渠道 | 地址 | 状态——事实都在第 3 列，
    按「第 key 的下一个单元格」取会取错列，所以整行最省心）。"""
    scope = _section(doc, section) if section else doc
    for line in scope.splitlines():
        s = line.strip()
        if s.startswith("|") and key in s:
            return s
    return None


def _cell(doc, key, section=None):
    """取表格里含 key 的那一行的**值单元格**；找不到返回 None。

    找不到就报红（不默认通过）——见文件头「解析不到就报红」。
    section 给定时只在那一小节里找（同一份文件里同样的数字可能出现在多处）。
    """
    scope = _section(doc, section) if section else doc
    for line in scope.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        for i, c in enumerate(cells):
            if key in c and i + 1 < len(cells):
                return cells[i + 1]
    return None


def _ints(text):
    return [int(x.replace(",", "")) for x in re.findall(r"([\d,]+)", text)]


def _bytes_of(text):
    m = re.search(r"([\d,]+)\s*字节", text)
    return int(m.group(1).replace(",", "")) if m else None


def check(doc_path, product_path, bank=None):
    """返回问题清单（空列表 = 全部对得上）。"""
    problems = []
    if not os.path.isfile(doc_path):
        return ["找不到文档：%s" % doc_path]
    if not os.path.isfile(product_path):
        return ["找不到成品：%s" % product_path]
    doc = _read(doc_path).decode("utf-8")

    size = os.path.getsize(product_path)
    sha = _sha256(product_path)

    # ⓪ §0 渠道表：同样写着线上字节与 SHA（2026-11-13 实测：这节原先也是旧值）
    s0 = "## 0. 部署渠道"
    s1 = "## 1. 现状速查"
    cell = _row(doc, "GitHub Pages（推荐）", s0)
    if cell is None:
        problems.append("§0 渠道表里找不到「GitHub Pages（推荐）」这一行")
    else:
        got = _bytes_of(cell)
        if got is None:
            problems.append("§0 Pages 行里读不出线上字节数：%s" % cell[:70])
        elif got != size:
            problems.append("§0 写的 Pages 线上字节 %s != 本地成品 %d" % (format(got, ","), size))
        m = re.search(r"`?([0-9A-Fa-f]{16})", cell)
        if m and not sha.startswith(m.group(1).upper()):
            problems.append("§0 写的 Pages 线上 SHA 前缀 %s != 真实 %s" % (m.group(1).upper(), sha[:12]))
    cell = _row(doc, "mcode 站点", s0)
    if cell is None:
        problems.append("§0 渠道表里找不到「mcode 站点」这一行")
    else:
        m = re.search(r"线上\s*\**([\d,]+)\s*字节", cell)
        if not m:
            problems.append("§0 mcode 行里读不出线上字节数：%s" % cell[:70])
        else:
            mc = int(m.group(1).replace(",", ""))
            m2 = re.search(r"本地成品\s*([\d,]+)\s*\+\s*\**([\d,]+)", cell)
            if not m2:
                problems.append("§0 mcode 行里读不出「本地成品 + 埋块」的写法：%s" % cell[:70])
            else:
                local_said = int(m2.group(1).replace(",", ""))
                embed = int(m2.group(2).replace(",", ""))
                if local_said != size:
                    problems.append("§0 写的本地成品字节 %s != 真实 %d" % (format(local_said, ","), size))
                if mc - local_said != embed:
                    problems.append("§0 内部不自洽：线上 %d − 本地 %d = %d，但文中写埋块 %d"
                                    % (mc, local_said, mc - local_said, embed))

    # ① 本地成品大小 / SHA256
    cell = _cell(doc, "本地成品大小", s1)
    if cell is None:
        problems.append("文档里找不到「本地成品大小 / SHA256」这一行（表格被改名或删掉了？）")
    else:
        got = _bytes_of(cell)
        if got is None:
            problems.append("「本地成品大小」行里读不出字节数：%s" % cell[:60])
        elif got != size:
            problems.append("文档写的本地成品大小 %s 字节 != 真实 %d 字节" % (format(got, ","), size))
        m = re.search(r"`([0-9A-Fa-f]{8,})", cell)
        if not m:
            problems.append("「本地成品大小」行里读不出 SHA256：%s" % cell[:60])
        elif not sha.startswith(m.group(1).upper()):
            problems.append("文档写的 SHA256 前缀 %s != 真实 %s" % (m.group(1).upper(), sha[:12]))

    # ②③ 线上与本地是否一致
    cell = _cell(doc, "线上与本地是否一致", s1)
    if cell is None:
        problems.append("文档里找不到「线上与本地是否一致」这一行")
    else:
        m = re.search(r"GitHub Pages 线上\s*\**([\d,]+)\s*字节", cell)
        if not m:
            problems.append("「线上与本地是否一致」行里读不出 GitHub Pages 线上字节数")
        else:
            pages = int(m.group(1).replace(",", ""))
            if pages != size:
                problems.append("文档写的 Pages 线上字节 %s != 本地成品 %d（Pages 与本地产物应逐字节相同）"
                                % (format(pages, ","), size))
        m = re.search(r"mcode 线上\s*([\d,]+)\s*字节", cell)
        if not m:
            problems.append("「线上与本地是否一致」行里读不出 mcode 线上字节数")
        else:
            mc = int(m.group(1).replace(",", ""))
            if mc < size:
                problems.append("文档写的 mcode 线上字节 %d < 本地成品 %d（线上不可能比本地产物小）"
                                % (mc, size))
            d = re.search(r"多\s*([\d,]+)", cell)
            if not d:
                problems.append("「线上与本地是否一致」行里读不出 mcode 埋块字节数（应写「多 N 字节」）")
            else:
                stated = int(d.group(1).replace(",", ""))
                if mc - size != stated:
                    problems.append("文档内部不自洽：mcode 线上 %d − 本地 %d = %d，但文中写「多 %d 字节」"
                                    % (mc, size, mc - size, stated))

    # ④ 题量 / 题型 / 难度分布
    if bank is None:
        from qa_bank import load_bank
        bank = load_bank()
    c_type = Counter(q["typeGroup"] for q in bank)
    c_diff = Counter(q["difficulty"] for q in bank)
    total = len(bank)

    cell = _cell(doc, "本地题库", s1)
    if cell is None:
        problems.append("文档里找不到「本地题库」这一行")
    else:
        m = re.search(r"\*\*(\d+)\s*题\*\*", cell)
        if not m:
            problems.append("「本地题库」行里读不出题量：%s" % cell[:60])
        elif int(m.group(1)) != total:
            problems.append("文档写的题量 %s != 实际题库 %d 题" % (m.group(1), total))
        m = re.search(r"难度分布\s*([^，）]+)", cell)
        if not m:
            problems.append("「本地题库」行里读不出难度分布")
        else:
            pairs = re.findall(r"([一-龥]+)\s*(\d+)", m.group(1))
            got = [int(n) for _, n in pairs]
            want = [c_diff.get(k, 0) for k in ("basic", "medium", "hard")]
            labels = [l for l, _ in pairs]
            if labels != [DIFF_SHORT[k] for k in ("basic", "medium", "hard")]:
                problems.append("难度分布标签顺序不对：%r（应为 基础/中等/困难）" % labels)
            elif got != want:
                problems.append("文档写的难度分布 %r != 实际 %r" % (got, want))
        m = re.search(r"题型\s*([^）]+)", cell)
        if not m:
            problems.append("「本地题库」行里读不出题型分布")
        else:
            pairs = re.findall(r"([一-龥]+)\s*(\d+)", m.group(1))
            got = [int(n) for _, n in pairs]
            labels = [l for l, _ in pairs]
            order = list(TYPE_SHORT)
            if labels != [TYPE_SHORT[k] for k in order]:
                problems.append("题型分布标签或顺序不对：%r（应为 %r）"
                                % (labels, [TYPE_SHORT[k] for k in order]))
            else:
                want = [c_type.get(k, 0) for k in order]
                if got != want:
                    problems.append("文档写的题型分布 %r != 实际 %r" % (got, want))

    # 线上地址两行的题量（顺带钉住，别让「528 题」在别处过期）
    for key in ("线上地址（主）", "线上地址（备用）"):
        cell = _cell(doc, key, s1)
        if cell is None:
            problems.append("文档里找不到「%s」这一行" % key)
            continue
        m = re.search(r"(\d+)\s*题", cell)
        if not m:
            problems.append("「%s」行里读不出题量" % key)
        elif int(m.group(1)) != total:
            problems.append("「%s」行写的题量 %s != 实际题库 %d" % (key, m.group(1), total))

    return problems


def main():
    ap = argparse.ArgumentParser(description="交付文档里的数字必须与真实产物一致")
    ap.add_argument("--doc", default=os.path.join(ROOT, DOC_NAME))
    ap.add_argument("--product", default=None, help="成品路径（默认按候选名找）")
    args = ap.parse_args()

    product = args.product
    if product is None:
        for name in PRODUCT_CANDIDATES:
            p = os.path.join(ROOT, name)
            if os.path.isfile(p):
                product = p
                break
        else:
            print("[FAIL] 找不到成品（候选：%s）" % "、".join(PRODUCT_CANDIDATES))
            return 1

    problems = check(args.doc, product)
    if problems:
        print("[FAIL] 交付文档与产物对不上 %d 处：" % len(problems))
        for p in problems:
            print("   ⚠ " + p)
        print("修法：改文档（数字要跟产物一致），别改产物去迁就文档。")
        return 1
    print("[OK ] 文档里的题量 / 分布 / 字节 / SHA 与真实产物一致（%s）" % os.path.basename(product))
    return 0


if __name__ == "__main__":
    sys.exit(main())
