# -*- coding: utf-8 -*-
r"""导入守卫 + 错题本计数：**行为**门禁（2026-11-22 新增）。

用法：
    python tools/platform/check_import_guard.py                 # 查模板 + 五个学科副本
    python tools/platform/check_import_guard.py --app <路径>    # 只查指定文件（可重复）

【这道门禁在防什么】
2026-11-22 浏览器实答在平台子站抓出两个真缺陷（门禁全绿的情况下）：
  ① 跨学科进度文件被**静默合并**——app.js 的 applyImportPayload 只校验
     kind/version/state.v/checksum，从不校验文件里明写着的 subject/bankId。
     实测：把 dataviz 的进度导进 ml 子站，页面只提示「导入完成」，一个字的
     异常都没有，外来会话与外来题号原样进了本学科的状态。
  ② 错题本 badge 说谎——renderWrong 用 Object.keys(state.wrongBook).length
     当计数，而渲染时题库里没有的题号会被跳过 ⇒ 页面显示「共 2 题」、
     列表只有 1 题。store.js 的注释早就写着「失效题号在渲染时自动跳过」，
     但计数没跟着过滤。

【为什么必须驱动真实代码】
这两个都是**运行期行为**，不是源码里的一句话。grep 源码等于「拿参数重放自己」：
把变量名一改就骗过去了。所以这里在 Node 里装载**真实的 app.js**（垫片见
jsdom_lite.js），用**真的按钮**触发，断言**真的 localStorage 与页面文本**。

【Node 缺失怎么办】
直接判失败，不静默跳过——「找不到就默认通过」是本项目明令禁止的病根。
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLATFORM = os.path.abspath(os.path.join(HERE, "..", ".."))
TEST_JS = os.path.join(HERE, "test_import_guard.js")


def node_exe():
    """找 node。找不到就报错退出——不许「找不到就当通过」。"""
    for name in ("node", "node.exe"):
        p = shutil.which(name)
        if p:
            return p
    raise SystemExit(
        "[import-guard] 找不到 node：这道门禁要在 Node 里跑真实的 app.js。\n"
        "    找不到 node 就当失败，不静默跳过（那等于没有门禁）。\n"
        "    CI 已在 setup-node 里装好 Node 20；本机请装 Node 后重跑。")


def default_targets():
    out = [os.path.join(HERE, "template_subject", "assets", "js", "app.js")]
    subjects = os.path.join(PLATFORM, "subjects")
    if os.path.isdir(subjects):
        for sid in sorted(os.listdir(subjects)):
            p = os.path.join(subjects, sid, "assets", "js", "app.js")
            if os.path.isfile(p):
                out.append(p)
    return out


def rel(path):
    try:
        return os.path.relpath(path, PLATFORM).replace("\\", "/")
    except ValueError:
        return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", action="append", help="只检查指定文件（可重复）")
    args = ap.parse_args()

    if not os.path.isfile(TEST_JS):
        raise SystemExit("[import-guard] 缺 %s（行为测试脚本不见了）" % TEST_JS)
    node = node_exe()
    targets = [os.path.abspath(a) for a in args.app] if args.app else default_targets()
    if not targets:
        raise SystemExit("[import-guard] 没有任何被测文件")

    bad = 0
    for p in targets:
        if not os.path.isfile(p):
            print("[FAIL] 缺文件：%s" % p)
            bad += 1
            continue
        r = subprocess.run([node, TEST_JS, p],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = r.stdout.decode("utf-8", "replace")
        lines = [l for l in out.splitlines() if l.strip()]
        if r.returncode == 0:
            print("[OK ] %s —— %s" % (rel(p), lines[-1] if lines else "通过"))
        else:
            bad += 1
            print("[FAIL] %s —— 行为门禁不通过：" % rel(p))
            for l in lines:
                s = l.strip()
                if s.startswith("- "):
                    print("       " + s[2:])
    if bad:
        raise SystemExit("[import-guard] %d 个被测文件未通过行为门禁。" % bad)
    print("[OK ] 导入守卫 + 错题本计数：%d 个被测文件全部通过（真实 app.js 行为）"
          % len(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
