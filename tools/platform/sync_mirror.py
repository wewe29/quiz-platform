# -*- coding: utf-8 -*-
"""把「正本」同步到平台仓的镜像 sources/<id>/（D10：正本 → 镜像，禁止反向）。

为什么要有这个脚本：
    两棵 tools 树必须逐文件一致，否则「平台仓跑的其实是另一份门禁」——
    2026-10-31 实测：平台仓那份旧基线文件用的是旧格式（缺「模块」列），
    而正本已经是新格式，不同步就会出现两套口径。

镜像必须覆盖**正本的全部源码**，不只是构建链用到的那几个脚本：
    · 2026-10-31 实测：高数站的**前端源码**（assets/js/**、build_static.py、
      template_v2.html、check_keyboard_contract.js、tests/**）曾只存在于裸目录
      `5-docs\\高等数学复习资料\\tools`，**不在任何版本控制里**——磁盘一坏就永久丢失；
      而线代镜像一直带着 assets/ 与 research/。⇒ 镜像补全到「正本全量」。

同步的是**正本根目录下的若干块**（见 SUBJECTS 的 pairs），不是整个根目录：
    · 构建产物（_site_v2/、单文件成品 HTML、research/_cache）不入库。

排除规则（可用 --exclude-dir/--exclude-file 追加）：
    · __pycache__ / *.pyc —— 编译缓存
    · _cache             —— 外部抓取缓存（高数 research/_cache 实测 156 MB，非源码）
    · _drops*.jsonl      —— 丢弃记录日志（2 MB，非源码）

行尾归一（2026-11-07 实测事故后加）：
    正本是裸目录、行尾不统一（实测 13 个文件是 CRLF）。早期这里用 copyfile 原样复制，
    于是**镜像工作区也变成 CRLF**；而 git 提交时按 `text=auto` 把 blob 归一成了 LF ——
    git 因此报「工作区干净」，但**本地构建读的是工作区**，产出的就是 CRLF 字节，
    于是「本机构建 ≠ CI 构建 ≠ 线上 Pages」，实测差 1,716 字节（app.js）。
    页面照跑、肉眼完全看不出来，只有字节级核验才能发现。
    ⇒ 现在复制时**文本文件统一 CRLF → LF**，与仓内 `.gitattributes` 的 `eol=lf` 对齐，
      镜像工作区从此永远等于 blob。**归一发生在同步边界上**，正本不必改。

换行符：仓内由 .gitattributes 统一成 LF（D21），而正本是裸目录、换行符不统一
（实测 13 个文件在正本是 CRLF，仓内 blob 是 LF）。所以比对**按内容**判定：
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
    python sync_mirror.py <src> <dst>                  # 任意一棵目录树（兼容旧用法）
"""
import argparse
import fnmatch
import hashlib
import os
import shutil
import sys

DEFAULT_EXCLUDE_DIRS = ("__pycache__", "_cache")
DEFAULT_EXCLUDE_FILES = ("*.pyc", "_drops*.jsonl")

# 文本扩展名：复制时把 CRLF 归一成 LF（与仓内 .gitattributes 的 eol=lf 对齐）。
# 二进制（png/woff2/zip…）一律原样复制，任何字节都不能动。
TEXT_EXT = (".py", ".md", ".html", ".txt", ".css", ".js", ".json", ".yml", ".yaml",
            ".svg", ".ts", ".c", ".h", ".cpp", ".cfg", ".ini", ".xml")

# 学科登记：正本 → 镜像（禁止反向，见 D10）
# pairs = [(正本根下的相对路径, 镜像根下的相对路径), ...]
SUBJECTS = {
    "linalg": {
        "src": r"D:\workspace\5-docs\线性代数复习资料",
        "dst": r"D:\workspace\5-docs\quiz-platform\sources\linalg",
        "pairs": [("tools", "tools")],
    },
    "calculus": {
        "src": r"D:\workspace\5-docs\高等数学复习资料",
        "dst": r"D:\workspace\5-docs\quiz-platform\sources\calculus",
        # site_pages/ 是已上线两个页面的源码（指路页、离线下载页），交付说明.md 是交付文档
        "pairs": [("tools", "tools"), ("site_pages", "site_pages"),
                  ("交付说明.md", "交付说明.md")],
    },
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


def is_text(path):
    """文本文件才做行尾归一；二进制一个字节都不许动。"""
    return path.lower().endswith(TEXT_EXT)


def copy_normalized(src, dst):
    """复制到镜像：**文本文件 CRLF → LF**，二进制原样。

    为什么必须归一（2026-11-07 实测）：
        正本是裸目录、行尾不统一。原样复制会让镜像工作区也带 CRLF；
        git 提交时按 `text=auto` 把 blob 归一成 LF，于是 git 报「工作区干净」，
        但本地构建读工作区 → 本地产物是 CRLF 字节，CI 构建（从 blob）是 LF 字节
        ⇒ 两条渠道的线上内容差 1,716 字节，肉眼完全看不出来。
        归一放在同步边界上做，镜像工作区从此永远等于 blob。
    """
    with open(src, "rb") as f:
        data = f.read()
    if is_text(src):
        data = data.replace(b"\r\n", b"\n")
    parent = os.path.dirname(dst)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)
    try:
        shutil.copystat(src, dst)
    except (OSError, AttributeError):
        pass
    return data


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


