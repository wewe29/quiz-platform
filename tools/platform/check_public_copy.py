# -*- coding: utf-8 -*-
r"""tools/platform/check_public_copy.py — 对外文案页里的数字必须与真实产物一致

为什么要有这道门禁（2026-11-14 浏览器实答时实测出来的真缺陷）：
    离线下载页 https://7qzdvmxrwxnez.space.mcode.cn 上写着「主站 · 五学科 2060 题」，
    真实题量是 **2116**（905+283+528+244+156）。2060 是概率统计还只有 100 题时的旧数
    （2026-11-03 扩到 156），**线上错了一个多月**，而当时全部门禁全绿 ——
    因为内容门禁只看题库、字节门禁只看「线上 == HEAD」，**对外文案页根本没人管**。

    这跟 2026-11-13 抓到的「文档层是门禁的盲区」是同一条病根：
    **数字写在哪儿，哪儿就得有门禁**。文档要管，对外文案更要管（它是给用户看的假话）。

口径（每条声明都必须能解析出来，解析不到一律报红 —— 不许「找不到就默认通过」）：
    · 平台总题量        ← subjects/registry.json 的 total 求和
    · 高数题量/章数/真题数 ← registry 里的 calculus 条目
    · 题型分布/难度分布   ← subjects/calculus/data/*.json（提交进仓的构建产物）
    · 单文件离线版字节数  ← 构建产物本身（--single-file 传入；未传则该条记为「未检查」并显式告警）

用法：
    python tools/platform/check_public_copy.py
    python tools/platform/check_public_copy.py --single-file "<单文件包路径>"
    python tools/platform/check_public_copy.py --canon-root "<高数正本目录>"
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM_ROOT = os.path.dirname(os.path.dirname(HERE))          # 仓库根
MIRROR_CALCULUS = os.path.join(PLATFORM_ROOT, "sources", "calculus")
PAGES = ("offline-download.html", "retired-notice.html")

# 页面上的中文题型标签 ← 题库 data 里的 type
TYPE_LABEL_TO_TYPES = {
    "单选": ("single",),
    "多选": ("multi",),
    "判断": ("judge",),
    "填空": ("blank",),
    "简答": ("term", "short"),      # 「简答与名词解释」在数据里拆成 term + short
    "计算与分析": ("calc",),
}
DIFF_LABEL_TO_TYPES = {"基础": "basic", "中等": "medium", "困难": "hard"}


class FactError(Exception):
    """事实源缺失或解析不出来 —— 一律当错误，不当通过。"""


# --------------------------------------------------------------------------- 事实源
def load_registry(platform_root):
    path = os.path.join(platform_root, "subjects", "registry.json")
    if not os.path.isfile(path):
        raise FactError("找不到注册表：%s" % path)
    with open(path, encoding="utf-8") as f:
        reg = json.load(f)
    subjects = reg.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise FactError("注册表里没有 subjects：%s" % path)
    total = 0
    for s in subjects:
        if not isinstance(s.get("total"), int):
            raise FactError("注册表条目 %r 缺 total" % s.get("id"))
        total += s["total"]
    calc = None
    for s in subjects:
        if s.get("id") == "calculus":
            calc = s
    if calc is None:
        raise FactError("注册表里没有 calculus 条目：%s" % path)
    return {"platform_total": total, "calculus": calc}


def load_calculus_dist(platform_root):
    """从提交进仓的学科构建产物里数题型/难度分布。"""
    root = os.path.join(platform_root, "subjects", "calculus", "data")
    files = sorted(glob.glob(os.path.join(root, "ch*.json")))
    if not files:
        raise FactError("找不到高数学科数据：%s" % root)
    types = collections.Counter()
    diffs = collections.Counter()
    total = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("questions", data.get("items", []))
        for q in items:
            if not isinstance(q, dict):
                continue
            total += 1
            types[q.get("type")] += 1
            diffs[q.get("difficulty")] += 1
    if not total:
        raise FactError("高数学科数据是空的：%s" % root)
    return {"total": total, "types": types, "diffs": diffs}


# --------------------------------------------------------------------------- 页面声明
def _all(html, pattern, flags=0):
    return re.findall(pattern, html, flags)


def _ints(html, pattern, flags=0):
    out = []
    for m in _all(html, pattern, flags):
        if isinstance(m, tuple):
            out.append(tuple(int(x.replace(",", "")) for x in m))
        else:
            out.append(int(m.replace(",", "")))
    return out


def _require(values, page, label):
    if not values:
        raise FactError("%s：解析不到「%s」这一条声明（不许默认通过）" % (page, label))
    return values


def check_offline_download(html, facts, dist, single_file_bytes):
    """返回 (errors, notes)。"""
    errors = []
    notes = []
    page = "offline-download.html"
    reg = facts["calculus"]

    def want(label, values, expected):
        for v in values:
            if v != expected:
                errors.append("%s：%s 声明为 %s，真实值是 %s" % (page, label, v, expected))

    # 平台总题量（漂过一次的地方，最该盯）
    want("主站题量", _require(_ints(html, r"五学科 (\d+) 题"), page, "五学科 N 题"), facts["platform_total"])

    # 高数题量：标题/描述/h1/题量行/专站链接都各写了一遍，全部要一致
    for pat, label in [(r"高等数学 (\d+) 题", "标题里的高数题量"),
                       (r"（(\d+) 题、零外部依赖）", "meta description 里的高数题量"),
                       (r"(\d+) 题，(\d+) 章", "题量行"),
                       (r"高数专站 · (\d+) 题", "高数专站链接")]:
        vals = _require(_ints(html, pat), page, label)
        if pat == r"(\d+) 题，(\d+) 章":
            want("高数题量", [v[0] for v in vals], reg["total"])
            want("高数章节数", [v[1] for v in vals], reg["chapters"])
        else:
            want(label, vals, reg["total"])

    # 题型分布：单选 257 / 多选 24 / 判断 36 / 填空 147 / 简答 24 / 计算与分析 417
    m = _require(_ints(html, r"题型 (\d+) 种（单选 (\d+) / 多选 (\d+) / 判断 (\d+) / "
                             r"填空 (\d+) / 简答 (\d+) / 计算与分析 (\d+)）"), page, "题型分布")
    want("题型种类数", [v[0] for v in m], len(TYPE_LABEL_TO_TYPES))
    for gi, label in enumerate(TYPE_LABEL_TO_TYPES, start=2):   # gi = 正则里的第几组
        expect = sum(dist["types"].get(t, 0) for t in TYPE_LABEL_TO_TYPES[label])
        want("「%s」题数" % label, [v[gi - 1] for v in m], expect)

    # 难度分布：基础 229 / 中等 372 / 困难 304
    m = _require(_ints(html, r"基础 (\d+) / 中等 (\d+) / 困难 (\d+)"), page, "难度分布")
    for gi, label in enumerate(DIFF_LABEL_TO_TYPES, start=1):   # gi = 正则里的第几组
        want("「%s」题数" % label, [v[gi - 1] for v in m], dist["diffs"].get(DIFF_LABEL_TO_TYPES[label], 0))

    # 真题数
    want("真题数", _require(_ints(html, r"(\d+) 道考研与自考真题"), page, "真题数"), reg["realExamTagged"])

    # 单文件字节数（需要构建产物；没给就显式记「未检查」，不装作通过）
    vals = _require(_ints(html, r"· ([\d,]+) 字节"), page, "单文件字节数")
    if single_file_bytes is None:
        notes.append("%s：单文件字节数声明为 %s —— **未检查**（没给 --single-file 产物路径）"
                     % (page, vals[0]))
    else:
        want("单文件字节数", vals, single_file_bytes)

    return errors, notes


def check_retired_notice(html, facts):
    errors = []
    page = "retired-notice.html"
    reg = facts["calculus"]

    def want(label, values, expected):
        for v in values:
            if v != expected:
                errors.append("%s：%s 声明为 %s，真实值是 %s" % (page, label, v, expected))

    want("主站题量", _require(_ints(html, r"五学科 (\d+) 题"), page, "五学科 N 题"), facts["platform_total"])
    want("高数题量", _require(_ints(html, r"(\d+) 道题"), page, "N 道题"), reg["total"])
    want("高数题量", _require(_ints(html, r"(\d+) 道高数题"), page, "N 道高数题"), reg["total"])
    return errors, []


CHECKERS = {
    "offline-download.html": check_offline_download,
    "retired-notice.html": check_retired_notice,
}


# --------------------------------------------------------------------------- 主流程
def check_page(path, facts, dist, single_file_bytes):
    """检查单个页面文件，返回 (errors, notes)。"""
    if not os.path.isfile(path):
        return (["找不到页面文件：%s" % path], [])
    with open(path, encoding="utf-8") as f:
        html = f.read()
    name = os.path.basename(path)
    fn = CHECKERS.get(name)
    if fn is None:
        return (["没有为 %s 定义的检查规则（新增页面必须同时加检查）" % name], [])
    if name == "retired-notice.html":
        return fn(html, facts)
    return fn(html, facts, dist, single_file_bytes)


def _same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def main(argv=None):
    ap = argparse.ArgumentParser(description="对外文案页的数字必须与真实产物一致")
    ap.add_argument("--platform-root", default=PLATFORM_ROOT, help="平台仓根目录")
    ap.add_argument("--calculus-root", default=MIRROR_CALCULUS,
                    help="高数源码所在目录（仓内镜像 sources/calculus 或高数正本）")
    ap.add_argument("--canon-root", default=None,
                    help="高数正本目录（给了就额外检查正本那份，并要求与镜像逐字节一致）")
    ap.add_argument("--single-file", default=None,
                    help="单文件离线版构建产物路径（给了才检查字节数声明）")
    args = ap.parse_args(argv)

    errors = []
    notes = []
    try:
        facts = load_registry(args.platform_root)
        dist = load_calculus_dist(args.platform_root)
    except FactError as e:
        print("[FAIL] 事实源读不出来：%s" % e)
        return 2

    single_bytes = None
    if args.single_file:
        if not os.path.isfile(args.single_file):
            print("[FAIL] --single-file 指定的产物不存在：%s" % args.single_file)
            return 2
        single_bytes = os.path.getsize(args.single_file)

    print("[事实源] 平台总题量=%d｜高数题量=%d 章=%d 真题=%d｜题型分布=%s｜难度分布=%s"
          % (facts["platform_total"], facts["calculus"]["total"], facts["calculus"]["chapters"],
             facts["calculus"]["realExamTagged"],
             dict(dist["types"]), dict(dist["diffs"])))

    roots = [(args.calculus_root, "镜像/正本")]
    if args.canon_root:
        roots.append((args.canon_root, "高数正本"))

    seen = {}
    for root, label in roots:
        site_pages = os.path.join(root, "site_pages")
        if not os.path.isdir(site_pages):
            errors.append("[%s] 找不到 site_pages 目录：%s" % (label, site_pages))
            continue
        for name in PAGES:
            path = os.path.join(site_pages, name)
            try:
                e, n = check_page(path, facts, dist, single_bytes)
            except FactError as exc:
                # 解析不到声明 ⇒ 报红（但要报得干净，不能靠抛异常让 CI 看堆栈）
                e, n = [str(exc)], []
            errors.extend(e)
            notes.extend(n)
            if os.path.isfile(path):
                seen.setdefault(name, []).append((label, path))
                print("  [检查] %s / %s" % (label, name))

    # 正本与镜像必须逐字节一致（否则线上（用正本暂存）与仓里（用镜像）说的不是同一句话）
    if args.canon_root:
        for name, lst in seen.items():
            if len(lst) < 2:
                continue
            paths = [p for _l, p in lst]
            if not all(_same_bytes(paths[0], p) for p in paths[1:]):
                errors.append("「%s」正本与镜像不一致（正本 %s / 镜像 %s）：线上发的和仓里存的不是同一份"
                              % (name, paths[0], paths[-1]))
            else:
                print("  [OK ] %s：正本与镜像逐字节一致" % name)

    for n in notes:
        print("[注意] %s" % n)
    if errors:
        for e in errors:
            print("[FAIL] %s" % e)
        return 1
    print("[OK ] 对外文案页的数字全部与真实产物一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
