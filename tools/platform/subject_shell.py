# -*- coding: utf-8 -*-
"""子站壳（index.html + 共享前端 + 盖戳清单）的生成口径。

【这个模块为什么必须存在】
2026-11-01 的一次 `new_subject.py --restamp`（漏传 --name）把五个学科的壳名
写成了空字符串。线上五个子站的标题于是变成「大学《》题库刷题」，页面上那颗
大标题也跟着空掉——而**当时全部门禁全绿**：门禁只会拿「盖戳清单里的参数」
去重放模板，盖戳清单自己被改空了，重放当然自洽。
**自洽式校验没有牙齿。**

所以这里把三件事钉死：
  ① 壳名与描述的唯一来源 = 该学科 manifest（subject.name / summary.desc）。
     命令行参数只作兜底；**旧盖戳清单排在 manifest 之后**——题量变了、
     summary.desc 变了，壳必须跟着重盖，不能停在旧题量上。
  ② 离线链接的唯一来源 = 平台级 offline_links.json（部署事实不写死在模板里：
     模板里写死的那条链接曾经让四个学科都指向线代的离线版）。
  ③ 渲染规则只有这一份：写（new_subject / build_all）与验（validate_platform）
     都调它，不会各写一份而再次漂移。
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATE_DIR = os.path.join(HERE, "template_subject")
OFFLINE_LINKS_FILE = os.path.join(HERE, "offline_links.json")

# 共享前端：模板改了就必须逐字节同步到每个学科（validate_platform 校验）
SHARED_FILES = [
    "assets/js/app.js",
    "assets/js/core/store.js",
    "assets/js/core/bank.js",
    "assets/css/subject.css",
]

NAME_PH = "__SUBJECT_NAME__"
DESC_PH = "__SUBJECT_DESC__"
OFFLINE_PH = "__OFFLINE_LINE__"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
H1_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
META_RE = re.compile(r'(<meta\s+name="description"\s+content=")([^"]*)(">)')
# 页脚固定行：前半段固定，后半段是「离线链接」从句（可能为空）
FOOT_RE = re.compile(r'<p class="muted">(本子站属于 <a href="[^"]*">[^<]*</a>)(.*?)</p>', re.S)


def subjects_root(subjects_dir=None):
    return subjects_dir or os.path.join(PLATFORM, "subjects")


def template_version():
    p = os.path.join(TEMPLATE_DIR, "VERSION")
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    return "1"


def read_template():
    with open(os.path.join(TEMPLATE_DIR, "index.html"), encoding="utf-8") as f:
        return f.read()


def load_offline_links():
    if not os.path.isfile(OFFLINE_LINKS_FILE):
        return {}
    with open(OFFLINE_LINKS_FILE, encoding="utf-8") as f:
        return json.load(f)


def offline_spec(sid):
    """该学科的单文件离线版去向；没有就 None（页脚不出现离线从句）。"""
    return load_offline_links().get(sid) or None


def offline_line(spec):
    if not spec:
        return ""
    return ' · 单文件离线版：<a href="%s" rel="noopener">%s</a>' % (spec["url"], spec["label"])


def render(tpl_html, name, desc, spec=None):
    return (tpl_html.replace(NAME_PH, name)
                    .replace(DESC_PH, desc)
                    .replace(OFFLINE_PH, offline_line(spec)))


def manifest_facts(sid, subjects_dir=None):
    """该学科 manifest 里的壳名与描述。缺 manifest 返回 (None, None)。"""
    p = os.path.join(subjects_root(subjects_dir), sid, "data", "manifest.json")
    if not os.path.isfile(p):
        return None, None
    with open(p, encoding="utf-8") as f:
        m = json.load(f)
    name = (m.get("subject") or {}).get("name") or ""
    desc = (m.get("summary") or {}).get("desc") or ""
    return name or None, desc or None


def load_stamp(sid, subjects_dir=None):
    p = os.path.join(subjects_root(subjects_dir), sid, ".stamp.json")
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def resolve_facts(sid, name=None, desc=None, subjects_dir=None):
    """壳名/描述的解析顺序：命令行 → manifest → 旧盖戳清单 → 空。

    manifest 排在旧盖戳清单**前面**：题量变了以后旧盖戳里的描述就是陈旧的，
    留着它等于让 meta description 停在旧题量上（2026-11-08 的门户 meta 就是
    这样悄悄过期了很久）。
    """
    m_name, m_desc = manifest_facts(sid, subjects_dir)
    st = load_stamp(sid, subjects_dir)
    final_name = (name or m_name or st.get("name") or "").strip()
    final_desc = desc if desc is not None else (m_desc or st.get("desc") or "")
    return final_name, final_desc


def write_shell(sid, name, desc, spec=None, legacy_json="[]", subjects_dir=None,
                create_subject_js=True):
    """生成/重盖一个学科的壳，并落盖戳清单。返回盖戳清单。"""
    out = os.path.join(subjects_root(subjects_dir), sid)
    html = render(read_template(), name, desc, spec)
    os.makedirs(os.path.join(out, "assets", "js", "core"), exist_ok=True)
    os.makedirs(os.path.join(out, "assets", "css"), exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    for rel in SHARED_FILES:
        src = os.path.join(TEMPLATE_DIR, rel)
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    if create_subject_js:
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
                    "};\n" % (name, sid, name, sid, legacy_json))
    stamp = {"templateVersion": template_version(), "name": name, "desc": desc,
             "offline": spec or None}
    with open(os.path.join(out, ".stamp.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(stamp, f, ensure_ascii=False, indent=1)
    return stamp


def restamp_all(subjects_dir=None, verbose=True):
    """按 manifest 重盖所有学科的壳。

    谁该调它：build_all.py（构建流水线里自动重盖——壳是**构建产物**，
    不是手工维护的文件；模板升级、题量变化、名称订正都从这里走一遍）。
    新建学科：先跑 build_subject 产出 manifest，再重盖。
    """
    root = subjects_root(subjects_dir)
    done = []
    for sid in sorted(os.listdir(root)):
        sdir = os.path.join(root, sid)
        if not os.path.isdir(sdir):
            continue
        name, desc = manifest_facts(sid, root)
        if not name:
            if verbose:
                print("  [skip] %s：无 manifest（先跑 build_subject 产出题库）" % sid)
            continue
        spec = offline_spec(sid)
        write_shell(sid, name, desc, spec, subjects_dir=root)
        done.append((sid, name))
        if verbose:
            print("  [stamp] %-10s 壳名=%s 离线版=%s"
                  % (sid, name, spec["label"] if spec else "（无）"))
    return done
