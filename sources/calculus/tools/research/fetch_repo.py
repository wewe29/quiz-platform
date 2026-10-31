# -*- coding: utf-8 -*-
"""下载真题源仓库 zip 到 tools/research/_cache/。

用法: python research/fetch_repo.py Kaoyan-Math2-Papers
"""
import os
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")

# 本机 HTTP_PROXY 指向的端口可能无监听，会让下载失败；直连最稳
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(k, None)

repo = sys.argv[1]
owner = repo.split("/")[0] if "/" in repo else "TsekaLuk"
name = repo.split("/")[-1]
out = os.path.join(CACHE, "%s_%s.zip" % (owner, name))
url = "https://codeload.github.com/%s/%s/zip/refs/heads/main" % (owner, name)

if os.path.exists(out) and os.path.getsize(out) > 1024:
    print("已存在，跳过：%s (%.1f MB)" % (out, os.path.getsize(out) / 1048576.0))
    raise SystemExit(0)

os.makedirs(CACHE, exist_ok=True)
tmp = out + ".part"
print("下载 %s" % url, flush=True)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (qa-bank-fetch)"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
    total = r.headers.get("Content-Length")
    total = int(total) if total else 0
    got = 0
    last = 0
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        f.write(chunk)
        got += len(chunk)
        if got - last > 20 * 1048576:
            last = got
            print("   %.1f MB%s" % (got / 1048576.0,
                                   (" / %.1f MB" % (total / 1048576.0)) if total else ""),
                  flush=True)
os.replace(tmp, out)
print("完成：%s (%.1f MB, %.0fs)" % (out, os.path.getsize(out) / 1048576.0, time.time() - t0))
