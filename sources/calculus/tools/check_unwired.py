# -*- coding: utf-8 -*-
"""「定义了却从没接线」门禁。

背景：本轮实测抓到两类同源缺陷——
  · card.setBadge()  整个项目从未被调用 → 答题卡计数恒为「0 题」
  · stats.recompute() 整个项目从未被调用 → 统计面板整块是 0 / 「暂无数据」
两者单测都测不出来（单测直接调函数），数据门禁也测不出来
（数据是对的，只是渲染/装配层没接上）。

做法：扫 assets/js 下每个模块的导出对象 `ns.<mod> = { ... }`，
把导出块从源码文本里摘掉，然后统计每个导出名在剩余代码里的
「属性访问」`.name` 与「直接调用」`name(` 次数（减去它自己的函数定义）。
两者都是 0 ⇒ 这个导出从来没被任何地方用到 ⇒ 悬空导出。

用法：
    python tools/check_unwired.py            # 与基线比对，有新增悬空导出就失败
    python tools/check_unwired.py --list     # 只打印当前清单
    python tools/check_unwired.py --update   # 把当前清单写成基线
退出码非 0 表示出现了新的悬空导出。

为什么要基线：
    项目里本来就有一批「导出了但暂时没接线」的工具型 API
    （dom.pct / schema.TYPES / bank.setBasePath …），它们不是缺陷。
    所以规则是「**不许新增**」：基线里的已登记，新增的直接失败。
    这样本轮抓到的 card.setBadge / stats.recompute 两类真缺陷
    （导出了却从没被调用 ⇒ 整块功能是死的）能被拦住，
    又不会把已有工具 API 误判成错误。
"""
from __future__ import print_function

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JS_DIR = os.path.join(HERE, "assets", "js")
BASELINE = os.path.join(HERE, "unwired_baseline.txt")

EXPORT_START_RE = re.compile(r"ns\.([A-Za-z_$][\w$]*)\s*=\s*\{")


def _match_block(text, open_idx):
    """从 '{' 处扫描到配对的 '}'，跳过字符串字面量。返回结束位置（'}' 的下标）。"""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            quote = c
            i += 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == quote:
                    break
                i += 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def find_export_blocks(text):
    """返回 [(模块名, 导出块完整文本, 块内顶层键名列表)]。

    不能用正则：单行导出 `ns.catalog = { kpLabel: ... };` 与多行导出会互相串味，
    非贪婪匹配会从一行导出的 '{' 一路吞到后面某个 '\n  };'，
    把中间整段业务代码当成「导出块」删掉 —— 实测导致 39 个假阳性。
    """
    out = []
    for m in EXPORT_START_RE.finditer(text):
        brace = text.index("{", m.end() - 1)
        end = _match_block(text, brace)
        if end < 0:
            continue
        block = text[m.start():end + 1]
        inner = text[brace + 1:end]
        names = []
        for part in inner.split(","):
            part = part.strip()
            if not part:
                continue
            mm = re.match(r"([A-Za-z_$][\w$]*)\s*:", part)
            if mm:
                names.append(mm.group(1))
        out.append((m.group(1), block, names))
    return out


def collect():
    """返回 (exports, sources)：exports = {模块: [导出名...]}，sources = {相对路径: 文本}"""
    exports = {}
    sources = {}
    for root, dirs, files in os.walk(JS_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in sorted(files):
            if not fn.endswith(".js"):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, JS_DIR).replace("\\", "/")
            text = io.open(p, encoding="utf-8").read()
            sources[rel] = text
            for mod, block, names in find_export_blocks(text):
                exports.setdefault(mod, []).extend(names)
    return exports, sources


def collect_gate_sources():
    """tools/ 下的门禁脚本也算「使用点」。

    有些导出只有构建门禁在用（例如 filters.chipKeys —— 门禁要用它验证
    「点这个 chip 能选出题」）。这类导出是活的，不该被算成悬空。
    """
    out = {}
    if not os.path.isdir(HERE):
        return out
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".js"):
            continue
        p = os.path.join(HERE, fn)
        if not os.path.isfile(p):
            continue
        out["tools/" + fn] = io.open(p, encoding="utf-8").read()
    return out


def main():
    exports, sources = collect()

    # 把所有导出块从文本里摘掉，剩下的才是「真正的使用点」
    stripped = {}
    for rel, text in sources.items():
        blocks = find_export_blocks(text)
        out = text
        for mod, block, names in sorted(blocks, key=lambda b: -len(b[1])):
            out = out.replace(block, "")
        stripped[rel] = out

    all_text = "\n".join(stripped.values())
    # 门禁脚本（tools\*.js）里的调用也是真实使用点
    for rel, text in sorted(collect_gate_sources().items()):
        all_text += "\n" + text
    # 去掉注释，避免注释里的名字被当成使用点
    all_text = re.sub(r"/\*.*?\*/", "", all_text, flags=re.S)
    all_text = re.sub(r"//[^\n]*", "", all_text)

    dead = []
    for mod, names in sorted(exports.items()):
        for name in sorted(set(names)):
            prop = len(re.findall(r"\." + re.escape(name) + r"\b", all_text))
            calls = len(re.findall(r"(?<![\w.$])" + re.escape(name) + r"\s*\(", all_text))
            if re.search(r"function\s+" + re.escape(name) + r"\s*\(", all_text):
                calls -= 1              # 减去它自己的函数定义
            if prop == 0 and calls <= 0:
                dead.append("%s.%s" % (mod, name))
    dead.sort()

    print("[unwired] 扫描模块 %d 个，导出 %d 个" % (len(exports), sum(len(v) for v in exports.values())))
    print("[unwired] 当前悬空导出 %d 个" % len(dead))

    if "--list" in sys.argv:
        for d in dead:
            print("  %s" % d)
        return 0

    if "--update" in sys.argv:
        io.open(BASELINE, "w", encoding="utf-8", newline="\n").write("\n".join(dead) + "\n")
        print("[unwired] 基线已更新：%s" % BASELINE)
        return 0

    baseline = []
    if os.path.exists(BASELINE):
        baseline = [l.strip() for l in io.open(BASELINE, encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print("[unwired] 没有基线文件 %s（用 --update 生成）" % BASELINE)
        return 1

    known = set(baseline)
    cur = set(dead)
    added = sorted(cur - known)
    removed = sorted(known - cur)

    if removed:
        print("[unwired] 以下基线项已不再悬空（可从基线移除）：%s" % ", ".join(removed))
    if added:
        print("[unwired] 新增 %d 个悬空导出（导出了却从没被调用 ⇒ 对应功能是死的）：" % len(added))
        for d in added:
            print("  [FAIL] %s" % d)
        return 1
    print("[unwired] 没有新增悬空导出（基线 %d 项）" % len(known))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
