# -*- coding: utf-8 -*-
"""sync_mirror.py 的回归测试（反向测试：造错必须报错，正常情况不得误报）。

与 test_platform_gates.py 同性质——门禁本身要有门禁。
跑法：
    python tools/platform/test_sync_mirror.py

判据来源：镜像漂移检查若按字节比对，会被 .gitattributes 的换行归一（D21）误伤，
所以「仅换行符差异」必须**不**算漂移；而内容真差异与缺失必须**要**被抓出来。
"""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "sync_mirror.py")

_spec = importlib.util.spec_from_file_location("sync_mirror", MOD)
sm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sm)

FAILS = []


def case(name, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def setup(base):
    src = os.path.join(base, "src")
    dst = os.path.join(base, "dst")
    os.makedirs(os.path.join(src, "sub"))
    os.makedirs(dst)
    # 正本：a.txt 用 CRLF，b.txt 用 LF，另加一个嵌套文件与两个应被排除的缓存目录
    write(os.path.join(src, "a.txt"), b"line1\r\nline2\r\n")
    write(os.path.join(src, "b.txt"), b"line1\nline2\n")
    write(os.path.join(src, "sub", "c.js"), b"x = 1;\n")
    os.makedirs(os.path.join(src, "__pycache__"))
    write(os.path.join(src, "__pycache__", "junk.pyc"), b"\x00")
    os.makedirs(os.path.join(src, "research", "_cache"))
    write(os.path.join(src, "research", "_cache", "big.bin"), b"x" * 100)
    return src, dst


def main():
    base = tempfile.mkdtemp(prefix="sync_mirror_test_")
    try:
        src, dst = setup(base)

        print("T1 初始（镜像空）：--check 必须退出 1（缺文件）")
        case("缺文件被检出", sm.main([src, dst, "--check"]) == 1)

        print("T2 同步后：--check 必须退出 0")
        case("同步成功", sm.main([src, dst]) == 0)
        case("同步后无漂移", sm.main([src, dst, "--check"]) == 0)

        print("T3 排除规则生效：__pycache__ 与 research/_cache 不得进镜像")
        files = []
        for r, dirs, fs in os.walk(dst):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in fs:
                files.append(os.path.relpath(os.path.join(r, fn), dst).replace("\\", "/"))
        case("无 __pycache__/pyc", not any("__pycache__" in f or f.endswith(".pyc") for f in files))
        case("无 _cache", not any("_cache" in f for f in files))
        case("源文件已进镜像", sorted(files) == ["a.txt", "b.txt", "sub/c.js"], str(sorted(files)))

        print("T4 造真差异：改镜像文件内容 → --check 必须退出 1")
        write(os.path.join(dst, "b.txt"), b"TAMPERED\n")
        case("真差异被检出", sm.main([src, dst, "--check"]) == 1)
        write(os.path.join(dst, "b.txt"), b"line1\nline2\n")

        print("T5 造缺文件：删镜像文件 → --check 必须退出 1")
        os.remove(os.path.join(dst, "sub", "c.js"))
        case("缺文件被检出", sm.main([src, dst, "--check"]) == 1)
        case("补回后退出 0", sm.main([src, dst]) == 0)

        print("T6 仅换行符差异：镜像文件改成 CRLF（内容不变）→ --check 必须退出 0（不误报）")
        write(os.path.join(dst, "b.txt"), b"line1\r\nline2\r\n")
        case("仅换行符差异不误报", sm.main([src, dst, "--check"]) == 0)

        print("T7 仅换行符差异下同步：应把工作区对齐回正本，且退出 0")
        case("同步退出 0", sm.main([src, dst]) == 0)
        with open(os.path.join(dst, "b.txt"), "rb") as f:
            got = f.read()
        case("镜像内容已对齐正本", got == b"line1\nline2\n", repr(got))

        print("T8 多路径对（目录对 + 单文件对）：同步与漂移判定")
        src2 = os.path.join(base, "sub_src")
        dst2 = os.path.join(base, "sub_dst")
        os.makedirs(os.path.join(src2, "inner"))
        os.makedirs(dst2)
        write(os.path.join(src2, "inner", "x.js"), b"let a=1;\n")
        write(os.path.join(src2, "readme.md"), "# 交付说明\n".encode("utf-8"))
        sm.SUBJECTS["_t"] = {"src": src2, "dst": dst2,
                             "pairs": [("inner", "inner"), ("readme.md", "readme.md")]}
        case("多路径对同步成功", sm.main(["--subject", "_t"]) == 0)
        case("多路径对无漂移", sm.main(["--subject", "_t", "--check"]) == 0)
        case("单文件已进镜像", os.path.isfile(os.path.join(dst2, "readme.md")))
        case("目录对已进镜像", os.path.isfile(os.path.join(dst2, "inner", "x.js")))

        write(os.path.join(dst2, "readme.md"), "# 被改\n".encode("utf-8"))
        case("单文件对真差异被检出", sm.main(["--subject", "_t", "--check"]) == 1)

        os.remove(os.path.join(dst2, "inner", "x.js"))
        case("目录对缺文件被检出", sm.main(["--subject", "_t", "--check"]) == 1)

        case("修复后退出 0", sm.main(["--subject", "_t"]) == 0)
        case("最终无漂移", sm.main(["--subject", "_t", "--check"]) == 0)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if FAILS:
        print("反向测试失败 %d 项：%s" % (len(FAILS), FAILS))
        return 1
    print("反向测试全绿：造错必报错，仅换行符差异不误报。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
