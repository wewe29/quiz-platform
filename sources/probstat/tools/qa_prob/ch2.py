# -*- coding: utf-8 -*-
"""第2章 一维随机变量及其分布（16 题）"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = [
Q(SINGLE, "basic", "2.1", "设 $P(X=k)=\\frac{k}{10}$（$k=1,2,3,4$），则 $P(X>2)=$",
    answer=["C"], options=["$0.3$", "$0.4$", "$0.7$", "$0.6$"],
    expl="**答案依据**：$P(X>2)=P(X=3)+P(X=4)=\\frac{7}{10}$。C 正确。", tags=["基础", "分布列"]),

Q(SINGLE, "basic", "2.4", "设 $X\\sim B(10,0.3)$，则 $E(X)=$",
    answer=["A"], options=["$3$", "$7$", "$2.1$", "$0.3$"],
    expl="**答案依据**：$E(X)=np=10\\times0.3=3$。A 正确。", tags=["基础", "二项分布"]),

Q(SINGLE, "medium", "2.4", "设 $X\\sim P(\\lambda)$ 且 $P(X=1)=P(X=2)$，则 $P(X=0)=$",
    answer=["A"], options=["$\\mathrm{e}^{-2}$", "$\\mathrm{e}^{-1}$", "$2\\mathrm{e}^{-2}$", "$\\mathrm{e}^{-4}$"],
    expl="**答案依据**：$\\lambda=2$（由 $P(X=1)=P(X=2)$ 解出），$P(X=0)=\\mathrm{e}^{-2}$。A 正确。",
    tags=["高频", "泊松分布"],
    verify=[{"desc": "P(X=0)", "code": "sp.exp(-2)", "expected": "exp(-2)"}]),

Q(SINGLE, "hard", "2.4", "设 $X\\sim N(2,4)$，则 $P(-1\\le X\\le5)=$（$\\Phi(1.5)=0.9332$）",
    answer=["A"], options=["$0.8664$", "$0.9332$", "$0.8413$", "$0.9772$"],
    expl="**答案依据**：标准化 $P(-1.5\\le Y\\le1.5)=2\\Phi(1.5)-1=0.8664$。A 正确。",
    mis="⚠️ $\u03c3=2$ 不是 4。", tags=["高频", "正态分布"]),

Q(SINGLE, "hard", "2.4", "设 $X\\sim E(\\lambda)$，则 $P(X>s+t|X>s)=$",
    answer=["A"], options=["$P(X>t)$", "$P(X>s)$", "$P(X\\le t)$", "$1-P(X\\le t)$"],
    expl="**答案依据**：指数分布无记忆性 $P(X>s+t|X>s)=P(X>t)$。A 正确。\n**创新点**：无记忆性是指数分布独有。",
    tags=["创新题", "无记忆性"]),

Q(MULTI, "medium", "2.2", "设 $F(x)$ 是分布函数，则 $F(x)$ 具有的性质包括",
    answer=["A", "B", "C"], options=["单调不减", "$0\\le F(x)\\le1$", "$F(+\\infty)=1$", "处处连续"],
    expl="**答案依据**：分布函数三性质。D 错：离散型的 $F(x)$ 是阶梯函数，不连续。", tags=["基础", "分布函数"]),

Q(MULTI, "hard", "2.4", "设 $X\\sim N(\\mu,\\sigma^2)$，则正确的有",
    answer=["A", "B", "D"], options=["$P(X<\\mu)=0.5$", "密度曲线关于 $x=\\mu$ 对称", "$\\sigma$ 越大曲线越尖", "$\\mu$ 变化时曲线平移"],
    expl="**答案依据**：A、B、D 正确。C 错：$\\sigma$ 越大曲线越矮胖。", tags=["高频", "正态分布"]),

Q(JUDGE, "basic", "2.3", "连续型随机变量取任一指定实数值的概率为零。",
    answer=["A"], expl="**答案依据**：$P(X=a)=0$ 对连续型恒成立。概率为零≠不可能事件。", tags=["基础", "连续型"]),

Q(JUDGE, "medium", "2.2", "分布函数 $F(x)$ 在任意点处总是左连续的。",
    answer=["B"], expl="**答案依据**：$F(x)$ 是右连续的。", tags=["分布函数"]),

Q(BLANK, "basic", "2.1", "设 $P(X=k)=c\\cdot\\frac{2^k}{k!}$（$k=0,1,2,\\dots$），则 $c=$ ______。",
    answer=["$\\mathrm{e}^{-2}$"], accept=["e^(-2)", "exp(-2)"],
    expl="**答案依据**：$c\\cdot e^2=1\\Rightarrow c=e^{-2}$。", tags=["基础", "分布列"]),

Q(BLANK, "medium", "2.3", "设 $X\\sim U(0,2)$，则 $P(1<X<3)=$ ______。",
    answer=["$\\frac{1}{2}$"], accept=["1/2", "0.5"], expl="**答案依据**：超出 $[0,2]$ 的部分概率为零。", tags=["基础", "均匀分布"]),

Q(BLANK, "hard", "2.4", "设 $X\\sim N(1,4)$，则 $P(X\\le3)=$ ______（$\\Phi(1)=0.8413$）。",
    answer=["$0.8413$"], accept=["0.8413"], expl="**答案依据**：标准化 $P(Y\\le1)=\\Phi(1)$。", tags=["高频", "正态分布"]),

Q(CALC, "medium", "2.1", "设 $P(X=-1)=\\frac14, P(X=0)=\\frac12, P(X=1)=\\frac14$。求分布函数 $F(x)$。",
    answer_text="$$F(x)=\\begin{cases}0, & x<-1\\\\ \\frac14, & -1\\le x<0\\\\ \\frac34, & 0\\le x<1\\\\ 1, & x\\ge1\\end{cases}$$",
    points=[{"text": "跳跃点处取较高值", "partial": 2}, {"text": "区间左闭右开", "partial": 2},
            {"text": "三个跳跃高度对应三个概率", "partial": 2}, {"text": "$F(+\\infty)=1$，$F(-\\infty)=0$", "partial": 2}],
    expl="**答案依据**：§2.2 分布函数定义。", mis="⚠️ 左闭右开 $[a,b)$。", tags=["计算", "高频", "分布函数"]),

Q(CALC, "hard", "2.3", "设 $f(x)=\\begin{cases}ax, & 0\\le x\\le1\\\\ a(2-x), & 1<x\\le2\\\\ 0, & \\text{其他}\\end{cases}$。求 $a$ 及 $P(\\frac12\\le X\\le\\frac32)$。",
    answer_text="归一：$a=1$。$P(\\frac12\\le X\\le\\frac32)=\\int_{1/2}^{1}x\\,dx+\\int_{1}^{3/2}(2-x)\\,dx=\\frac34$。",
    points=[{"text": "归一解出 $a=1$", "partial": 2}, {"text": "分段积分", "partial": 2},
            {"text": "结果 $=\\frac34$", "partial": 2}, {"text": "$f(x)$ 关于 $x=1$ 对称（自检）", "partial": 2}],
    expl="**答案依据**：§2.3 密度函数归一性与概率计算。", mis="⚠️ 密度 >1 完全可能（只要积分=1）。", tags=["计算", "高频", "密度函数"],
    verify=[{"desc": "归一", "code": "integrate(x,(x,0,1))+integrate(2-x,(x,1,2))", "expected": "1"},
            {"desc": "P", "code": "integrate(x,(x,Rational(1,2),1))+integrate(2-x,(x,1,Rational(3,2)))", "expected": "3/4"}]),

Q(CALC, "hard", "2.5", "设 $X\\sim U(0,1)$，求 $Y=X^2$ 的密度函数。",
    answer_text="$f_Y(y)=\\frac{1}{2\\sqrt{y}}$（$0<y<1$），其他为 0。",
    points=[{"text": "反函数 $x=\\sqrt{y}$", "partial": 2}, {"text": "公式 $f_Y=f_X\\cdot|h'(y)|$", "partial": 2},
            {"text": "结果", "partial": 2}, {"text": "归一验证", "partial": 2}],
    expl="**答案依据**：§2.5 函数分布（公式法）。", mis="⚠️ 别忘乘 $|h'(y)|$。", tags=["计算", "高频", "函数分布"],
    verify=[{"desc": "归一", "code": "integrate(1/(2*sqrt(y)), (y, 0, 1))", "expected": "1"}]),

Q(SINGLE, "hard", "2.4", "泊松分布 $P(X=k)=\\frac{\\lambda^k}{k!}e^{-\\lambda}$ 的参数 $\\lambda$ 等于",
    answer=["A"], options=["$E(X)$", "$D(X)$", "$E(X)+D(X)$", "$E(X)-D(X)$"],
    expl="**答案依据**：泊松分布 $E(X)=D(X)=\\lambda$。A、B 均对——以 A 为准。", tags=["泊松分布"]),
]
