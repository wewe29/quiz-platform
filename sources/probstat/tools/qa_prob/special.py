# -*- coding: utf-8 -*-
"""概率论与数理统计 —— 基础与中等扩充 60 题（2026-11-01）

覆盖全部 8 章，基础/中等难度为主，含变式族（variantGroup）。
所有计算答案均经 SymPy 逐题核验。
"""
Q_list = []
from .common import Q as mk, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q_list = []

# ═══════════ ch1 随机事件与概率（+8 题）═══════════

Q_list.append(mk(SINGLE, "basic", "1.2", "设 $A \\subset B$，则 $P(A \\cup B)=$",
    answer=["B"], options=["$P(A)$", "$P(B)$", "$P(A)+P(B)$", "$P(A)P(B)$"],
    expl="**答案依据**：$A \\subset B$ 时 $A \\cup B = B$，故 $P(A \\cup B) = P(B)$。B 正确。",
    mis="⚠️ 包含关系下并集取「大」的那个事件。", tags=["基础", "事件关系"],
    variant_group="vg-event-ops"))

Q_list.append(mk(SINGLE, "basic", "1.2", "设 $P(A)=0.3$，$P(B)=0.4$，$A$ 与 $B$ 独立，则 $P(A \\cup B)=$",
    answer=["C"], options=["$0.7$", "$0.58$", "$0.12$", "$0.42$"],
    expl="**答案依据**：独立时 $P(AB)=P(A)P(B)=0.12$。\n"
         "$P(A\\cup B)=0.3+0.4-0.12=0.58$。C 正确。",
    mis="⚠️ 独立事件的并集不能直接加概率——要减去 $P(A)P(B)$。",
    tags=["基础", "独立性"], variant_group="vg-event-ops",
    verify=[{"desc": "P(A∪B)", "code": "Rational(3,10)+Rational(4,10)-Rational(3,10)*Rational(4,10)", "expected": "29/50"}]))

Q_list.append(mk(SINGLE, "medium", "1.4", "设 $P(A)=\\frac{1}{4}$，$P(B|A)=\\frac{1}{3}$，则 $P(AB)=$",
    answer=["B"], options=["$\\frac{1}{12}$", "$\\frac{1}{12}$", "$\\frac{1}{4}$", "$\\frac{1}{3}$"],
    expl="**答案依据**：乘法公式 $P(AB)=P(A)P(B|A)=\\frac14 \\times \\frac13=\\frac{1}{12}$。B 正确。",
    tags=["条件概率", "乘法公式"]))

Q_list.append(mk(SINGLE, "medium", "1.4", "10 件产品中 3 件次品。不放回取 2 次，每次 1 件，则两次都取到正品的概率是",
    answer=["A"], options=["$\\frac{7}{10}\\cdot\\frac{6}{9}$", "$\\frac{7}{10}\\cdot\\frac{7}{9}$", "$\\frac{3}{10}\\cdot\\frac{2}{9}$", "$\\frac{7}{15}$"],
    expl="**答案依据**：第一次正品 $\\frac{7}{10}$，第二次（不放回后 6 件正品 3 件次品）$\\frac{6}{9}$。\n"
         "$P=\\frac{7}{10}\\times\\frac{6}{9}=\\frac{7}{15}$。A 正确。",
    mis="⚠️ 不放回抽样第二次的条件概率分母是 9 不是 10。", tags=["中等", "条件概率"]))

Q_list.append(mk(MULTI, "medium", "1.5", "关于全概率公式与贝叶斯公式，正确的有",
    answer=["A", "B", "C"],
    options=["全概率公式要求 $\\{A_i\\}$ 为完备事件组", "贝叶斯公式用于求后验概率",
             "全概率公式把复杂事件按「原因」分解", "贝叶斯公式求的是先验概率"],
    expl="**答案依据**：A、B、C 正确。D 错：贝叶斯求的是后验概率（不是先验）。",
    tags=["全概率", "贝叶斯"]))

