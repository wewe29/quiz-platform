# -*- coding: utf-8 -*-
"""第3章 多维随机变量及其分布（14 题）"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = [
Q(SINGLE, "basic", "3.1", "设 $(X,Y)$ 联合分布列 $P(X=i,Y=j)=c(i+j)$（$i,j=1,2$），则 $c=$",
    answer=["A"], options=["$\\frac{1}{18}$", "$\\frac{1}{12}$", "$\\frac{1}{6}$", "$\\frac{1}{9}$"],
    expl="**答案依据**：$\\sum P=1$：$c(2+3+3+4)=12c=1$，$c=\\frac{1}{18}$。A 正确。",
    tags=["基础", "联合分布"]),

Q(SINGLE, "medium", "3.2", "$X$ 的边缘分布 $P(X=i)=$",
    answer=["A"], options=["$\\sum_j P(X=i,Y=j)$", "$\\sum_i P(X=i,Y=j)$", "$P(X=i,Y=i)$", "$P(X=i)\\cdot P(Y=j)$"],
    expl="**答案依据**：边缘分布 = 联合分布对另一变量求和。A 正确。", tags=["基础", "边缘分布"]),

Q(SINGLE, "medium", "3.4", "$(X,Y)$ 相互独立当且仅当",
    answer=["B"], options=["$E(XY)=E(X)E(Y)$", "$P(X=i,Y=j)=P(X=i)P(Y=j)$ 对所有 $i,j$", "$P(X<Y)=0.5$", "$X+Y$ 是正态分布"],
    expl="**答案依据**：离散型独立性 = 联合分布列 = 边缘分布列之积（所有 $(i,j)$）。B 正确。", tags=["独立性"]),

Q(SINGLE, "hard", "3.3", "$(X,Y)$ 在 $D=\\{(x,y):0<x<1,0<y<x\\}$ 上均匀分布，条件密度 $f_{Y|X}(y|x)=$",
    answer=["A"], options=["$\\frac{1}{x}$（$0<y<x$）", "$\\frac{1}{y}$", "$1$", "$x$"],
    expl="**答案依据**：$D$ 面积 $=\\frac{1}{2}$，$f(x,y)=2$。$f_X(x)=2x$，$f_{Y|X}=\\frac{2}{2x}=\\frac{1}{x}$。A 正确。",
    tags=["高频", "条件分布"]),

Q(MULTI, "medium", "3.4", "设 $X,Y$ 独立，则正确的有",
    answer=["A", "B", "C"], options=["$f(x,y)=f_X(x)f_Y(y)$", "$F(x,y)=F_X(x)F_Y(y)$", "$X$ 的取值不影响 $Y$ 的分布", "$X+Y$ 一定服从正态分布"],
    expl="**答案依据**：A、B、C 正确。D 错：独立不一定和为正态。", tags=["独立性"]),

Q(MULTI, "hard", "3.2", "关于边缘分布，正确的有",
    answer=["A", "B"], options=["边缘分布可由联合分布唯一确定", "边缘分布一般不能唯一确定联合分布", "边缘分布总是连续函数", "两个边缘都是正态则联合也是正态"],
    expl="**答案依据**：A、B 正确。C 错：离散型的边缘是分布列。D 错：反例存在。", tags=["边缘分布"]),

Q(JUDGE, "basic", "3.2", "知道了 $X$ 和 $Y$ 的边缘分布，就能唯一确定 $(X,Y)$ 的联合分布。",
    answer=["B"], expl="**答案依据**：边缘分布一般不能唯一确定联合分布。", tags=["边缘分布"]),

Q(JUDGE, "medium", "3.4", "若 $(X,Y)$ 服从二维正态分布，则 $X$ 与 $Y$ 独立当且仅当它们不相关。",
    answer=["A"], expl="**答案依据**：二维正态的特有性质——独立 ⇔ ρ=0。一般分布不成立。", tags=["高频", "二维正态"]),

Q(BLANK, "basic", "3.1", "$(X,Y)$ 在 $D=\\{(x,y):0\\le x\\le1,0\\le y\\le2\\}$ 上均匀分布，则 $P(X+Y\\le1)=$ ______。",
    answer=["$\\frac{1}{4}$"], accept=["1/4", "0.25"],
    expl="**答案依据**：$D$ 面积 2，条件区域三角形面积 $\\frac12$，$P=\\frac{1/2}{2}=\\frac14$。", tags=["均匀分布"]),

Q(BLANK, "medium", "3.2", "联合密度 $f(x,y)=2e^{-(2x+y)}$（$x>0,y>0$），$f_X(x)=$ ______（$x>0$）。",
    answer=["$2e^{-2x}$"], accept=["2e^(-2x)", "2exp(-2x)"],
    expl="**答案依据**：$f_X(x)=\\int_0^{\\infty}2e^{-(2x+y)}dy=2e^{-2x}$。", tags=["边缘密度"]),

Q(CALC, "medium", "3.2", "$(X,Y)$ 联合分布列：$P(0,0)=\\frac16, P(0,1)=\\frac13, P(1,0)=\\frac19, P(1,1)=\\frac29$。求边缘分布并判断独立性。",
    answer_text="$P(X=0)=\\frac12, P(X=1)=\\frac12$；$P(Y=0)=\\frac59, P(Y=1)=\\frac49$。$P(0,0)=\\frac16\\neq\\frac12\\times\\frac59=\\frac5{18}$——不独立。",
    points=[{"text": "求出边缘分布列", "partial": 2}, {"text": "检验独立性", "partial": 2}, {"text": "结论不独立", "partial": 2}, {"text": "举出反例", "partial": 2}],
    expl="**答案依据**：§3.2 边缘分布 + §3.4 独立性判定。", mis="⚠️ 独立性必须对所有 $(i,j)$ 验证。", tags=["计算", "独立性"]),

Q(CALC, "hard", "3.3", "$X,Y$ 独立且均服从 $U(0,1)$。求 $Z=X+Y$ 的密度函数。",
    answer_text="卷积公式。$0<z<1$：$f_Z(z)=z$；$1\\le z<2$：$f_Z(z)=2-z$。（三角形密度）",
    points=[{"text": "写出卷积公式", "partial": 2}, {"text": "确定积分限（分段）", "partial": 2}, {"text": "结果", "partial": 2}, {"text": "归一验证", "partial": 2}],
    expl="**答案依据**：§3.3 卷积公式。", mis="⚠️ 积分限由 $0<x<1$ 和 $0<z-x<1$ 的交集决定。", tags=["计算", "高频", "卷积公式"],
    verify=[{"desc": "归一", "code": "integrate(z,(z,0,1))+integrate(2-z,(z,1,2))", "expected": "1"}]),

Q(CALC, "hard", "3.4", "$X,Y$ 独立且均服从 $U(0,1)$。求 $M=\\max(X,Y)$ 的分布函数与密度函数。",
    answer_text="$F_M(z)=z^2$（$0\\le z\\le1$），$f_M(z)=2z$。",
    points=[{"text": "用独立性分解", "partial": 2}, {"text": "结果 $F_M(z)=z^2$", "partial": 2}, {"text": "密度 $f_M(z)=2z$", "partial": 2}, {"text": "归一验证", "partial": 2}],
    expl="**答案依据**：§3.4 最大值分布。", mis="⚠️ max 用乘积，min 用 $1-F$。", tags=["计算", "max/min"],
    verify=[{"desc": "E(M)", "code": "integrate(2*z*z, (z, 0, 1))", "expected": "2/3"}]),

Q(SINGLE, "hard", "3.4", "设 $M=\\max(X,Y)$，$N=\\min(X,Y)$，则 $M\\ge N$",
    answer=["A"], options=["恒成立", "不成立", "仅当 $X=Y$", "仅当 $X,Y$ 独立"],
    expl="**答案依据**：max ≥ min 恒成立（取的是同一对值）。A 正确。", tags=["max/min"]),
]
