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
import json
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
import subject_shell                                      # noqa: E402
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


def _fake_subject(tmp, sid, name, desc, stamp_name=None, stamp_desc=None,
                  stamp_offline=None, html=None, render_spec=None):
    """造一个学科壳目录（盖戳清单 + index.html），返回 (目录, manifest 事实)。

    render_spec=None 表示「按平台台账渲染正确链接」；要造错就显式给一个错的 spec。
    """
    sdir = os.path.join(tmp, sid)
    os.makedirs(os.path.join(sdir, "data"), exist_ok=True)
    meta = {"subject": {"name": name, "id": sid}, "summary": {"desc": desc}}
    stamp = {
        "templateVersion": subject_shell.template_version(),
        "name": name if stamp_name is None else stamp_name,
        "desc": desc if stamp_desc is None else stamp_desc,
        "offline": stamp_offline,
    }
    with open(os.path.join(sdir, ".stamp.json"), "w", encoding="utf-8") as f:
        json.dump(stamp, f, ensure_ascii=False, indent=1)
    if html is None:
        spec = subject_shell.offline_spec(sid) if render_spec is None else render_spec
        html = subject_shell.render(subject_shell.read_template(),
                                    stamp["name"], stamp["desc"], spec)
    with open(os.path.join(sdir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return sdir, meta


def _run_identity(tmp, sid, sdir, meta):
    validate_platform.errors.clear()
    validate_platform.check_subject_identity(sid, sdir, meta)
    return list(validate_platform.errors)


def test_subject_identity_gate():
    """T5–T10：壳的身份门禁——**造错必须报错**，好的时候不得误报。

    2026-11-08 实证反面：一次 --restamp 漏传 --name 把五个学科的壳名写空，
    线上标题变成「大学《》题库刷题」，而当时全部门禁全绿——
    因为门禁只会拿盖戳参数去重放模板，参数本身错了它照样通过。
    """
    tmp = tempfile.mkdtemp(prefix="shellgate-")
    name, desc = "演示学科", "演示学科 10 题刷题子站：示例说明。"
    try:
        # T5 盖戳里的壳名为空 → 必须报错（这正是 2026-11-08 线上那副样子）
        sdir, meta = _fake_subject(tmp, "demo", name, desc, stamp_name="")
        errs = _run_identity(tmp, "demo", sdir, meta)
        check("T5 空壳名被门禁拦下", any("壳名为空" in e for e in errs), "errors=%r" % errs[:3])

        # T6 壳名与 manifest 不一致 → 必须报错
        sdir, meta = _fake_subject(tmp, "demo", name, desc, stamp_name="别的学科")
        errs = _run_identity(tmp, "demo", sdir, meta)
        check("T6 壳名与 manifest 不符被拦下", any("与 manifest" in e for e in errs),
              "errors=%r" % errs[:3])

        # T7 index.html 里出现空壳名「大学《》」（壳名对、页面被改坏）→ 必须报错
        sdir, meta = _fake_subject(tmp, "demo", name, desc)
        idx = os.path.join(sdir, "index.html")
        with open(idx, encoding="utf-8") as f:
            good_html = f.read()
        with open(idx, "w", encoding="utf-8", newline="\n") as f:
            f.write(good_html.replace("大学《%s》" % name, "大学《》"))
        errs = _run_identity(tmp, "demo", sdir, meta)
        check("T7 页面里出现「大学《》」被拦下", any("大学《》" in e for e in errs),
              "errors=%r" % errs[:3])

        # T8 描述停在旧题量（manifest 已更新）→ 必须报错
        sdir, meta = _fake_subject(tmp, "demo", name, desc,
                                   stamp_desc="演示学科 8 题刷题子站：示例说明。")
        errs = _run_identity(tmp, "demo", sdir, meta)
        check("T8 陈旧描述被拦下", any("描述" in e for e in errs), "errors=%r" % errs[:3])

        # T9 页脚离线链接与平台台账不符（模板曾把它写死成线代）→ 必须报错
        links = subject_shell.load_offline_links()
        with_link = sorted(links)[0] if links else None
        if with_link:
            wrong = {"url": "https://example.invalid/wrong", "label": "错的离线版"}
            sdir, meta = _fake_subject(tmp, with_link, links[with_link]["label"], desc,
                                       stamp_offline=wrong, render_spec=wrong)
            errs = _run_identity(tmp, with_link, sdir, meta)
            check("T9 页脚离线链接错配被拦下", any("离线链接" in e for e in errs),
                  "errors=%r" % errs[:3])
        else:
            print("  [skip] T9 offline_links.json 为空，无带离线版的学科可测")

        # T10 一切正确 → 不得误报
        sdir, meta = _fake_subject(tmp, "demo", name, desc)
        errs = _run_identity(tmp, "demo", sdir, meta)
        check("T10 正确的壳不误报", not errs, "errors=%r" % errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_facts_precedence():
    """T11：重盖时 manifest 优先于旧盖戳清单。

    题量涨了以后，旧盖戳里的描述就是陈旧的；留着它等于让 meta description
    停在旧题量上（2026-10-31 门户 meta 就是这么悄悄过期了很久）。
    """
    tmp = tempfile.mkdtemp(prefix="facts-")
    try:
        sdir = os.path.join(tmp, "demo")
        os.makedirs(os.path.join(sdir, "data"))
        with open(os.path.join(sdir, "data", "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"subject": {"name": "新名字"}, "summary": {"desc": "新描述 12 题"}},
                      f, ensure_ascii=False)
        with open(os.path.join(sdir, ".stamp.json"), "w", encoding="utf-8") as f:
            json.dump({"templateVersion": "3", "name": "旧名字", "desc": "旧描述 10 题"},
                      f, ensure_ascii=False)
        name, desc = subject_shell.resolve_facts("demo", subjects_dir=tmp)
        check("T11 壳名取 manifest", name == "新名字", "name=%r" % name)
        check("T11 描述取 manifest", desc == "新描述 12 题", "desc=%r" % desc)

        name, desc = subject_shell.resolve_facts("demo", name="命令行优先", subjects_dir=tmp)
        check("T11 命令行参数优先于 manifest", name == "命令行优先", "name=%r" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_new_subject_refuses_empty_name():
    """T12：解析不出壳名时 new_subject.py 必须报错退出，绝不写空壳。"""
    import new_subject
    old_argv = sys.argv
    try:
        # 「ghost」学科：没有 manifest、没有盖戳清单 → 名字解析不出来
        sys.argv = ["new_subject.py", "--id", "ghost"]
        raised = None
        try:
            new_subject.main()
        except SystemExit as e:
            raised = str(e)
        check("T12 解析不出名字时报错退出", raised is not None and "拒绝写出空壳" in raised,
              "raised=%r" % raised)
    finally:
        sys.argv = old_argv


def main():
    print("[test] 平台自检开始")
    test_dist_fallback_branch()
    test_dist_real_cwd_lock()
    test_portal_meta_gate()
    test_portal_meta_roundtrip()
    test_katex_strict_gate()
    test_subject_identity_gate()
    test_resolve_facts_precedence()
    test_new_subject_refuses_empty_name()
    print("-" * 60)
    if failures:
        print("平台自检 FAIL：%d 项 -> %s" % (len(failures), ", ".join(failures)))
        return 1
    print("平台自检全绿。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