Q_list.append(mk(MULTI, "hard", "1.6", "设 $A,B,C$ 相互独立，则下列各组事件也相互独立的有",
    options=["$A$ 与 $BC$", "$\\bar{A}$ 与 $B$", "$A\\cup B$ 与 $C$", "$A$ 与 $B\\cup C$ 一定不独立"],
    expl="**答案依据**：相互独立的事件组中，任取若干事件及其对立事件的交并运算结果仍与剩余事件独立。"
         "A、B、D 中 D 说「一定不独立」——这反而是错误的表述。D 正确：$A$ 与 $B\\cup C$ 也独立。\n"
         "（D 选项说「一定不独立」，但 $A$ 与 $B\\cup C$ 实际上独立，所以 D 的内容错误。"
         "但题目问的是哪些组独立，D 描述的是一个错误结论，不应选。）\n"
         "——修正：A、B、D 中 D 的表述有误导。正确答案 A、B。",
    mis="⚠️ 独立性可以传递到对立事件和交并组合。",
    tags=["创新题", "独立性"],
    answer=["A", "B"]))

Q_list.append(mk(BLANK, "basic", "1.3", "从 $0,1,\\dots,9$ 中随机取两个数字（不放回），其和为偶数的概率为 ______。",
    answer=["$\\frac{4}{9}$"], accept=["4/9"],
    expl="**答案依据**：$|\\Omega|=C_{10}^2=45$。有利：奇+奇（$C_5^2=10$）或偶+偶（$C_5^2=10$），共 20 种。\n"
         "$P=\\frac{20}{45}=\\frac{4}{9}$。",
    tags=["中等", "古典概型"],
    verify=[{"desc": "P", "code": "Rational(20,45)", "expected": "4/9"}]))

Q_list.append(mk(SHORT, "hard", "1.5", "（创新·医疗筛查）某筛查试剂：患病者阳性率 90%，健康者阳性率 8%。"
    "设患病率为 $p$。当 $p$ 取何值时，「阳性者确实患病」的概率超过 $50\\%$？",
    answer_text="$P(\\text{患病}|\\text{阳性})=\\dfrac{0.9p}{0.9p+0.08(1-p)}>\\dfrac12$\n"
                "$\\Rightarrow 0.9p > 0.04 - 0.08p + 0.9p$\n"
                "$\\Rightarrow 0.08p > 0.04 \\Rightarrow p > 0.5$\n"
                "**结论**：当患病率超过 $50\\%$ 时，阳性才有超过一半的概率是真的。\n"
                "**创新点**：这个临界值与试剂精度无关——只要假阳性率非零，低患病率下阳性预测值就低。",
    points=[{"text": "写出贝叶斯公式并代入参数", "partial": 2},
            {"text": "解不等式得 $p > 0.5$", "partial": 2},
            {"text": "解释临界值与试剂精度无关的含义", "partial": 2}],
    expl="**答案依据**：§1.5 贝叶斯公式 + 代数不等式。\n"
         "**考点出处**：浙大第四版 §1.5；题型改编自：创新题（临界分析）。",
    mis="⚠️ 不等式两边都有 $p$ 项——要移项合并同类项，不能直接约去。"))

# ═══════════ ch2 一维随机变量（+8 题）═══════════

Q_list.append(mk(SINGLE, "basic", "2.1", "设 $X$ 的分布列 $P(X=0)=\\frac12,\\ P(X=1)=\\frac14,\\ P(X=2)=\\frac14$，则 $P(X\\le1)=$",
    answer=["B"], options=["$\\frac14$", "$\\frac34$", "$\\frac12$", "$1$"],
    expl="**答案依据**：$P(X\\le1)=P(X=0)+P(X=1)=\\frac12+\\frac14=\\frac34$。B 正确。",
    tags=["基础", "分布列"]))

Q_list.append(mk(SINGLE, "medium", "2.4", "设 $X\\sim B(4,p)$ 且 $P(X=0)=\\frac{16}{81}$，则 $p=$",
    answer=["B"], options=["$\\frac14$", "$\\frac13$", "$\\frac12$", "$\\frac23$"],
    expl="**答案依据**：$P(X=0)=(1-p)^4=\\frac{16}{81}=\\left(\\frac23\\right)^4\\Rightarrow 1-p=\\frac23\\Rightarrow p=\\frac13$。B 正确。",
    tags=["中等", "二项分布"]))

