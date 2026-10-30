# -*- coding: utf-8 -*-
r"""平台总构建：对 sources/ 里登记的每个学科跑「完整门禁 + 产物导出」，再生成注册表并校验。

用法：
    python tools/platform/build_all.py            # 全量构建 + 校验
    python tools/platform/build_all.py --dist     # 校验通过后组装 dist/（Pages 部署目录）

学科登记：sources/<id>/tools 必须存在（由各学科工作区同步而来）；
产物写到 subjects/<id>/。CI 与本机共用这一个入口——CI 就是部署者，不存在构建漂移。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))


def run(cmd, cwd, label, extra_env=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if extra_env:
        env.update(extra_env)
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    lines = [l for l in out.splitlines() if l.strip()]
    print("[%s] %s" % ("OK " if p.returncode == 0 else "FAIL", label))
    for l in lines[-8:]:
        print("      " + l)
    if p.returncode != 0:
        raise SystemExit("[build_all] %s 失败，中止。" % label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", action="store_true", help="校验通过后组装 dist/")
    ap.add_argument("--skip-gates", action="store_true", help="透传给 build_subject（仅调试）")
    args = ap.parse_args()

    sources = os.path.join(PLATFORM, "sources")
    ids = sorted(d for d in os.listdir(sources)
                 if os.path.isdir(os.path.join(sources, d)) and os.path.isdir(os.path.join(sources, d, "tools")))
    if not ids:
        raise SystemExit("[build_all] sources/ 下没有登记任何学科（应有 sources/<id>/tools）")

    extra = ["--skip-gates"] if args.skip_gates else []
    for sid in ids:
        print("=" * 60)
        print("[subject] %s" % sid)
        out = os.path.join(PLATFORM, "subjects", sid)
        # 门禁链里的单文件构建（update_site）会把成品写到「项目根」；
        # 平台构建把它重定向到临时目录，避免 1.6MB 副产品污染 sources/。
        env_tmp = os.path.join(PLATFORM, ".build-tmp", sid)
        os.makedirs(env_tmp, exist_ok=True)
        run([sys.executable, os.path.join(sources, sid, "tools", "build_subject.py"),
             "--out", out] + extra,
            cwd=os.path.join(sources, sid, "tools"), label="%s 门禁+导出" % sid,
            extra_env={"QUIZ_PROJECT_DIR": env_tmp})
        run([sys.executable, os.path.join(HERE, "katex_assets.py"),
             "--subject-dir", out],
            cwd=HERE, label="%s KaTeX 自托管" % sid)

    # 注册表：门户唯一数据源（题量/章节数/真题标注数全部来自 manifest，门户不手写）
    registry = {"schema": "quiz-platform-registry-v1", "subjects": []}
    for sid in ids:
        mpath = os.path.join(PLATFORM, "subjects", sid, "data", "manifest.json")
        with open(mpath, encoding="utf-8") as f:
            m = json.load(f)
        registry["subjects"].append({
            "id": sid,
            "name": m["subject"]["name"],
            "textbook": m["subject"]["textbook"],
            "url": "subjects/%s/" % sid,
            "total": m["caliber"]["total"],
            "chapters": m["subject"]["chapters"],
            "realExamTagged": (m.get("summary") or {}).get("realExamTagged", 0),
        })
    with open(os.path.join(PLATFORM, "subjects", "registry.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(registry, f, ensure_ascii=False, indent=1)
    print("[OK ] registry.json：%s" % ", ".join("%s=%d题" % (s["id"], s["total"]) for s in registry["subjects"]))

    print("=" * 60)
    run([sys.executable, os.path.join(HERE, "validate_platform.py")], cwd=HERE, label="平台校验")

    if args.dist:
        dist = os.path.join(PLATFORM, "dist")
        if os.path.isdir(dist):
            shutil.rmtree(dist)
        os.makedirs(dist)
        for name in ("index.html", "assets", "subjects"):
            src = os.path.join(PLATFORM, name)
            dst = os.path.join(dist, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src, dst)
        size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dist) for f in fs)
        print("[OK ] dist/ 组装完成：%.2f MB" % (size / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
