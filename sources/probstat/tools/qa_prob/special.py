# -*- coding: utf-8 -*-
"""概率论与数理统计 —— 基础与中等扩充 56 题（2026-11-01 第二批）"""
from .common import Q as mk, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

_qlist = []

# ═══ ch1 随机事件与概率（+8）═══
_qlist.append(mk(SINGLE, "basic", "1.3", "从 5 名男同学和 3 名女同学中随机选 3 名，恰好选中 2 男 1 女的概率是",
    answer=["B"], options=["$\\frac{15}{28}$", "$\\frac{15}{56}$", "$\\frac{5}{14}$", "$\\frac{3}{8}$"],
    expl="**答案依据**：$P=\\frac{C_5^2 C_3^1}{C_8^3}=\\frac{10\\times3}{56}=\\frac{15}{28}$。B 正确。",
    tags=["基础", "古典概型"],
    verify=[{"desc": "P", "code": "Rational(sp.binomial(5,2)*sp.binomial(3,1), sp.binomial(8,3))", "expected": "15/28"}]))

_qlist.append(mk(SINGLE, "medium", "1.4", "设 $P(A)=0.3, P(B)=0.4, P(A\\cup B)=0.6$，则 $P(A|B)=$",
    answer=["A"], options=["$\\frac{1}{4}$", "$\\frac{1}{5}$", "$\\frac{3}{4}$", "$\\frac{1}{3}$"],
    expl="**答案依据**：$P(AB)=P(A)+P(B)-P(A\\cup B)=0.1$。$P(A|B)=\\frac{0.1}{0.4}=\\frac14$。A 正确。",
    tags=["中等", "条件概率"]))

_qlist.append(mk(SINGLE, "medium", "1.5", "三个口袋各 3 球：甲袋 2 红 1 白，乙袋 1 红 2 白，丙袋 2 红 2 白。随机选一袋再取一球，取到红球的概率是",
    answer=["A"], options=["$\\frac{1}{2}$", "$\\frac{2}{3}$", "$\\frac{1}{3}$", "$\\frac{5}{9}$"],
    expl="**答案依据**：全概率 $P(B)=\\frac13(\\frac23+\\frac13+\\frac12)=\\frac{1}{2}$。A 正确。",
    tags=["中等", "全概率公式"], variant_group="vg-fullprob"))

_qlist.append(mk(SINGLE, "hard", "1.5", "接上题：已知取到红球，则来自甲袋的概率是",
    answer=["A"], options=["$\\frac{4}{9}$", "$\\frac{2}{3}$", "$\\frac{1}{3}$", "$\\frac{5}{9}$"],
    expl="**答案依据**：贝叶斯 $P(\\text{甲}|\\text{红})=\\frac{2/9}{1/2}=\\frac{4}{9}$。A 正确。",
    tags=["创新题", "贝叶斯公式"], variant_group="vg-fullprob"))

_qlist.append(mk(MULTI, "medium", "1.6", "设 $A,B$ 为两事件且 $P(A)>0$，则 $P(B|A)$ 的正确表达式有",
    answer=["A", "C"], options=["$\\frac{P(AB)}{P(A)}$", "$\\frac{P(AB)}{P(B)}$", "$\\frac{P(A|B)P(B)}{P(A)}$", "$P(A)P(B)$"],
    expl="**答案依据**：条件概率定义 $P(B|A)=\\frac{P(AB)}{P(A)}$（A）；乘法公式 $P(AB)=P(B|A)P(A)$ 也可写作 $P(B|A)=\\frac{P(A|B)P(B)}{P(A)}$（C，由 $P(AB)=P(A|B)P(B)$ 变形）。B 分母错，D 是独立性结论。", tags=["条件概率"]))

_qlist.append(mk(JUDGE, "basic", "1.2", "$P(A\\cup B)\\le P(A)+P(B)$ 恒成立。",
    answer=["A"], expl="**答案依据**：$P(A\\cup B)=P(A)+P(B)-P(AB)\\le P(A)+P(B)$。", tags=["基础"]))