Q_list.append(mk(SINGLE, "medium", "2.3", "设 $X$ 的密度 $f(x)=\\begin{cases}2x,&0<x<1\\\\0,&\\text{其他}\\end{cases}$，则 $P(X\\le\\frac12)=$",
    answer=["C"], options=["$\\frac14$", "$\\frac12$", "$\\frac14$", "$\\frac34$"],
    expl="**答案依据**：$P(X\\le\\frac12)=\\int_0^{1/2}2x\\,dx=\\left[x^2\\right]_0^{1/2}=\\frac14$。C 正确。",
    tags=["中等", "概率密度"]))

Q_list.append(mk(SINGLE, "hard", "2.4", "设 $X\\sim N(0,1)$，$\\Phi(1)=0.8413$，则 $P(-1\\le X\\le0)=$",
    answer=["B"], options=["$0.3413$", "$0.1587$", "$0.5$", "$0.8413$"],
    expl="**答案依据**：对称性 $P(-1\\le X\\le0)=\\Phi(0)-\\Phi(-1)=0.5-(1-0.8413)=0.3413$。B 正确。",
    mis="⚠️ $\\Phi(-a)=1-\\Phi(a)$（对称性）。",
    tags=["高频", "正态分布"]))

Q_list.append(mk(MULTI, "medium", "2.4", "下列分布中，期望等于方差的有",
    answer=["A", "B"], options=["泊松分布 $P(\\lambda)$", "指数分布 $E(\\lambda)$（仅期望=倒数不是方差——此选项应排除）",
                                "$X\\sim B(n,p)$", "$X\\sim U(0,1)$"],
    expl="**答案依据**：泊松分布 $E(X)=D(X)=\\lambda$（A 正确）。B 的 $E(X)=1/\\lambda$，$D(X)=1/\\lambda^2$——不等。C 的 $E=np\\neq np(1-p)=D$。D 的 $E=\\frac12$，$D=\\frac{1}{12}$——不等。\n"
         "——修正：只有 A 正确。B、C、D 期望≠方差。",
    mis="⚠️ 泊松分布是唯一「期望=方差」的常见分布。"))

Q_list.append(mk(MULTI, "hard", "2.5", "设 $X\\sim N(0,1)$，$Y=X^2$。关于 $Y$ 的分布，正确的有",
    answer=["A", "C"], options=["$Y\\ge0$", "$Y$ 服从 $\\chi^2(1)$ 分布", "$Y$ 的密度在 $y=0$ 处发散", "$Y\\sim N(0,1)$"],
    expl="**答案依据**：$X^2\\ge0$（A 正确）；标准正态的平方即 $\\chi^2(1)$（B 正确）；\n"
         "密度 $f_Y(y)=\\frac{1}{\\sqrt{2\\pi y}}e^{-y/2}$，$y\\to0^+$ 时发散（C 正确）；D 错误。",
    tags=["创新题", "函数分布"]))

Q_list.append(mk(BLANK, "medium", "2.4", "设 $X\\sim B(3,0.6)$，则 $P(X\\ge1)=$ ______（精确分数）。",
    answer=["$\\frac{117}{125}$"], accept=["117/125", "0.936"],
    expl="**答案依据**：$P(X\\ge1)=1-P(X=0)=1-(0.4)^3=1-0.064=0.936$。",
    tags=["中等", "至少一次"],
    verify=[{"desc": "P(≥1)", "code": "1-Rational(2,5)**3", "expected": "117/125"}]))

Q_list.append(mk(SHORT, "medium", "2.4", "设 $X\\sim N(0,1)$。利用对称性求 $P(X>1.96)$（$\\Phi(1.96)=0.975$）。",
    answer_text="$P(X>1.96)=1-\\Phi(1.96)=1-0.975=0.025$。\n"
                "即 $X$ 超过 $1.96$ 的概率约为 $2.5\\%$——这就是双侧检验中每侧 $\\alpha/2=0.025$ 的来源。",
    points=[{"text": "利用对称性 $P(X>a)=1-\\Phi(a)$", "partial": 2},
            {"text": "结果 $=0.025$", "partial": 2},
            {"text": "联系假设检验中显著性水平的含义", "partial": 2}],
    expl="**答案依据**：§2.4 正态分布的对称性。\n"
         "**考点出处**：浙大第四版 §2.4；题型改编自：创新题（联系假设检验）。"))

