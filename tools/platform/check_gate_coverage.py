# -*- coding: utf-8 -*-
r"""门禁清单对账：CI 跑的门禁 与 本地构建链跑的门禁，必须与唯一清单 gate_manifest.json 一致。

为什么要有这道门禁（2026-11-22 实测）：
    本地 `build_all.py --dist` 全绿，CI 的 build job 却红了 —— 红的不是代码，
    是「离线下载页对外声明的单文件字节数已经过期」。
    根因不是「漏改了一个数字」，而是**检查集合两边不一样**：
        · CI 的 build job 跑 10 项检查；
        · 本地构建链只跑 1 项（check_app_behavior.py）——
          对外文案门禁（check_public_copy.py）本地**根本没跑**。
    ⇒「本地全绿」是个假信号。修法不是再补一道门禁，而是把门禁清单收敛成
    唯一事实源（gate_manifest.json），两边都按它走，这道门禁负责对账。

对账规则（每条都能造错 ⇒ 必须报红）：
    ① 清单里登记的门禁脚本必须真实存在；声明了反向测试的，反向测试也必须存在；
    ② tools/platform/ 下的 check_*.py 与 test_*.py 必须全部登记进清单
       （新增门禁忘了登记 ⇒ 清单与现实脱节）；
    ③ 清单里 in_ci=true 的门禁（及其反向测试），CI 工作流必须显式引用它；
    ④ CI 工作流里引用的门禁，必须都在清单里
       （CI 跑了个清单外的东西 ⇒ 清单漏登记，两边又要漂移）；
    ⑤ 某个门禁若存在 test_<同名>.py，清单里必须把它登记为该门禁的反向测试
       ⇒「新增门禁必须配反向测试」这条纪律被机器化。

用法：
    python tools/platform/check_gate_coverage.py
    python tools/platform/check_gate_coverage.py --manifest <清单> --workflow <yml> --tools-dir <目录>
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
MANIFEST = os.path.join(HERE, "gate_manifest.json")
WORKFLOW = os.path.join(PLATFORM, ".github", "workflows", "deploy.yml")

CI_REF = re.compile(r"tools/platform/([A-Za-z0-9_]+\.py)")
GATE_FILE = re.compile(r"^(?:check|test)_[A-Za-z0-9_]+\.py$")


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        raise ValueError("门禁清单格式不对：gates 必须是非空数组（%s）" % path)
    return data


def ci_referenced(workflow_path):
    """CI 工作流里显式引用到的 tools/platform/*.py。"""
    with open(workflow_path, encoding="utf-8") as f:
        text = f.read()
    return set(CI_REF.findall(text))


def check(manifest_path=MANIFEST, workflow_path=WORKFLOW, tools_dir=HERE):
    """返回错误明细列表（空列表 = 一致）。"""
    errors = []
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return ["门禁清单读不出来：%s" % e]
    gates = manifest["gates"]
    ci = ci_referenced(workflow_path)

    declared_scripts = {}
    declared_reverse = set()
    for g in gates:
        script = g.get("script")
        sid = g.get("id") or script
        if not script:
            errors.append("清单条目 %r 没有 script 字段" % sid)
            continue
        if script in declared_scripts:
            errors.append("清单里 %s 登记了两次" % script)
        declared_scripts[script] = g
        if not os.path.isfile(os.path.join(tools_dir, script)):
            errors.append("清单登记的门禁脚本不存在：tools/platform/%s" % script)
        rt = g.get("reverse_test")
        kind = g.get("kind", "gate")
        if rt:
            declared_reverse.add(rt)
            if not os.path.isfile(os.path.join(tools_dir, rt)):
                errors.append("清单登记的反向测试不存在：tools/platform/%s" % rt)
        elif kind == "gate":
            sibling = "test_%s.py" % os.path.splitext(script)[0]
            if os.path.isfile(os.path.join(tools_dir, sibling)):
                errors.append("门禁 %s 有配套反向测试 %s，但清单里没登记 ⇒ 新增门禁必须配反向测试"
                              % (script, sibling))

    # ② 目录里的门禁/反向测试文件必须都登记进清单
    for fn in sorted(os.listdir(tools_dir)):
        if not GATE_FILE.match(fn):
            continue
        if fn in declared_scripts or fn in declared_reverse:
            continue
        errors.append("tools/platform/%s 是门禁或反向测试，但没有登记进 gate_manifest.json ⇒ 清单与现实脱节" % fn)

    # ③ 清单标了 in_ci=true 的，CI 必须覆盖它
    #    覆盖方式有两种：CI 工作流显式引用它，或它在构建链里
    #    （CI 就是跑 build_all.py 部署的 ⇒ 在构建链里 = CI 也跑）。
    #    反向测试默认是 CI 的活（门禁自己的回归测试），必须显式引用；
    #    也可以用 reverse_in_build_chain 把它挪进构建链。
    for g in gates:
        if not g.get("in_ci"):
            continue
        script = g.get("script")
        if script and script not in ci and not g.get("in_build_chain"):
            errors.append("清单里 %s 标了 in_ci=true，但 CI 既没显式引用它、它也不在构建链里 ⇒ CI 不会跑这道门禁"
                          % script)
        rt = g.get("reverse_test")
        if rt and rt not in ci and not g.get("reverse_in_build_chain"):
            errors.append("清单里 %s 的反向测试 %s 没有被 CI 引用 ⇒ 这道门禁的回归没人跑"
                          % (script, rt))

    # ④ CI 引用的门禁必须在清单里
    for name in sorted(ci):
        if name in declared_scripts or name in declared_reverse:
            continue
        errors.append("CI 工作流引用了 tools/platform/%s，但它不在 gate_manifest.json 里 ⇒ 清单漏登记" % name)

    return errors


def main():
    ap = argparse.ArgumentParser(description="CI 与本地构建链的门禁清单必须一致")
    ap.add_argument("--manifest", default=MANIFEST, help="门禁清单路径")
    ap.add_argument("--workflow", default=WORKFLOW, help="CI 工作流路径")
    ap.add_argument("--tools-dir", default=HERE, help="门禁脚本所在目录")
    args = ap.parse_args()
    errors = check(args.manifest, args.workflow, args.tools_dir)
    if errors:
        print("[FAIL] 门禁清单对账失败")
        for e in errors:
            print("- %s" % e)
        return 1
    print("[OK ] 门禁清单一致：CI 与本地构建链覆盖同一套门禁")
    return 0


if __name__ == "__main__":
    sys.exit(main())
