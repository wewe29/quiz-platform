# -*- coding: utf-8 -*-
r"""tools/platform/check_worktree_eol.py — 工作区 vs 仓内 blob 的逐字节一致性门禁

**为什么需要这道门禁**：git 看不见行尾污染。
    仓内 `.gitattributes` 是 `* text=auto eol=lf`，所以 git 在**比对**时会把工作区的
    CRLF 归一成 LF 再比 —— 于是「工作区文件是 CRLF、blob 是 LF」这种状态，
    `git status` 报**干净**，`git diff` 报**无差异**。
    但**构建读的是工作区**：本地构建产出 CRLF 字节，CI 构建（从 blob）产出 LF 字节
    ⇒ 两条发布渠道的线上内容差 1,716 字节（2026-11-07 实测：app.js）。
    页面照跑、渲染一模一样，肉眼与普通 diff 全都看不出来，**只有字节级核验能发现**。

**本门禁的判据**：工作区里的已跟踪文本文件，必须与 `HEAD` 的 blob **逐字节相同**。
    - 二进制（含 NUL 字节）跳过 —— 任何字节都不能动。
    - 差异分两类如实报告：**行尾污染**（内容一致，仅 CRLF↔LF）与**真差异**。

**这不是 git 的重复检查**：git 的语义是「内容相同就算干净」，
    本门禁的语义是「字节相同才算干净」——正是那一类被 git 归一掉的差异。

用法：
    python tools/platform/check_worktree_eol.py            # 检查全部已跟踪文件
    python tools/platform/check_worktree_eol.py --fix      # 检查并修复行尾污染
    python tools/platform/check_worktree_eol.py --path X    # 只检查某些路径
退出码：0 = 干净；1 = 有污染或真差异；2 = 环境问题（不是 git 仓等）。

为什么自带 --fix 而不让人去跑 `git checkout -- <路径>`：
    git 的 index **stat cache 记的就是污染后（CRLF）的尺寸**，于是 git 认为文件
    「未变」而**连内容都不读** —— `git checkout -- .` 与 `git checkout-index -f --all`
    都会因此跳过重写（2026-11-07 实测：两者都跑完，污染依旧）。
    ⇒ 修复必须**绕过 git 的快捷路径，直接把 blob 字节写回工作区**。

为什么 --fix 只修行尾污染、不碰「真差异」：
    「真差异」可能是使用者**还没提交的工作**。自动覆盖会毁掉它
    （2026-11-07 实测踩到过：门禁把自己尚未提交的新版本覆盖成了 blob 里的旧版）。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))


def git_bytes(args):
    return subprocess.run(["git", "-C", PLATFORM] + args, capture_output=True).stdout


def list_tracked(only=None):
    out = git_bytes(["ls-files", "-z"])
    files = [f for f in out.decode("utf-8").split("\x00") if f]
    if only:
        pref = tuple(only)
        files = [f for f in files if f.startswith(pref)]
    return files


def batch_blobs(paths):
    """一次 `git cat-file --batch` 取回全部 blob（逐个起进程会慢 20 倍）。"""
    if not paths:
        return {}
    proc = subprocess.Popen(["git", "-C", PLATFORM, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    payload = ("\n".join("HEAD:" + p for p in paths) + "\n").encode("utf-8")
    out, _ = proc.communicate(payload)
    res = {}
    i = 0
    for p in paths:
        j = out.find(b"\n", i)
        if j < 0:
            break
        parts = out[i:j].split()
        if len(parts) != 3:
            break
        size = int(parts[2])
        res[p] = out[j + 1:j + 1 + size]
        i = j + 1 + size + 1
    return res


def is_binary(data):
    return b"\x00" in data[:8192]


def main(argv=None):
    ap = argparse.ArgumentParser(description="工作区已跟踪文本文件必须与 blob 逐字节一致")
    ap.add_argument("--path", action="append", default=[],
                    help="只检查这些路径前缀（可重复）")
    ap.add_argument("--fix", action="store_true",
                    help="把行尾污染的文件用 blob 字节重新物化（绕过 git 的 stat cache）")
    args = ap.parse_args(argv or sys.argv[1:])

    if not os.path.isdir(os.path.join(PLATFORM, ".git")):
        print("[FAIL] 不是 git 仓：%s" % PLATFORM)
        return 2
    paths = list_tracked(args.path)
    if not paths:
        print("[FAIL] 没有可检查的已跟踪文件")
        return 2
    blobs = batch_blobs(paths)

    eol_bad, real_bad, skipped = [], [], 0
    for rel in paths:
        full = os.path.join(PLATFORM, rel.replace("/", os.sep))
        if not os.path.isfile(full):
            continue
        with open(full, "rb") as f:
            work = f.read()
        blob = blobs.get(rel)
        if blob is None:
            continue
        if is_binary(work) or is_binary(blob):
            skipped += 1
            continue
        if work == blob:
            continue
        if work.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"):
            eol_bad.append((rel, work.count(b"\r\n")))
        else:
            real_bad.append((rel, len(work), len(blob)))

    total = len(paths)
    print("已跟踪文件 %d 个；跳过二进制 %d 个" % (total, skipped))
    if eol_bad:
        print("[FAIL] 行尾污染 %d 个（工作区 CRLF ≠ blob LF —— 本地构建会产出与 CI 不同的字节）："
              % len(eol_bad))
        for rel, n in eol_bad[:40]:
            print("   %-72s CRLF=%d" % (rel, n))
        if len(eol_bad) > 40:
            print("   … 还有 %d 个" % (len(eol_bad) - 40))
    if real_bad:
        print("[FAIL] 真差异 %d 个（工作区与 blob 内容不同）：" % len(real_bad))
        for rel, a, b in real_bad[:40]:
            print("   %-72s 工作区 %d B vs blob %d B" % (rel, a, b))
    if eol_bad or real_bad:
        if args.fix:
            # ⚠ 只修「行尾污染」这一类（内容一致、仅 CRLF↔LF）。
            # 「真差异」**一律不动** —— 那可能是使用者还没提交的工作，
            # 自动覆盖会毁掉未提交的改动（2026-11-07 实测踩到过：
            # 门禁把自己尚未提交的新版本覆盖成了 blob 里的旧版）。
            fixed = 0
            for rel, _n in eol_bad:
                blob = blobs.get(rel)
                if blob is None:
                    continue
                full = os.path.join(PLATFORM, rel.replace("/", os.sep))
                with open(full, "wb") as f:
                    f.write(blob)
                fixed += 1
            print("[FIX ] 已从 blob 重新物化 %d 个行尾污染文件" % fixed)
            if real_bad:
                print("[WARN] %d 个「真差异」文件**未改动**（可能是未提交的工作）：" % len(real_bad))
                for rel, a, b in real_bad[:20]:
                    print("   %-72s 工作区 %d B vs blob %d B" % (rel, a, b))
            remain = 0
            for rel, _n in eol_bad:
                full = os.path.join(PLATFORM, rel.replace("/", os.sep))
                blob = blobs.get(rel)
                if blob is None or not os.path.isfile(full):
                    continue
                with open(full, "rb") as f:
                    if f.read() != blob:
                        remain += 1
            if remain:
                print("[FAIL] 修复后仍有 %d 个行尾污染文件与 blob 不一致" % remain)
                return 1
            if real_bad:
                print("[FAIL] 仍有 %d 个真差异文件未处理（--fix 不动它们，需人工确认）" % len(real_bad))
                return 1
            print("[OK ] 修复后工作区与 blob 逐字节一致")
            return 0
        print("修法：python tools/platform/check_worktree_eol.py --fix（从 blob 重新物化行尾污染）")
        print("      注意：`git checkout -- .` 会被 index 的 stat cache 短路，不可靠。")
        return 1
    print("[OK ] 工作区与 blob 逐字节一致（无行尾污染、无真差异）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