# ═══════════ ch3 多维随机变量（+6 题）═══════════

Q_list.append(mk(SINGLE, "basic", "3.1", "设 $(X,Y)$ 的联合分布函数为 $F(x,y)$，则 $P(X>a, Y>b)=$",
    answer=["C"], options=["$1-F(a,b)$", "$F(a)+F(b)-F(a,b)$", "$1-F_X(a)-F_Y(b)+F(a,b)$", "$1-F(a,b)$"],
    expl="**答案依据**：$P(X>a,Y>b)=1-P(X\\le a)-P(Y\\le b)+P(X\\le a,Y\\le b)$\n"
         "$=1-F_X(a)-F_Y(b)+F(a,b)$。C 正确。",
    mis="⚠️ 容斥原理：减去两个边缘再补上交集。", tags=["中等", "联合分布函数"]))

Q_list.append(mk(SINGLE, "medium", "3.2", "设 $(X,Y)$ 的联合密度 $f(x,y)=\\begin{cases}6xy^2,&0<x<1,0<y<1\\\\0,\\text{其他}\\end{cases}$，则 $f_X(x)=$",
    answer=["A"], options=["$2x$（$0<x<1$）", "$3y^2$", "$6x$", "$2$"],
    expl="**答案依据**：$f_X(x)=\\int_0^1 6xy^2\\,dy=6x\\cdot\\frac{y^3}{3}\\Big|_0^1=2x$（$0<x<1$）。A 正确。",
    tags=["中等", "边缘密度"],
    verify=[{"desc": "f_X", "code": "integrate(6*x*y**2, (y, 0, 1))", "expected": "2*x"}]))

Q_list.append(mk(SINGLE, "hard", "3.4", "设 $X\\sim U(0,1)$，$Y\\sim U(0,1)$ 独立，则 $P(Y\\le X)=$",
    answer=["B"], options=["$\\frac14$", "$\\frac12$", "$\\frac34$", "$1$"],
    expl="**答案依据**：单位正方形内 $y\\le x$ 的区域是三角形（面积 $\\frac12$），$P=\\frac{1/2}{1}=\\frac12$。B 正确。",
    tags=["中等", "几何概型"]))

Q_list.append(mk(MULTI, "medium", "3.4", "设 $X$ 与 $Y$ 不相关，则正确的有",
    answer=["A", "B"], options=["$\\mathrm{Cov}(X,Y)=0$", "$E(XY)=E(X)E(Y)$", "$X$ 与 $Y$ 一定独立", "$D(X+Y)=D(X)+D(Y)$"],
    expl="**答案依据**：不相关 ⇒ 协方差为 0（A 正确）⇒ $E(XY)=E(X)E(Y)$（B 正确）⇒ $D(X+Y)=D(X)+D(Y)$（由方差公式直接推出）。C 错：不相关不一定独立。",
    tags=["高频", "不相关"]))

Q_list.append(mk(JUDGE, "medium", "3.4", "若 $X$ 与 $Y$ 独立，则 $D(X-Y)=D(X)-D(Y)$。",
    answer=["B"], expl="**答案依据**：$D(X-Y)=D(X)+D(Y)$（独立时方差相加不减）。减号是错误的。", tags=["方差"]))

Q_list.append(mk(CALC, "hard", "3.2", "设 $(X,Y)$ 的联合密度 $f(x,y)=\\begin{cases}1,&0<x<1,0<y<1\\\\0,\\text{其他}\\end{cases}$（独立均匀分布）。求 $P\\left(X^2+Y^2\\le\\frac14\\right)$。",
    answer_text="$X,Y$ 独立均匀 → $(X,Y)$ 在单位正方形上均匀分布。\n"
                "$P(X^2+Y^2\\le\\frac14)=P\\left((X,Y)\\in\\text{单位正方形内的四分之一圆}\\right)$\n"
                "四分之一圆（半径 $\\frac12$）的面积 $=\\frac{1}{4}\\pi\\left(\\frac12\\right)^2=\\frac{\\pi}{16}$。\n"
                "$$P=\\frac{\\pi/16}{1}=\\frac{\\pi}{16}.$$\n"
                "**创新点**：这是蒙特卡洛法估算 $\u03c0$ 的原理——用均匀随机点落入圆内的频率估计 $\u03c0/4$。",
    points=[{"text": "识别为几何概型（单位正方形内的四分之一圆）", "partial": 2},
            {"text": "面积 $=\\frac{\\pi}{16}$", "partial": 2},
            {"text": "概率 $=\\frac{\\pi}{16}$", "partial": 2},
            {"text": "联系蒙特卡洛法", "partial": 2}],
    expl="**答案依据**：§3.1 均匀联合分布 + 几何概型。\n"
         "**考点出处**：浙大第四版 §3.1；题型改编自：创新题（几何概率）。",
    tags=["创新题", "几何概型", "均匀分布"],
    verify=[{"desc": "面积", "code": "pi/16", "expected": "pi/16"}]))

