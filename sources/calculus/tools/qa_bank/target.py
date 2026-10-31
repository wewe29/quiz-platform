# -*- coding: utf-8 -*-
r"""题库口径的**单一事实源**（Single Source of Truth）。

背景（真实踩过的坑）：
    高数题库从「180 道教材命题」一路扩到「229 道教材命题 + 676 道考研真题 = 905 题」，
    但**题量门禁仍写死在 4 个文件里**（build_quiz.py / build_single.py / build_static.py /
    qa_bank/common.py 的 audit 全局不变量），全都是 180。
    结果：静态站与单文件离线包**任何一次正式构建都会失败**，只能靠 --allow-partial
    硬绕过——而那个开关的语义是「分章写作期的部分构建」，拿它当正式发布口，
    等于把门禁关掉。

    根因与线代那边完全一样：**同一个口径（题量/配额）分散写在多个文件里，
    改一处忘一处就出错版**。线代那边的解法是 `qa_bank/target.py`（见
    `D:\workspace\5-docs\线性代数复习资料\tools\qa_bank\target.py`），
    这里照抄同一个形状。

规则：口径只在本文件改，其余文件一律 import，不许再写死数字；
      页面上的题量文案由构建脚本按**实际题库**自动生成，不手写。

当前口径 = 905 题（229 教材命题 + 676 考研真题，同济《高等数学》第七版 12 章）。
2026-10-31 生效（此前写死的 180 属 v1 教材库旧口径）。

更新口径的正确做法（不要手抄数字）：
    python tools/tally.py --emit-target
    → 打印可直接粘贴的本文件常量块。题库一变就跑一次，门禁会提醒你。
"""

# ---------------------------------------------------------------- 规模
TOTAL = 905
CHAPTERS = 12               # 章节数

# ---------------------------------------------------------------- 题型配额
# 键为题型组：single / multi / judge / blank / short（简答与名词解释合并）/ calc
BY_TYPE = {
    "single": 257,
    "multi": 24,
    "judge": 36,
    "blank": 147,
    "short": 24,
    "calc": 417,
}

TYPE_ORDER = ["single", "multi", "judge", "blank", "short", "calc"]

TYPE_LABEL = {
    "single": "单选",
    "multi": "多选",
    "judge": "判断",
    "blank": "填空",
    "short": "简答与名词解释",
    "calc": "计算与分析题",
}

# ---------------------------------------------------------------- 难度配额
BY_DIFF = {
    "basic": 229,
    "medium": 372,
    "hard": 304,
}

DIFF_ORDER = ["basic", "medium", "hard"]

DIFF_LABEL = {"basic": "基础", "medium": "中等", "hard": "困难"}

# ---------------------------------------------------------------- 章节配额
BY_CHAPTER = {
    1: 154, 2: 97, 3: 82, 4: 34, 5: 81, 6: 53,
    7: 89, 8: 69, 9: 77, 10: 61, 11: 36, 12: 72,
}

# ---------------------------------------------------------------- 出处构成
TEXTBOOK_TOTAL = 229        # 教材命题
EXAM_TOTAL = 676            # 考研真题（原题 + 改编）


def summary_line():
    """页面/日志里的一句话口径，**按实际题库**拼，不手写数字。"""
    t = " · ".join("%s %d" % (TYPE_LABEL[k], BY_TYPE[k]) for k in TYPE_ORDER)
    d = " · ".join("%s %d" % (DIFF_LABEL[k], BY_DIFF[k]) for k in DIFF_ORDER)
    return "同济第七版 %d 章 · %d 题 · 六题型 · 三难度" % (CHAPTERS, TOTAL)
