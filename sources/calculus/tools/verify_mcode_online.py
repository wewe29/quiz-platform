# -*- coding: utf-8 -*-
r"""tools/verify_mcode_online.py — mcode 公网站的线上核验

**判据为什么不是「线上字节 = 本地字节」**：
    宿主在每个被服务的 HTML 文件里都会注入埋点与悬浮球（实测正文 +6,530 字节，
    注入点是 `</body>` 前的 `<script data-minimax-analytics="...">` 块）。
    所以线上字节**必然**比本地多，拿整文件判等会把「发布成功」误判成「发布失败」。
    正确判据：
        ① **剥掉宿主注入块后**，线上文件与本地成品逐字节相同；
        ② 题库 JSON 逐字节相同 + 题量一致；
        ③ Last-Modified 是本次发布时间。
    再加上浏览器实答 + 控制台 0 error（字节对不代表渲染对，更不代表交互对）。
    CDN / Service Worker 缓存要绕：URL 追加 `?cb=<随机>`。

站点结构（2026-10-31 合并后）：
    ukhfwff2y0f0h   高数专站（活，905 题）
    6aww9gws3iacg   已下线 → 指路页
    7qzdvmxrwxnez   离线单文件版下载页（页面 + 单文件包本体）
    study-math      五学科平台版（2060 题）

用法：python tools\verify_mcode_online.py
"""
import gzip
import hashlib
import io
import json
import os
import random
import sys
import urllib.request

for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(k, None)

CANON = r"D:\workspace\5-docs\高等数学复习资料"
LOCAL_SITE = os.path.join(CANON, "_site_v2")
LOCAL_SINGLE = os.path.join(CANON, "01《高等数学》题库刷题网页 v2.html")
LOCAL_PAGES = os.path.join(CANON, "site_pages")
LOCAL_DIST = r"D:\workspace\5-docs\quiz-platform\dist"

MARK = b"window.__BANK__ = "
INJECT_START = b'<script data-minimax-analytics="minimax-website-analytics-v1">'

SITES = [
    ("高数专站(活)", "https://ukhfwff2y0f0h.space.mcode.cn", "quiz"),
    ("孪生站(已下线)", "https://6aww9gws3iacg.space.mcode.cn", "notice"),
    ("离线单文件下载页", "https://7qzdvmxrwxnez.space.mcode.cn", "download"),
    ("五学科平台版", "https://study-math.space.mcode.cn", "platform"),
]

fails = []


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest().upper()


