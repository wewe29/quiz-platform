# -*- coding: utf-8 -*-
"""题库口径的**单一事实源**（Single Source of Truth）。

背景（真实踩过的坑）：
    2026-10-28 计划把题库从 180 题扩到 500 题，率先改了 build_quiz.py 的题量门禁、
    qa_bank/common.py 的全局不变量、verify_quiz.py 的矩阵、template.html 的页脚文案、
    assets/app.js 的答案位置阈值——但新题一道未写。结果：当前源码树**任何一次构建都会
    失败**；强行加 --allow-partial 又会印出「题库共 500 题」而实际只有 180 题。

    根因：同一个口径（题量/配额/阈值/文案）分散写在 5 个文件里，改一处忘一处就出错版。

规则：口径只在本文件改，其余文件一律 import，不许再写死数字；
      页面上的题量文案由构建脚本按**实际题库**自动生成，不手写。

当前口径 = 500 题（180 题基础库 + ch1b…ch6b 共 320 题扩写，全部已落地）。

更新口径的正确做法（不要手抄数字）：
    python tools/tally.py --emit-target
    → 打印可直接粘贴的本文件常量块。题库一变就跑一次，门禁会提醒你。
"""

# ---------------------------------------------------------------- 规模
TOTAL = 500                 # 题库总题数（构建门禁：实际题数必须等于它）
CHAPTERS = 6                # 章节数

# ---------------------------------------------------------------- 题型配额
# 键为题型组：single / multi / judge / blank / short（简答与名词解释合并）/ calc
BY_TYPE = {
    "single": 84,
    "multi": 83,
    "judge": 83,
    "blank": 84,
    "short": 83,
    "calc": 83,
}

TYPE_ORDER = ["single", "multi", "judge", "blank", "short", "calc"]

TYPE_LABEL = {
    "single": "单选",
    "multi": "多选",
    "judge": "判断",
    "blank": "填空",
    "short": "简答与名词解释",
    "calc": "计算与分析",
}

# ---------------------------------------------------------------- 难度配额
DIFF_ORDER = ["basic", "medium", "hard"]

DIFF_LABEL = {
    "basic": "基础",
    "medium": "中等",
    "hard": "困难",
}

BY_DIFFICULTY = {
    "basic": 247,
    "medium": 173,
    "hard": 80,
}

# ---------------------------------------------------------------- 章节配额
BY_CHAPTER = {
    1: 82,
    2: 96,
    3: 84,
    4: 96,
    5: 106,
    6: 36,
}

# 题型 × 章节 矩阵：MATRIX[题型][章号] = 题数
MATRIX = {
    "single": {1: 14, 2: 17, 3: 15, 4: 15, 5: 17, 6: 6},
    "multi":  {1: 14, 2: 16, 3: 14, 4: 16, 5: 17, 6: 6},
    "judge":  {1: 15, 2: 17, 3: 14, 4: 16, 5: 15, 6: 6},
    "blank":  {1: 14, 2: 16, 3: 14, 4: 16, 5: 18, 6: 6},
    "short":  {1: 13, 2: 15, 3: 14, 4: 16, 5: 19, 6: 6},
    "calc":   {1: 12, 2: 15, 3: 13, 4: 17, 5: 20, 6: 6},
}

# ---------------------------------------------------------------- 答案位置均衡阈值
# 单选：每个字母（A/B/C/D）的出现次数必须落在 [MIN, MAX]
# 500 题时单选 84 题，每字母期望 21.00，实测 A/B/C/D 各 21，容差 ±35%
SINGLE_LETTER_MIN = 13
SINGLE_LETTER_MAX = 29
# 多选：四个字母出现次数的极差上限
# 多选 246 题次，每字母期望 61.50，实测 A70/B58/C57/D61，极差 13 ≤ 平均的 55%
MULTI_LETTER_RANGE = 33

# ---------------------------------------------------------------- 题库说明用
# 带此标签的题视为「真题改编」，页面会自动统计并据此改写「题库说明」段落
EXTENSION_TAG = "真题改编"

# ---------------------------------------------------------------- 教材信息
TEXTBOOK = "同济大学《工程数学·线性代数》第六版"
TEXTBOOK_ISBN = "978-7-04-039661-4"


def summary_lines():
    """返回 (副标题, meta description, 页脚题量行) 三段文案。

    全部由上面的常量拼出——**不要**在模板里手写题量，否则加题后一定会漏改。
    """
    sub = "同济第六版 %d 章 · %d 题 · 六题型 · 三难度" % (CHAPTERS, TOTAL)
    desc = ("大学线性代数 %d 题单文件刷题网页：六题型、三难度、逐题解析与考点出处，"
            "零外部依赖。" % TOTAL)
    type_part = " · ".join(
        "%s %d" % (TYPE_LABEL[t], BY_TYPE[t]) for t in TYPE_ORDER)
    diff_part = " · ".join(
        "%s %d" % (DIFF_LABEL[d], BY_DIFFICULTY[d]) for d in DIFF_ORDER)
    footer = ("<p>题库共 <b>%d</b> 题：%s；难度 %s。</p>" % (TOTAL, type_part, diff_part))
    return sub, desc, footer


def limits():
    """页面「答案位置统计」表用到的判定阈值（由 app.js 从题库 JSON 读取）。"""
    return {
        "singleMin": SINGLE_LETTER_MIN,
        "singleMax": SINGLE_LETTER_MAX,
        "multiRange": MULTI_LETTER_RANGE,
    }