_qlist.append(mk(BLANK, "medium", "1.2", "德摩根律：$\\overline{A\\cup B}=$ ______ $\\cap$ ______。",
    answer=["$\\bar{A}$", "$\\bar{B}$"], expl="**答案依据**：德摩根律。", tags=["中等", "德摩根律"]))

_qlist.append(mk(CALC, "hard", "1.4", "（创新）甲、乙、丙三人独立破译同一密码，破译概率分别为 $\\frac12,\\frac13,\\frac14$。求密码被破译的概率。",
    answer_text="$P=1-\\frac12\\cdot\\frac23\\cdot\\frac34=\\frac34$。",
    points=[{"text": "用对立事件", "partial": 2}, {"text": "三人独立概率相乘", "partial": 2},
            {"text": "结果 $=\\frac34$", "partial": 2}, {"text": "说明为何不用全概率", "partial": 2}],
    expl="**答案依据**：§1.6 独立性+对立事件。", mis="⚠️ 不能直接相加概率。",
    tags=["创新题", "独立性", "至少一次"],
    verify=[{"desc": "P", "code": "1-Rational(1,2)*Rational(2,3)*Rational(3,4)", "expected": "3/4"}]))

# ═══ ch2 一维随机变量（+8）═══
_qlist.append(mk(SINGLE, "basic", "2.1", "设 $P(X=k)=\\frac{c}{2^k}$（$k=1,2,3$），则 $c=$",
    answer=["A"], options=["$\\frac{4}{7}$", "$\\frac{2}{7}$", "$\\frac{1}{7}$", "$\\frac{8}{7}$"],
    expl="**答案依据**：$c(\\frac12+\\frac14+\\frac18)=c\\cdot\\frac74=1$，$c=\\frac47$。A 正确。", tags=["基础", "分布列"]))

_qlist.append(mk(SINGLE, "medium", "2.4", "设 $X\\sim B(4,\\frac13)$，则 $P(X\\ge1)=$",
    answer=["A"], options=["$1-(\\frac23)^4$", "$\\frac{65}{81}$", "$\\frac{8}{27}$", "$\\frac{32}{81}$"],
    expl="**答案依据**：$1-(\\frac23)^4=\\frac{65}{81}$。A 正确。", tags=["中等", "二项分布"],
    variant_group="vg-binomial",
    verify=[{"desc": "P(≥1)", "code": "1-Rational(2,3)**4", "expected": "65/81"}]))

_qlist.append(mk(SINGLE, "medium", "2.4", "设 $X\\sim P(2)$，则 $P(X\\le1)=$",
    answer=["A"], options=["$3e^{-2}$", "$e^{-2}$", "$e^{-4}$", "$2e^{-2}$"],
    expl="**答案依据**：$e^{-2}+2e^{-2}=3e^{-2}$。A 正确。", tags=["中等", "泊松分布"],
    verify=[{"desc": "P(X≤1)", "code": "sp.exp(-2)+2*sp.exp(-2)", "expected": "3*exp(-2)"}]))

_qlist.append(mk(SINGLE, "hard", "2.4", "设 $X\\sim N(1,4)$，则 $P(X\\le3)=$（$\\Phi(1)=0.8413$）",
    answer=["A"], options=["$0.8413$", "$0.9772$", "$0.5$", "$0.1587$"],
    expl="**答案依据**：$P(Z\\le1)=0.8413$。A 正确。", tags=["高频", "正态分布"]))

_qlist.append(mk(SINGLE, "medium", "2.3", "设 $X\\sim U(0,2)$，则 $P(X>\\frac32)=$",
    answer=["B"], options=["$\\frac{1}{2}$", "$\\frac{1}{4}$", "$\\frac{3}{4}$", "$\\frac{1}{8}$"],
    expl="**答案依据**：$\\frac{2-1.5}{2}=\\frac14$。B 正确。", tags=["中等", "均匀分布"]))

