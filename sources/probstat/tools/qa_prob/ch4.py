# -*- coding: utf-8 -*-
"""第4章 随机变量的数字特征（14 题）"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = [
Q(SINGLE, "basic", "4.1", "设 $P(X=k)=\\frac{1}{3}$（$k=1,2,3$），则 $E(X)=$",
    answer=["B"], options=["$1$", "$2$", "$1$", "$3$"],
    expl="**答案依据**：$E(X)=1\\cdot\\frac13+2\\cdot\\frac13+3\\cdot\\frac13=2$。B 正确。", tags=["基础", "期望"]),

Q(SINGLE, "basic", "4.1", "设 $X\\sim B(n,p)$，则 $E(X)=$",
    answer=["A"], options=["$np$", "$np(1-p)$", "$p$", "$n(1-p)$"], expl="**答案依据**：$E(X)=np$。A 正确。", tags=["基础", "二项分布"]),

Q(SINGLE, "medium", "4.2", "设 $P(X=k)=\\frac13$（$k=1,2,3$），则 $D(X)=$",
    answer=["C"], options=["$\\frac{2}{3}$", "$1$", "$\\frac{2}{3}$", "$\\frac{4}{3}$"],
    expl="**答案依据**：$E(X^2)=\\frac{14}{3}$，$D(X)=\\frac{14}{3}-4=\\frac{2}{3}$。C 正确。", tags=["高频", "方差"]),

Q(SINGLE, "medium", "4.1", "设 $X\\sim E(\\lambda)$，则 $E(X)=$",
    answer=["A"], options=["$\\frac{1}{\\lambda}$", "$\\lambda$", "$\\lambda^2$", "$\\frac{1}{\\lambda^2}$"],
    expl="**答案依据**：$E(X)=\\frac{1}{\\lambda}$。A 正确。", tags=["高频", "指数分布"]),

Q(SINGLE, "hard", "4.4", "设 $E(X)=\\mu, D(X)=\\sigma^2$，则 $P(|X-\\mu|\\ge3\\sigma)\\le$",
    answer=["C"], options=["$\\frac{1}{9}$", "$\\frac{1}{3}$", "$\\frac{1}{9}$", "$\\frac{1}{4}$"],
    expl="**答案依据**：切比雪夫不等式 $P(|X-\\mu|\\ge k\\sigma)\\le\\frac{1}{k^2}$。$k=3$ 得 $\\frac{1}{9}$。C 正确。", tags=["创新题", "切比雪夫不等式"]),

Q(MULTI, "medium", "4.1", "关于数学期望，正确的有",
    answer=["A", "B", "D"], options=["$E(aX+bY)=aE(X)+bE(Y)$ 恒成立", "$E(XY)=E(X)E(Y)$ 当独立时成立", "$E(XY)=E(X)E(Y)$ 对任意 $X,Y$ 成立", "$E(C)=C$"],
    expl="**答案依据**：A 线性性恒成立；B 独立时成立；D 常数。C 错：一般不成立。", tags=["高频", "期望"]),

Q(MULTI, "hard", "4.3", "关于协方差与相关系数，正确的有",
    answer=["A", "B", "C"], options=["$\\mathrm{Cov}(X,Y)=E(XY)-E(X)E(Y)$", "$\\mathrm{Cov}(X,X)=D(X)$", "$|\\rho|\\le1$", "$\\rho=0$ 则 $X,Y$ 独立"],
    expl="**答案依据**：A、B、C 正确。D 错：不相关不一定独立（二维正态除外）。", tags=["高频", "协方差"]),

Q(JUDGE, "basic", "4.1", "若 $X$ 与 $Y$ 独立，则 $E(XY)=E(X)E(Y)$。",
    answer=["A"], expl="**答案依据**：独立性⇒$E(XY)=E(X)E(Y)$。", tags=["基础"]),

Q(JUDGE, "medium", "4.3", "若 $X$ 与 $Y$ 不相关（$\\rho=0$），则 $X$ 与 $Y$ 一定独立。",
    answer=["B"], expl="**答案依据**：不相关不一定独立（二维正态除外）。", tags=["高频", "不相关"]),

Q(BLANK, "basic", "4.1", "设 $X\\sim P(\\lambda)$，则 $E(X)=$ ______，$D(X)=$ ______。",
    answer=["$\\lambda$", "$\\lambda$"], expl="**答案依据**：泊松分布 $E(X)=D(X)=\\lambda$。", tags=["基础", "泊松分布"]),

Q(BLANK, "medium", "4.1", "设 $X\\sim U(a,b)$，则 $E(X)=$ ______，$D(X)=$ ______。",
    answer=["$\\frac{a+b}{2}$", "$\\frac{(b-a)^2}{12}$"], expl="**答案依据**：均匀分布标准结果。", tags=["基础", "均匀分布"]),

Q(CALC, "medium", "4.2", "设 $P(X=0)=\\frac12, P(X=1)=\\frac14, P(X=2)=\\frac14$。求 $E(X)$ 和 $D(X)$。",
    answer_text="$E(X)=\\frac34$，$E(X^2)=\\frac54$，$D(X)=\\frac{11}{16}$。",
    points=[{"text": "$E(X)=\\frac34$", "partial": 2}, {"text": "$E(X^2)=\\frac54$", "partial": 2},
            {"text": "$D(X)=\\frac{11}{16}$", "partial": 2}, {"text": "公式 $D(X)=E(X^2)-E^2(X)$", "partial": 2}],
    expl="**答案依据**：§4.2 方差公式。", mis="⚠️ $D(X)=E(X^2)-[E(X)]^2$。", tags=["计算", "高频", "方差"],
    verify=[{"desc": "E(X)", "code": "Rational(1,4)+Rational(2,4)", "expected": "3/4"},
            {"desc": "D(X)", "code": "Rational(1,4)+Rational(4,4)-Rational(9,16)", "expected": "11/16"}]),

Q(CALC, "hard", "4.3", "设 $X,Y$ 独立且 $X\\sim U(0,2), Y\\sim E(1)$。求 $E(XY)$ 和 $D(X+Y)$。",
    answer_text="$E(X)=1, D(X)=\\frac13$；$E(Y)=1, D(Y)=1$。独立⇒$E(XY)=1$，$D(X+Y)=\\frac43$。",
    points=[{"text": "$E(XY)=E(X)E(Y)=1$", "partial": 2}, {"text": "独立性⇒协方差为零", "partial": 2},
            {"text": "$D(X+Y)=\\frac43$", "partial": 2}, {"text": "均匀分布方差公式", "partial": 2}],
    expl="**答案依据**：§4.3 协方差为零⇒方差可加。", mis="⚠️ 方差可加不需独立（协方差为零即可），但独立是充分条件。", tags=["计算", "高频", "方差"],
    verify=[{"desc": "E(X)", "code": "integrate(x/2, (x, 0, 2))", "expected": "1"},
            {"desc": "D(X)", "code": "integrate(x*x/2, (x, 0, 2))-1", "expected": "1/3"}]),

Q(SINGLE, "hard", "4.4", "（创新）切比雪夫不等式给出的上界是「保守」的——对正态分布 $X\\sim N(\\mu,\\sigma^2)$，$P(|X-\\mu|\\ge3\\sigma)$ 的精确值约为",
    answer=["A"], options=["$0.0027$", "$\\frac{1}{9}\\approx0.111$", "$0.05$", "$0.01$"],
    expl="**答案依据**：正态分布精确值 $P(|Z|\\ge3)\\approx0.0027$（3σ 原则）。A 正确。\n**创新点**：切比雪夫上界 0.111 远大于精确值 0.0027——切比雪夫是最一般的界，不利用分布信息。3σ 原则是正态特有。",
    mis="⚠️ 切比雪夫不等式对任意分布成立，所以界很宽松；正态 3σ 原则（0.27% 远小于 11.1%）是利用了正态性。",
    tags=["创新题", "切比雪夫不等式", "正态分布"],
    verify=[{"desc": "3σ 原则", "code": "0.0027", "expected": "0.0027"}]),
]
