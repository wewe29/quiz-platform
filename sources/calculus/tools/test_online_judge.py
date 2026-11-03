# -*- coding: utf-8 -*-
"""tools/test_online_judge.py — 线上核验判据的**反向测试**：造错必须报错，否则门禁是假的。

用法：python tools/test_online_judge.py      （失败时退出码非 0）

覆盖两类东西：
  ① 判据本身（tools/online_judge.py）：
     正例 —— 干净的宿主遥测注入、线上与本地完全一致；
     **反例 —— 正文被改 / 被截断 / 被塞垃圾 / 多出非遥测内容 / 两处改动，
       一律必须判失败。**（尤其 T7：注入块带遥测标记但正文同时被改，
       只看「有没有遥测标记」会误判通过 —— 这正是判据必须「剥块后再逐字节比」的原因。）
  ② 台账（tools/mcode_nodes.json）：
     节点 id / node_id / URL / 基准类型必须齐全，基准路径必须能解析到真实文件；
     并且**必须包含线代单文件站**（2026-11-03 教训：核验器漏了它，它就落后 HEAD 两天）。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from online_judge import build_url, is_telemetry, judge  # noqa: E402

failures = []

HEAD = b"<html><body><p>HEAD</p>"
TAIL = b"<p>BODY</p><p>TAIL</p></body></html>"
LOCAL = HEAD + TAIL
INJECTION = (
    b'<script data-minimax-analytics="minimax-website-analytics-v1">\n'
    b'window.__MINIMAX__={id:"site",v:1};\n'
    b'</script>\n'
    b'<style id="minimax-floating-ball">.fb{position:fixed}</style>\n'
    b'<div id="minimax-floating-ball"></div>\n'
)


def check(name, ok, detail=""):
    if ok:
        print("  [PASS] %s" % name)
    else:
        print("  [FAIL] %s%s" % (name, ("  ← " + detail) if detail else ""))
        failures.append(name)


def test_positives():
    v = judge(LOCAL + INJECTION, LOCAL)
    check("正例：宿主遥测注入（文件末尾）→ 通过", v["ok"], v["reason"])

    v = judge(HEAD + INJECTION + TAIL, LOCAL)
    check("正例：宿主遥测注入（文件中间）→ 通过", v["ok"], v["reason"])

    v = judge(LOCAL, LOCAL)
    check("正例：线上与本地完全一致 → 通过", v["ok"], v["reason"])


def test_negatives():
    # 正文中间被改
    bad = LOCAL.replace(b"BODY", b"BODX")
    v = judge(bad + INJECTION, LOCAL)
    check("反例：正文被改 → 必须失败", not v["ok"], v["reason"])

    # 正文被截断
    v = judge(LOCAL[:40] + INJECTION, LOCAL)
    check("反例：正文被截断 → 必须失败", not v["ok"], v["reason"])

    # 头部被塞垃圾
    v = judge(b"<h1>JUNK</h1>" + LOCAL + INJECTION, LOCAL)
    check("反例：头部被塞垃圾 → 必须失败", not v["ok"], v["reason"])

    # 尾部多出非遥测内容
    v = judge(LOCAL + b"<p>EXTRA</p>", LOCAL)
    check("反例：尾部多出非遥测内容 → 必须失败", not v["ok"], v["reason"])

    # **关键反例**：注入块带遥测标记，但正文同时被改
    tampered = LOCAL.replace(b"BODY", b"BODX") + INJECTION
    v = judge(tampered, LOCAL)
    check("反例：带遥测标记但正文同时被改 → 必须失败", not v["ok"], v["reason"])

    # 两处改动（两块差异）
    v = judge(LOCAL.replace(b"HEAD", b"HEDX") + INJECTION + LOCAL.replace(b"TAIL", b"TALX"), LOCAL)
    check("反例：两处改动（差异变成两块）→ 必须失败", not v["ok"], v["reason"])

    # 差异块没有遥测标记
    v = judge(LOCAL.replace(b"BODY", b"BODX"), LOCAL)
    check("反例：差异块不含遥测标记 → 必须失败", not v["ok"], v["reason"])

    # 线上比本地短且前缀相同
    v = judge(LOCAL[:-20], LOCAL)
    check("反例：线上尾部缺失 → 必须失败", not v["ok"], v["reason"])


def test_helpers():
    check("is_telemetry：认得宿主埋块", is_telemetry(INJECTION))
    check("is_telemetry：拒绝普通 HTML", not is_telemetry(b"<p>hello</p>"))
    check("is_telemetry：拒绝空块", not is_telemetry(b""))

    u1 = build_url("https://x.example/a/b")
    u2 = build_url("https://x.example/a/b")
    check("build_url：追加 ?cb= 参数", "?cb=" in u1, u1)
    check("build_url：两次调用取值不同（绕缓存）", u1 != u2, "%s / %s" % (u1, u2))
    check("build_url：已有查询串时用 & 续接", build_url("https://x.example/a?b=1", cb=42) ==
          "https://x.example/a?b=1&cb=42")


def test_ledger():
    path = os.path.join(HERE, "mcode_nodes.json")
    if not os.path.isfile(path):
        check("台账文件存在", False, path)
        return
    with open(path, "rb") as f:
        ledger = json.loads(f.read().decode("utf-8"))
    check("台账 schema 正确", ledger.get("schema") == "mcode-node-ledger-v1", ledger.get("schema"))
    check("台账写明判据", bool(ledger.get("judge")))

    nodes = ledger.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    check("台账至少 5 个节点", len(nodes) >= 5, "实际 %d" % len(nodes))
    check("台账包含线代单文件站（2026-11-03 漏核验的回归锁）", "linalg-single" in ids, ", ".join(ids))
    for n in nodes:
        nid = n.get("id")
        check("节点 %s 有 node_id" % nid, bool(n.get("node_id")))
        check("节点 %s 的 URL 形如 https://*.space.mcode.cn" % nid,
              (n.get("url") or "").startswith("https://") and ".space.mcode.cn" in (n.get("url") or ""),
              n.get("url"))
        checks = n.get("checks") or []
        check("节点 %s 有核验项" % nid, len(checks) >= 1)
        for spec in checks:
            check("节点 %s 的核验类型已知" % nid, spec.get("type") in ("tree", "file"), spec.get("type"))

    # 基准路径必须能解析到真实文件（根目录不存在时跳过——CI 上路径不同）
    roots = ledger.get("roots") or {}
    missing_roots = [k for k, v in roots.items() if not os.path.isdir(v)]
    if missing_roots:
        print("  [SKIP] 基准路径实存校验：本机根目录缺失 %s" % ", ".join(missing_roots))
    else:
        for n in nodes:
            for spec in n.get("checks") or []:
                raw = spec.get("local") or ""
                root, _, rel = raw.partition(":")
                base = roots.get(root) if root in roots else None
                if base is None:
                    continue
                target = os.path.join(base, rel.replace("/", os.sep))
                if spec.get("type") == "tree":
                    check("节点 %s 的基准目录存在：%s" % (n["id"], raw), os.path.isdir(target), target)
                else:
                    check("节点 %s 的基准文件存在：%s" % (n["id"], raw), os.path.isfile(target), target)


def main():
    print("线上核验判据 —— 反向测试")
    test_positives()
    test_negatives()
    test_helpers()
    test_ledger()
    print()
    if failures:
        print("[结果] %d 项不通过：" % len(failures))
        for f in failures:
            print("   - %s" % f)
        return 1
    print("[结果] 全部通过：判据在正例上放行、在造错上报红")
    return 0


if __name__ == "__main__":
    sys.exit(main())
