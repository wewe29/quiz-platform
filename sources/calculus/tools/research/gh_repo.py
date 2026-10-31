# -*- coding: utf-8 -*-
"""下载 GitHub 真题仓库的 zip（不走 API，避免限流），并打印文件清单。"""
import io
import os
import sys
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"


def download(repo, branch="main"):
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    out = os.path.join(CACHE, repo.replace("/", "_") + ".zip")
    if not os.path.exists(out):
        url = "https://codeload.github.com/%s/zip/refs/heads/%s" % (repo, branch)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
        with open(out, "wb") as f:
            f.write(data)
        print("下载 %s -> %.1f MB" % (repo, len(data) / 1048576.0))
    else:
        print("缓存命中 %s (%.1f MB)" % (repo, os.path.getsize(out) / 1048576.0))
    return out


def main():
    repo = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    path = download(repo, branch)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        print("条目数：%d" % len(names))
        total = 0
        for n in names:
            if n.endswith("/"):
                continue
            info = z.getinfo(n)
            total += info.file_size
            print("  %-90s %8d" % (n, info.file_size))
        print("解压后合计：%.2f MB" % (total / 1048576.0))


if __name__ == "__main__":
    main()