def fetch(url):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        "%s%scb=%d" % (url, sep, random.randint(10 ** 9, 10 ** 10 - 1)),
        headers={"User-Agent": "Mozilla/5.0 verify/1.0", "Accept-Encoding": "identity",
                 "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return r.status, data, dict(r.headers)


def diff_vs_local(online, local):
    """返回 (线上相对本地多出来的那一块, 剥掉后的字节)。

    宿主在 `</body>` 前插入一整块连续内容（实测 6,530 字节：analytics 脚本 +
    悬浮球样式 + div + 初始化脚本），并在插入处多留一个换行。
    所以判据不是「猜注入长什么样」，而是：
        **线上与本地的差异必须只有一块连续插入，且这一块只能含宿主遥测标记。**
    用最长公共前缀 + 最长公共后缀定位插入点；若线上被改过正文（比如漏了标签），
    差异会变成两块或更多 ⇒ 判等失败。

    注意：不能反过来用「先 diff 再断言相等」——那样是同义反复、必然通过。
    这里额外断言插入块含 minimax 遥测标记，才是有意义的判据。
    """
    n = min(len(online), len(local))
    p = 0
    while p < n and online[p] == local[p]:
        p += 1
    s = 0
    while s < n - p and online[len(online) - 1 - s] == local[len(local) - 1 - s]:
        s += 1
    inserted = online[p:len(online) - s]
    return inserted, online[:p] + online[len(online) - s:]


def check_host_injection(label, online, local):
    """线上文件与本地成品的差异，必须**只有一块宿主遥测插入**；其余逐字节相同。"""
    inserted, stripped = diff_vs_local(online, local)
    only_telemetry = (b"minimax" in inserted.lower()) and (b"minimax-analytics" in inserted.lower()
                                                          or b"floating-ball" in inserted.lower())
    ok = check("线上仅多出宿主遥测块（%d 字节）" % len(inserted), only_telemetry,
               "" if only_telemetry else "插入块内容异常")
    ok = check("剥掉遥测块后与本地逐字节相同", stripped == local,
               "剥后 %d B / sha %s vs 本地 %d B / sha %s"
               % (len(stripped), sha256_bytes(stripped)[:16],
                  len(local), sha256_bytes(local)[:16])) and ok
    return stripped


def check(label, cond, detail=""):
    print("  [%s] %s %s" % ("OK " if cond else "FAIL", label, detail))
    if not cond:
        fails.append("%s %s" % (label, detail))
    return cond


def count_questions(data):
    m = data.find(MARK)
    if m < 0:
        return None
    obj = json.JSONDecoder().raw_decode(data[m + len(MARK):].decode("utf-8"))[0]
    return len(obj.get("questions") or [])


def main():
    local_index = io.open(os.path.join(LOCAL_SITE, "data", "index.json"), "rb").read()
    total = json.loads(local_index.decode("utf-8"))["total"]
    local_single = io.open(LOCAL_SINGLE, "rb").read()
    local_notice = io.open(os.path.join(LOCAL_PAGES, "retired-notice.html"), "rb").read()
    local_dl = io.open(os.path.join(LOCAL_PAGES, "offline-download.html"), "rb").read()
    print("本地基准：index.json %d B / total=%d ；单文件包 %d B / %d 题；指路页 %d B；下载页 %d B"
          % (len(local_index), total, len(local_single), count_questions(local_single),
             len(local_notice), len(local_dl)))

    for label, url, kind in SITES:
        print("\n--- %s\n    %s" % (label, url))
        try:
            status, html, hdrs = fetch(url + ("/" if url.endswith("space.mcode.cn") else "/index.html"))
        except Exception as e:
            check("HTTP 200", False, str(e))
            continue
        check("HTTP 200", status == 200, "status=%d" % status)
        print("    Last-Modified: %s" % (hdrs.get("Last-Modified") or hdrs.get("last-modified")))
        print("    线上 %d 字节（本地对应文件 %d 字节）" % (len(html), len(local_index)))

        if kind == "quiz":
            check_host_injection("高数专站 index.html", html,
                                 io.open(os.path.join(LOCAL_SITE, "index.html"), "rb").read())
            try:
                _s, idx, _h = fetch(url + "/data/index.json")
            except Exception as e:
                check("data/index.json 可取", False, str(e))
                continue
            check("data/index.json 与本地逐字节相同", idx == local_index,
                  "线上 %d B / sha %s" % (len(idx), sha256_bytes(idx)[:16]))
            q_total = 0
            shard_ok = True
            for ch in range(1, 13):
                fn = "ch%02d.json" % ch
                try:
                    _s3, b3, _h3 = fetch(url + "/data/" + fn)
                except Exception as e:
                    shard_ok = False
                    print("       分片 %s 取失败：%s" % (fn, e))
                    continue
                if b3 != io.open(os.path.join(LOCAL_SITE, "data", fn), "rb").read():
                    shard_ok = False
                    print("       分片 %s 与本地不一致" % fn)
                try:
                    q_total += len(json.loads(b3.decode("utf-8"))["questions"])
                except Exception:
                    shard_ok = False
            check("12 个分片全部逐字节相同", shard_ok)
            check("分片题数合计 = %d" % total, q_total == total, "线上合计 %d 题" % q_total)
            try:
                _s4, rjs, _h4 = fetch(url + "/assets/js/ui/render.js")
                ljs = io.open(os.path.join(LOCAL_SITE, "assets", "js", "ui", "render.js"), "rb").read()
                check("线上 render.js 与本地逐字节相同", rjs == ljs,
                      "线上 %d B / sha %s" % (len(rjs), sha256_bytes(rjs)[:16]))
                bad = b"addEventListener('keydown'" in rjs or b'addEventListener("keydown"' in rjs
                check("线上 render.js 无选项 keydown 处理器（Enter=提交 修复已上线）", not bad,
                      "命中" if bad else "未命中")
            except Exception as e:
                check("线上 render.js 可取", False, str(e))

        elif kind == "notice":
            stripped = check_host_injection("指路页", html, local_notice)
            t = stripped.decode("utf-8", "replace")
            check("是「已合并」指路页", "这个链接已经合并了" in t)
            check("指向主站 study-math", "https://study-math.space.mcode.cn/" in t)
            check("指向高数专站 ukhfwff2y0f0h", "https://ukhfwff2y0f0h.space.mcode.cn/" in t)
            check("已不含刷题界面", "window.__BANK__" not in t and "当前筛选命中" not in t)

        elif kind == "download":
            stripped = check_host_injection("下载页", html, local_dl)
            t = stripped.decode("utf-8", "replace")
            check("是下载页标题", "离线单文件版下载" in t)
            check("有下载链接", 'href="calculus-quiz-offline.html"' in t)
            check("本页不再是在线刷题站", "window.__BANK__" not in t)
            try:
                _s5, pkg, _h5 = fetch(url + "/calculus-quiz-offline.html")
            except Exception as e:
                check("单文件包可下载", False, str(e))
                continue
            p_stripped = check_host_injection("下载包 calculus-quiz-offline.html", pkg, local_single)
            check("下载包内含 %d 题" % total, count_questions(pkg) == total,
                  "实际 %s 题" % count_questions(pkg))

        elif kind == "platform":
            local_reg = io.open(os.path.join(LOCAL_DIST, "subjects", "registry.json"), "rb").read()
            try:
                _s6, reg, _h6 = fetch(url + "/subjects/registry.json")
            except Exception as e:
                check("registry.json 可取", False, str(e))
                continue
            check("registry.json 与本地逐字节相同", reg == local_reg,
                  "线上 %d B / sha %s" % (len(reg), sha256_bytes(reg)[:16]))
            if reg == local_reg:
                r = json.loads(reg.decode("utf-8"))
                tot = sum(x["total"] for x in r["subjects"])
                check("五学科题量合计 = 2060", tot == 2060,
                      "线上 %d 题（%s）" % (tot, ", ".join("%s %d" % (x["id"], x["total"]) for x in r["subjects"])))
            try:
                _s7, mcalc, _h7 = fetch(url + "/subjects/calculus/data/manifest.json")
                lmc = io.open(os.path.join(LOCAL_DIST, "subjects", "calculus", "data", "manifest.json"), "rb").read()
                check("高数子站 manifest.json 与本地逐字节相同", mcalc == lmc,
                      "线上 %d B / sha %s" % (len(mcalc), sha256_bytes(mcalc)[:16]))
            except Exception as e:
                check("高数子站 manifest 可取", False, str(e))

    print()
    if fails:
        print("[结果] %d 项不通过：" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("[结果] 全部线上核验通过")
    print("提醒：字节一致 ≠ 渲染正确 ≠ 交互正确 —— 还要在浏览器里实答一次，并查控制台。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
