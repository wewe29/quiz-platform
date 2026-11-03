# -*- coding: utf-8 -*-
r"""tools/online_judge.py — mcode 线上核验的**判据核心**（纯逻辑，可单测）

判据一句话：**剥掉宿主在 </body> 前注入的那一整块遥测内容后，线上文件与本地成品逐字节相同。**

为什么不能写成「线上字节 = 本地字节 + N」：
    注入块大小**不是常数**（实测高数专站 6,530 B、线代单文件站 1,523 B），
    宿主会随版本与页面结构变化。所以只能用「差异的**形状**」来定位：
        线上 − 本地 的差异，必须**只有一块连续插入**，且这一块只能含宿主遥测标记。
    一旦线上正文被改过（少一段、标签被吃掉、多一段），差异会变成两块或更多 ⇒ 判等失败。

为什么必须绕缓存：
    CDN / Service Worker 会把旧副本发给同样的 URL。核验 URL 一律追加 `?cb=<随机>`，
    否则会读到发布前的旧文件，误判「部署没生效」。

为什么必须绕代理：
    本机 HTTP_PROXY / HTTPS_PROXY 指向 127.0.0.1:17897（该端口无监听）。
    urllib 默认读环境变量代理，必须显式 `ProxyHandler({})` 禁用，否则请求全失败。

用法：
    from online_judge import fetch, judge
    status, body, headers = fetch(url)
    v = judge(body, local_bytes)
    if not v["ok"]: print(v["reason"])
"""
import gzip
import hashlib
import io
import json
import os
import random
import urllib.request

# 本机代理指向无监听的端口，urllib 默认会走它 → 必须显式禁用。
# 放在模块级，构造一次即可（默认 opener 是懒建的，但显式更可控）。
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# 宿主遥测块的标记。注入形如：
#   <script data-minimax-analytics="minimax-website-analytics-v1"> ... </script>
#   + 悬浮球（floating-ball）样式/div/初始化脚本
TELEMETRY_MARKERS = (b"minimax",)
TELEMETRY_STRONG = (b"minimax-analytics", b"floating-ball", b"data-minimax")

MARK = b"window.__BANK__ = "


def sha256_bytes(b):
    """字节 → sha256 十六进制（大写，取前 16 位便于人眼对账）。"""
    return hashlib.sha256(b).hexdigest().upper()


def build_url(url, cb=None):
    """核验 URL 一律追加 `?cb=<随机>`，绕开 CDN / Service Worker 的旧副本。

    `cb=None` 时生成随机数；显式传值可复现（测试用）。
    """
    if cb is None:
        cb = random.randint(10 ** 9, 10 ** 10 - 1)
    sep = "&" if "?" in url else "?"
    return "%s%scb=%s" % (url, sep, cb)


def fetch(url, timeout=60, cb=None, opener=None):
    """取回一个 URL 的原始字节。

    返回 (status, body, headers)。请求头强制 `Accept-Encoding: identity`，
    避免服务端压缩后与本地字节对不上（万一服务端仍压缩，则就地解压）。
    """
    req = urllib.request.Request(
        build_url(url, cb),
        headers={"User-Agent": "Mozilla/5.0 mcode-online-judge/1.0",
                 "Accept-Encoding": "identity",
                 "Cache-Control": "no-cache",
                 "Pragma": "no-cache"},
    )
    op = opener or _OPENER
    with op.open(req, timeout=timeout) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return r.status, data, dict(r.headers)


def is_telemetry(block):
    """这一块注入内容是不是**宿主遥测块**（而不是别的什么东西）。"""
    low = block.lower()
    if not any(m in low for m in TELEMETRY_MARKERS):
        return False
    return any(m in low for m in TELEMETRY_STRONG)


def judge(online, local):
    """核心判据：线上字节 vs 本地成品字节 → 判定结果。

    返回 dict：
        ok            布尔，是否判定通过
        reason        中文说明（失败时给出可读原因）
        inserted_len  被判定为宿主注入块的字节数
        telemetry_only 这一块是不是宿主遥测块
        stripped      剥掉注入块后的线上字节

    三种通过情形：
        ① 线上 == 本地（宿主未注入）→ 通过；
        ② 差异只有一块连续插入、该块含宿主遥测标记、剥掉后 == 本地 → 通过；
        ③ 其他一切情形 → 不通过。
    """
    if online == local:
        return {"ok": True, "reason": "线上与本地逐字节相同（宿主未注入遥测块）",
                "inserted_len": 0, "telemetry_only": True, "stripped": online}

    n = min(len(online), len(local))
    p = 0
    while p < n and online[p] == local[p]:
        p += 1
    s = 0
    while s < n - p and online[len(online) - 1 - s] == local[len(local) - 1 - s]:
        s += 1
    inserted = online[p:len(online) - s]
    stripped = online[:p] + online[len(online) - s:]

    telemetry_only = is_telemetry(inserted)
    same_after_strip = (stripped == local)

    if same_after_strip and telemetry_only:
        return {"ok": True,
                "reason": "差异只有一块宿主遥测插入（%d 字节），剥掉后逐字节相同" % len(inserted),
                "inserted_len": len(inserted), "telemetry_only": True, "stripped": stripped}

    if not same_after_strip:
        return {"ok": False,
                "reason": "剥掉疑似注入块后仍与本地不一致："
                          "线上 %d B / sha %s vs 本地 %d B / sha %s"
                          % (len(stripped), sha256_bytes(stripped)[:16],
                             len(local), sha256_bytes(local)[:16]),
                "inserted_len": len(inserted), "telemetry_only": telemetry_only, "stripped": stripped}

    return {"ok": False,
            "reason": "差异块不含宿主遥测标记（%d 字节）：%r" % (len(inserted), inserted[:80]),
            "inserted_len": len(inserted), "telemetry_only": False, "stripped": stripped}


def count_questions(data):
    """从单文件 HTML 里读出内联题库的题量（读不到返回 None）。"""
    m = data.find(MARK)
    if m < 0:
        return None
    obj = json.JSONDecoder().raw_decode(data[m + len(MARK):].decode("utf-8"))[0]
    return len(obj.get("questions") or [])


def read_file(path):
    """按二进制读文件（不做任何换行转换，避免 CRLF/LF 差异引入假阳性）。"""
    with io.open(path, "rb") as f:
        return f.read()
