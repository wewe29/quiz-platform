# -*- coding: utf-8 -*-
r"""gate_chain 的反向测试：清单驱动的链**真的**执行了清单里的门禁吗？

用法：python tools/platform/test_gate_chain.py      （失败时退出码非 0）

为什么要有这道测试：
    2026-11-22 的教训是「本地构建链只跑 1 道门禁、CI 跑 10 道 ⇒ 本地全绿是假信号」。
    把清单收敛到 gate_manifest.json 之后，新的风险是：
    **清单写了，但链没真跑**（比如某道门禁被静默跳过、失败被吞掉）。
    ⇒ 这道测试用假的门禁脚本证明：清单里的门禁会被执行、失败会传出来、
      不在构建链里的门禁确实不会被跑。
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gate_chain  # noqa: E402

FAILED = []

STUB_OK = "print('stub ok')\n"
STUB_BAD = "import sys\nprint('stub bad')\nsys.exit(3)\n"
STUB_MARK = ("import os\n"
             "open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ran.txt'), 'w').write('x')\n")


def check(name, ok, detail=""):
    print("  %s %s%s" % ("[OK ]" if ok else "[FAIL]", name, ("  ← " + detail) if (detail and not ok) else ""))
    if not ok:
        FAILED.append(name)


def _tmp():
    d = tempfile.mkdtemp(prefix="gatechain-")
    for fn, body in (("stub_ok.py", STUB_OK), ("stub_bad.py", STUB_BAD), ("stub_mark.py", STUB_MARK)):
        with open(os.path.join(d, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    return d


def _manifest(entries):
    return {"gates": entries}


def _entry(script, in_chain=True):
    return {"id": script[:-3], "script": script, "reverse_test": None,
            "in_ci": False, "in_build_chain": in_chain, "why": "测试用"}


def test_chain_runs_manifest_gate():
    d = _tmp()
    try:
        ok, failures, ran = gate_chain.run_chain(_manifest([_entry("stub_ok.py")]), here=d)
        check("清单里的门禁确实被执行", ok and ran == ["stub_ok"], "ok=%s ran=%s" % (ok, ran))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_failure_propagates():
    d = _tmp()
    try:
        ok, failures, ran = gate_chain.run_chain(_manifest([_entry("stub_bad.py")]), here=d)
        named = any("stub_bad.py" in f[1] for f in failures)
        check("门禁失败必须让整条链失败并点名", (not ok) and named, "ok=%s failures=%s" % (ok, failures))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_not_in_chain_not_run():
    d = _tmp()
    try:
        # 清单里必须至少有一道在构建链里的门禁（空清单＝构建链没跑门禁＝报红），
        # 这里配一道真跑的门禁 + 一道标记门禁，验证标记门禁确实没被执行。
        ok, failures, ran = gate_chain.run_chain(
            _manifest([_entry("stub_ok.py"), _entry("stub_mark.py", in_chain=False)]), here=d)
        marker = os.path.join(d, "ran.txt")
        check("不在构建链里的门禁不会被执行",
              ok and not os.path.isfile(marker) and ran == ["stub_ok"],
              "ok=%s marker=%s ran=%s" % (ok, os.path.isfile(marker), ran))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_missing_script_is_failure():
    d = _tmp()
    try:
        ok, failures, ran = gate_chain.run_chain(_manifest([_entry("stub_absent.py")]), here=d)
        check("清单里的脚本不存在 ⇒ 必须报红（不许静默跳过）",
              (not ok) and any("stub_absent.py" in f[1] for f in failures), "ok=%s failures=%s" % (ok, failures))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_empty_chain_is_failure():
    ok, failures, ran = gate_chain.run_chain({"gates": []}, here=_tmp())
    check("清单为空 ⇒ 必须报红（构建链等于没跑门禁）", not ok, "ok=%s" % ok)


def main():
    print("gate_chain 反向测试（清单驱动的链真的执行清单里的门禁）")
    for fn in (test_chain_runs_manifest_gate,
               test_failure_propagates,
               test_not_in_chain_not_run,
               test_missing_script_is_failure,
               test_empty_chain_is_failure):
        fn()
    if FAILED:
        print("\n[FAIL] %d 项反向测试没过：%s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("\n[OK ] 全部反向测试通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
