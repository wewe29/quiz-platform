# -*- coding: utf-8 -*-
"""把「单文件版正本」同步到 GitHub Pages 发布克隆。

为什么要有这个脚本：
    发布仓 `publish/linear-algebra-quiz` 是**独立克隆**，每次发布都要把
    正本的成品、工具链、文档搬过去。以前这一步靠手工复制，
    结果出现过「仓里的成品是旧的、工具链也是旧的」这种漂移。
    放成脚本 = 下回合直接跑一条命令，不用重想搬哪些文件。

同步内容：
    1. 正本 tools/ 全部文件 → 发布仓 tools/（发布仓自己的 tools/vendor/katex 不动，CI 构建要用）
    2. 正本成品 HTML → 发布仓 index.html（部署用的就是它）
    3. 正本 更新指南.md → 发布仓 更新指南.md
    4. 平台仓的《应用化实施方案与迭代计划.md》→ 发布仓同名文件（D10：正本 → 镜像）

换行符：发布仓的约定是 LF（core.autocrlf=false + core.eol=lf）。
本机正本里部分文件是 CRLF，直接拷进去会改掉 blob 字节（构建产物不受影响，
但仓库字节与线上不再一致），所以这里统一转成 LF。

用法：python tools/sync_to_publish.py
"""
import hashlib
import os
import shutil

SRC_ROOT = r"D:\workspace\5-docs\线性代数复习资料"
PLATFORM = r"D:\workspace\5-docs\quiz-platform"
DST_ROOT = r"D:\workspace\5-docs\线性代数复习资料\publish\linear-algebra-quiz"

TEXT_EXT = (".py", ".md", ".html", ".txt", ".css", ".js", ".json", ".yml", ".yaml")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def copy_text(src, dst):
    """按字节拷贝并把 CRLF 统一成 LF。"""
    with open(src, "rb") as f:
        data = f.read()
    if src.lower().endswith(TEXT_EXT):
        data = data.replace(b"\r\n", b"\n")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)


def main():
    n = 0
    changed = []

    # 1) tools 全树（发布仓的 vendor/katex 不动）
    src_tools = os.path.join(SRC_ROOT, "tools")
    for root, dirs, files in os.walk(src_tools):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, src_tools)
            dst = os.path.join(DST_ROOT, "tools", rel)
            before = sha256(dst) if os.path.isfile(dst) else None
            copy_text(src, dst)
            if before != sha256(dst):
                changed.append("tools/" + rel.replace("\\", "/"))
            n += 1

    # 2) 成品
    src = os.path.join(SRC_ROOT, "01《线性代数》题库刷题网页.html")
    dst = os.path.join(DST_ROOT, "index.html")
    before = sha256(dst)
    copy_text(src, dst)
    if before != sha256(dst):
        changed.append("index.html")
    n += 1

    # 3) 更新指南
    src = os.path.join(SRC_ROOT, "更新指南.md")
    dst = os.path.join(DST_ROOT, "更新指南.md")
    before = sha256(dst)
    copy_text(src, dst)
    if before != sha256(dst):
        changed.append("更新指南.md")
    n += 1

    # 4) 方案文档（正本在平台仓）
    src = os.path.join(PLATFORM, "docs", "应用化实施方案与迭代计划.md")
    dst = os.path.join(DST_ROOT, "应用化实施方案与迭代计划.md")
    before = sha256(dst)
    copy_text(src, dst)
    if before != sha256(dst):
        changed.append("应用化实施方案与迭代计划.md")
    n += 1

    print("同步 %d 个文件；内容有变化的 %d 个：" % (n, len(changed)))
    for c in changed:
        print("   " + c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