_qlist.append(mk(CALC, "hard", "2.5", "设 $X\\sim U(-1,2)$，求 $Y=2X+1$ 的分布函数。",
    answer_text="$F_Y(y)=0(y<-1), \\frac{y+1}{6}(-1\\le y<5), 1(y\\ge5)$。",
    points=[{"text": "确定 $Y$ 的范围", "partial": 2}, {"text": "分布函数", "partial": 2},
            {"text": "结果", "partial": 2}, {"text": "边界验证", "partial": 2}],
    expl="**答案依据**：§2.5 线性变换分布函数法。", tags=["计算", "函数分布"],
    verify=[{"desc": "F(5)", "code": "Rational(6,6)", "expected": "1"}]))

_qlist.append(mk(BLANK, "basic", "2.2", "$F(+\\infty)=$ ______，$F(-\\infty)=$ ______。",
    answer=["$1$", "$0$"], expl="分布函数边界性质。", tags=["基础", "分布函数"]))

_qlist.append(mk(JUDGE, "medium", "2.3", "若 $f(x)$ 是概率密度函数，则 $f(x)\\le1$。",
    answer=["B"], expl="**答案依据**：密度只需 $f\\ge0$ 且 $\\int f=1$。$f$ 可以 >1。", tags=["中等", "密度函数"]))

# ═══ ch3 多维随机变量（+8）═══
_qlist.append(mk(SINGLE, "basic", "3.1", "$(X,Y)$ 联合密度 $f(x,y)=c(x+y)$（$0<x<1,0<y<1$），则 $c=$",
    answer=["A"], options=["$1$", "$\\frac{1}{2}$", "$2$", "$\\frac{1}{3}$"],
    expl="**答案依据**：$\\int\\int=1$：$c\\cdot\\int_0^1\\int_0^1(x+y)dxdy=c\\cdot1=1$，$c=1$。A 正确。", tags=["基础", "联合密度"],
    variant_group="vg-jointxy",
    verify=[{"desc": "归一", "code": "integrate(integrate(x+y,(x,0,1)),(y,0,1))", "expected": "1"}]))

_qlist.append(mk(SINGLE, "medium", "3.2", "接上题：$f_X(x)=$（$0<x<1$）",
    answer=["A"], options=["$x+\\frac{1}{2}$", "$x$", "$2x+\\frac{1}{2}$", "$1$"],
    expl="**答案依据**：$f_X=\\int_0^1(x+y)dy=x+\\frac12$。A 正确。", tags=["中等", "边缘密度"],
    variant_group="vg-jointxy"))

_qlist.append(mk(SINGLE, "medium", "3.4", "接上题：$X,Y$ 是否独立？",
    answer=["B"], options=["独立", "不独立", "无法判断", "当 $x=y$ 时独立"],
    expl="**答案依据**：$f_X f_Y\\neq f(x,y)$。B 正确。", tags=["中等", "独立性"],
    variant_group="vg-jointxy"))

_qlist.append(mk(SINGLE, "hard", "3.4", "$X\\sim U(0,1)$，$Y\\sim U(0,1)$ 独立。$P(X+Y\\le1)=$",
    answer=["B"], options=["$\\frac14$", "$\\frac12$", "$\\frac34$", "$1$"],
    expl="**答案依据**：几何概型，三角形面积 $\\frac12$。B 正确。", tags=["中等", "几何概型"]))

_qlist.append(mk(MULTI, "medium", "3.2", "设 $(X,Y)$ 联合密度为 $f(x,y)$，则 $f_X(x)=$",
    answer=["A", "C"], options=["$\\int_{-\\infty}^{+\\infty}f(x,y)dy$", "对 $y$ 积分", "$\\int_{-\\infty}^{+\\infty}f(x,y)dx$", "$f(x,y)$ 对 $x$ 积分"],
    expl="**答案依据**：边缘密度 = 联合密度对另一变量积分。A、C 等价。", tags=["边缘密度"]))

