# -*- coding: utf-8 -*-
r"""学科子站盖章器：从 template_subject 生成/重盖 subjects/<id> 的壳与共享前端。

用法：
    python tools/platform/new_subject.py --id linalg --name 线性代数 --desc "500 题"
    python tools/platform/new_subject.py --id linalg --restamp   # 重盖已存在的学科（模板升级后用）

防分叉机制（见 docs/decisions.md D15）：
    core/store.js、core/bank.js、app.js、subject.css 与模板**字节一致**（validate_platform 校验）；
    index.html = 模板替换 __SUBJECT_NAME__ / __SUBJECT_DESC__ 后的字节（同样校验）。
    改共享前端 → 改模板 → 对每个学科 --restamp。subject.js（学科配置）与 data/ 不归模板管。
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATE = os.path.join(HERE, "template_subject")

SHARED_FILES = [
    "assets/js/app.js",
    "assets/js/core/store.js",
    "assets/js/core/bank.js",
    "assets/css/subject.css",
]


def stamp(subject_id, name, desc, legacy_json="[]"):
    out = os.path.join(PLATFORM, "subjects", subject_id)
    tpl_html = open(os.path.join(TEMPLATE, "index.html"), encoding="utf-8").read()
    html = tpl_html.replace("__SUBJECT_NAME__", name).replace("__SUBJECT_DESC__", desc)
    os.makedirs(os.path.join(out, "assets", "js", "core"), exist_ok=True)
    os.makedirs(os.path.join(out, "assets", "css"), exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    for rel in SHARED_FILES:
        src = os.path.join(TEMPLATE, rel)
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    # subject.js：已存在则保留（学科自己的配置）；新学科写最小骨架
    sj = os.path.join(out, "assets", "js", "subject.js")
    if not os.path.exists(sj):
        with open(sj, "w", encoding="utf-8", newline="\n") as f:
            f.write(
                "/* %s 子站配置 —— 数据契约由 data/manifest.json 提供 */\n"
                "window.SUBJECT = {\n"
                "  id: '%s',\n"
                "  name: '%s',\n"
                "  dataDir: 'data/',\n"
                "  storageKey: 'quiz-%s-v2',\n"
                "  legacyKeys: %s,\n"
                "  portalUrl: '../../',\n"
                "  katex: 'assets/vendor/katex/'\n"
                "};\n" % (name, subject_id, name, subject_id, legacy_json))
    # 盖章清单：validate_platform 用它重放模板替换、逐字节防分叉
    with open(os.path.join(out, ".stamp.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"templateVersion": template_version(), "name": name, "desc": desc},
                  f, ensure_ascii=False, indent=1)
    print("[stamp] subjects/%s 盖章完成（模板版本 %s）" % (subject_id, template_version()))


def template_version():
    v = os.path.join(TEMPLATE, "VERSION")
    if os.path.isfile(v):
        return open(v, encoding="utf-8").read().strip()
    return "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--name")
    ap.add_argument("--desc", default="")
    ap.add_argument("--legacy", default="[]", help="legacyKeys JSON 数组")
    ap.add_argument("--restamp", action="store_true", help="重盖已存在学科（保留 subject.js 与 data/）")
    args = ap.parse_args()

    out = os.path.join(PLATFORM, "subjects", args.id)
    if args.restamp:
        if not os.path.isdir(out):
            raise SystemExit("[stamp] %s 不存在，无法 restamp" % args.id)
        stamp(args.id, args.name or "", args.desc or "")
        return 0
    stamp(args.id, args.name or args.id, args.desc or "", args.legacy)


if __name__ == "__main__":
    sys.exit(main())
