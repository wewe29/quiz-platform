# -*- coding: utf-8 -*-
r"""平台总构建：对 sources/ 里登记的每个学科跑「完整门禁 + 产物导出」，再生成注册表并校验。

用法：
    python tools/platform/build_all.py            # 全量构建 + 校验
    python tools/platform/build_all.py --dist     # 校验通过后组装 dist/（Pages 部署目录）

学科登记：sources/<id>/tools 必须存在（由各学科工作区同步而来）；
产物写到 subjects/<id>/。CI 与本机共用这一个入口——CI 就是部署者，不存在构建漂移。
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))

sys.path.insert(0, HERE)   # portal_meta 与本脚本同目录；被当模块导入时也要能找到
from portal_meta import describe as portal_desc, read_meta, apply_meta  # noqa: E402


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


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel_files(root):
    """目录下的文件清单（相对路径 → 字节数），跳过 __pycache__ 与 .pyc（复制时同样跳过）。"""
    out = {}
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            p = os.path.join(r, fn)
            out[os.path.relpath(p, root).replace("\\", "/")] = os.path.getsize(p)
    return out


def _clear_dist(dist):
    """把 dist/ 准备成一个干净目录，返回处置方式（打印实况，便于事后追因）。

    Windows 特例：若某进程把当前工作目录放在 dist/ 里（典型是本地预览服务器
    直接 `cd dist` 起 http.server，忘了文档里写的 `-d dist`），
    shutil.rmtree 能删光内容却删不掉目录本身，抛 WinError 32——
    2026-10-31 实测这一下把整条流水线打断，dist/ 变成 0 文件的空目录。

    这里：重试删除 → 仍失败就退化为「就地清空 + 复用目录」，
    构建不因为一个预览进程而死。
    """
    if not os.path.isdir(dist):
        os.makedirs(dist)
        return "新建"
    for _ in range(3):
        try:
            shutil.rmtree(dist)
            os.makedirs(dist)
            return "重建"
        except OSError as e:
            if getattr(e, "winerror", None) not in (5, 32):
                raise
            time.sleep(0.5)
    leftover = []
    for entry in sorted(os.listdir(dist)):
        p = os.path.join(dist, entry)
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        except OSError:
            leftover.append(entry)
    if leftover:
        print("[warn] dist/ 有 %d 项被占用未清除：%s" % (len(leftover), ", ".join(leftover[:5])))
        return "就地清空（%d 项残留）" % len(leftover)
    return "就地清空"


def _verify_dist(dist):
    """组装后逐字节核对 dist/ 与源目录一致——不轻信 copytree 的成功返回。"""
    problems = []
    for name in ("index.html", "sw.js", "manifest.webmanifest"):
        s = os.path.join(PLATFORM, name)
        d = os.path.join(dist, name)
        if not os.path.isfile(d):
            problems.append("缺 %s" % name)
        elif _sha256(s) != _sha256(d):
            problems.append("%s 字节不一致" % name)
    for name in ("assets", "subjects"):
        s = os.path.join(PLATFORM, name)
        d = os.path.join(dist, name)
        if not os.path.isdir(d):
            problems.append("缺 %s/" % name)
            continue
        ss, ds = _rel_files(s), _rel_files(d)
        missing = sorted(set(ss) - set(ds))
        extra = sorted(set(ds) - set(ss))
        if missing:
            problems.append("%s/ 缺 %d 个文件（如 %s）" % (name, len(missing), missing[:3]))
        if extra:
            problems.append("%s/ 多出 %d 个文件（如 %s）" % (name, len(extra), extra[:3]))
        for rel in sorted(set(ss) & set(ds)):
            if ss[rel] != ds[rel]:
                problems.append("%s/%s 大小不符（%d != %d）" % (name, rel, ss[rel], ds[rel]))
    return problems


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
    # 学科门禁链里的单文件构建（build_quiz）需要 KaTeX 发行版：
    # 统一注入平台级 vendor 路径，任何镜像都不必各自携带 3MB dist（CI/异机同理）。
    platform_katex = os.path.join(PLATFORM, "tools", "vendor", "katex", "dist")
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
            extra_env={"QUIZ_PROJECT_DIR": env_tmp, "KATEX_DIR": platform_katex})
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

    # 门户 meta 文案跟着 registry 走（口径单一事实源）：加学科/改题量后文案不会过期。
    # 2026-10-31 实证过反面：ML 与数可视早已上线，文案还写着「接计划接入」。
    portal_path = os.path.join(PLATFORM, "index.html")
    with open(portal_path, encoding="utf-8", newline="") as f:
        html = f.read()
    want_desc = portal_desc(registry["subjects"])
    if read_meta(html) != want_desc:
        with open(portal_path, "w", encoding="utf-8", newline="") as f:
            f.write(apply_meta(html, want_desc))
        print("[sync] 门户 meta description 已按 registry 重写")

    print("=" * 60)
    run([sys.executable, os.path.join(HERE, "validate_platform.py")], cwd=HERE, label="平台校验")

    if args.dist:
        dist = os.path.join(PLATFORM, "dist")
        mode = _clear_dist(dist)
        for name in ("index.html", "sw.js", "manifest.webmanifest", "assets", "subjects"):
            src = os.path.join(PLATFORM, name)
            dst = os.path.join(dist, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src, dst)
        problems = _verify_dist(dist)
        if problems:
            print("[FAIL] dist/ 与源目录不一致：")
            for p in problems[:20]:
                print("       " + p)
            raise SystemExit("[build_all] dist 组装校验失败，中止。")
        n = sum(len(fs) for _, _, fs in os.walk(dist))
        size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dist) for f in fs)
        print("[OK ] dist/ 组装完成（%s）：%d 个文件 / %.2f MB，逐字节核对通过"
              % (mode, n, size / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
