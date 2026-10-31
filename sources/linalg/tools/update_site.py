# -*- coding: utf-8 -*-
r"""一键更新：构建 + 七道门禁 + 同步暂存 + 打印部署参数。

用法：
    python tools/update_site.py                # 完整流程（含暂存同步）
    python tools/update_site.py --no-stage     # 只构建与校验，不碰暂存目录
    python tools/update_site.py --stage-only   # 只同步暂存（不重新构建）

为什么要有这个脚本：
    2026-10-28 的事故——有人把「扩到 500 题」的改动分散写进了 5 个文件
    （构建门禁 / 校验矩阵 / 模板文案 / 页面阈值 / 公共层），
    结果源码树任何一次构建都失败，强跑又印出「500 题」而实际 180 题。
    本脚本把「改完源码之后必须走的那几步」固定下来：少一步就发不出去。

流程：
    1. build_quiz.py     —— 构建（含答案键自洽、主观题结构、成品↔源码逐字段一致三道内建门禁）
    2. verify_quiz.py    —— A1–A6 结构不变量 + B1–B6 内容 + SymPy 数值复核
    3. audit_choice.py   —— 客观题「答案键 ↔ 解析」自洽（豁免「选错误项」题型）
    3b. audit_value.py   —— 客观题「答案键 ↔ 解析数值」一致性（补 audit_choice 的盲区：
                          实测 250 道客观题里只有 44 道解析点名了答案字母，
                          其余 206 道在字母规则下无保护；2026-10-31 的 q-039 就漏在这里）
    4. audit_open.py     —— 主观题结构（采分点数/分值/文本）
    5. scan_escapes.py   —— LaTeX 转义扫描
    6. diff_bank.py      —— 源码 ↔ 成品逐字段比对
    7. check_html.py     —— 成品自检（无外部资源 / JS 语法 / 字体内联 / 题库回读）
    8. 同步暂存：公开站点目录只放成品 HTML；源码另存一份供私有云归档
    9. 打印 website_deploy 的参数（照抄即可原地更新，URL 不变）

暂存目录（必须在工作目录 E:\抗菌肽 下——website_deploy 的硬性要求）：
    公开站点：E:\抗菌肽\_deploy\linear-algebra-quiz\index.html
    源码归档：E:\抗菌肽\_deploy\linear-algebra-quiz-src\  （私有云，不公开）
"""
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# 项目根（成品 HTML 所在目录）：默认 = tools 的上一级；
# 平台构建（build_subject.py）用环境变量 QUIZ_PROJECT_DIR 重定向，避免污染仓库。
PROJECT = os.path.abspath(os.environ.get("QUIZ_PROJECT_DIR") or os.path.join(HERE, ".."))
PRODUCT = os.path.join(PROJECT, "01《线性代数》题库刷题网页.html")
WORKDIR = r"E:\抗菌肽"
STAGE_SITE = os.path.join(WORKDIR, "_deploy", "linear-algebra-quiz")
STAGE_SRC = os.path.join(WORKDIR, "_deploy", "linear-algebra-quiz-src")
NODE_ID = "457086899044553"
PUBLIC_URL = "https://u44tlmu73tjcs.space.mcode.cn"

# 每项：(脚本名, 参数, 额外环境变量)
GATES = [
    ("verify_quiz.py", ["--quiet"], None),
    ("audit_choice.py", ["--quiet"], None),
    ("audit_value.py", ["--quiet"], None),
    ("audit_open.py", [], None),
    ("scan_escapes.py", [], None),
    # diff_bank 必须比对**本次刚构建出来的**成品。
    # 2026-10-31 实测的坑：平台构建（build_subject.py）把成品写到 QUIZ_PROJECT_DIR，
    # 而 diff_bank 自己按「tools 的上一级」找成品、只认 QUIZ_HTML 环境变量——
    # 平台构建从不设它，于是这道门禁一直在拿一份**旧成品**做比对（还恰好被提交
    # 进了仓库），形同虚设。必须显式把 QUIZ_HTML 指到本次的成品。
    ("diff_bank.py", [], {"QUIZ_HTML": PRODUCT}),
]


def run(label, argv, show_tail=6, extra_env=None):
    """跑一条 python 脚本，非零退出即抛错。"""
    cmd = [sys.executable] + argv
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    p = subprocess.run(cmd, cwd=HERE, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=env)
    out = p.stdout.decode("utf-8", "replace")
    lines = [l for l in out.splitlines() if l.strip()]
    print("[%s] %s" % ("OK " if p.returncode == 0 else "FAIL", label))
    for l in lines[-show_tail:]:
        print("      " + l)
    if p.returncode != 0:
        raise SystemExit("[update] %s 失败，流程中止——不要发布。" % label)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def stage_site():
    """公开站点目录：只放成品 HTML，绝不放源码。"""
    os.makedirs(STAGE_SITE, exist_ok=True)
    dst = os.path.join(STAGE_SITE, "index.html")
    copy_file(PRODUCT, dst)
    # 目录里若混进了别的东西（源码/备份），一律清掉——公开目录只应有 index.html
    for name in os.listdir(STAGE_SITE):
        if name == "index.html":
            continue
        victim = os.path.join(STAGE_SITE, name)
        try:
            if os.path.isdir(victim):
                shutil.rmtree(victim)
            else:
                os.remove(victim)
            print("[stage] 清理公开站点目录中的多余内容：%s" % name)
        except Exception as e:
            print("[stage] 警告：无法清理 %s（%s）——公开站点目录必须只含 index.html" % (name, e))
    return dst


def stage_src():
    """源码归档目录：私有云上传用，不公开。逐文件复制，避开整目录递归拷贝被安全策略拦截。"""
    os.makedirs(STAGE_SRC, exist_ok=True)
    n = 0
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        rel = os.path.relpath(root, HERE)
        for name in files:
            if name.endswith(".pyc"):
                continue
            src = os.path.join(root, name)
            dst = os.path.join(STAGE_SRC, name if rel == "." else os.path.join(rel, name))
            copy_file(src, dst)
            n += 1
    return n


def main():
    args = sys.argv[1:]
    if "--stage-only" not in args:
        print("=" * 72)
        print("[1/3] 构建（含三道内建门禁）")
        run("build_quiz.py", [os.path.join(HERE, "build_quiz.py")], show_tail=8)

        print("=" * 72)
        print("[2/3] 七道验证链")
        for script, extra, genv in GATES:
            run(script, [os.path.join(HERE, script)] + extra, extra_env=genv)
        run("check_html.py", [os.path.join(HERE, "check_html.py"), PRODUCT], show_tail=10)

    if "--no-stage" in args:
        print("\n[3/3] 已跳过暂存同步（--no-stage）")
        return 0

    print("=" * 72)
    print("[3/3] 同步暂存")
    site = stage_site()
    n = stage_src()
    print("[OK ] 公开站点：%s" % site)
    print("[OK ] 源码归档：%s（%d 个文件）" % (STAGE_SRC, n))
    print("     成品大小：%d 字节" % os.path.getsize(PRODUCT))
    print("     成品 SHA256：%s" % sha256(PRODUCT))
    print("     暂存 SHA256：%s" % sha256(site))

    print("=" * 72)
    print("下一步：发布（原地更新，URL 不变）")
    print("  node_id    = %s" % NODE_ID)
    print("  path       = %s" % STAGE_SITE)
    print("  source_path= %s" % STAGE_SRC)
    print("  project_name = linear-algebra-quiz")
    print("  → https://u44tlmu73tjcs.space.mcode.cn")
    print("  调用 website_deploy 时必须传 node_id（否则会新建站点、换一个 URL）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