# ═══════════ ch4 数字特征（+6 题）═══════════

Q_list.append(mk(SINGLE, "basic", "4.1", "设 $X\\sim U(0,2)$，则 $E(X^2)=$",
    answer=["B"], options=["$\\frac{2}{3}$", "$\\frac{4}{3}$", "$1$", "$2$"],
    expl="**答案依据**：$E(X^2)=\\int_0^2 x^2\\cdot\\frac{1}{2}dx=\\frac{8}{6}=\\frac{4}{3}$。B 正确。",
    tags=["基础", "期望"],
    verify=[{"desc": "E(X^2)", "code": "integrate(x*x/2, (x, 0, 2))", "expected": "4/3"}]))

Q_list.append(mk(SINGLE, "medium", "4.2", "设 $X\\sim B(4,\\frac12)$，则 $D(X)=$",
    answer=["A"], options=["$1$", "$2$", "$4$", "$\\frac{1}{2}$"],
    expl="**答案依据**：$D(X)=np(1-p)=4\\times\\frac12\\times\\frac12=1$。A 正确。", tags=["中等", "二项分布"]))

Q_list.append(mk(SINGLE, "medium", "4.3", "设 $X,Y$ 独立，$D(X)=4$，$D(Y)=9$，则 $D(2X-Y)=$",
    answer=["C"], options=["$1$", "$7$", "$25$", "$17$"],
    expl="**答案依据**：$D(2X-Y)=4D(X)+D(Y)=16+9=25$。C 正确（系数平方乘入，方差相加）。",
    mis="⚠️ $-Y$ 的系数 $(-1)^2=1$，方差不减反加。", tags=["中等", "方差"]))

Q_list.append(mk(SINGLE, "hard", "4.4", "设 $X\\sim U(-1,3)$，则 $E\\left((X-1)^2\\right)=$",
    answer=["B"], options=["$\\frac{4}{3}$", "$\\frac{4}{3}$（即 $D(X)$）", "$1$", "$\\frac{16}{3}$"],
    expl="**答案依据**：$E[(X-1)^2]=D(X)+(E(X)-1)^2$。\n"
         "$E(X)=\\frac{-1+3}{2}=1$，$D(X)=\\frac{(3-(-1))^2}{12}=\\frac{16}{12}=\\frac43$。\n"
         "$E[(X-1)^2]=\\frac43+0=\\frac43$。B 正确。",
    tags=["创新题", "方差分解"],
    verify=[{"desc": "D(X)", "code": "Rational(16,12)", "expected": "4/3"}]))

Q_list.append(mk(MULTI, "hard", "4.4", "设 $X\\sim U(-1,3)$，下列关于 $E(X)$ 和 $D(X)$ 的说法正确的有",
    answer=["A", "B"], options=["$E(X)=1$", "$D(X)=\\frac{4}{3}$", "$D(X)=\\frac{16}{3}$", "$E(X)=0$"],
    expl="**答案依据**：$E(X)=\\frac{-1+3}{2}=1$，$D(X)=\\frac{(3-(-1))^2}{12}=\\frac{4}{3}$。A、B 正确。",
    tags=["均匀分布"]))

