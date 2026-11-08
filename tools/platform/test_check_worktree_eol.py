# -*- coding: utf-8 -*-
"""tools/platform/test_check_worktree_eol.py — 行尾污染门禁的反向测试：造错必须报错。

用法：python tools/platform/test_check_worktree_eol.py      （失败时退出码非 0）

为什么要有它（2026-11-07 实测事故）：
    工作区文件是 CRLF、blob 是 LF 时，**git 的 diff 报「无差异」** ——
    因为 index 的 stat cache 记的就是 CRLF 尺寸，git 连内容都不读就判「未变」；
    `text=auto` 又让它在真去比的时候也归一。两层掩护之下，污染能长期潜伏，
    直到字节级核验才发现两条发布渠道差 1,716 字节。
    ⇒ 必须有一道**逐字节**的门禁，并且它自己也要被反向测试：
        ① 干净仓 → 退出 0；
        ② 注入 CRLF 污染 → 必须退出 1；
        ③ git diff 对污染报「无差异」，而门禁必须报出来；
        ④ 注入真内容差异 → 必须退出 1；
        ⑤ 二进制文件 → 必须跳过（不误报）。
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "check_worktree_eol.py")

_spec = importlib.util.spec_from_file_location("check_worktree_eol", MOD)
cw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cw)

FAILS = []


def case(name, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True)


def make_repo(base):
    repo = os.path.join(base, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "gate@example.com")
    git(repo, "config", "user.name", "gate")
    # ⚠ 必须复现**事故现场的配置**：本机系统级 `core.autocrlf=true`，
    # 而平台仓按 D21 设了 local `core.autocrlf=false` 覆盖它。
    # 只有在这个配置下，CRLF 工作区文件才会让 `git status` 报「干净」——
    # 那正是污染能长期潜伏的原因（换个配置 git 反而会报 modified）。
    git(repo, "config", "core.autocrlf", "false")
    write(os.path.join(repo, "a.txt"), b"line1\nline2\n")
    write(os.path.join(repo, "b.py"), b"x = 1\n")
    write(os.path.join(repo, "bin.dat"), b"\x00\x01\x02binary\r\n")
    with open(os.path.join(repo, ".gitattributes"), "wb") as f:
        f.write(b"* text=auto eol=lf\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def run_gate(repo, paths=()):
    """把门禁的 PLATFORM 指到临时仓再跑（门禁是从仓根推导路径的）。"""
    old = cw.PLATFORM
    cw.PLATFORM = repo
    try:
        argv = []
        for p in paths:
            argv += ["--path", p]
        return cw.main(argv)
    finally:
        cw.PLATFORM = old


def main():
    base = tempfile.mkdtemp(prefix="eol_gate_test_")
    try:
        repo = make_repo(base)

        print("T1 干净仓：必须退出 0")
        case("干净仓退出 0", run_gate(repo) == 0)

        print("T2 注入行尾污染：工作区 CRLF、blob LF → 必须退出 1")
        write(os.path.join(repo, "a.txt"), b"line1\r\nline2\r\n")
        case("污染被检出", run_gate(repo) == 1)

        print("T3 关键：git 的 diff 对这类污染**完全看不见**（报「无差异」）—— 门禁必须看得见")
        d = git(repo, "diff", "--numstat").stdout
        case("git diff 确实报无差异（所以需要这道门禁）", d.strip() == b"", repr(d))
        case("门禁仍能检出", run_gate(repo) == 1)

        print("T4 修法有效：git checkout 后必须退出 0")
        git(repo, "checkout", "--", "a.txt")
        case("checkout 后退出 0", run_gate(repo) == 0)

        print("T5 注入真内容差异：必须退出 1")
        write(os.path.join(repo, "b.py"), b"x = 999\n")
        case("真差异被检出", run_gate(repo) == 1)
        git(repo, "checkout", "--", "b.py")
        case("恢复后退出 0", run_gate(repo) == 0)

        print("T6 二进制文件不得误报（bin.dat 里有 CRLF 与 NUL）")
        write(os.path.join(repo, "bin.dat"), b"\x00\x01\x02binary\r\n")
        case("二进制不误报", run_gate(repo) == 0)

        print("T7 --path 只检查指定前缀")
        write(os.path.join(repo, "a.txt"), b"line1\r\nline2\r\n")
        case("只查 b.py 时不报 a.txt 的污染", run_gate(repo, paths=("b.py",)) == 0)
        case("查 a.txt 时报污染", run_gate(repo, paths=("a.txt",)) == 1)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if FAILS:
        print("反向测试失败 %d 项：%s" % (len(FAILS), FAILS))
        return 1
    print("反向测试全绿：污染必报错、二进制不误报、git 看不见的那类差异被抓住。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
