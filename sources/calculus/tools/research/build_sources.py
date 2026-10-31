# -*- coding: utf-8 -*-
r"""真题素材清单：汇总每一份源卷面的出处，并逐条验证链接可访问。

产出：
    tools/research/sources.json      结构化清单（机读）
    tools/research/真题素材摘要.md    人读摘要

用法：
    python tools/research/build_sources.py            # 生成 + 校验
    python tools/research/build_sources.py --no-net   # 只生成不联网
"""
import collections
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from qa_bank import load_bank  # noqa: E402

URL_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/blob/main/(.+)$")

REPO_DESC = {
    ("TsekaLuk", "Kaoyan-Math1-Papers"): {
        "name": "考研数学（一）真题与解析",
        "desc": "全国硕士研究生招生考试数学（一）历年真题（papers/）"
                "与逐题答案解析（solutions/）。",
        "license": "见仓库 LICENSE（社区整理）",
    },
    ("TsekaLuk", "Kaoyan-Math2-Papers"): {
        "name": "考研数学（二 / 三）真题与解析",
        "desc": "1987–2024 年考研数学二（1987–1996 年卷面标为「试卷三」）真题，"
                "解析文件里题干与解析同在，按题号切块即可；"
                "2020–2024 仅有原卷题目、无答案解析，故只采用 1987–2019。",
        "license": "见仓库 LICENSE（社区整理）",
    },
    ("huangnaisheng", "zikao-exam-solutions"): {
        "name": "自考 00023《高等数学（工本）》历年真题与逐题解析",
        "desc": "高等教育自学考试《高等数学（工本）》（课程代码 00023）历年真题，"
                "逐题给出答案、考点、解析与易错提醒。",
        "license": "见仓库 LICENSE（社区整理）",
    },
}


def head_ok(url, timeout=20):
    # 源卷面文件名带中文（1987年考研数学(一)真题.md），URL 必须先做百分号编码，
    # 否则 urllib 会拿 ASCII 去编码而直接抛 UnicodeEncodeError。
    safe = ":/?&=#%"
    enc = urllib.parse.quote(url, safe=safe)
    req = urllib.request.Request(enc, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0 (qa-bank-audit)")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, "HTTP %d" % e.code
    except Exception as e:
        return 0, str(e)[:120]


def head_ok_many(urls, workers=16):
    """并发做 HEAD 校验。

    串行跑 600+ 条要十几分钟（本机到 GitHub 单条可达 0.3–2 s），
    后台任务会被 900 s 上限打断，所以这里用线程池。
    """
    from concurrent.futures import ThreadPoolExecutor
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(head_ok, u): u for u in urls}
        for fut in futs:
            u = futs[fut]
            try:
                results[u] = fut.result()
            except Exception as e:
                results[u] = (0, str(e)[:120])
    return results