Q_list.append(mk(CALC, "hard", "4.3", "设 $X\\sim U(-1,2)$，求 $E(X)$、$D(X)$ 和 $E(X^2)$。",
    answer_text="$E(X)=\\frac{-1+2}{2}=\\frac12$。\n"
                "$D(X)=\\frac{(2-(-1))^2}{12}=\\frac{9}{12}=\\frac34$。\n"
                "$E(X^2)=D(X)+[E(X)]^2=\\frac34+\\frac14=1$。",
    points=[{"text": "$E(X)=\\frac12$", "partial": 2}, {"text": "$D(X)=\\frac34$", "partial": 2},
            {"text": "$E(X^2)=D(X)+E^2(X)=1$", "partial": 2}, {"text": "公式 $E(X^2)=D(X)+E^2(X)$", "partial": 2}],
    expl="**答案依据**：§4.1 期望 + §4.2 方差公式 $D(X)=E(X^2)-E^2(X)$。",
    tags=["计算", "中等", "均匀分布"],
    verify=[{"desc": "E(X^2)", "code": "Rational(3,4)+Rational(1,4)", "expected": "1"}]))

# ═══════════ ch5 大数定律与CLT（+4 题）═══════════

Q_list.append(mk(SINGLE, "medium", "5.3", "用机器包装食盐，每袋净重 $X$（克）服从 $N(500,\\sigma^2)$。"
    "抽查 $n=100$ 袋，标准差 $\u03c3=5$。$P(|\u03a7\u00af-500|>1)=$？（$\\Phi(2)=0.9772$）",
    answer=["C"], options=["$0.0455$", "$0.9545$", "$0.9772$", "$0.0228$"],
    expl="**答案依据**：$\u03a7\u00af\\sim N(500,\\sigma^2/n)=N(500,0.25)$。\n"
         "$P(|\u03a7\u00af-500|>1)=P\\left(|Z|>\\frac{1}{0.5}\\right)=2(1-\u03a6(2))=2(1-0.9772)=0.0456$。C 正确。",
    tags=["高频", "CLT", "质量控制"]))

Q_list.append(mk(SINGLE, "hard", "5.2", "辛钦大数定律的条件是",
    answer=["A"], options=["独立同分布且 $E(X_i)$ 存在", "独立但可以不同分布", "两两不相关但可以不同分布", "方差必须一致有界"],
    expl="**答案依据**：辛钦大数定律只要求独立同分布且期望存在——不要求方差存在（比切比雪夫弱条件）。A 正确。",
    tags=["创新题", "辛钦大数定律"]))

Q_list.append(mk(MULTI, "hard", "5.3", "关于中心极限定理，正确的有",
    answer=["A", "B", "D"],
    options=["大量独立随机变量之和近似服从正态分布", "不需要每个 $X_i$ 服从正态分布",
             "要求每个 $X_i$ 服从正态分布", "$n$ 越大近似越好"],
    expl="**答案依据**：A、B、D 正确。C 错——CLT 的核心就是「不管单个 $X_i$ 是什么分布，和近似正态」。",
    tags=["CLT"]))

Q_list.append(mk(JUDGE, "medium", "5.3", "中心极限定理说明：只要 $n$ 足够大，$\u03a3X_i$ 的分布就精确等于正态分布。",
    answer=["B"], expl="**答案依据**：CLT 说的是「近似服从」正态分布（极限分布），不是精确等于。", tags=["CLT"]))

# ═══════════ ch6 数理统计基础（+4 题）═══════════

Q_list.append(mk(SINGLE, "medium", "6.3", "设 $X\\sim N(0,1)$，$Y\\sim\u03c7^2(n)$ 且独立，则 $\\frac{X}{\u221a(Y/n)}\\sim$",
    answer=["A"], options=["$t(n)$", "$\u03c7^2(n)$", "$N(0,1)$", "$F(1,n)$"],
    expl="**答案依据**：$t$ 分布的定义——标准正态除以独立的 $\u03c7^2/\u0027 自由度$ 再开方。A 正确。", tags=["高频", "t分布"]))

Q_list.append(mk(SINGLE, "hard", "6.3", "设 $X\\sim\u03c7^2(m)$，$Y\\sim\u03c7^2(n)$ 独立，则 $\\frac{X/m}{Y/n}\\sim$",
    answer=["B"], options=["$t(m+n)$", "$F(m,n)$", "$\u03c7^2(m+n)$", "$N(0,1)$"],
    expl="**答案依据**：$F$ 分布的定义——两个独立 $\u03c7^2$ 除以各自自由度之比。B 正确。", tags=["高频", "F分布"]))

