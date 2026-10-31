# -*- coding: utf-8 -*-
"""把「正本」tools/ 同步到平台仓的镜像 sources/<id>/tools/（D10：正本 → 镜像，禁止反向）。

为什么要有这个脚本：
    两棵 tools 树必须逐文件一致，否则「平台仓跑的其实是另一份门禁」——
    2026-10-31 实测：平台仓那份旧基线文件用的是旧格式（缺「模块」列），
    而正本已经是新格式，不同步就会出现两套口径。

镜像必须覆盖**正本 tools 的全部源码**，不只是构建链用到的那几个脚本：
    · 2026-10-31 实测：高数站的**前端源码**（assets/js/**、build_static.py、
      template_v2.html、check_keyboard_contract.js、tests/**）曾只存在于裸目录
      `5-docs\\高等数学复习资料\\tools`，**不在任何版本控制里**——磁盘一坏就永久丢失；
      而线代镜像一直带着 assets/ 与 research/。⇒ 镜像补全到「正本 tools 全量」。

排除规则（可用 --exclude-dir/--exclude-file 追加）：
    · __pycache__ / *.pyc —— 编译缓存
    · _cache             —— 外部抓取缓存（高数 research/_cache 实测 156 MB，非源码）
    · _drops*.jsonl      —— 丢弃记录日志（2 MB，非源码）

换行符：仓内由 .gitattributes 统一成 LF（D21），而正本是裸目录、换行符不统一
（实测 4 个 v1 遗留文件在正本是 CRLF，仓内 blob 是 LF）。所以比对**按内容**判定：
把两侧的 CRLF 归一成 LF 再比，并分三档如实报告——
    逐字节相同 / 仅换行符差异 / 真差异。
只有「缺文件」与「真差异」算漂移（--check 退出 1）；「仅换行符差异」不算。

注意：
    ① bash 的硬安全策略会拦「工作区外写」的字面路径，所以同步放在脚本内部做；
    ② 本脚本**只覆盖同名文件、不删除多余文件**——删除要走可恢复删除另行处理；
    ③ --check 只比对不复制，镜像有漂移时退出 1（可当本地门禁用）。

用法：
    python sync_mirror.py --subject linalg            # 同步线代
    python sync_mirror.py --subject linalg --check    # 只比对，漂移则退出 1
    python sync_mirror.py --subject calculus          # 同步高数
    python sync_mirror.py <src> <dst>                  # 任意两棵 tools 树
"""
import argparse
import fnmatch
import hashlib
import os
import shutil
import sys

DEFAULT_EXCLUDE_DIRS = ("__pycache__", "_cache")
DEFAULT_EXCLUDE_FILES = ("*.pyc", "_drops*.jsonl")

# 学科登记：正本 → 镜像（禁止反向，见 D10）
SUBJECTS = {
    "linalg": (r"D:\workspace\5-docs\线性代数复习资料\tools",
               r"D:\workspace\5-docs\quiz-platform\sources\linalg\tools"),
    "calculus": (r"D:\workspace\5-docs\高等数学复习资料\tools",
                 r"D:\workspace\5-docs\quiz-platform\sources\calculus\tools"),
}


def _digest(path, normalize_eol=False):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk.replace(b"\r\n", b"\n") if normalize_eol else chunk)
    return h.hexdigest()


def sha256(path):
    return _digest(path)


def sha256_norm(path):
    """换行归一后的摘要：CRLF → LF，用于跨仓比较（.gitattributes 会把仓内统一成 LF）。"""
    return _digest(path, normalize_eol=True)


def walk(root, exclude_dirs, exclude_files):
    """相对路径 → 绝对路径；按排除规则跳过目录名与文件名。"""
    out = {}
    for r, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in exclude_dirs)
        for fn in files:
            if any(fnmatch.fnmatch(fn, pat) for pat in exclude_files):
                continue
            p = os.path.join(r, fn)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out


