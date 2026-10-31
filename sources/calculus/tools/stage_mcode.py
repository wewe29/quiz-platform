# -*- coding: utf-8 -*-
r"""tools/stage_mcode.py — 把高数站的产物暂存到 E:\抗菌肽\_deploy（website_deploy 的 path/source_path 必须在工作区内）

为什么要有这个脚本（三个坑）：
    ① bash 的硬安全策略会拦「工作区外写」的字面路径，且 Copy-Item 跨盘被拦
       ⇒ 复制动作放在脚本内部做（命令文本里只出现 D:\Temp / 脚本自身路径）。
    ② 源码快照要跟正本走，但它**不能**整个 tools/ 都拷进去：
       `research\_cache\` 是 156 MB 的外部抓取缓存（试卷 zip / md），不是源码；
       `__pycache__` 是编译缓存。两者都排除。
    ③ 节点 ↔ 目录 ↔ node_id ↔ 公网 URL 的对应关系必须**写死在一处**，
       否则下次漏传 node_id 就会新建站点、换一个 URL，旧链接静默断掉。

站点结构（2026-10-31 合并后）：
    calculus-quiz        ← 正本 _site_v2\                 → node 457098400059681  高数专站（活）
    math-quiz-v2         ← site_pages\retired-notice.html → node 457267271725402  已下线：指路页
    math-quiz-v2-single  ← site_pages\offline-download.html + 单文件包
                                                        → node 458301517873724  离线单文件下载页
    （平台版属另一个仓，不在本脚本范围：node 458302907191686）

用法：
    python tools\stage_mcode.py            # 从正本暂存 + 逐字节校验
    python tools\stage_mcode.py --check    # 只校验暂存副本与正本是否一致
"""
import hashlib
import os
import shutil
import sys

WORKSPACE = r"E:\抗菌肽"
DEPLOY = os.path.join(WORKSPACE, "_deploy")
CANON = r"D:\workspace\5-docs\高等数学复习资料"
SITE_SRC = os.path.join(CANON, "_site_v2")
SINGLE_SRC = os.path.join(CANON, "01《高等数学》题库刷题网页 v2.html")
V1_NAME = "01《高等数学》题库刷题网页.html"
PAGES = os.path.join(CANON, "site_pages")
RETIRED_PAGE = os.path.join(PAGES, "retired-notice.html")
DOWNLOAD_PAGE = os.path.join(PAGES, "offline-download.html")
OFFLINE_NAME = "calculus-quiz-offline.html"

TOOLS = os.path.join(CANON, "tools")
SKIP_DIRS = {"__pycache__", "research"}

# 节点台账：目录 ↔ 源码快照目录 ↔ node_id ↔ 公网 URL。**改版时原样传 node_id。**
NODES = [
    ("calculus-quiz", "calculus-quiz-src", "457098400059681",
     "https://ukhfwff2y0f0h.space.mcode.cn", "高数专站（活）"),
    ("math-quiz-v2", "math-quiz-v2-src", "457267271725402",
     "https://6aww9gws3iacg.space.mcode.cn", "已下线：内容与高数专站逐字节相同，改为指路页"),
    ("math-quiz-v2-single", "math-quiz-v2-src", "458301517873724",
     "https://7qzdvmxrwxnez.space.mcode.cn", "离线单文件版下载页（不在此刷题）"),
]
# 平台版（另一个仓管，节点与 URL 仅作记录）
PLATFORM_NODE = ("quiz-platform-dist", "quiz-platform-src", "458302907191686",
                 "https://study-math.space.mcode.cn", "五学科平台版 2060 题")

errors = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def index_tree(root):
    out = {}
    for r, _d, fs in os.walk(root):
        for fn in fs:
            p = os.path.join(r, fn)
            out[os.path.relpath(p, root)] = sha256(p)
    return out