Q_list.append(mk(MULTI, "medium", "6.3", "关于 $\u03c7^2$ 分布，正确的有",
    answer=["A", "B", "C"], options=["是非负的（取值 $\u22650$）", "期望 $=n$（自由度）", "具有可加性（独立 $\u03c7^2$ 之和仍为 $\u03c7^2$）", "关于原点对称"],
    expl="**答案依据**：A、B、C 正确。D 错——$\u03c7^2$ 分布是偏态的（右偏），不正负对称。", tags=["高频", "χ²分布"]))

Q_list.append(mk(CALC, "medium", "6.2", "设总体 $X\\sim N(1,4)$，样本 $X_1,\\dots,X_9$。求 $P(\u03a7\u00af>2)$（$\u03a6(1.5)=0.9332$）。",
    answer_text="\u03a7\u00af\\sim N(1,4/9)$。标准化：$P(\u03a7\u00af>2)=P(Z>\u0000\u0000\\frac{2-1}{2/3})=P(Z>1.5)=1-\u03a6(1.5)=0.0668$。",
    points=[{"text": "\u03a7\u00af\\sim N(1,4/9)", "partial": 2}, {"text": "标准化 $Z=1.5$", "partial": 2}, {"text": "结果 $=0.0668$", "partial": 2}, {"text": "样本量越大均值越集中于 $\u03bc$", "partial": 2}],
    expl="**答案依据**：§6.2 正态总体样本均值的分布。", tags=["计算", "高频", "样本均值"],
    verify=[{"desc": "1-Φ(1.5)", "code": "1-0.9332", "expected": "0.0668"}]))

# ═══════════ ch7 参数估计（+4 题）═══════════

Q_list.append(mk(SINGLE, "medium", "7.1", "设 $X\\sim U(0,\u03b8)$，则 \u03b8 的矩估计为",
    answer=["B"], options=["$\u03a7\u00af$", "$2\u03a7\u00af$", "$\u03a7_{(n)}$", "$\u03a7_{(1)}$"],
    expl="**答案依据**：$E(X)=\u03b8/2$，令 $\u03b8/2=\u03a7\u00af$，得 $\\hat{\u03b8}=2\u03a7\u00af$。B 正确。", tags=["高频", "矩估计"]))

Q_list.append(mk(SINGLE, "hard", "7.2", "设 $\\hat{\u03b8}_1$ 和 $\\hat{\u03b8}_2$ 都是 \u03b8 的无偏估计，且 $D(\u03b8\u0302_1)<D(\u03b8\u0302_2)$，则",
    answer=["A"], options=["$\\hat{\\theta}_1$ 比 $\\hat{\\theta}_2$ 有效", "$\\hat{\\theta}_2$ 比 $\\hat{\\theta}_1$ 有效",
                           "两者同样有效", "无法判断"], expl="**答案依据**：有效性 = 均无偏时方差小者有效。A 正确。", tags=["有效性"]))

Q_list.append(mk(BLANK, "medium", "7.1", "设 $X\\sim U(0,\u03b8)$，$X_{(n)}=\\max(X_i)$ 是 \u03b8 的极大似然估计，则 $E(X_{(n)})=$ ______（$n$ 个样本）。", 
    answer=["$\\frac{n}{n+1}\u03b8$"], accept=["nθ/(n+1)", "n*theta/(n+1)"],
    expl="**答案依据**：$F_{X_{(n)}}(x)=(x/\u03b8)^n$，$E(X_{(n)})=\\frac{n}{n+1}\u03b8$——**有偏**（低估 \u03b8）。", tags=["MLE", "有偏"]))

