# -*- coding: utf-8 -*-
r"""公式型知识点规则 —— 高考/考研/自考三套建库脚本共用。

**为什么需要它**：真题卷面里有大量「题干几乎没有中文」的题，例如

    求 $\int \frac{\mathrm{d}x}{x\ln^2x}$
    设 $y = \ln(1 - x^{2})$ ，则 $y''|_{x=0} =$
    计算 $\int_0^\pi \sqrt{1 - \sin x} \, \mathrm{d}x$

`KP_RULES` 全靠中文关键词定位，这类题一条都匹配不上，
结果就是「无法归入高等数学知识点」被整题丢掉。

**放在中文规则之后**：`classify` 取最高分、同分取先命中者，
所以这些规则只在中文规则**一条都没命中**时才生效，
不会改变任何已经归对的题。

用法：
    from kp_rules import classify_full
    kp = classify_full(stem + " " + " ".join(options), solution)
"""
import re

# 与 build_kaoyan_bank.KP_RULES 同口径（同济第七版 12 章节次），
# 这里只放「靠符号就能定位」的题型。
EXTRA_KP_RULES = [
    (r"\\int[^$]{0,14}\\infty", "5.4"),            # 反常积分（积分限含无穷）
    (r"\\iiint", "10.3"),                         # 三重积分
    (r"\\iint", "10.2"),                          # 二重积分
    (r"\\int\s*_\s*[\{\d]", "5.1"),               # 定积分（∫ 带下限）
    (r"\\int(?!\s*_)", "4.1"),                    # 不定积分（∫ 无下限）
    (r"\\partial", "9.2"),                        # 偏导数
    (r"\\mathrm\s*\{\s*d\s*\}\s*y", "2.2"),       # 求微分 dy
    (r"y''|y\^\{\\prime\\prime\}", "2.3"),        # 二阶导数
    (r"渐进线|渐近线", "3.4"),                    # 源卷面常把「渐近线」写成「渐进线」
    (r"弧的长度|弧长", "6.4"),
    (r"质心|重心", "6.5"),
    (r"零点", "1.3"),                             # 函数零点的个数
    (r"初值问题|常微分方程", "7.1"),
    (r"\\begin\{cases\}", "2.1"),                 # 分段函数（连续/可导性）
]


def classify_full(kp_rules, text, sol=""):
    """在中文规则之后追加公式型规则做分类。"""
    best, best_score = None, 0
    for pat, key in kp_rules:
        score = len(re.findall(pat, text)) * 3 + len(re.findall(pat, sol[:400]))
        if score > best_score:
            best, best_score = key, score
    if best_score > 0:
        return best
    for pat, key in EXTRA_KP_RULES:
        score = len(re.findall(pat, text)) * 3 + len(re.findall(pat, sol[:400]))
        if score > best_score:
            best, best_score = key, score
    return best if best_score > 0 else None
