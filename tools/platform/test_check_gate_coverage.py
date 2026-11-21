# -*- coding: utf-8 -*-
r"""check_gate_coverage 的反向测试：**造错必须报错**，好的时候不得误报。

用法：python tools/platform/test_check_gate_coverage.py      （失败时退出码非 0）

这道门禁本身守的是「门禁清单不许漂」：
    · CI 引用了清单外的门禁 ⇒ 必须报红（否则清单会慢慢烂掉）；
    · 清单里有 CI 没跑的门禁 ⇒ 必须报红（否则等于没加）；
    · 目录里新增了门禁却没登记 ⇒ 必须报红；
    · 门禁没配反向测试 ⇒ 必须报红；
    · 同时：仓库现状必须通过（不得误报）。
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import check_gate_coverage as cgc  # noqa: E402

FAILED = []


def check(name, ok, detail=""):
    print("  %s %s%s" % ("[OK ]" if ok else "[FAIL]", name, ("  ← " + detail) if (detail and not ok) else ""))
    if not ok:
        FAILED.append(name)


def _env(tmp, manifest_mutator=None, workflow_mutator=None, extra_files=None):
    """搭一套临时的（清单 / 工作流 / 门禁目录），可注入漂移。"""
    tools = os.path.join(tmp, "tools")
    shutil.copytree(HERE, tools, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    man_path = os.path.join(tmp, "gate_manifest.json")
    shutil.copy2(os.path.join(HERE, "gate_manifest.json"), man_path)
    wf_path = os.path.join(tmp, "deploy.yml")
    shutil.copy2(cgc.WORKFLOW, wf_path)
    if manifest_mutator:
        with open(man_path, encoding="utf-8") as f:
            data = json.load(f)
        manifest_mutator(data)
        with open(man_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    if workflow_mutator:
        with open(wf_path, encoding="utf-8") as f:
            text = f.read()
        text = workflow_mutator(text)
        with open(wf_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    for name, content in (extra_files or {}).items():
        with open(os.path.join(tools, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return man_path, wf_path, tools


def _errors(**kw):
    tmp = tempfile.mkdtemp(prefix="gatecov-")
    try:
        man, wf, tools = _env(tmp, **kw)
        return cgc.check(man, wf, tools)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _mentions(errors, *keys):
    blob = "\n".join(errors)
    return [k for k in keys if k not in blob]


def test_positive():
    errs = _errors()
    check("正样本：仓库现状必须通过（不得误报）", errs == [], "; ".join(errs[:3]))


def test_ci_references_unknown_gate():
    errs = _errors(workflow_mutator=lambda t: t + "\n          python tools/platform/check_ghost.py\n")
    missing = _mentions(errs, "check_ghost.py")
    check("CI 引用了清单外的门禁 ⇒ 必须报红并点名", not missing, "没提到：%s" % missing)


def test_manifest_gate_not_in_ci():
    def mut(data):
        data["gates"].append({
            "id": "phantom", "script": "check_phantom.py", "reverse_test": None,
            "in_ci": True, "in_build_chain": False, "why": "注入用",
        })
    errs = _errors(manifest_mutator=mut,
                   extra_files={"check_phantom.py": "# 注入用\n"})
    missing = _mentions(errs, "check_phantom.py", "CI 不会跑这道门禁")
    check("清单标 in_ci=true 但 CI 没引用 ⇒ 必须报红并点名", not missing, "没提到：%s" % missing)


def test_manifest_script_missing():
    def mut(data):
        data["gates"].append({
            "id": "absent", "script": "check_absent.py", "reverse_test": None,
            "in_ci": False, "in_build_chain": False, "why": "注入用",
        })
    errs = _errors(manifest_mutator=mut)
    missing = _mentions(errs, "check_absent.py", "不存在")
    check("清单登记了不存在的门禁脚本 ⇒ 必须报红并点名", not missing, "没提到：%s" % missing)


def test_new_gate_not_registered():
    errs = _errors(extra_files={"check_brand_new.py": "# 新增但没登记\n"})
    missing = _mentions(errs, "check_brand_new.py", "清单与现实脱节")
    check("目录里新增门禁却没登记 ⇒ 必须报红并点名", not missing, "没提到：%s" % missing)


def test_gate_without_reverse_test():
    def mut(data):
        for g in data["gates"]:
            if g.get("script") == "check_plan_doc.py":
                g["reverse_test"] = None
    errs = _errors(manifest_mutator=mut)
    missing = _mentions(errs, "check_plan_doc.py", "必须配反向测试")
    check("门禁有配套反向测试却没登记 ⇒ 必须报红并点名", not missing, "没提到：%s" % missing)


def main():
    print("check_gate_coverage 反向测试（造错必须报错，好的时候不得误报）")
    for fn in (test_positive,
               test_ci_references_unknown_gate,
               test_manifest_gate_not_in_ci,
               test_manifest_script_missing,
               test_new_gate_not_registered,
               test_gate_without_reverse_test):
        fn()
    if FAILED:
        print("\n[FAIL] %d 项反向测试没过：%s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("\n[OK ] 全部反向测试通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
