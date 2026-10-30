# -*- coding: utf-8 -*-
"""真题库（按「卷 × 年份」分模块）。

与教材题（`qa_bank/ch*.py`）分开成包，理由有三个：

    1. **写入节奏不同**：教材题是 12 个大文件一次写完；真题是「一卷一模块」
       增量补，每补一卷就多一道可核验的出处，单独成包便于增量与审计。
    2. **溯源要求不同**：真题必须带 `source.year/region/paper/number/url`
       与 `provenance`，教材题不需要。混在一个包里容易让写题的人漏字段。
    3. **去重要跨包**：同一道真题常被多套汇编收录，跨包指纹去重只能在
       合并之后做（见 `tools/validate_bank.py`）。

模块命名：`ky{YYYY}_{1|2|3}.py` = 考研数学一/二/三 {YYYY} 年；
`final_{校名}.py` = 高校期末真题汇编。每个模块导出 `Q: list[dict]`。
"""
import importlib
import os

__all__ = ["EXAM_MODULES", "load_exam", "discover_modules"]

_HERE = os.path.dirname(os.path.abspath(__file__))


def discover_modules():
    """扫描包内 *.py（不含 __init__），按文件名排序返回模块名列表。"""
    names = []
    for fn in sorted(os.listdir(_HERE)):
        if fn.endswith(".py") and fn != "__init__.py":
            names.append(fn[:-3])
    return names


# 显式清单。留空则自动发现；显式列出可用来固定构建顺序。
EXAM_MODULES = []


def load_exam():
    """载入全部真题模块，返回题目列表。缺失模块会被跳过并提示。"""
    names = EXAM_MODULES or discover_modules()
    out = []
    for name in names:
        try:
            mod = importlib.import_module("qa_bank.exam." + name)
        except ImportError as e:
            print("[exam] 跳过模块 %s：%s" % (name, e))
            continue
        out.extend(getattr(mod, "Q", []))
    return out
