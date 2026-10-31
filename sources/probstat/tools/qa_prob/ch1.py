# -*- coding: utf-8 -*-
"""第1章 随机事件与概率（14 题）"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = [
Q(SINGLE, "basic", "1.3", "掷两枚均匀骰子，点数之和为 7 的概率是",
    answer=["B"], options=["$\\frac{1}{9}$", "$\\frac{1}{6}$", "$\\frac{1}{12}$", "$\\frac{7}{36}$"],
    expl="**答案依据**：古典概型 $|\\Omega|=36$。有利事件 6 个（和=7），$P=\\frac{6}{36}=\\frac{1}{6}$。B 正确。",
    mis="⚠️ (3,4) 和 (4,3) 是不同样本点。", tags=["基础", "古典概型"],
    verify=[{"desc": "P", "code": "Rational(6,36)", "expected": "1/6"}]),

Q(SINGLE, "basic", "1.2", "设 $A,B$ 为任意两事件，则 $(A\\cup B)\\cap A=$",
    answer=["A"], options=["$A$", "$B$", "$A\\cap B$", "$\\varnothing$"],
    expl="**答案依据**：吸收律。A 正确。", tags=["基础", "事件运算"]),

Q(SINGLE, "medium", "1.4", "设 $P(A)=0.5,\\ P(B)=0.4,\\ P(A|B)=0.6$，则 $P(A\\cup B)=$",
    answer=["A"], options=["$0.66$", "$0.7$", "$0.9$", "$0.6$"],
    expl="**答案依据**：$P(AB)=P(B)P(A|B)=0.24$，$P(A\\cup B)=0.5+0.4-0.24=0.66$。A 正确。",
    mis="⚠️ $P(A|B)$ 不是 $P(AB)$，必须乘 $P(B)$。", tags=["条件概率", "高频"]),

Q(SINGLE, "medium", "1.5", "甲乙两机器产量比 3:2，次品率分别 1% 和 2%。任取一件是次品，由甲厂生产的概率是",
    answer=["B"], options=["$\\frac{3}{5}$", "$\\frac{3}{7}$", "$\\frac{1}{2}$", "$\\frac{1}{7}$"],
    expl="**答案依据**：全概率 $P(B)=\\frac35\\times0.01+\\frac25\\times0.02=\\frac{7}{500}$。贝叶斯 $=\\frac{3/500}{7/500}=\\frac37$。B 正确。",
    mis="⚠️ 全概率的分母是各「先验×条件」之和。", tags=["高频", "贝叶斯公式"],
    verify=[{"desc": "P(B)", "code": "Rational(3,5)*Rational(1,100)+Rational(2,5)*Rational(2,100)", "expected": "7/500"},
            {"desc": "贝叶斯", "code": "Rational(3,500)/Rational(7,500)", "expected": "3/7"}]),

Q(SINGLE, "hard", "1.5", "某病发病率 1%，检测阳性率 95%（患者），假阳性率 5%（健康者）。检测结果阳性，确实患病的概率是",
    answer=["A"], options=["$\\frac{19}{118}$", "$95\\%$", "$50\\%$", "$\\frac{1}{2}$"],
    expl="**答案依据**：$P(\\text{阳})=0.01\\times0.95+0.99\\times0.05=0.059$。$P(\\text{病}\\mid\\text{阳})=\\frac{0.0095}{0.059}=\\frac{19}{118}\\approx16\\%$。A 正确。\n**创新点**：即使检出率 95%，阳性后患病概率也仅 16%——基率谬误。",
    mis="⚠️ 基率谬误：忽略大量健康人的假阳性贡献。", tags=["创新题", "贝叶斯公式"],
    verify=[{"desc": "P(病|阳)", "code": "Rational(95,1000)/Rational(59,1000)", "expected": "19/118"}]),

Q(MULTI, "medium", "1.6", "设 $A,B$ 独立且 $P(A)>0,P(B)>0$，则正确的有",
    answer=["A", "B", "D"],
    options=["$P(AB)=P(A)P(B)$", "$P(A|B)=P(A)$", "$A$ 与 $B$ 互斥", "$\\bar{A}$ 与 $\\bar{B}$ 独立"],
    expl="**答案依据**：独立性定义及推论。C 错：互斥 $P(AB)=0$，独立 $P(AB)=P(A)P(B)>0$——矛盾。",
    mis="⚠️ 互斥 ≠ 独立（正概率下互斥⇒不独立）。", tags=["高频", "独立性"]),

Q(MULTI, "hard", "1.6", "设 $A,B$ 互斥且 $P(A)>0,P(B)>0$，则正确的有",
    answer=["A", "C"],
    options=["$P(A\\cup B)=P(A)+P(B)$", "$A,B$ 独立", "$P(B|A)=0$", "$P(A)=P(B)$"],
    expl="**答案依据**：互斥⇒$P(AB)=0$⇒$P(B|A)=0$（C 正确）；加法公式退化为 A。B 错：$P(AB)=0\\neq P(A)P(B)$。",
    mis="⚠️ 互斥事件的条件概率恒为 0。", tags=["互斥", "条件概率"]),

Q(JUDGE, "basic", "1.2", "若 $P(A)=0$，则 $A$ 是不可能事件。",
    answer=["B"], expl="**答案依据**：零概率事件不一定是不可能事件（连续型反例）。", tags=["零概率事件"]),

Q(JUDGE, "basic", "1.6", "若 $A,B$ 互斥且概率均正，则 $A,B$ 一定不独立。",
    answer=["A"], expl="**答案依据**：互斥⇒$P(AB)=0\\neq P(A)P(B)>0$。", tags=["互斥与独立"]),

Q(BLANK, "basic", "1.2", "加法公式：$P(A\\cup B)=P(A)+P(B)-$ ______。",
    answer=["$P(AB)$"], accept=["P(AB)", "P(A∩B)"], expl="加法公式。", tags=["基础", "加法公式"]),

Q(BLANK, "medium", "1.4", "$n$ 次独立试验每次 $A$ 发生概率 $p$，则 $A$ 至少发生一次的概率为 ______。",
    answer=["$1-(1-p)^{n}$"], accept=["1-(1-p)^n", "1-(1-p)**n"],
    expl="对立事件法：全不发生 $(1-p)^n$。", tags=["高频", "至少一次"]),

Q(BLANK, "medium", "1.3", "在 $(0,1)$ 中随机取两数，两数之差的绝对值小于 $\\frac12$ 的概率为 ______。",
    answer=["$\\frac{3}{4}$"], accept=["3/4", "0.75"],
    expl="几何概型：$|x-y|<\\frac12$ 挖去两个三角形各面积 $\\frac18$，剩余 $\\frac34$。", tags=["几何概型"]),

Q(CALC, "hard", "1.5", "仓库 6 箱产品：甲厂 3 箱（次品率 1/10），乙厂 2 箱（1/15），丙厂 1 箱（1/20）。任取一件是次品，求由甲厂生产的概率。",
    answer_text="全概率：$P(B)=\\frac36\\cdot\\frac{1}{10}+\\frac26\\cdot\\frac{1}{15}+\\frac16\\cdot\\frac{1}{20}=\\frac{11}{120}$。\n贝叶斯：$P(A_1|B)=\\frac{1/20}{11/120}=\\frac{6}{11}$。",
    points=[{"text": "全概率 $=\\frac{11}{120}$", "partial": 2}, {"text": "贝叶斯 $=\\frac{6}{11}$", "partial": 2},
            {"text": "公式结构完整", "partial": 2}, {"text": "解读先验影响", "partial": 2}],
    expl="**答案依据**：§1.5 全概率与贝叶斯。", mis="⚠️ 全概率分母漏加某一厂。", tags=["计算", "高频", "贝叶斯公式"],
    verify=[{"desc": "P(B)", "code": "Rational(3,6)*Rational(1,10)+Rational(2,6)*Rational(1,15)+Rational(1,6)*Rational(1,20)", "expected": "11/120"},
            {"desc": "P(A1|B)", "code": "Rational(1,20)/Rational(11,120)", "expected": "6/11"}]),

Q(CALC, "hard", "1.3", "（创新·蒙特卡洛）正方形边长 2，内切圆半径 1。投点 N 个落入圆内 M 个。证明 $\\frac{4M}{N}\\xrightarrow{P}\\pi$。",
    answer_text="几何概型 $P(A)=\\frac{\\pi}{4}$。由伯努利大数定律 $\\frac{M}{N}\\xrightarrow{P}\\frac{\\pi}{4}$，故 $\\frac{4M}{N}\\xrightarrow{P}\\pi$。",
    points=[{"text": "几何概型 $P(A)=\\frac{\\pi}{4}$", "partial": 2}, {"text": "引用伯努利大数定律", "partial": 2},
            {"text": "得出结论", "partial": 2}, {"text": "蒙特卡洛思想", "partial": 2}],
    expl="**答案依据**：§1.3 几何概型 + §5.2 伯努利大数定律。", mis="⚠️ 依概率收敛≠数列极限。", tags=["创新题", "蒙特卡洛"],
    verify=[{"desc": "P(A)", "code": "pi/4", "expected": "pi/4"}]),
]
