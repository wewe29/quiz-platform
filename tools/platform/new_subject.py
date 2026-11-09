# -*- coding: utf-8 -*-
r"""学科子站盖章器：从 template_subject 生成/重盖 subjects/<id> 的壳与共享前端。

用法：
    python tools/platform/new_subject.py --id linalg --name 线性代数 --desc "528 题"
    python tools/platform/new_subject.py --id linalg --restamp        # 重盖已存在的学科
    python tools/platform/new_subject.py --id linalg --restamp --offline-url https://… --offline-label 名称

防分叉机制（见 docs/decisions.md D15 / D26）：
    core/store.js、core/bank.js、app.js、subject.css 与模板**字节一致**（validate_platform 校验）；
    index.html = 模板按盖戳清单重放替换的结果（同样校验）。

2026-11-08 的教训（必须留住这条纪律）：
    `--restamp` 曾经把 `args.name or ""` 直接写进盖戳清单——
    一次漏传 --name 的重盖，就把五个学科的壳名写成了空字符串，
    线上五个子站的标题变成「大学《》题库刷题」，而当时**全部门禁全绿**
    （门禁只做「模板重放」这种自洽式校验，看不见盖戳参数本身是错的）。

    现在：
      · 壳名与描述优先取自该学科的 manifest（subject.name / summary.desc）——
        manifest 是构建产物，题量变了它就跟着变；
      · 命令行参数只作兜底（新建学科、manifest 还没产出时）；
      · 解析不出名字就**报错退出**，绝不写空壳；
      · 离线链接取自平台级 tools/platform/offline_links.json（部署事实不写死在模板里）。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import subject_shell  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--name", help="壳名（缺省取 manifest.subject.name）")
    ap.add_argument("--desc", help="页头/元信息描述（缺省取 manifest.summary.desc）")
    ap.add_argument("--offline-url", help="该学科单文件离线版地址（缺省取 offline_links.json）")
    ap.add_argument("--offline-label", help="离线版链接文字")
    ap.add_argument("--no-offline", action="store_true", help="页脚不出现离线链接从句")
    ap.add_argument("--legacy", default="[]", help="legacyKeys JSON 数组")
    ap.add_argument("--restamp", action="store_true", help="重盖已存在的学科（保留 subject.js 与 data/）")
    args = ap.parse_args()

    sid = args.id
    out = os.path.join(PLATFORM, "subjects", sid)
    if args.restamp and not os.path.isdir(out):
        raise SystemExit("[stamp] subjects/%s 不存在，无法 restamp" % sid)

    name, desc = subject_shell.resolve_facts(sid, name=args.name, desc=args.desc)
    if not name:
        raise SystemExit(
            "[stamp] 解析不出学科名，拒绝写出空壳。\n"
            "        请显式传 --name，或先跑 build_subject 产出 data/manifest.json。\n"
            "        （2026-11-08：空壳名上线五天，全部门禁都没报出来——不能再让它发生。）")

    if args.no_offline:
        spec = None
    elif args.offline_url:
        spec = {"url": args.offline_url, "label": args.offline_label or args.offline_url}
    else:
        spec = subject_shell.offline_spec(sid)

    stamp = subject_shell.write_shell(sid, name, desc, spec, legacy_json=args.legacy)
    print("[stamp] subjects/%s 盖章完成（模板版本 %s，壳名=%r，离线版=%s）"
          % (sid, stamp["templateVersion"], name,
             (spec or {}).get("label", "（无）")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
