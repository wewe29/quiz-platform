# -*- coding: utf-8 -*-
r"""反向测试：check_import_guard 这道门禁自己有没有牙齿（2026-11-22）。

规则（项目纪律）：**每加一道门禁必须配反向测试——造错必须报错**。
这道门禁特别需要自证：它跑的是真实 app.js，万一它「怎么都过」，
那它就不是门禁而是摆设。

做法：把模板 app.js 复制到临时目录，逐个注入「还原缺陷」的改动，
再跑门禁——每一处都必须让门禁报错；另外，未改动的副本必须通过
（证明门禁不是见谁报谁、也不是永远报错）。

【为什么临时目录不用 %TEMP%】
本机的一次性产物约定是落 D:\Temp；但 CI 跑在 Linux 上，写死盘符不可移植。
这里用 tempfile（可用环境变量 QUIZ_TMPDIR 指定根目录），并在结束时删干净，
不往仓里留垃圾。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "check_import_guard.py")
TPL_JS = os.path.join(HERE, "template_subject", "assets", "js")
TPL_APP = os.path.join(TPL_JS, "app.js")
TPL_STORE = os.path.join(TPL_JS, "core", "store.js")

# (用例名, 要替换的原样片段, 替换成什么, 门禁报错里必须出现的关键字)
# 关键字这一列不是装饰：它保证门禁**点名了被撤掉的那条断言**，
# 而不是随便报个错就算数（否则「门禁坏了」也会被当成「抓到缺陷了」）。
MUTATIONS = [
    ("撤掉导入来源校验（跨学科文件又被静默合并）",
     "    assertImportMatchesBank(payload);\n", "", "被拒绝"),
    ("错题本计数改回未过滤（badge 又开始说谎）",
     "    var ids = wrongBookIds();\n",
     "    var ids = Object.keys(state.wrongBook);\n", "badge"),
    ("导入时不再忽略失效题号（外来题号又进错题本）",
     "      if (!qById[qid]) { skipped++; return; }\n", "", "题库里没有的题号"),
]

failures = []
passed = 0


def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + name)
    else:
        failures.append(name + ("：" + detail if detail else ""))
        print("  FAIL  " + name + ("：" + detail if detail else ""))


def stage(root, name, text):
    """摆一份可被测的 app.js（含 core/store.js）"""
    d = os.path.join(root, name, "assets", "js")
    os.makedirs(os.path.join(d, "core"), exist_ok=True)
    with open(os.path.join(d, "app.js"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    shutil.copyfile(TPL_STORE, os.path.join(d, "core", "store.js"))
    return os.path.join(d, "app.js")


def run_gate(app_path):
    p = subprocess.run([sys.executable, GATE, "--app", app_path],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def main():
    if not os.path.isfile(TPL_APP):
        print("[FAIL] 模板 app.js 不存在：%s" % TPL_APP)
        return 1
    with open(TPL_APP, encoding="utf-8") as f:
        original = f.read()

    root = tempfile.mkdtemp(prefix="import-guard-", dir=os.environ.get("QUIZ_TMPDIR") or None)
    try:
        # 0) 正样本：未改动的模板必须通过（门禁不能见谁报谁）
        print("· 未改动的模板应当通过")
        app = stage(root, "clean", original)
        rc, out = run_gate(app)
        check("未改动的 app.js 通过门禁（门禁不误报）", rc == 0, out.strip().splitlines()[-1] if out.strip() else "")

        # 1) 反向样本：逐个撤掉修复，门禁必须报错
        for i, (name, needle, repl, keyword) in enumerate(MUTATIONS):
            print("· 注入缺陷：" + name)
            if needle not in original:
                check("注入缺陷的锚点存在（源码改了名字就要同步改这里）", False,
                      "找不到片段：%r" % needle[:60])
                continue
            mutated = original.replace(needle, repl, 1)
            check("注入缺陷确实改了源码", mutated != original)
            app = stage(root, "mut%d" % i, mutated)
            rc, out = run_gate(app)
            check("门禁对注入的缺陷报错：" + name, rc != 0,
                  "门禁居然通过了：%s" % out.strip().splitlines()[-1] if out.strip() else "")
            if rc != 0:
                hit = [l for l in out.splitlines() if l.strip().startswith("- ")]
                check("报错里点名了被撤掉的那条断言：" + name, len(hit) > 0,
                      "报错里没有任何断言明细")
                check("报错里点名的是**对的那条**断言：" + name,
                      any(keyword in l for l in hit),
                      "报错明细里找不到关键字 %r" % keyword)

        # 2) 反向样本：被测文件根本不是 app.js 时，门禁必须报错而不是「通过」
        print("· 被测文件不是 app.js 时必须报错")
        app = stage(root, "junk", "/* 这不是 app.js */\n")
        rc, out = run_gate(app)
        check("门禁对非 app.js 的文件报错（解析不到断言 ⇒ 报红）", rc != 0)

        # 3) 反向样本：被测文件缺失时，门禁必须报错
        print("· 被测文件不存在时必须报错")
        rc, out = run_gate(os.path.join(root, "nonexistent", "assets", "js", "app.js"))
        check("门禁对缺失文件报错", rc != 0)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("")
    if failures:
        print("[FAIL] %d 项不通过（共 %d 项）：" % (len(failures), passed + len(failures)))
        for f in failures:
            print("  - " + f)
        return 1
    print("[OK ] %d 项全部通过（门禁有牙齿：撤掉修复必报错）" % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
