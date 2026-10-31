# -*- coding: utf-8 -*-
r"""核查考研数学源与自考源的答案覆盖与章节分布。"""
import collections
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")

KY = os.path.join(CACHE, "TsekaLuk_Kaoyan-Math1-Papers.zip")
ZK = os.path.join(CACHE, "huangnaisheng_zikao-exam-solutions.zip")


def main():
    print("=" * 70)
    print("考研数学一仓库")
    if not os.path.exists(KY):
        print("  缓存不存在")
    else:
        z = zipfile.ZipFile(KY)
        names = [n for n in z.namelist() if n.endswith(".md")]
        print("  md 文件 %d 个" % len(names))
        ans = 0
        withans = []
        for n in names:
            t = z.read(n).decode("utf-8", "replace")
            has = bool(re.search(r"(参考答案|答案|Answer|解答)", t))
            if has:
                ans += 1
                withans.append(n)
        print("  含答案字样的文件 %d 个" % ans)
        for n in withans[:20]:
            print("     " + n)
        # 看一个文件的结构
        if names:
            n = sorted(names)[-1]
            t = z.read(n).decode("utf-8", "replace")
            print("  ---- 样例 %s 前 1200 字 ----" % n)
            print(t[:1200])

    print()
    print("=" * 70)
    print("自考仓库")
    if not os.path.exists(ZK):
        print("  缓存不存在")
    else:
        z = zipfile.ZipFile(ZK)
        names = [n for n in z.namelist() if n.endswith(".md")]
        print("  md 文件 %d 个" % len(names))
        for n in sorted(names):
            print("     " + n)


if __name__ == "__main__":
    raise SystemExit(main())