_qlist.append(mk(JUDGE, "medium", "3.4", "若 $X$ 与 $Y$ 的协方差为零，则 $f(x,y)=f_X(x)f_Y(y)$。",
    answer=["B"], expl="**答案依据**：不相关不一定独立。反例：$X\\sim U(-1,1)$，$Y=X^2$。", tags=["不相关与独立"]))

_qlist.append(mk(BLANK, "basic", "3.1", "联合分布函数 $F(+\\infty,+\\infty)=$ ______，$F(-\\infty,-\\infty)=$ ______。",
    answer=["$1$", "$0$"], expl="联合分布函数边界性质。", tags=["基础", "联合分布函数"]))

_qlist.append(mk(CALC, "hard", "3.2", "联合密度 $f(x,y)=\\begin{cases}2-x-y,&0<x<1,0<y<1\\\\0,\\text{其他}\\end{cases}$。求 $P(X+Y\\le1)$。",
    answer_text="$P=\\int_0^1\\int_0^{1-x}(2-x-y)dydx=\\frac{2}{3}$。",
    points=[{"text": "确定积分区域", "partial": 2}, {"text": "内层积分", "partial": 2}, {"text": "外层积分，结果 $=\\frac23$", "partial": 2}, {"text": "自检 $P+P'=1$", "partial": 2}],
    expl="**答案依据**：§3.1 联合密度概率计算。", tags=["计算", "中等", "联合密度"],
    verify=[{"desc": "P", "code": "integrate(integrate(2-x-y,(y,0,1-x)),(x,0,1))", "expected": "2/3"}]))

# ═══ ch4 数字特征（+8）═══
_qlist.append(mk(SINGLE, "basic", "4.1", "$P(X=k)=\\frac13$（$k=1,2,3$），$E(2X+1)=$",
    answer=["B"], options=["$3$", "$5$", "$4$", "$2$"],
    expl="**答案依据**：$E(X)=2$，$E(2X+1)=5$。B 正确。", tags=["基础", "期望线性性"]))

_qlist.append(mk(SINGLE, "medium", "4.2", "$X\\sim U(-1,3)$，$D(X)=$",
    answer=["B"], options=["$1$", "$\\frac{4}{3}$", "$\\frac{16}{3}$", "$4$"],
    expl="**答案依据**：$\\frac{(3+1)^2}{12}=\\frac43$。B 正确。", tags=["中等", "均匀分布"]))

_qlist.append(mk(SINGLE, "medium", "4.3", "$X,Y$ 独立，$D(X)=4, D(Y)=9$，$D(X-Y)=$",
    answer=["B"], options=["$5$", "$13$", "$-5$", "$1$"],
    expl="**答案依据**：$D(X-Y)=D(X)+D(Y)=13$。B 正确。",
    mis="⚠️ 方差没有减法。", tags=["中等", "方差"]))

_qlist.append(mk(SINGLE, "hard", "4.3", "$X,Y$ 独立同分布，$E=\\mu, D=\\sigma^2$，$E[(X-Y)^2]=$",
    answer=["B"], options=["$0$", "$2\\sigma^2$", "$\\sigma^2$", "$4\\sigma^2$"],
    expl="**答案依据**：$E[(X-Y)^2]=D(X-Y)+[E(X-Y)]^2=2\\sigma^2+0$。B 正确。",
    tags=["创新题", "方差分解"]))

_qlist.append(mk(MULTI, "medium", "4.2", "关于方差，正确的有",
    answer=["A", "B", "C"], options=["$D(aX)=a^2D(X)$", "$D(X)\\ge0$", "$D(X)=E(X^2)-E^2(X)$", "$D(X+Y)=D(X)+D(Y)$ 恒成立"],
    expl="**答案依据**：A、B、C 正确。D 需要独立或协方差为零。", tags=["方差性质"]))

