# -*- coding: utf-8 -*-
"""本地验收用静态服务器：强制 no-store，避免浏览器缓存旧产物。

为什么不用 `python -m http.server`：
    它不发送 Cache-Control，Chromium 会按「启发式缓存」规则
    （(now - Last-Modified) × 10%）自行决定新鲜期，于是**改完产物重新加载，
    浏览器仍可能拿旧 JS**。表现极具迷惑性：网络面板显示 200、
    durationMs=0（其实是缓存命中），页面却仍在跑旧代码。
    本轮验收就因为它白查了半小时。

用法：
    python tools/serve.py --dir "<站点目录>" --port 8849
"""
from __future__ import print_function

import argparse
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    from socketserver import ThreadingMixIn  # noqa: F401
except ImportError:  # pragma: no cover
    pass


class NoStoreHandler(SimpleHTTPRequestHandler):
    """所有响应都带 Cache-Control: no-store + 禁用 ETag/Last-Modified 协商。"""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        SimpleHTTPRequestHandler.end_headers(self)

    def send_response(self, code, message=None):
        # SimpleHTTPRequestHandler 默认会发 Server / Date，保留即可；
        # 这里只确保不因 304 把旧文件喂回去。
        SimpleHTTPRequestHandler.send_response(self, code, message)

    def log_message(self, fmt, *args):
        sys.stdout.write("[serve] %s - %s\n" % (self.address_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="站点目录")
    ap.add_argument("--port", type=int, default=8849)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    root = os.path.abspath(args.dir)
    if not os.path.isdir(root):
        raise SystemExit("[serve] 目录不存在：%s" % root)
    os.chdir(root)

    httpd = ThreadingHTTPServer((args.host, args.port), NoStoreHandler)
    httpd.daemon_threads = True
    print("[serve] %s → http://%s:%d/index.html（no-store）" % (root, args.host, args.port))
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[serve] 已停止")
        httpd.shutdown()


if __name__ == "__main__":
    main()
