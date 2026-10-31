# -*- coding: utf-8 -*-
"""平台自检（回归测试）：**造错必须报错**，否则门禁是假的。

用法：python tools/platform/test_platform_gates.py      （失败时退出码非 0）

覆盖两件 2026-10-31 实证踩过的事：
  T1 dist 文件锁——预览服务器把 CWD 放在 dist/ 里，shutil.rmtree 删得掉内容却删不掉
     目录本身（WinError 32），2026-10-31 这一下把整条构建流水线打断，dist/ 变成空目录。
  T2 门户 meta 漂移——ML/数可视早已上线，meta 还写着「接计划接入」，而当时全部门禁全绿，
     因为没有任何一道门禁看这句文案。

Windows 特例说明：真实目录锁只在 Windows 上成立（Linux 下进程 CWD 不阻止 rmtree），
所以 T1 分两半——「降级分支」在所有平台都确定性验证，「真实文件锁」仅 Windows 跑。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import build_all                                          # noqa: E402
import validate_platform                                  # noqa: E402
from portal_meta import describe as portal_desc, read_meta, apply_meta  # noqa: E402

failures = []


def check(name, ok, detail=""):
    if ok:
        print("  [PASS] %s" % name)
    else:
        print("  [FAIL] %s%s" % (name, ("  ← " + detail) if detail else ""))
        failures.append(name)


def _make_winerror32():
    e = OSError(32, "另一个程序正在使用此文件，无法访问")
    e.winerror = 32
    return e


def test_dist_fallback_branch():
    """T1a（所有平台）：rmtree 连抛 WinError 32 时，_clear_dist 必须降级成功而不是炸掉。"""
    tmp = tempfile.mkdtemp(prefix="distfallback-")
    real_rmtree = shutil.rmtree
    calls = {"n": 0}

    def flaky(path, *a, **kw):
        calls["n"] += 1
        if calls["n"] <= 3:      # 前三次=重试循环，全部失败→必须走降级分支
            raise _make_winerror32()
        return real_rmtree(path, *a, **kw)

    try:
        with open(os.path.join(tmp, "stale.txt"), "w", encoding="utf-8") as f:
            f.write("old")
        with open(os.path.join(tmp, "sub"), "w", encoding="utf-8") as f:
            f.write("x")
        shutil.rmtree = flaky
        try:
            mode = build_all._clear_dist(tmp)
        finally:
            shutil.rmtree = real_rmtree
        check("T1a 连抛 WinError32 后降级不炸", True, "mode=%s" % mode)
        check("T1a 降级后目录仍可用", os.path.isdir(tmp) and not os.listdir(tmp),
              "内容=%r" % (os.listdir(tmp) if os.path.isdir(tmp) else None))
        shutil.copy2(__file__, os.path.join(tmp, "again.txt"))
        check("T1a 降级后目录可再写入", os.path.isfile(os.path.join(tmp, "again.txt")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_dist_real_cwd_lock():
    """T1b（仅 Windows）：子进程把 CWD 放在待清目录里，_clear_dist 必须照样成功。

    同步方式不用 sleep 赌时间：子进程在自己 CWD 里写下 ready.flag，
    父进程看到该文件即证明「子进程已初始化且 CWD 锁定生效」。
    （Popen 返回时子进程尚未完成初始化，直接 rmtree 会赢下竞态——这正是
      2026-10-31 那次「以为复现不了」的原因。）
    """
    if os.name != "nt":
        print("  [skip] T1b 真实文件锁仅 Windows 有效（本机 %s）" % os.name)
        return
    import time
    tmp = tempfile.mkdtemp(prefix="distlock-")
    child = None
    try:
        with open(os.path.join(tmp, "stale.txt"), "w", encoding="utf-8") as f:
            f.write("old")
        flag = os.path.join(tmp, "ready.flag")
        child = subprocess.Popen(
            [sys.executable, "-c",
             "import time; open('ready.flag','w').close(); time.sleep(30)"],
            cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 15
        while not os.path.isfile(flag) and time.time() < deadline:
            time.sleep(0.05)
        check("T1b 子进程已在目标目录内就位", os.path.isfile(flag))

        # 证明「锁是真的」：此刻直接 rmtree 必须失败
        try:
            shutil.rmtree(tmp)
            locked = False
        except OSError as e:
            locked = getattr(e, "winerror", None) == 32
        check("T1b 目录锁真实存在（直接 rmtree 失败）", locked)
        if not os.path.isdir(tmp):
            os.makedirs(tmp, exist_ok=True)

        mode = build_all._clear_dist(tmp)
        check("T1b 被占用的 dist 仍能清空", os.path.isdir(tmp) and not os.listdir(tmp),
              "mode=%s 内容=%r" % (mode, os.listdir(tmp) if os.path.isdir(tmp) else None))
        shutil.copy2(__file__, os.path.join(tmp, "again.txt"))
        check("T1b 清空后目录可复用", os.path.isfile(os.path.join(tmp, "again.txt")))
    finally:
        if child is not None:
            child.terminate()
            try:
                child.wait(timeout=10)
            except Exception:
                child.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def test_portal_meta_gate():
    """T2：门户 meta 与 registry 不一致必须被拦；一致时不得误报。"""
    tmp = tempfile.mkdtemp(prefix="metagate-")
    idx = os.path.join(tmp, "index.html")
    subjects = [{"name": "线性代数", "total": 500}, {"name": "机器学习", "total": 244}]
    try:
        with open(idx, "w", encoding="utf-8") as f:
            f.write('<html><head><meta name="description" content="过时文案：机器学习接计划接入">'
                    "</head><body></body></html>")
        validate_platform.errors.clear()
        validate_platform.check_portal_meta(tmp, subjects)
        caught = any("meta description" in e for e in validate_platform.errors)
        check("T2 过时 meta 被门禁拦下", caught, "errors=%r" % validate_platform.errors[:2])

        with open(idx, "w", encoding="utf-8") as f:
            f.write('<html><head><meta name="description" content="%s"></head></html>'
                    % portal_desc(subjects))
        validate_platform.errors.clear()
        validate_platform.check_portal_meta(tmp, subjects)
        check("T2 一致时不误报", not validate_platform.errors, "errors=%r" % validate_platform.errors[:2])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_portal_meta_roundtrip():
    """T3：文案生成/写回/读回自洽，且按题量降序。"""
    subjects = [{"name": "线性代数", "total": 500}, {"name": "机器学习", "total": 244}]
    desc = portal_desc(subjects)
    out = apply_meta('<meta name="description" content="旧">', desc)
    check("T3 写回后可读回", read_meta(out) == desc)
    check("T3 按题量降序排列", desc.index("线性代数") < desc.index("机器学习"), desc)
    check("T3 总题数出现在文案里", "744" in desc, desc)


def test_katex_strict_gate():
    """T4：数学模式里的裸中文 / 控制字符必须被拦；干净内容不得误报。

    2026-10-31 实证：概率论并入时解析里写了 `$P(阳)=...$`，KaTeX 每次渲染都报
    `unicodeTextInMathMode` 警告，**而当时全部门禁全绿**——没有任何一道门禁看公式内容。
    另外还查出一类更隐蔽的：源码里 `\\text` 少写一个反斜杠 → Python 解析成 TAB；
    以及概率论题库里残留的 NUL 字符（`\\u0000`）——两者都让公式渲染出乱码。
    """
    tmp = tempfile.mkdtemp(prefix="katexgate-")
    data_dir = os.path.join(tmp, "demo", "data")
    os.makedirs(data_dir)
    listed = {"demo": {"id": "demo", "total": 1}}

    def run(payload):
        with open(os.path.join(data_dir, "ch1.json"), "w", encoding="utf-8") as f:
            f.write(payload)
        validate_platform.errors.clear()
        validate_platform.check_katex_strict(tmp, listed)
        return list(validate_platform.errors)

    try:
        errs = run('{"questions":[{"explanation":"$P(\\u0028阳\\u0029)=0.059$"}]}')
        check("T4 裸中文被门禁拦下", any("裸中文" in e for e in errs), "errors=%r" % errs[:2])

        errs = run('{"questions":[{"explanation":"$P(\\t ext)=1$"}]}')
        check("T4 控制字符被门禁拦下", any("控制字符" in e for e in errs), "errors=%r" % errs[:2])

        errs = run('{"questions":[{"explanation":"$P(\\\\text{阳})=0.059$"}]}')
        check("T4 正确写法不误报", not errs, "errors=%r" % errs[:2])

        # 散文夹在两个数学段之间 → 不是数学段，不该被当成裸中文
        errs = run('{"questions":[{"explanation":"$N$ 的列都是齐次方程 $(A-E)y=0$ 的解"}]}')
        check("T4 数学段之间的散文不误报", not errs, "errors=%r" % errs[:2])

        # 多行显示公式里的换行是正常写法
        errs = run('{"questions":[{"explanation":"$$\\\\frac{1}{2}$$"}]}')
        check("T4 换行不误报", not errs, "errors=%r" % errs[:2])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print("[test] 平台自检开始")
    test_dist_fallback_branch()
    test_dist_real_cwd_lock()
    test_portal_meta_gate()
    test_portal_meta_roundtrip()
    test_katex_strict_gate()
    print("-" * 60)
    if failures:
        print("平台自检 FAIL：%d 项 -> %s" % (len(failures), ", ".join(failures)))
        return 1
    print("平台自检全绿。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