_qlist.append(mk(CALC, "medium", "4.2", "$P(X=-1)=\\frac16, P(X=0)=\\frac13, P(X=1)=\\frac12$。求 $E(X)$ 和 $D(X)$。",
    answer_text="$E(X)=\\frac13$，$E(X^2)=\\frac23$，$D(X)=\\frac59$。",
    points=[{"text": "$E(X)=\\frac13$", "partial": 2}, {"text": "$E(X^2)=\\frac23$", "partial": 2},
            {"text": "$D(X)=\\frac59$", "partial": 2}, {"text": "公式", "partial": 2}],
    expl="**答案依据**：§4.2 方差公式。", tags=["计算", "中等", "方差"],
    verify=[{"desc": "D", "code": "Rational(2,3)-Rational(1,9)", "expected": "5/9"}]))

_qlist.append(mk(CALC, "hard", "4.1", "$X\\sim U(0,2)$。求 $E(X^2)$ 和 $E[(X-1)^2]$。",
    answer_text="$E(X^2)=\\frac43$，$E[(X-1)^2]=\\frac13$。",
    points=[{"text": "$E(X^2)=\\frac43$", "partial": 2}, {"text": "$E(X)=1$", "partial": 2},
            {"text": "$E[(X-1)^2]=\\frac13$", "partial": 2}, {"text": "= $D(X)$ 的联系", "partial": 2}],
    expl="**答案依据**：§4.1-4.2。", tags=["计算", "中等", "期望"],
    verify=[{"desc": "E[(X-1)^2]", "code": "integrate((x-1)**2/2, (x, 0, 2))", "expected": "1/3"}]))

_qlist.append(mk(BLANK, "medium", "4.2", "$X\\sim B(n,p)$。$E(X)=$ ______，$D(X)=$ ______。",
    answer=["$np$", "$np(1-p)$"], expl="二项分布标准结果。", tags=["基础", "二项分布"],
    variant_group="vg-binomial"))

# ═══ ch5 大数定律与 CLT（+6）═══
_qlist.append(mk(SINGLE, "medium", "5.1", "依概率收敛的定义是",
    answer=["A"], options=["$\\forall\\varepsilon>0,\\lim P(|X_n-a|\\ge\\varepsilon)=0$", "$\\lim X_n=a$", "$P(|X_n-a|=0)\\to1$", "$\\mathrm{Var}(X_n)\\to0$"],
    expl="**答案依据**：依概率收敛定义。A 正确。", tags=["依概率收敛"]))

_qlist.append(mk(SINGLE, "medium", "5.2", "辛钦大数定律的条件是",
    answer=["A"], options=["独立同分布且 $E(X_i)$ 存在", "独立但可以不同分布", "两两不相关", "方差必须一致有界"],
    expl="**答案依据**：辛钦只要求独立同分布且期望存在。A 正确。", tags=["创新题", "辛钦大数定律"]))

_qlist.append(mk(SINGLE, "hard", "5.3", "$X_i$ 独立同分布于 $B(1,0.5)$，$n=100$。由 CLT，$P(45\\le\\sum X_i\\le55)\\approx$",
    answer=["B"], options=["$0.9544$", "$0.6826$", "$0.9973$", "$0.8413$"],
    expl="**答案依据**：$E=50,\\sigma=\\sqrt{25}=5$。$P(45\\le\\sum\\le55)=P(-1\\le Z\\le1)=2\\Phi(1)-1=0.6826$。B 正确。", tags=["高频", "CLT"]))

_qlist.append(mk(CALC, "hard", "5.3", "某车间 200 台车床独立工作，开工率 0.6。每台耗电 1 千瓦。供电所至少供应多少千瓦，才能以 99.9% 概率保证正常生产？（$\\Phi(3)=0.9987$）",
    answer_text="$X\\sim B(200,0.6)$，$E=120, D=48$。$\\frac{k-120}{\\sqrt{48}}\\ge3\\Rightarrow k\\ge141$。至少供应 **141 千瓦**。",
    points=[{"text": "识别为 De Moivre-Laplace 模型", "partial": 2}, {"text": "标准化求临界值", "partial": 2},
            {"text": "$k\\ge141$", "partial": 2}, {"text": "向上取整说明", "partial": 2}],
    expl="**答案依据**：§5.3 CLT。", tags=["计算", "高频", "CLT"],
    verify=[{"desc": "k", "code": "round(120+3*sp.sqrt(48))", "expected": "141"}]))