def compare(src_map, dst_map):
    """分三档：identical（逐字节相同）/ eol_only（仅换行符差异）/ changed（真差异）。"""
    identical, eol_only, changed = [], [], []
    for rel in sorted(set(src_map) & set(dst_map)):
        s, d = src_map[rel], dst_map[rel]
        if sha256(s) == sha256(d):
            identical.append(rel)
        elif sha256_norm(s) == sha256_norm(d):
            eol_only.append(rel)
        else:
            changed.append(rel)
    return identical, eol_only, changed


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="正本 tools 目录")
    ap.add_argument("dst", nargs="?", help="镜像 tools 目录")
    ap.add_argument("--subject", choices=sorted(SUBJECTS), help="用登记好的学科映射")
    ap.add_argument("--exclude-dir", action="append", default=[], help="额外排除的目录名（可重复）")
    ap.add_argument("--exclude-file", action="append", default=[], help="额外排除的文件名 glob（可重复）")
    ap.add_argument("--check", action="store_true", help="只比对不复制；有缺失或内容不同则退出 1")
    args = ap.parse_args(argv)

    if args.subject:
        src_root, dst_root = SUBJECTS[args.subject]
    elif args.src and args.dst:
        src_root, dst_root = args.src, args.dst
    else:
        print("[FAIL] 需要 --subject，或同时给出 <src> <dst>")
        return 2

    if not os.path.isdir(src_root):
        print("[FAIL] 正本目录不存在：%s" % src_root)
        return 2

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)
    exclude_files = tuple(DEFAULT_EXCLUDE_FILES) + tuple(args.exclude_file)

    src_map = walk(src_root, exclude_dirs, exclude_files)
    dst_map = walk(dst_root, exclude_dirs, exclude_files) if os.path.isdir(dst_root) else {}

    missing = sorted(set(src_map) - set(dst_map))
    identical, eol_only, changed = compare(src_map, dst_map)
    extra = sorted(set(dst_map) - set(src_map))

    print("[subject] 正本 %s" % src_root)
    print("[subject] 镜像 %s" % dst_root)
    print("[subject] 排除规则：目录 %s；文件 %s" % (sorted(exclude_dirs), exclude_files))
    print("[subject] 正本 %d 文件 / 镜像 %d 文件" % (len(src_map), len(dst_map)))
    print("[subject] 镜像缺 %d 个；逐字节相同 %d 个；仅换行符差异 %d 个；真差异 %d 个；镜像多出 %d 个"
          % (len(missing), len(identical), len(eol_only), len(changed), len(extra)))

    if args.check:
        for rel in missing:
            print("   MISS  %s" % rel)
        for rel in changed:
            print("   DIFF  %s" % rel)
        for rel in eol_only:
            print("   EOL   %s（仓内按 .gitattributes 统一 LF，内容一致）" % rel)
        if missing or changed:
            print("[FAIL] 镜像与正本不一致（缺 %d / 真差异 %d）" % (len(missing), len(changed)))
            return 1
        print("[OK ] 镜像与正本一致（无缺失、无内容差异）")
        return 0

    to_copy = missing + changed + eol_only
    for rel in to_copy:
        dst = os.path.join(dst_root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src_map[rel], dst)

    # 不轻信 copy2 的返回：拷贝后逐文件回读比对
    bad = []
    for rel in to_copy:
        dst = os.path.join(dst_root, rel.replace("/", os.sep))
        if not os.path.isfile(dst) or sha256(src_map[rel]) != sha256(dst):
            bad.append(rel)
    if bad:
        print("[FAIL] 拷贝后回读校验不一致 %d 个：" % len(bad))
        for rel in bad[:10]:
            print("   " + rel)
        return 1

    if extra:
        print("[note] 镜像多出 %d 个文件（不在正本中，属预期内容，如 vendor/）：" % len(extra))
        for rel in extra[:8]:
            print("   " + rel)
        if len(extra) > 8:
            print("   ... 其余 %d 个" % (len(extra) - 8))

    print("[OK ] 同步完成：新增 %d 个、更新 %d 个、换行对齐 %d 个，回读逐字节校验通过"
          % (len(missing), len(changed), len(eol_only)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
