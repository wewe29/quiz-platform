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

sys.path.insert(0, HERE)   # portal_meta 与本脚本同目录
from portal_meta import describe as portal_desc, read_meta  # noqa: E402

SHARD_BUDGET = 200 * 1024          # 单分片字节上限
SHELL_BUDGET = 300 * 1024          # 学科壳（html + js + css，不含 vendor/data）上限
PORTAL_BUDGET = 100 * 1024         # 门户（index.html + portal js/css）上限

REQUIRED_Q_FIELDS = ["id", "type", "typeGroup", "difficulty", "chapter",
                     "knowledgePoint", "source", "stem", "answer", "explanation"]
TYPES = {"single", "multi", "judge", "blank", "term", "short", "calc"}
DIFFS = {"basic", "medium", "hard"}
SUBJECTIVE = {"term", "short", "calc"}

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
                # 跨学科规则：主观题必须有参考答案与 ≥1 个采分点（含分值）；
                # 采分点「数量」的学科口径由各学科自己的门禁管（线代 2/3/4 点、高数 1–6 点不定），
                # 平台端只保证满分（Σpartial）可计算。
                if not q.get("answerText"):
                    err("%s/%s: 主观题缺参考答案" % (sid, q["id"]))
                pts = q.get("points") or []
                if not pts:
                    err("%s/%s: 主观题缺采分点" % (sid, q["id"]))
                else:
                    total_partial = 0
                    for p in pts:
                        if isinstance(p, dict) and p.get("text"):
                            total_partial += p.get("partial") or 2
                        else:
                            err("%s/%s: 采分点不是 {text,partial} 结构" % (sid, q["id"]))
                            break
                    if total_partial <= 0:
                        err("%s/%s: 采分点分值合计 ≤ 0" % (sid, q["id"]))
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


def check_subject_shell(sid, sdir):
    """壳防分叉（D15）+ 模块接线（R2）：
    1) core/*.js、app.js、subject.css 必须与模板字节一致；index.html 必须等于模板按
       .stamp.json 重放替换的结果——改共享前端必须走模板 + new_subject --restamp；
    2) index.html 必须引用全部 core 模块与 app.js/subject.js/KaTeX；app.js 必须真实
       调用 LAStore/LABank（R2：不建没有调用方的模块）。"""
    tpl = os.path.join(HERE, "template_subject")
    stamp_p = os.path.join(sdir, ".stamp.json")
    if not os.path.isfile(stamp_p):
        err("%s: 缺 .stamp.json（用 tools/platform/new_subject.py 盖章）" % sid)
        return
    with open(stamp_p, encoding="utf-8") as f:
        stamp = json.load(f)

    for rel in ("assets/js/app.js", "assets/js/core/store.js",
                "assets/js/core/bank.js", "assets/css/subject.css"):
        t, s = os.path.join(tpl, rel), os.path.join(sdir, rel)
        if not os.path.isfile(s):
            err("%s: 缺 %s" % (sid, rel))
            continue
        if open(t, "rb").read() != open(s, "rb").read():
            err("%s: %s 与模板不一致（改模板后需 new_subject.py --restamp）" % (sid, rel))

    tpl_html = open(os.path.join(tpl, "index.html"), encoding="utf-8").read()
    expect_html = tpl_html.replace("__SUBJECT_NAME__", stamp.get("name", "")) \
                          .replace("__SUBJECT_DESC__", stamp.get("desc", ""))
    idx = os.path.join(sdir, "index.html")
    if os.path.isfile(idx):
        got = open(idx, encoding="utf-8").read()
        if got != expect_html:
            err("%s: index.html 与模板盖章结果不一致（D15）" % sid)
        for need in ("core/store.js", "core/bank.js", "assets/js/app.js",
                     "assets/js/subject.js", "katex.min.js", "auto-render.min.js"):
            if need not in got:
                err("%s: index.html 未引用 %s" % (sid, need))
    app_js = os.path.join(sdir, "assets", "js", "app.js")
    if os.path.isfile(app_js):
        txt = open(app_js, encoding="utf-8").read()
        for sym in ("LAStore", "LABank"):
            if sym not in txt:
                err("%s: app.js 未调用 %s（R2 未接线）" % (sid, sym))


def check_pwa(platform):
    """PWA 结构门禁（迭代 3）：manifest / 图标 / sw.js / 页面注册齐备。
    Lighthouse 打分属托管方自测（部署不在本项目范围）；这里拦「结构性缺失」。"""
    mf = os.path.join(platform, "manifest.webmanifest")
    if not os.path.isfile(mf):
        err("缺 manifest.webmanifest")
        return
    try:
        m = json.load(open(mf, encoding="utf-8"))
        for k in ("name", "start_url", "display", "icons"):
            if k not in m:
                err("manifest.webmanifest 缺 %s" % k)
        icons = m.get("icons") or []
        if not any(i.get("src", "").endswith(".png") for i in icons):
            warn("manifest 图标缺 PNG（部分浏览器安装要求 PNG）")
        for i in icons:
            p = os.path.join(platform, i.get("src", ""))
            if not os.path.isfile(p):
                err("manifest 图标不存在：%s" % i.get("src"))
    except Exception as e:
        err("manifest.webmanifest 解析失败：%s" % e)

    sw = os.path.join(platform, "sw.js")
    if not os.path.isfile(sw):
        err("缺 sw.js")
    else:
        txt = open(sw, encoding="utf-8").read()
        for need in ("activate", "SKIP_WAITING", "caches.delete"):
            if need not in txt:
                err("sw.js 缺 %s（版本清理/SKIP_WAITING 是更新横幅的前提）" % need)

    for rel in ("index.html", os.path.join("subjects", "linalg", "index.html"),
                os.path.join("subjects", "calculus", "index.html")):
        p = os.path.join(platform, rel)
        if not os.path.isfile(p):
            continue
        txt = open(p, encoding="utf-8").read()
        if "serviceWorker" not in txt:
            err("%s 缺 SW 注册脚本" % rel)
        if "sw-banner" not in txt:
            err("%s 缺 SW 更新横幅" % rel)
    print("  [pwa] manifest/sw/注册/横幅 结构齐备" if not errors else "  [pwa] 见 FAIL 项")


def check_portal_meta(platform, subjects):
    """门户 meta 文案必须与 registry 一致（口径单一事实源，防手改漂移）。

    2026-10-31 实证过反面：ML 与数可视早已上线，meta 仍写着「接计划接入」，
    线上对外文案是错的，而当时全部门禁全绿——因为没有任何一道门禁看这句文案。
    """
    p = os.path.join(platform, "index.html")
    if not os.path.isfile(p):
        err("缺门户 index.html")
        return
    html = open(p, encoding="utf-8").read()
    got = read_meta(html)
    want = portal_desc(subjects)
    if got is None:
        err('门户 index.html 缺 <meta name="description">')
    elif got != want:
        err("门户 meta description 与 registry 不一致：\n        期望：%s\n        实际：%s"
            % (want, got))


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

    check_portal_meta(PLATFORM, list(listed.values()))

    for sid in sorted(listed):
        print("  [check] 学科 %s" % sid)
        check_subject(subjects_dir, sid)
        check_subject_shell(sid, os.path.join(subjects_dir, sid))

    check_pwa(PLATFORM)

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