def main():
    no_net = "--no-net" in sys.argv
    bank = load_bank()
    exams = [q for q in bank if (q.get("provenance") or {}).get("level") == "original"]

    by_url = collections.defaultdict(list)
    for q in exams:
        prov = q.get("provenance") or {}
        url = prov.get("url")
        if not url:
            continue
        by_url[url].append(q)

    entries = []
    for url in sorted(by_url):
        qs = by_url[url]
        m = URL_RE.match(url)
        owner, repo, path = (m.group(1), m.group(2), m.group(3)) if m else ("", "", url)
        years = sorted({q.get("source", {}).get("year") for q in qs
                        if isinstance(q.get("source"), dict) and q["source"].get("year")})
        papers = sorted({q.get("source", {}).get("paper") for q in qs
                         if isinstance(q.get("source"), dict) and q["source"].get("paper")})
        regions = sorted({q.get("source", {}).get("region") for q in qs
                          if isinstance(q.get("source"), dict) and q["source"].get("region")})
        entry = {
            "url": url,
            "repo": "%s/%s" % (owner, repo),
            "path": path,
            "years": years,
            "papers": papers,
            "regions": regions,
            "count": len(qs),
            "kinds": sorted({t for t in ("高考真题", "考研真题", "自考真题")
                             for q in qs if t in (q.get("tags") or [])}),
        }
        if not no_net:
            entry["httpStatus"] = None
            entry["reachable"] = None
        else:
            entry["reachable"] = None
        entries.append(entry)

    if not no_net:
        print("[net] 并发 HEAD 校验 %d 条链接…" % len(entries), flush=True)
        results = head_ok_many([e["url"] for e in entries])
        for e in entries:
            code, err = results.get(e["url"], (0, "no result"))
            e["httpStatus"] = code
            e["reachable"] = (code == 200)
            if err:
                e["error"] = err
        ok = sum(1 for e in entries if e["reachable"])
        print("[net] 可达 %d / %d" % (ok, len(entries)), flush=True)

    out = {
        "generatedAt": "2026-10-28",
        "questionCount": len(exams),
        "sourceFileCount": len(entries),
        "repos": [
            dict({"id": "%s/%s" % k}, **v, fileCount=sum(
                1 for e in entries if e["repo"] == "%s/%s" % k))
            for k, v in REPO_DESC.items()],
        "sources": entries,
    }
    path_json = os.path.join(HERE, "sources.json")
    with io.open(path_json, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1))

    # ---- 人读摘要 ----
    by_repo = collections.defaultdict(list)
    for e in entries:
        by_repo[e["repo"]].append(e)
    md = []
    md.append("# 真题素材摘要\n")
    md.append("题库真题共 **%d** 道，分布在 **%d** 份源卷面文件中，"
              "全部来自 %d 个公开仓库。\n" % (len(exams), len(entries), len(by_repo)))
    md.append("> 溯源级别：全部为 `original`（原题），题号 / 年份 / 地区 / 卷别均取自"
              "源卷面文件自带的字段，未做任何编造。\n")
    md.append("## 素材来源\n")
    for repo, es in sorted(by_repo.items(), key=lambda kv: -len(kv[1])):
        meta = REPO_DESC.get(tuple(repo.split("/", 1)))
        md.append("### %s\n" % repo)
        if meta:
            md.append("- **名称**：%s" % meta["name"])
            md.append("- **内容**：%s" % meta["desc"])
            md.append("- **许可**：%s" % meta["license"])
        md.append("- **本库收录**：%d 道，来自 %d 份卷面文件\n" %
                  (sum(e["count"] for e in es), len(es)))
        kinds = sorted({k for e in es for k in e["kinds"]})
        years = sorted({y for e in es for y in e["years"]})
        md.append("- **年份跨度**：%s" % ("—".join(str(y) for y in years) if years else "—"))
        md.append("- **标签**：%s" % ("、".join(kinds) if kinds else "—"))
        if not no_net:
            ok = sum(1 for e in es if e.get("reachable"))
            md.append("- **链接可达性**：%d / %d 条返回 200\n" % (ok, len(es)))
    md.append("## 逐份卷面\n")
    md.append("| 仓库 | 卷面 | 年份 | 地区 | 题数 | 链接 | 可达 |")
    md.append("|---|---|---|---|---|---|---|")
    for e in entries:
        md.append("| %s | %s | %s | %s | %d | [卷面](%s) | %s |" % (
            e["repo"], e["papers"][0] if e["papers"] else "—",
            "/".join(str(y) for y in e["years"]) or "—",
            "/".join(e["regions"]) or "—",
            e["count"], e["url"],
            ("200" if e.get("reachable") else
             ("未校验" if e.get("reachable") is None else "失败"))))
    md.append("")
    path_md = os.path.join(HERE, "真题素材摘要.md")
    with io.open(path_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))

    print("真题 %d 道，源卷面 %d 份" % (len(exams), len(entries)))
    for repo, es in sorted(by_repo.items(), key=lambda kv: -len(kv[1])):
        ok = sum(1 for e in es if e.get("reachable") is True)
        fail = [e for e in es if e.get("reachable") is False]
        print("   %-46s %4d 道 / %3d 份  可达 %s" % (
            repo, sum(e["count"] for e in es), len(es),
            ("%d/%d" % (ok, len(es))) if not no_net else "未校验"))
        for e in fail[:5]:
            print("        ✗ %s  %s" % (e["url"], e.get("error", "")))
    print("写出：%s" % path_json)
    print("写出：%s" % path_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
