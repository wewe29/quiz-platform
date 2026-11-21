# -*- coding: utf-8 -*-
r"""门禁链执行器：本地构建链与 CI 跑的是**同一份清单**。

为什么要有这个文件（2026-11-22 实测）：
    本地 `build_all.py --dist` 全绿，CI 的 build job 却红了。
    红的不是代码，是「离线下载页对外声明的单文件字节数已经过期」。
    查下来的根因不是「漏改了一个数字」，而是**检查集合两边不一样**：
        · CI 的 build job 跑 10 项检查；
        · 本地构建链只跑 1 项（check_app_behavior.py）——
          对外文案门禁（check_public_copy.py）本地**根本没跑**。
    ⇒「本地全绿」是个假信号：本地永远发现不了对外文案的数字过期。
    修法不是再补一道门禁，而是把**门禁清单收敛成唯一事实源**
    （gate_manifest.json），两边都按它走，check_gate_coverage.py 负责对账。

清单条目字段：
    script            门禁脚本文件名（tools/platform/ 下）
    reverse_test      该门禁的反向测试文件名（没有就写 null）
    in_ci             CI（.github/workflows/deploy.yml）必须显式引用它
    in_build_chain    本地构建链必须跑它
    requires_dist     该门禁要读真实 dist/ 的体积 ⇒ 只有本次构建组装了 dist/ 才能跑
    args              传给门禁的额外参数
    needs_single_file 该门禁需要单文件产物（构建链会先构建再把路径传进去）
    why               这道门禁为什么存在（写下来，别让它变成没人知道为什么的摆设）

用法：
    python tools/platform/gate_chain.py             # 跑一遍构建链门禁
    python tools/platform/gate_chain.py --dry-run   # 只列清单，不执行
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
MANIFEST = os.path.join(HERE, "gate_manifest.json")


def load_manifest(path=None):
    """读门禁清单；格式不对就直接报错，不当通过。"""
    path = path or MANIFEST
    if not os.path.isfile(path):
        raise SystemExit("[gate_chain] 找不到门禁清单：%s" % path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        raise SystemExit("[gate_chain] 门禁清单格式不对（gates 必须是非空数组）：%s" % path)
    return data


def chain_gates(manifest):
    """构建链要跑的门禁（按清单顺序，不自己另排一套）。"""
    return [g for g in manifest["gates"] if g.get("in_build_chain")]


def build_single_file(out_path):
    """构建高数单文件离线包 —— 对外文案页声明的那个字节数的基准。

    与 CI 的 build job 同一条命令、同一个 KaTeX 源（平台仓 vendor），
    所以本地跑出来的字节数 = CI 跑出来的字节数 = 线上发出去的字节数。
    """
    src = os.path.join(PLATFORM, "sources", "calculus", "tools", "build_single.py")
    if not os.path.isfile(src):
        raise SystemExit("[gate_chain] 找不到单文件构建器：%s" % src)
    katex = os.path.join(PLATFORM, "tools", "vendor", "katex", "dist")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", KATEX_DIR=katex)
    p = subprocess.run([sys.executable, src, "--out=" + out_path],
                       cwd=os.path.dirname(src), env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    if p.returncode != 0:
        for l in out.splitlines()[-10:]:
            print("      " + l)
        raise SystemExit("[gate_chain] 单文件包构建失败 —— 对外文案门禁没有事实源可比")
    return out_path


def run_chain(manifest, here=HERE, dry_run=False, dist_ready=True):
    """按清单逐道跑构建链门禁。

    返回 (ok, failures, ran)：
        failures = [(id, script, 原因), ...]
        ran      = 实际跑过的门禁 id 列表
    故意**不**在第一道失败就退出：一次把全部失败摆出来，省得来回试。

    dist_ready=False 表示本次构建**没有**组装 dist/ ⇒ 需要真实 dist/ 的门禁
    （check_plan_doc）跳过，但必须**显式说明跳过原因**，不许静默当通过
    （"解析不到断言也必须报红"是同一条纪律）。
    """
    failures = []
    ran = []
    gates = chain_gates(manifest)
    if not gates:
        return (False, [("-", "-", "清单里没有任何 in_build_chain 的门禁 —— 构建链等于没跑门禁")], ran)

    single_path = None
    if any(g.get("needs_single_file") for g in gates) and not dry_run:
        tmp_dir = os.path.join(PLATFORM, ".build-tmp", "single-file")
        os.makedirs(tmp_dir, exist_ok=True)
        single_path = os.path.join(tmp_dir, "calculus-quiz-offline.html")
        print("[gate_chain] 构建单文件包（对外文案声明字节数的基准）…")
        build_single_file(single_path)

    for g in gates:
        script = g.get("script")
        label = g.get("id") or script
        if not script:
            failures.append((label, "-", "清单条目没有 script 字段"))
            continue
        path = os.path.join(here, script)
        if not os.path.isfile(path):
            failures.append((label, script, "门禁脚本不存在：%s" % path))
            continue
        if g.get("requires_dist") and not dist_ready:
            print("[注意] 门禁 %-22s 跳过：本次构建没有组装 dist/，它的断言没有事实源可对（不装作通过）" % label)
            continue
        args = list(g.get("args") or [])
        if g.get("needs_single_file"):
            if not single_path:
                failures.append((label, script, "需要单文件产物，但没能构建出来"))
                continue
            args += ["--single-file", single_path]
        if dry_run:
            print("[dry-run] %-22s %s %s" % (label, script, " ".join(args)))
            continue
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, path] + args, cwd=here, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        lines = [l for l in out.splitlines() if l.strip()]
        ok = p.returncode == 0
        print("[%s] 门禁 %-22s %s" % ("OK " if ok else "FAIL", label, script))
        for l in lines[-8:]:
            print("      " + l)
        ran.append(label)
        if not ok:
            failures.append((label, script, "退出码 %d" % p.returncode))
    return (not failures), failures, ran


def main():
    ap = argparse.ArgumentParser(description="按唯一清单跑构建链门禁")
    ap.add_argument("--manifest", default=MANIFEST, help="门禁清单路径")
    ap.add_argument("--dry-run", action="store_true", help="只列清单，不执行")
    args = ap.parse_args()
    manifest = load_manifest(args.manifest)
    ok, failures, ran = run_chain(manifest, dry_run=args.dry_run)
    if args.dry_run:
        return 0
    print("[gate_chain] 构建链门禁共 %d 道" % len(ran))
    if failures:
        for label, script, why in failures:
            print("[FAIL] 门禁 %s（%s）：%s" % (label, script, why))
        return 1
    print("[OK ] 构建链门禁全绿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