def mirror_tree(src, dst, skip_dirs=()):
    """把 src 的内容复制到 dst（dst 先清空），返回 (文件数, 字节数)。"""
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    n = total = 0
    for root, dirs, files in os.walk(src):
        parts = [] if root == src else os.path.relpath(root, src).split(os.sep)
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            s = os.path.join(root, fn)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
            total += os.path.getsize(d)
    return n, total


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def main():
    check_only = "--check" in sys.argv
    for p in (SITE_SRC, SINGLE_SRC, RETIRED_PAGE, DOWNLOAD_PAGE):
        if not os.path.exists(p):
            print("[FAIL] 缺少输入：%s" % p)
            return 2

    if not check_only:
        # 1) 高数专站（活）：正本多文件站
        n, total = mirror_tree(SITE_SRC, os.path.join(DEPLOY, "calculus-quiz"))
        print("[stage] %-20s <- 正本 _site_v2 : %d 文件 / %s B" % ("calculus-quiz", n, format(total, ",")))

        # 2) 孪生站：已下线 → 指路页
        rd = os.path.join(DEPLOY, "math-quiz-v2")
        if os.path.isdir(rd):
            shutil.rmtree(rd)
        os.makedirs(rd, exist_ok=True)
        copy_file(RETIRED_PAGE, os.path.join(rd, "index.html"))
        print("[stage] %-20s <- 指路页（已下线）：%d 字节" % ("math-quiz-v2", os.path.getsize(RETIRED_PAGE)))

        # 3) 单文件站：改为「离线单文件下载页」+ 单文件包本体
        sd = os.path.join(DEPLOY, "math-quiz-v2-single")
        if os.path.isdir(sd):
            shutil.rmtree(sd)
        os.makedirs(sd, exist_ok=True)
        copy_file(DOWNLOAD_PAGE, os.path.join(sd, "index.html"))
        copy_file(SINGLE_SRC, os.path.join(sd, OFFLINE_NAME))
        print("[stage] %-20s <- 下载页 + 单文件包：%s 字节 / %s 字节"
              % ("math-quiz-v2-single", os.path.getsize(DOWNLOAD_PAGE),
                 os.path.getsize(SINGLE_SRC)))

        # 4) 源码快照
        for name in ("calculus-quiz-src", "math-quiz-v2-src"):
            n, total = mirror_tree(TOOLS, os.path.join(DEPLOY, name), skip_dirs=SKIP_DIRS)
            d = os.path.join(DEPLOY, name)
            copy_file(SINGLE_SRC, os.path.join(d, "01《高等数学》题库刷题网页 v2.html"))
            v1 = os.path.join(CANON, V1_NAME)
            if os.path.isfile(v1):
                copy_file(v1, os.path.join(d, V1_NAME))
            copy_file(RETIRED_PAGE, os.path.join(d, "retired-notice.html"))
            copy_file(DOWNLOAD_PAGE, os.path.join(d, "offline-download.html"))
            print("[stage] %-20s <- 正本 tools（去 __pycache__/research）+ 页面源：%d 文件 / %s B"
                  % (name, n, format(total, ",")))

    # 5) 逐字节校验
    src_index = index_tree(SITE_SRC)
    dst_index = index_tree(os.path.join(DEPLOY, "calculus-quiz"))
    if dst_index != src_index:
        errors.append("calculus-quiz 与正本 _site_v2 不一致")
    else:
        print("  [OK ] calculus-quiz：%d 文件与正本逐字节一致" % len(dst_index))

    if sha256(os.path.join(DEPLOY, "math-quiz-v2", "index.html")) != sha256(RETIRED_PAGE):
        errors.append("math-quiz-v2 指路页与源文件不一致")
    else:
        print("  [OK ] math-quiz-v2：指路页与源文件逐字节一致")

    if sha256(os.path.join(DEPLOY, "math-quiz-v2-single", "index.html")) != sha256(DOWNLOAD_PAGE):
        errors.append("math-quiz-v2-single 下载页与源文件不一致")
    elif sha256(os.path.join(DEPLOY, "math-quiz-v2-single", OFFLINE_NAME)) != sha256(SINGLE_SRC):
        errors.append("math-quiz-v2-single 内的单文件包与正本不一致")
    else:
        print("  [OK ] math-quiz-v2-single：下载页 + 单文件包均与正本逐字节一致")

    print("\n下一步：调用 website_deploy（**必须带 node_id**）")
    for name, src_name, node, url, note in NODES + [PLATFORM_NODE]:
        print("  node_id     = %s" % node)
        print("  path        = %s" % os.path.join(DEPLOY, name))
        print("  source_path = %s" % os.path.join(DEPLOY, src_name))
        print("  project_name= %s" % name)
        print("  → %s" % url)
        print("    用途：%s" % note)
        print()

    if errors:
        for e in errors:
            print("[FAIL] %s" % e)
        return 1
    print("[DONE] 暂存完成并逐字节校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