_qlist.append(mk(MULTI, "medium", "5.2", "关于大数定律，正确的有",
    answer=["A", "B", "C"], options=["伯努利大数定律是频率估计概率的理论依据", "辛钦大数定律要求独立同分布且期望存在", "切比雪夫大数定律允许不同分布但方差一致有界", "大数定律说的是算术平均趋于零"],
    expl="**答案依据**：A、B、C 正确。D 错：算术平均趋于数学期望。", tags=["大数定律"]))

_qlist.append(mk(JUDGE, "medium", "5.1", "依概率收敛与高等数学中的数列极限（逐点收敛）是同一个概念。",
    answer=["B"], expl="**答案依据**：依概率收敛 weaker 于逐点收敛。", tags=["依概率收敛"]))

# ═══ ch6 数理统计基础（+6）═══
_qlist.append(mk(SINGLE, "basic", "6.1", "样本 $X_1,\\dots,X_n$ 满足的条件是",
    answer=["A"], options=["与总体同分布且相互独立", "同分布但不独立", "独立但可以不同分布", "正态分布"],
    expl="**答案依据**：简单随机样本——同分布+独立。A 正确。", tags=["基础", "简单随机样本"]))

_qlist.append(mk(SINGLE, "medium", "6.2", "设总体 $X\\sim N(\\mu,\\sigma^2)$，样本均值 $\\bar{X}$ 服从",
    answer=["B"], options=["$N(\\mu,\\sigma^2)$", "$N(\\mu,\\sigma^2/n)$", "$N(0,1)$", "$N(n\\mu,n\\sigma^2)$"],
    expl="**答案依据**：$\\bar{X}\\sim N(\\mu,\\sigma^2/n)$。B 正确。", tags=["高频", "样本均值"]))

_qlist.append(mk(SINGLE, "hard", "6.3", "设 $X\\sim N(0,1)$，$Y\\sim\\chi^2(n)$ 独立，则 $\\frac{X}{\\sqrt{Y/n}}\\sim$",
    answer=["A"], options=["$t(n)$", "$\\chi^2(n)$", "$N(0,1)$", "$F(1,n)$"],
    expl="**答案依据**：$t$ 分布定义。A 正确。", tags=["高频", "t分布"]))

_qlist.append(mk(MULTI, "hard", "6.3", "关于三大抽样分布，正确的有",
    answer=["A", "B", "C"], options=["$\\chi^2$ 分布是非负的", "$t$ 分布关于 0 对称", "$F$ 分布是非负的", "$t$ 分布的方差恒为 1"],
    expl="**答案依据**：A、B、C 正确。D 错：$t$ 分布方差 $=\\frac{n}{n-2}$。", tags=["三大分布"]))

_qlist.append(mk(BLANK, "medium", "6.2", "设 $X\\sim N(0,1)$，$X_1,\\dots,X_n$ 为样本，则 $\\sum X_i^2\\sim$ ______。",
    answer=["$\\chi^2(n)$"], accept=["chi2(n)"], expl="**答案依据**：标准正态平方和。", tags=["基础", "χ²分布"]))

_qlist.append(mk(CALC, "medium", "6.2", "设总体 $X\\sim N(2,9)$，样本 $n=9$。求 $P(\\bar{X}>3)$（$\\Phi(1)=0.8413$）。",
    answer_text="$\\bar{X}\\sim N(2,1)$。$P(\\bar{X}>3)=1-\\Phi(1)=0.1587$。",
    points=[{"text": "$\\bar{X}\\sim N(2,1)$", "partial": 2}, {"text": "标准化 $Z=1$", "partial": 2},
            {"text": "结果 $=0.1587$", "partial": 2}, {"text": "样本量越大 $\\bar{X}$ 越集中", "partial": 2}],
    expl="**答案依据**：§6.2 正态总体样本均值分布。", tags=["计算", "高频", "样本均值"],
    verify=[{"desc": "1-Φ(1)", "code": "1-0.8413", "expected": "0.1587"}]))

