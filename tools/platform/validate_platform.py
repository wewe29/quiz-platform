# -*- coding: utf-8 -*-
"""平台产物校验器：schema / manifest 一致性 / 分片结构 / 体积预算 / 外链扫描。

任何一项 FAIL 都以非零码退出——部署 workflow 依赖这一点拦截坏发布。
门禁分工：内容门禁（SymPy 复核、答案键自洽等）在学科 build_subject.py 里跑，
本文件只管「平台契约」：产物结构完整、数字对得上、体积不超标、无外部依赖。
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))

SHARD_BUDGET = 200 * 1024          # 单分片字节上限
SHELL_BUDGET = 300 * 1024          # 学科壳（html + js + css，不含 vendor/data）上限
PORTAL_BUDGET = 100 * 1024         # 门户（index.html + portal js/css）上限

REQUIRED_Q_FIELDS = ["id", "type", "typeGroup", "difficulty", "chapter",
                     "knowledgePoint", "source", "stem", "answer", "explanation"]
TYPES = {"single", "multi", "judge", "blank", "term", "short", "calc"}
DIFFS = {"basic", "medium", "hard"}
SUBJECTIVE = {"term": 2, "short": 3, "calc": 4}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def check_subject(subjects_dir, sid):
    sdir = os.path.join(subjects_dir, sid)
    mpath = os.path.join(sdir, "data", "manifest.json")
    if not os.path.isfile(mpath):
        err("%s: 缺 data/manifest.json" % sid)
        return None
    with open(mpath, encoding="utf-8") as f:
        m = json.load(f)

    if m.get("schema") != "quiz-platform-subject-v1":
        err("%s: manifest.schema 非法：%r" % (sid, m.get("schema")))
    sub = m.get("subject") or {}
    for k in ("id", "name", "textbook", "bankId", "chapters", "chapterLabels"):
        if k not in sub:
            err("%s: manifest.subject 缺 %s" % (sid, k))
    if sub.get("id") != sid:
        err("%s: manifest.subject.id=%r 与目录名不符" % (sid, sub.get("id")))

    # 分片：存在、哈希、题数
    total = 0
    by_diff = {}
    for s in m.get("shards", []):
        p = os.path.join(sdir, "data", s["file"])
        if not os.path.isfile(p):
            err("%s: 分片缺失 %s" % (sid, s["file"]))
            continue
        size = os.path.getsize(p)
        if size > SHARD_BUDGET:
            err("%s: 分片 %s（%d 字节）超预算 %d" % (sid, s["file"], size, SHARD_BUDGET))
        if sha256(p) != s.get("sha256"):
            err("%s: 分片 %s SHA256 与 manifest 不符（先跑 build_all 再发布）" % (sid, s["file"]))
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        qs = data.get("questions", [])
        if len(qs) != s.get("count"):
            err("%s: 分片 %s 题数 %d != manifest %d" % (sid, s["file"], len(qs), s.get("count")))
        if data.get("chapter") != s.get("chapter"):
            err("%s: 分片 %s chapter 与 manifest 不符" % (sid, s["file"]))
        for q in qs:
            total += 1
            for k in REQUIRED_Q_FIELDS:
                if k not in q:
                    err("%s/%s: 缺字段 %s" % (sid, q.get("id", "?"), k))
            if q.get("type") not in TYPES:
                err("%s/%s: type 非法 %r" % (sid, q.get("id", "?"), q.get("type")))
            if q.get("difficulty") not in DIFFS:
                err("%s/%s: difficulty 非法 %r" % (sid, q.get("id", "?"), q.get("difficulty")))
            opts = q.get("options") or []
            if q.get("type") in ("single", "multi", "judge"):
                letters = "ABCDE"[:len(opts)]
                if not opts:
                    err("%s/%s: 客观题缺选项" % (sid, q["id"]))
                for a in q.get("answer") or []:
                    if a not in letters:
                        err("%s/%s: 答案 %r 不在选项内" % (sid, q["id"], a))
                if q["type"] in ("single", "judge") and len(q.get("answer") or []) != 1:
                    err("%s/%s: 单选/判断答案数 != 1" % (sid, q["id"]))
                if q["type"] == "multi" and len(q.get("answer") or []) < 2:
                    err("%s/%s: 多选答案数 < 2" % (sid, q["id"]))
            if q.get("type") in SUBJECTIVE:
                if not q.get("answerText"):
                    err("%s/%s: 主观题缺参考答案" % (sid, q["id"]))
                pts = q.get("points") or []
                if len(pts) != SUBJECTIVE[q["type"]]:
                    err("%s/%s: 采分点数 %d != %d" % (sid, q["id"], len(pts), SUBJECTIVE[q["type"]]))
            by_diff[q.get("difficulty")] = by_diff.get(q.get("difficulty"), 0) + 1

    cal = m.get("caliber") or {}
    if cal.get("total") != total:
        err("%s: caliber.total=%r != 实际题数 %d" % (sid, cal.get("total"), total))
    if cal.get("byDifficulty") != by_diff:
        err("%s: caliber.byDifficulty 与分片实况不符：%r vs %r" % (sid, cal.get("byDifficulty"), by_diff))
    ids = set()
    dup = []
    for s in m.get("shards", []):
        p = os.path.join(sdir, "data", s["file"])
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            for q in json.load(f).get("questions", []):
                if q["id"] in ids:
                    dup.append(q["id"])
                ids.add(q["id"])
    if dup:
        err("%s: 重复题号 %s" % (sid, sorted(dup)[:8]))

    # 壳体积预算（html + js + css，不含 vendor 与 data）
    shell = 0
    for root, dirs, files in os.walk(sdir):
        rel = os.path.relpath(root, sdir)
        if rel.startswith("assets" + os.sep + "vendor") or rel == "data":
            continue
        for fn in files:
            shell += os.path.getsize(os.path.join(root, fn))
    if shell > SHELL_BUDGET:
        err("%s: 壳体积 %d 字节超预算 %d" % (sid, shell, SHELL_BUDGET))
    else:
        print("  [%s] 壳 %6.1f KB / 预算 %d KB" % (sid, shell / 1024.0, SHELL_BUDGET // 1024))
    return m


def check_external_refs(platform):
    """站点文件（门户+子站，不含 sources/tools）不得引用 http(s) 外部「自动加载资源」：
    script/img/iframe/source/video/audio 的 src、link 的 href。
    页面正文里的说明性 <a href> 链接不拦截（那是指路，不是加载）。"""
    pat_res = re.compile(
        r'<(?:script|img|iframe|source|video|audio)\b[^>]*?\ssrc\s*=\s*["\']([^"\']*)["\']'
        r'|<link\b[^>]*?\shref\s*=\s*["\']([^"\']*)["\']', re.I)
    for root, dirs, files in os.walk(platform):
        rel = os.path.relpath(root, platform)
        top = rel.split(os.sep)[0]
        if top in ("sources", "tools", ".git", ".github", "docs", "dist"):
            dirs[:] = []
            continue
        for fn in files:
            if not fn.endswith(".html"):
                continue
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8") as f:
                html = f.read()
            for m in pat_res.finditer(html):
                ref = (m.group(1) or m.group(2) or "").strip()
                if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("//"):
                    err("%s: 外部自动加载资源 %s" % (os.path.relpath(p, platform), ref[:80]))


def main():
    subjects_dir = os.path.join(PLATFORM, "subjects")
    reg_path = os.path.join(subjects_dir, "registry.json")
    if not os.path.isfile(reg_path):
        err("缺 subjects/registry.json（build_all.py 生成）")
    else:
        with open(reg_path, encoding="utf-8") as f:
            reg = json.load(f)
        listed = {s["id"]: s for s in reg.get("subjects", [])}
        actual = sorted(d for d in os.listdir(subjects_dir)
                        if os.path.isdir(os.path.join(subjects_dir, d)) and d != "registry.json")
        for sid in actual:
            if sid not in listed:
                err("registry.json 缺学科 %s（重新跑 build_all.py）" % sid)
        for sid in listed:
            if sid not in actual:
                err("registry.json 里的 %s 没有对应目录" % sid)

    portal_size = 0
    for fn in ("index.html", os.path.join("assets", "css", "tokens.css"),
               os.path.join("assets", "css", "portal.css"), os.path.join("assets", "js", "portal.js")):
        p = os.path.join(PLATFORM, fn)
        if os.path.isfile(p):
            portal_size += os.path.getsize(p)
    if portal_size > PORTAL_BUDGET:
        err("门户体积 %d 字节超预算 %d" % (portal_size, PORTAL_BUDGET))
    else:
        print("  [portal] %6.1f KB / 预算 %d KB" % (portal_size / 1024.0, PORTAL_BUDGET // 1024))

    for sid in sorted(listed):
        print("  [check] 学科 %s" % sid)
        check_subject(subjects_dir, sid)

    check_external_refs(PLATFORM)

    for w in warnings:
        print("  [warn] %s" % w)
    print("-" * 60)
    if errors:
        print("平台校验 FAIL：%d 项" % len(errors))
        for e in errors:
            print("  [FAIL] %s" % e)
        return 1
    print("平台校验通过（schema / manifest / 结构 / 预算 / 外链）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