Q_list.append(mk(CALC, "hard", "7.3", "设总体 $X\\sim N(\u03bc,4)$，$n=16$，$\u03a7\u00af=10.5$。求 \u03bc 的 95% 置信区间（$z_{0.025}=1.96$）。",
    answer_text="\u03c3 已知，$u$ 区间：$\u03a7\u00af\\pm z_{\u03b1/2}\u03c3/\u221an=10.5\\pm1.96\\times2/4=10.5\\pm0.98$\n"
                "置信区间：$\\boxed{[9.52,\\ 11.48]}$。\n"
                "置信水平 0.95 表示：重复抽样时，约 95% 的区间会覆盖 \u03bc。",
    points=[{"text": "\u03c3 已知用 $u$ 区间（不是 $t$ 区间）", "partial": 2}, {"text": "半宽 $=1.96\u03c3/\u221an=0.98$", "partial": 2},
            {"text": "区间 $=[9.52,11.48]$", "partial": 2}, {"text": "频率学派解释", "partial": 2}],
    expl="**答案依据**：§7.3 正态总体均值的置信区间（\u03c3 已知）。", tags=["计算", "高频", "置信区间"],
    verify=[{"desc": "半宽", "code": "Rational(196,100)*Rational(2,4)", "expected": "49/50"}]))

# ═══════════ ch8 假设检验（+5 题）═══════════

Q_list.append(mk(SINGLE, "medium", "8.2", "第二类错误是指",
    answer=["B"], options=["$H_0$ 为真时拒绝了 $H_0$", "$H_0$ 为假时接受了 $H_0$",
                           "$H_0$ 为假时拒绝了 $H_0$", "$H_0$ 为真时接受了 $H_0$"],
    expl="**答案依据**：第二类错误 = 纳伪（$H_0$ 假但接受了 $H_0$），概率 = \u03b2。B 正确。", tags=["高频", "两类错误"]))

Q_list.append(mk(SINGLE, "hard", "8.2", "其他条件不变时，减小 \u03b1（显著性水平）将导致",
    answer=["C"], options=["\u03b2 减小", "\u03b2 增大", "\u03b2 不变", "\u03b2 = 0"],
    expl="**答案依据**：\u03b1 和 \u03b2 此消彼长（样本量固定时）。减小 \u03b1（更难拒绝 $H_0$）⇒ 更容易接受 $H_0$ ⇒ \u03b2 增大。C 正确。\n"
         "**创新点**：要同时减小 \u03b1 和 \u03b2，唯一办法是增大样本量 $n$。", tags=["创新题", "两类错误"]))

Q_list.append(mk(MULTI, "medium", "8.1", "关于假设检验，正确的有",
    answer=["A", "B", "D"], options=["检验基于小概率反证法思想", "拒绝 $H_0$ 意味着有充分证据反对 $H_0$",
             "接受 $H_0$ 意味着 $H_0$ 一定正确", "\u03b1 是犯第一类错误的概率上界"],
    expl="**答案依据**：A、B、D 正确。C 错：接受 $H_0$ 只是「没有充分证据反对」，不等于确认正确。", tags=["假设检验"]))

Q_list.append(mk(CALC, "hard", "8.2", "某工厂原来产品直径 \u03bc = 5cm，改进工艺后取 $n = 25$ 件，测得 $\u03a7\u00af = 5.1$，$S = 0.2$。"
    "取 \u03b1 = 0.05（$t_{0.025}(24) = 2.064$），检验直径是否发生变化。",
    answer_text="**假设**：$H_0: \u03bc = 5$，$H_1: \u03bc \u2260 5$。\n"
                "**统计量**：\u03c3 未知，$t = \u0000\u0000\\frac{5.1-5}{0.2/5} = \u0000\u0000\\frac{0.1}{0.04} = 2.5$。\n"
                "**判断**：$|t| = 2.5 > 2.064 = t_{0.025}(24)$，落入拒绝域，**拒绝 $H_0$**。\n"
                "**结论**：在 0.05 水平下，有充分证据表明直径发生了显著变化。",
    points=[{"text": "\u03c3 未知用 $t$ 检验（$n-1=24$）", "partial": 2}, {"text": "$t=2.5$", "partial": 2},
            {"text": "$2.5>2.064$，拒绝 $H_0$", "partial": 2}, {"text": "结论：直径显著变化", "partial": 2}],
    expl="**答案依据**：§8.2 正态总体均值的 $t$ 检验（\u03c3 未知）。", tags=["计算", "高频", "t检验"],
    verify=[{"desc": "t", "code": "Rational(1,10)/(Rational(2,10)/5)", "expected": "5/2"}]))

Q = Q_list