# ═══ ch7 参数估计（+6）═══
_qlist.append(mk(SINGLE, "medium", "7.1", "矩估计法的基本思想是",
    answer=["A"], options=["用样本矩替换总体矩", "使似然函数最大", "使方差最小", "使偏差最小"],
    expl="**答案依据**：矩估计 = 用样本矩替换相应的总体矩（令样本均值 = 总体期望等）。A 正确。B 是极大似然的思想。", tags=["高频", "矩估计"]))

_qlist.append(mk(SINGLE, "medium", "7.1", "极大似然估计法的基本思想是",
    answer=["A"], options=["选取使观测到样本出现概率最大的参数值", "用样本矩替换总体矩", "使方差最小", "使偏差绝对值最小"],
    expl="**答案依据**：极大似然 = 最大化 L(θ)。A 正确。", tags=["高频", "极大似然"]))

_qlist.append(mk(SINGLE, "hard", "7.2", "设 $T_1, T_2$ 都是 $\\mu$ 的无偏估计且 $D(T_1) < D(T_2)$，则",
    answer=["A"], options=["$T_1$ 比 $T_2$ 有效", "$T_2$ 比 $T_1$ 有效", "两者一样好", "无法比较"],
    expl="**答案依据**：有效性 = 均无偏时方差小者有效。A 正确。", tags=["高频", "有效性"]))

_qlist.append(mk(CALC, "medium", "7.1", "设 $X\\sim U(0,\\theta)$，$X_1,\\dots,X_n$ 为样本。求 θ 的矩估计。",
    answer_text="$E(X)=\\theta/2$。令 $\\theta/2=\\bar{X}$，得 $\\hat{\\theta}=2\\bar{X}$。",
    points=[{"text": "$E(X)=\\theta/2$", "partial": 2}, {"text": "令 $\\theta/2=\\bar{X}$", "partial": 2},
            {"text": "$\\hat{\\theta}=2\\bar{X}$", "partial": 2}, {"text": "对比 MLE $=X_{(n)}$", "partial": 2}],
    expl="**答案依据**：§7.1 矩估计法。", tags=["计算", "高频", "矩估计"]))

_qlist.append(mk(BLANK, "medium", "7.3", "正态总体 σ 已知时，$\\mu$ 的 95% 置信区间为 $\\bar{X}\\pm$ ______。",
    answer=["$1.96\\frac{\\sigma}{\\sqrt{n}}$"], accept=["1.96sigma/sqrt(n)"], expl="**答案依据**：σ 已知的 $u$ 区间。", tags=["置信区间"]))

_qlist.append(mk(CALC, "hard", "7.2", "设 $T$ 是 $\\mu$ 的无偏估计，证明 $E[(T-\\mu)^2]=D(T)$。",
    answer_text="$E[(T-\\mu)^2]=E(T^2-2\\mu T+\\mu^2)=E(T^2)-2\\mu E(T)+\\mu^2$。\n"
                "由无偏性 $E(T)=\\mu$：$=E(T^2)-\\mu^2$。\n"
                "又 $D(T)=E(T^2)-[E(T)]^2=E(T^2)-\\mu^2$。两者相等。$\\blacksquare$\n"
                "**创新点**：均方误差 = 方差 + 偏差²。无偏时偏差 = 0，故 MSE = 方差。",
    points=[{"text": "展开 $E[(T-\\mu)^2]$", "partial": 2}, {"text": "代入无偏性 $E(T)=\\mu$", "partial": 2},
            {"text": "得到 $E(T^2)-\\mu^2=D(T)$", "partial": 2}, {"text": "联系 MSE = 方差 + 偏差²", "partial": 2}],
    expl="**答案依据**：§7.2 无偏性与有效性的关系（MSE 分解）。", tags=["证明", "无偏性", "MSE"]))