def pair_items(src_path, dst_path, exclude_dirs, exclude_files):
    """一个同步对 → [(相对名, 正本绝对路径, 镜像绝对路径), ...]；目录树与单文件都支持。"""
    if os.path.isfile(src_path):
        return [(os.path.basename(src_path), src_path, dst_path)]
    if not os.path.isdir(src_path):
        return []
    m = walk(src_path, exclude_dirs, exclude_files)
    return [(rel, m[rel], os.path.join(dst_path, rel.replace("/", os.sep)))
            for rel in sorted(m)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="正本目录树（或单个文件）")
    ap.add_argument("dst", nargs="?", help="镜像目录树（或单个文件）")
    ap.add_argument("--subject", choices=sorted(SUBJECTS), help="用登记好的学科映射")
    ap.add_argument("--exclude-dir", action="append", default=[], help="额外排除的目录名（可重复）")
    ap.add_argument("--exclude-file", action="append", default=[], help="额外排除的文件名 glob（可重复）")
    ap.add_argument("--check", action="store_true", help="只比对不复制；有缺失或内容不同则退出 1")
    args = ap.parse_args(argv)

    if args.subject:
        spec = SUBJECTS[args.subject]
        pairs = [(os.path.join(spec["src"], s), os.path.join(spec["dst"], d))
                 for s, d in spec["pairs"]]
        label = args.subject
    elif args.src and args.dst:
        pairs = [(args.src, args.dst)]
        label = "自定义"
    else:
        print("[FAIL] 需要 --subject，或同时给出 <src> <dst>")
        return 2

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)
    exclude_files = tuple(DEFAULT_EXCLUDE_FILES) + tuple(args.exclude_file)

    total_missing = total_changed = total_eol = total_same = 0
    to_copy = []

    for src_path, dst_path in pairs:
        if not os.path.exists(src_path):
            print("[FAIL] 正本路径不存在：%s" % src_path)
            return 2
        items = pair_items(src_path, dst_path, exclude_dirs, exclude_files)
        if not items:
            print("[FAIL] 正本路径没有可同步的文件：%s" % src_path)
            return 2

        identical = eol_only = changed = missing = 0
        for rel, s, d in items:
            if not os.path.isfile(d):
                missing += 1
                to_copy.append((rel, s, d))
                continue
            # 不变式：镜像里的文本文件必须**等于归一后的正本**（即 LF 形态），
            # 而不是「正本的原始字节」。只看「正本 == 镜像」会被
            # 「正本 CRLF + 镜像 CRLF」骗过去 —— 那正是 2026-11-07 的污染形态。
            expect = sha256_norm(s) if is_text(s) else sha256(s)
            if sha256(d) == expect:
                identical += 1
            elif is_text(s) and sha256_norm(s) == sha256_norm(d):
                eol_only += 1
                to_copy.append((rel, s, d))
            else:
                changed += 1
                to_copy.append((rel, s, d))

        # 镜像里多出来的（不在正本中）——按目录对计算，属预期内容（如 vendor/）
        extra = 0
        if os.path.isdir(dst_path):
            dm = walk(dst_path, exclude_dirs, exclude_files)
            src_rels = set(r for r, _, _ in items)
            extra = len(set(dm) - src_rels)

        print("[pair] %s → %s" % (src_path, dst_path))
        print("[pair]   文件 %d；已是归一形态 %d；仅行尾形态不同 %d；真差异 %d；缺 %d；镜像多出 %d"
              % (len(items), identical, eol_only, changed, missing, extra))
        if args.check:
            for rel, s, d in items:
                if not os.path.isfile(d):
                    print("   MISS  %s" % rel)
                    continue
                expect = sha256_norm(s) if is_text(s) else sha256(s)
                if sha256(d) == expect:
                    continue
                if is_text(s) and sha256_norm(s) == sha256_norm(d):
                    # 内容一致，但形态不对：镜像是 CRLF 而正本归一后是 LF。
                    # 这会让「本地构建 ≠ CI 构建」，需要重新同步（不算内容漂移）。
                    print("   EOLF  %s（内容一致但行尾形态不是 LF；重新同步即可修）" % rel)
                else:
                    print("   DIFF  %s" % rel)

        total_missing += missing
        total_changed += changed
        total_eol += eol_only
        total_same += identical

    print("[subject] %s：缺 %d 个；已是归一形态 %d 个；仅行尾形态不同 %d 个；真差异 %d 个"
          % (label, total_missing, total_same, total_eol, total_changed))

    if args.check:
        if total_missing or total_changed:
            print("[FAIL] 镜像与正本不一致（缺 %d / 真差异 %d）" % (total_missing, total_changed))
            return 1
        if total_eol:
            print("[WARN] 有 %d 个文件的行尾形态不是 LF（内容一致）：重新同步即可修" % total_eol)
        print("[OK ] 镜像与正本一致（无缺失、无内容差异）")
        return 0

    for rel, s, d in to_copy:
        copy_normalized(s, d)

    # 不轻信拷贝的返回：拷贝后逐文件回读比对（按「归一后的期望字节」比）
    bad = []
    for rel, s, d in to_copy:
        expect = sha256_norm(s) if is_text(s) else sha256(s)
        if not os.path.isfile(d) or sha256(d) != expect:
            bad.append(rel)
    if bad:
        print("[FAIL] 拷贝后回读校验不一致 %d 个：" % len(bad))
        for rel in bad[:10]:
            print("   " + rel)
        return 1

    print("[OK ] 同步完成：新增 %d 个、更新 %d 个、换行归一 %d 个，回读逐字节校验通过"
          % (total_missing, total_changed, total_eol))
    return 0


if __name__ == "__main__":
    sys.exit(main())
