# -*- coding: utf-8 -*-
r"""tools/verify_mcode_online.py — mcode 公网站的线上核验

**核验的是「线上 == 当前 HEAD 的成品」，不是「线上 == 某个写死的数字」。**

判据（核心实现见 tools/online_judge.py）：
    剥掉宿主在 </body> 前注入的那一整块遥测内容后，线上文件与本地成品**逐字节相同**。
    ① 注入块大小不是常数（实测高数专站 6,530 B、线代单文件站 1,523 B）
       ⇒ 不能用「线上 = 本地 + 固定字节数」；
    ② 差异必须**只有一块连续插入**且含宿主遥测标记
       ⇒ 线上正文被改过（少一段 / 标签被吃 / 多一段）就会判失败；
    ③ 核验 URL 一律追加 `?cb=<随机>`，绕开 CDN / Service Worker 的旧副本。

**这一道门禁覆盖了语义级断言**：基准文件就是当前 HEAD 的成品，所以「线上是否含某个修复」
不必再单独断言（字节相同 ⇒ 修复在位；字节不同 ⇒ 失败）。这比堆一串零散断言更严。

节点台账见 tools/mcode_nodes.json（node_id / URL / 基准产物的唯一事实源）。
    ⚠ 2026-11-03 的教训：此前这个脚本按站点类型写死分支，**漏了线代单文件站**，
      而那个站恰恰是落后 HEAD 两天的那个 —— 漏核验 = 漂移可以潜伏。

用法：
    python tools\verify_mcode_online.py                # 全部节点
    python tools\verify_mcode_online.py --only linalg-single
    python tools\verify_mcode_online.py --root platform=D:\somewhere\else
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from online_judge import (  # noqa: E402
    build_url, count_questions, fetch, judge, read_file, sha256_bytes,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(HERE, "mcode_nodes.json")

fails = []
notes = []


def check(label, cond, detail=""):
    print("  [%s] %s %s" % ("OK " if cond else "FAIL", label, detail))
    if not cond:
        fails.append("%s %s" % (label, detail))
    return cond


def resolve(spec, roots):
    """`root:relpath` → 绝对路径；绝对路径原样返回。"""
    if ":" in spec:
        root, rel = spec.split(":", 1)
        if root not in roots:
            raise SystemExit("[verify] 台账里的 root %r 不在 roots 中（%s）" % (root, ", ".join(roots)))
        return os.path.join(roots[root], rel.replace("/", os.sep))
    return spec


def walk_files(root):
    """列出目录下所有文件（相对路径，posix 风格），排序保证顺序稳定。"""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            out.append((rel, full))
    out.sort()
    return out


def compare_file(node, spec):
    """一个文件对一个 URL 路径。"""
    local_path = resolve(spec["local"], ROOTS)
    url = node["url"].rstrip("/") + spec.get("url_path", "/")
    if not os.path.isfile(local_path):
        check("本地基准存在 %s" % spec["local"], False, local_path)
        return
    local = read_file(local_path)
    try:
        status, body, hdrs = fetch(url)
    except Exception as e:
        check("可取 %s" % spec.get("url_path", "/"), False, str(e))
        return
    if status != 200:
        check("HTTP 200 %s" % spec.get("url_path", "/"), False, "status=%d" % status)
        return
    v = judge(body, local)
    check("%s 与本地逐字节一致（线上 %d B / 本地 %d B）"
          % (spec.get("url_path", "/"), len(body), len(local)), v["ok"], v["reason"])
    n_q = count_questions(body)
    if n_q is not None:
        notes.append("%s：单文件内联题库 %d 题" % (node["label"], n_q))
    print("    Last-Modified: %s" % (hdrs.get("Last-Modified") or hdrs.get("last-modified") or "—"))


def compare_tree(node, spec):
    """整棵树逐文件比对。"""
    local_root = resolve(spec["local"], ROOTS)
    url_prefix = spec.get("url_prefix", "").strip("/")
    if not os.path.isdir(local_root):
        check("本地基准目录存在 %s" % spec["local"], False, local_root)
        return
    files = walk_files(local_root)
    if not files:
        check("本地基准目录非空 %s" % spec["local"], False, local_root)
        return
    print("    基准 %s：%d 个文件" % (spec["local"], len(files)))
    bad = []
    total_bytes = 0
    for rel, full in files:
        url = node["url"].rstrip("/") + "/" + ((url_prefix + "/") if url_prefix else "") + rel
        local = read_file(full)
        try:
            status, body, hdrs = fetch(url)
        except Exception as e:
            bad.append("%s 取失败：%s" % (rel, e))
            continue
        if status != 200:
            bad.append("%s status=%d" % (rel, status))
            continue
        v = judge(body, local)
        if not v["ok"]:
            bad.append("%s：%s" % (rel, v["reason"]))
        total_bytes += len(local)
    check("%d 个文件全部与本地一致（合计 %d B）" % (len(files), total_bytes),
          not bad, "" if not bad else "；".join(bad[:6]) + ("…" if len(bad) > 6 else ""))
    # 题量口径（人眼对账用，不参与判定）
    reg = os.path.join(local_root, "subjects", "registry.json")
    idx = os.path.join(local_root, "data", "index.json")
    if os.path.isfile(reg):
        try:
            r = json.loads(read_file(reg).decode("utf-8"))
            notes.append("%s：题量合计 %d（%s）" % (
                node["label"], sum(x["total"] for x in r["subjects"]),
                ", ".join("%s %d" % (x["id"], x["total"]) for x in r["subjects"])))
        except Exception:
            pass
    if os.path.isfile(idx):
        try:
            j = json.loads(read_file(idx).decode("utf-8"))
            notes.append("%s：题量 %s" % (node["label"], j.get("total")))
        except Exception:
            pass


def parse_args(argv):
    ap = argparse.ArgumentParser(description="mcode 公网站线上核验（线上 == 当前 HEAD 成品）")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER, help="节点台账路径")
    ap.add_argument("--only", default="", help="只核验这些节点 id（逗号分隔）")
    ap.add_argument("--root", action="append", default=[], metavar="NAME=PATH",
                    help="覆盖台账里的 root（可重复）")
    return ap.parse_args(argv)


def main(argv=None):
    global ROOTS
    args = parse_args(argv or sys.argv[1:])
    with open(args.ledger, "rb") as f:
        ledger = json.loads(f.read().decode("utf-8"))
    ROOTS = dict(ledger.get("roots") or {})
    for item in args.root:
        if "=" not in item:
            raise SystemExit("[verify] --root 格式应为 NAME=PATH")
        k, v = item.split("=", 1)
        ROOTS[k] = v
    only = [x.strip() for x in args.only.split(",") if x.strip()]

    print("判据：%s" % ledger.get("judge"))
    print("台账：%s（更新于 %s，%d 个节点）" % (args.ledger, ledger.get("updated"), len(ledger["nodes"])))
    print("根目录：" + "；".join("%s=%s" % (k, v) for k, v in sorted(ROOTS.items())))

    for node in ledger["nodes"]:
        if only and node["id"] not in only:
            continue
        print("\n--- %s（%s）" % (node["label"], node["id"]))
        print("    %s   node_id=%s" % (node["url"], node.get("node_id", "—")))
        for spec in node.get("checks") or []:
            if spec.get("type") == "tree":
                compare_tree(node, spec)
            elif spec.get("type") == "file":
                compare_file(node, spec)
            else:
                check("台账 check 类型已知", False, spec.get("type"))

    print()
    for n in notes:
        print("  · %s" % n)
    if fails:
        print("[结果] %d 项不通过：" % len(fails))
        for f in fails:
            print("   - %s" % f)
        print("提醒：字节不一致先看是「线上落后 HEAD」还是「本地基准没重建」，再决定补发还是重建。")
        return 1
    print("[结果] 全部线上核验通过：线上 == 当前 HEAD 成品（剥掉宿主遥测块后逐字节相同）")
    print("提醒：字节一致 ≠ 渲染正确 ≠ 交互正确 —— 发布后还要在浏览器里实答一次，并查控制台。")
    return 0


ROOTS = {}

if __name__ == "__main__":
    sys.exit(main())