# ═══ ch8 假设检验（+6）═══
_qlist.append(mk(SINGLE, "basic", "8.1", "假设检验的基本思想是",
    answer=["A"], options=["概率反证法（小概率事件在一次试验中几乎不发生）", "数学归纳法", "反证法（逻辑矛盾）", "贝叶斯更新"],
    expl="**答案依据**：假设检验用小概率原理做概率反证。A 正确。", tags=["基础", "假设检验"]))

_qlist.append(mk(SINGLE, "medium", "8.2", "假设检验中，第一类错误是指",
    answer=["A"], options=["$H_0$ 为真时拒绝了 $H_0$", "$H_0$ 为假时接受了 $H_0$", "$H_1$ 为真时拒绝了 $H_1$", "样本量太大"],
    expl="**答案依据**：第一类错误 = 弃真（$H_0$ 真但拒绝 $H_0$），概率 = α。A 正确。", tags=["高频", "两类错误"]))

_qlist.append(mk(SINGLE, "hard", "8.2", "某工厂声称产品合格率为 95%。随机抽取 100 件发现 10 件次品。"
    "在 $H_0: p = 0.95$ 下，$P(X\\le 90)\\approx \\Phi(-2.06) \\approx 0.0197$。结论是",
    answer=["A"], options=["$p$ 值 $\\approx 0.02 < 0.05$，拒绝 $H_0$", "接受 $H_0$", "需要更多数据", "第二类错误"],
    expl="**答案依据**：$p$ 值 $\\approx 0.02 < \\alpha = 0.05$，拒绝 $H_0$。A 正确。", tags=["创新题", "p值"],
    variant_group="vg-pvalue"))

_qlist.append(mk(MULTI, "medium", "8.1", "关于假设检验的 $p$ 值，正确的有",
    answer=["A", "B", "C"], options=["$p$ 值越小越有理由拒绝 $H_0$", "$p$ 值是 $H_0$ 成立时观测到当前结果的概率",
             "$p < \\alpha$ 时拒绝 $H_0$", "$p$ 值是 $H_0$ 为假的概率"],
    expl="**答案依据**：A、B、C 正确。D 错——$p$ 值不是 $H_0$ 为假的概率。", tags=["p值"],
    variant_group="vg-pvalue"))

_qlist.append(mk(BLANK, "medium", "8.2", "正态总体均值的 $t$ 检验中，统计量 $t = \\frac{\\bar{X}-\\mu_0}{S/\\sqrt{n}}$ 服从自由度为 ______ 的 $t$ 分布。",
    answer=["$n-1$"], accept=["n-1"], expl="**答案依据**：自由度 = $n-1$。", tags=["t检验"]))

_qlist.append(mk(CALC, "hard", "8.2",
    "某电池寿命 $X\\sim N(\\mu,\\sigma^2)$。声称平均寿命 $\\mu\\ge 200$ 小时。取 $n = 9$ 块，测得 $\\bar{X} = 195,\\ S = 6$。"
    "取 $\\alpha = 0.05$（$t_{0.05}(8) = 1.860$，单侧），检验 $H_0: \\mu \\ge 200$ vs $H_1: \\mu < 200$。",
    answer_text="$t = \\frac{195-200}{6/3} = -2.5$。$t = -2.5 < -1.860$，拒绝 $H_0$。有充分证据表明平均寿命低于 200 小时。",
    points=[{"text": "单侧（左侧）检验", "partial": 2}, {"text": "$t = -2.5$", "partial": 2},
            {"text": "$-2.5 < -1.860$，拒绝 $H_0$", "partial": 2}, {"text": "结论：寿命显著低于声称值", "partial": 2}],
    expl="**答案依据**：§8.2 单侧 $t$ 检验。", tags=["计算", "高频", "t检验"],
    verify=[{"desc": "t", "code": "Rational(195-200, 2)", "expected": "-5/2"}]))

Q = _qlist
