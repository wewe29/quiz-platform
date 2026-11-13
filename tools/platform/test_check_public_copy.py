# -*- coding: utf-8 -*-
r"""check_public_copy 的反向测试：**造错必须报错**，好的时候不得误报。

用法：python tools/platform/test_check_public_copy.py      （失败时退出码非 0）

为什么要有这道测试：
    对外文案页写着「主站 · 五学科 2060 题」，真实是 2116 —— 线上错了近一个月，
    而全部门禁全绿（内容门禁只看题库、字节门禁只看线上 == HEAD，**没人看对外文案**）。
    这道测试要证明两件事：
      ① 门禁**真的会红**（改错任何一个数字都得被抓出来）；
      ② **删掉声明也算错** —— 解析不到断言时必须报红，
         绝不能「找不到就默认通过」（那正是让腐烂静默的写法）。
"""
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import check_public_copy as cpc  # noqa: E402

MIRROR_PAGES = os.path.join(PLATFORM, "sources", "calculus", "site_pages")
REGISTRY = os.path.join(PLATFORM, "subjects", "registry.json")
CANON_PAGES = r"D:\workspace\5-docs\高等数学复习资料\site_pages"
SINGLE_FILE = r"D:\workspace\5-docs\高等数学复习资料\01《高等数学》题库刷题网页 v2.html"

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


def _errors(page_path, facts, dist, single_bytes):
    """跑一次页面检查，返回错误列表（把「解析不到」也算错误）。"""
    try:
        errs, _notes = cpc.check_page(page_path, facts, dist, single_bytes)
        return list(errs)
    except cpc.FactError as exc:
        return [str(exc)]


def main():
    print("[test] 对外文案事实门禁 · 反向测试")
    if not os.path.isfile(REGISTRY):
        print("[FAIL] 缺 registry.json，先跑 build_all.py")
        return 1
    if not os.path.isdir(MIRROR_PAGES):
        print("[FAIL] 缺 sources/calculus/site_pages，先跑 sync_mirror.py")
        return 1

    facts = cpc.load_registry(PLATFORM)
    dist = cpc.load_calculus_dist(PLATFORM)

    with io.open(os.path.join(MIRROR_PAGES, "offline-download.html"), encoding="utf-8") as f:
        good_dl = f.read()
    with io.open(os.path.join(MIRROR_PAGES, "retired-notice.html"), encoding="utf-8") as f:
        good_rn = f.read()

    # 页面里声明的单文件字节数（当期望值用；产物在不在都不影响这几项测试）
    import re
    m = re.search(r"· ([\d,]+) 字节", good_dl)
    if not m:
        print("[FAIL] 页面上找不到单文件字节数声明")
        return 1
    claimed_bytes = int(m.group(1).replace(",", ""))
    real_bytes = os.path.getsize(SINGLE_FILE) if os.path.isfile(SINGLE_FILE) else claimed_bytes

    tmp = tempfile.mkdtemp(prefix="publiccopy-")
    try:
        pages = os.path.join(tmp, "site_pages")
        os.makedirs(pages)

        def write(name, text):
            p = os.path.join(pages, name)
            with io.open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            return p

        # T0 正例
        p = write("offline-download.html", good_dl)
        errs = _errors(p, facts, dist, real_bytes)
        check("T0 正确的下载页不误报", not errs, "errors=%r" % errs[:3])
        p = write("retired-notice.html", good_rn)
        errs = _errors(p, facts, dist, real_bytes)
        check("T0 正确的指路页不误报", not errs, "errors=%r" % errs[:3])

        # T1 平台总题量写错（这条正是线上真的发生过的那次）
        p = write("offline-download.html",
                  _mutate(good_dl, "五学科 2116 题", "五学科 2060 题"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T1 平台总题量写错要报错", any("主站题量" in e for e in errs), "errors=%r" % errs[:3])

        p = write("retired-notice.html",
                  _mutate(good_rn, "五学科 2116 题", "五学科 2060 题"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T1 指路页平台总题量写错要报错", any("主站题量" in e for e in errs), "errors=%r" % errs[:3])

        # T2 高数题量写错
        p = write("offline-download.html",
                  _mutate(good_dl, "高等数学 905 题", "高等数学 999 题"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T2 高数题量写错要报错", any("高数题量" in e for e in errs), "errors=%r" % errs[:3])

        # T3 章节数写错
        p = write("offline-download.html",
                  _mutate(good_dl, "905 题，12 章", "905 题，11 章"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T3 章节数写错要报错", any("章节数" in e for e in errs), "errors=%r" % errs[:3])

        # T4 题型分布写错
        p = write("offline-download.html",
                  _mutate(good_dl, "单选 257 /", "单选 250 /"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T4 题型分布写错要报错", any("「单选」题数" in e for e in errs), "errors=%r" % errs[:3])

        # T5 难度分布写错
        p = write("offline-download.html",
                  _mutate(good_dl, "基础 229 /", "基础 220 /"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T5 难度分布写错要报错", any("「基础」题数" in e for e in errs), "errors=%r" % errs[:3])

        # T6 真题数写错
        p = write("offline-download.html",
                  _mutate(good_dl, "676 道考研与自考真题", "600 道考研与自考真题"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T6 真题数写错要报错", any("真题数" in e for e in errs), "errors=%r" % errs[:3])

        # T7 单文件字节数写错
        p = write("offline-download.html",
                  _mutate(good_dl, "{:,} 字节".format(claimed_bytes),
                          "{:,} 字节".format(claimed_bytes + 1)))
        errs = _errors(p, facts, dist, real_bytes)
        check("T7 单文件字节数写错要报错", any("字节数" in e for e in errs), "errors=%r" % errs[:3])

        # T8 删掉声明 ⇒ 报红（解析不到不许默认通过）
        p = write("offline-download.html",
                  good_dl.replace("主站 · 五学科 2116 题", "主站"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T8 删掉平台总题量声明要报红", any("解析不到" in e for e in errs), "errors=%r" % errs[:3])

        p = write("offline-download.html",
                  good_dl.replace("题型 6 种（单选 257 / 多选 24 / 判断 36 / 填空 147 / 简答 24 / 计算与分析 417）", "题型 6 种"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T8 删掉题型分布声明要报红", any("解析不到" in e for e in errs), "errors=%r" % errs[:3])

        p = write("retired-notice.html", good_rn.replace("主站 · 五学科 2116 题", "主站"))
        errs = _errors(p, facts, dist, real_bytes)
        check("T8 指路页删掉声明要报红", any("解析不到" in e for e in errs), "errors=%r" % errs[:3])

        # T9 事实源变了（改了 registry 的题量），页面没跟着改 ⇒ 也要报红
        p = write("offline-download.html", good_dl)
        bad_facts = {"platform_total": facts["platform_total"] + 1,
                     "calculus": facts["calculus"]}
        errs = _errors(p, bad_facts, dist, real_bytes)
        check("T9 事实源题量变了要报红", any("主站题量" in e for e in errs), "errors=%r" % errs[:3])

        # T10 事实源读不出来 ⇒ 退出码 2（红），不许当成通过
        rc = cpc.main(["--platform-root", os.path.join(tmp, "no-such-repo")])
        check("T10 事实源缺失要报红", rc != 0, "rc=%r" % rc)

        # T11 正本与镜像不一致 ⇒ 报红（线上发的和仓里存的不是同一句话）
        if os.path.isdir(CANON_PAGES):
            mirror_root = os.path.join(tmp, "mirror-root")
            canon_root = os.path.join(tmp, "canon-root")
            for root in (mirror_root, canon_root):
                os.makedirs(os.path.join(root, "site_pages"))
                for name in cpc.PAGES:
                    shutil.copy2(os.path.join(MIRROR_PAGES, name),
                                 os.path.join(root, "site_pages", name))
            # 把正本那份改坏，模拟「正本改了但没同步进仓」
            cp = os.path.join(canon_root, "site_pages", "offline-download.html")
            with io.open(cp, encoding="utf-8") as f:
                txt = f.read()
            with io.open(cp, "w", encoding="utf-8", newline="\n") as f:
                f.write(_mutate(txt, "五学科 2116 题", "五学科 2060 题"))
            rc = cpc.main(["--platform-root", PLATFORM,
                           "--calculus-root", mirror_root,
                           "--canon-root", canon_root])
            check("T11 正本与镜像不一致要报红", rc != 0, "rc=%r" % rc)
        else:
            print("  [SKIP] T11 正本不在本机，跳过")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if failures:
        print("[FAIL] 反向测试 %d 项未通过：%s" % (len(failures), "、".join(failures)))
        return 1
    print("[OK ] 对外文案事实门禁 · 反向测试全绿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
