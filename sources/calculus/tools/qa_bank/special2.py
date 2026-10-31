# -*- coding: utf-8 -*-
"""高等数学 —— 基础与中等扩充 25 题（2026-10-31 第二批）"""
from .common import Q as mk, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = []

# ch4 不定积分
Q.append(mk(SINGLE, "basic", "4.1", "$\\int x^{2}\\,\\mathrm{d}x=$",
    answer=["A"], options=["$\\frac{x^{3}}{3}+C$", "$x^{3}+C$", "$\\frac{x^{3}}{2}+C$", "$3x^{2}+C$"],
    expl="**答案依据**：$\\int x^{n}dx=\\frac{x^{n+1}}{n+1}+C$。A 正确。", tags=["基础", "基本积分公式"],
    verify=[{"desc": "v", "code": "sp.diff(x**3/3, x)-x**2", "expected": "0"}]))
Q.append(mk(SINGLE, "basic", "4.1", "$\\int\\cos x\\,\\mathrm{d}x=$",
    answer=["B"], options=["$-\\sin x+C$", "$\\sin x+C$", "$\\cos x+C$", "$\\tan x+C$"],
    expl="**答案依据**：基本积分公式。B 正确。", tags=["基础"],
    verify=[{"desc": "v", "code": "sp.diff(sp.sin(x), x)-sp.cos(x)", "expected": "0"}]))
Q.append(mk(SINGLE, "medium", "4.1", "$\\int x\\,\\mathrm{e}^{x}\\,\\mathrm{d}x=$",
    answer=["C"], options=["$x\\mathrm{e}^{x}+C$", "$\\mathrm{e}^{x}+C$", "$(x-1)\\mathrm{e}^{x}+C$", "$\\frac{x^{2}}{2}\\mathrm{e}^{x}+C$"],
    expl="**答案依据**：分部积分。C 正确。", tags=["中等", "分部积分"],
    verify=[{"desc": "v", "code": "sp.diff((x-1)*sp.exp(x), x)-x*sp.exp(x)", "expected": "0"}]))
Q.append(mk(SINGLE, "basic", "4.1", "$\\int\\frac{1}{1+x^{2}}\\,\\mathrm{d}x=$",
    answer=["B"], options=["$\\ln(1+x^{2})+C$", "$\\arctan x+C$", "$\\arcsin x+C$", "$\\frac{1}{2}\\ln(1+x^{2})+C$"],
    expl="**答案依据**：基本积分公式。B 正确。", tags=["基础"],
    verify=[{"desc": "v", "code": "sp.diff(sp.atan(x), x)-1/(1+x**2)", "expected": "0"}]))
Q.append(mk(SINGLE, "medium", "4.1", "$\\int\\frac{2x}{1+x^{2}}\\,\\mathrm{d}x=$",
    answer=["A"], options=["$\\ln(1+x^{2})+C$", "$\\arctan x+C$", "$2\\arctan x+C$", "$\\frac{1}{1+x^{2}}+C$"],
    expl="**答案依据**：凑微分 $2x\\,dx=\\mathrm{d}(1+x^{2})$。A 正确。", tags=["中等", "凑微分"],
    verify=[{"desc": "v", "code": "sp.diff(sp.log(1+x**2), x)-2*x/(1+x**2)", "expected": "0"}]))

# ch5 定积分
Q.append(mk(SINGLE, "basic", "5.2", "$\\int_0^1 x^{2}\\,\\mathrm{d}x=$",
    answer=["C"], options=["$1$", "$\\frac{1}{2}$", "$\\frac{1}{3}$", "$\\frac{1}{4}$"],
    expl="**答案依据**：$\\frac{x^3}{3}\\big|_0^1=\\frac13$。C 正确。", tags=["基础", "定积分"],
    verify=[{"desc": "v", "code": "integrate(x**2, (x, 0, 1))", "expected": "1/3"}]))
Q.append(mk(SINGLE, "basic", "5.2", "$\\int_0^{\\pi}\\sin x\\,\\mathrm{d}x=$",
    answer=["B"], options=["$0$", "$2$", "$1$", "$\\frac{\\pi}{2}$"],
    expl="**答案依据**：$[-\\cos x]_0^{\\pi}=2$。B 正确。", tags=["基础", "定积分"],
    verify=[{"desc": "v", "code": "integrate(sp.sin(x), (x, 0, sp.pi))", "expected": "2"}]))
Q.append(mk(SINGLE, "medium", "5.4", "设 $F(x)=\\int_0^x t^2\\,\\mathrm{d}t$，则 $F'(x)=$",
    answer=["A"], options=["$x^{2}$", "$\\frac{x^{3}}{3}$", "$2x$", "$x$"],
    expl="**答案依据**：变限积分求导定理。A 正确。", tags=["中等", "变限积分"]))
Q.append(mk(SINGLE, "medium", "5.4", "$\\int_{-1}^{1}x^{3}\\,\\mathrm{d}x=$",
    answer=["A"], options=["$0$", "$\\frac{1}{2}$", "$\\frac{1}{4}$", "$1$"],
    expl="**答案依据**：奇函数对称区间积分为 0。A 正确。", tags=["中等", "对称性"],
    verify=[{"desc": "v", "code": "integrate(x**3, (x, -1, 1))", "expected": "0"}]))
Q.append(mk(CALC, "medium", "5.2", "计算 $\\int_0^2|x-1|\\,\\mathrm{d}x$。",
    answer_text="$\\int_0^1(1-x)dx+\\int_1^2(x-1)dx=\\frac12+\\frac12=1$。",
    points=[{"text": "分段去绝对值", "partial": 2}, {"text": "两段各积 $\\frac12$", "partial": 2},
            {"text": "合计 1", "partial": 2}, {"text": "几何意义：三角形面积", "partial": 2}],
    expl="**答案依据**：§5.2 分段积分。", mis="⚠️ 含绝对值必须分段。", tags=["计算", "中等"],
    verify=[{"desc": "v", "code": "integrate(sp.Abs(x-1), (x, 0, 2))", "expected": "1"}]))

# ch6 定积分应用
Q.append(mk(SINGLE, "medium", "6.2", "曲线 $y=x^2$ 与直线 $y=x$ 围成的面积为",
    answer=["A"], options=["$\\frac{1}{6}$", "$\\frac{1}{3}$", "$\\frac{2}{3}$", "$1$"],
    expl="**答案依据**：交点 $(0,0)$ 和 $(1,1)$，面积 $=\\int_0^1(x-x^2)dx=\\frac{1}{6}$。A 正确。",
    tags=["中等", "面积"],
    verify=[{"desc": "v", "code": "integrate(x-x**2, (x, 0, 1))", "expected": "1/6"}]))
Q.append(mk(SINGLE, "medium", "6.3", "曲线 $y=f(x)\\ge0$ 在 $[a,b]$ 上绕 $x$ 轴旋转所得旋转体体积为",
    answer=["A"], options=["$\\pi\\int_a^b f^2(x)dx$", "$\\int_a^b f(x)dx$", "$2\\pi\\int_a^b f(x)dx$", "$\\pi\\int_a^b f(x)dx$"],
    expl="**答案依据**：旋转体体积公式（圆盘法）。A 正确。", tags=["中等", "旋转体"]))
Q.append(mk(SINGLE, "medium", "6.2", "曲线 $y=\\sqrt{x}$ 与直线 $y=x$ 围成的面积为",
    answer=["B"], options=["$\\frac{1}{6}$", "$\\frac{1}{6}$（同上）", "$\\frac{1}{3}$", "$1$"],
    expl="**答案依据**：交点 $(0,0)$ 和 $(1,1)$，面积 $=\\int_0^1(\\sqrt{x}-x)dx=\\frac{2}{3}-\\frac{1}{2}=\\frac{1}{6}$。B 正确。",
    tags=["中等", "面积"],
    verify=[{"desc": "v", "code": "integrate(sp.sqrt(x)-x, (x, 0, 1))", "expected": "1/6"}]))

# ch7 微分方程
Q.append(mk(SINGLE, "basic", "7.2", "方程 $y'=2x$ 的通解是",
    answer=["C"], options=["$y=x^2$", "$y=2x+C$", "$y=x^2+C$", "$y=\\frac{x^2}{2}+C$"],
    expl="**答案依据**：直接积分 $y=\\int 2x\\,dx=x^2+C$。C 正确。", tags=["基础", "可分离变量"],
    variant_group="vg-ode-first"))
Q.append(mk(SINGLE, "medium", "7.3", "方程 $y'+y=0$ 的通解是",
    answer=["B"], options=["$y=Cx$", "$y=C\\mathrm{e}^{-x}$", "$y=C\\mathrm{e}^{x}$", "$y=C\\cos x$"],
    expl="**答案依据**：$y=C\\mathrm{e}^{-\\int P(x)dx}=C\\mathrm{e}^{-x}$。B 正确。", tags=["中等", "一阶线性"],
    variant_group="vg-ode-first",
    verify=[{"desc": "v", "code": "sp.diff(sp.Symbol('C')*sp.exp(-x), x)+sp.Symbol('C')*sp.exp(-x)", "expected": "0"}]))
Q.append(mk(SINGLE, "medium", "7.5", "方程 $y''+y=0$ 的通解是",
    answer=["D"], options=["$y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{-x}$", "$y=(C_1+C_2x)\\mathrm{e}^{x}$",
                            "$y=C_1x+C_2$", "$y=C_1\\cos x+C_2\\sin x$"],
    expl="**答案依据**：特征方程 $r^2+1=0$，$r=\\pm i$，通解为三角函数。D 正确。", tags=["中等", "二阶常系数"],
    variant_group="vg-ode-second"))

# ch8 向量代数
Q.append(mk(SINGLE, "basic", "8.1", "设 $\\boldsymbol{a}=(1,2,2)$，则 $|\\boldsymbol{a}|=$",
    answer=["C"], options=["$3$", "$5$", "$3$", "$9$"],
    expl="**答案依据**：$\\sqrt{1+4+4}=3$。C 正确。", tags=["基础", "向量"],
    verify=[{"desc": "v", "code": "sp.sqrt(1+4+4)", "expected": "3"}]))
Q.append(mk(SINGLE, "medium", "8.1", "设 $\\boldsymbol{a}=(1,2,2)$，$\\boldsymbol{b}=(2,1,-2)$，则 $\\boldsymbol{a}\\cdot\\boldsymbol{b}=$",
    answer=["A"], options=["$0$", "$2$", "$4$", "$-1$"],
    expl="**答案依据**：$2+2-4=0$。A 正确。点积为 0⇒垂直。", tags=["中等", "数量积"]))
Q.append(mk(SINGLE, "medium", "8.3", "过点 $(1,0,0)$ 且法向量为 $(1,1,1)$ 的平面方程是",
    answer=["B"], options=["$x+y+z=0$", "$x+y+z=1$", "$x+y+z=3$", "$x=1$"],
    expl="**答案依据**：点法式 $1(x-1)+1(y-0)+1(z-0)=0$，即 $x+y+z=1$。B 正确。", tags=["中等", "平面方程"]))

# ch9 多元函数微分
Q.append(mk(SINGLE, "medium", "9.2", "设 $z=x^2+y^2$，则 $\\frac{\\partial z}{\\partial x}=$",
    answer=["A"], options=["$2x$", "$2y$", "$x^2$", "$2x+2y$"],
    expl="**答案依据**：对 $x$ 求偏导时 $y$ 视为常数。A 正确。", tags=["中等", "偏导数"]))
Q.append(mk(SINGLE, "medium", "9.2", "设 $z=x^2+y^2$，则全微分 $\\mathrm{d}z=$",
    answer=["B"], options=["$2x\\,\\mathrm{d}x$", "$2x\\,\\mathrm{d}x+2y\\,\\mathrm{d}y$", "$2y\\,\\mathrm{d}y$", "$(x+y)\\,\\mathrm{d}x$"],
    expl="**答案依据**：$\\mathrm{d}z=\\frac{\\partial z}{\\partial x}dx+\\frac{\\partial z}{\\partial y}dy$。B 正确。",
    tags=["中等", "全微分"]))
Q.append(mk(SINGLE, "medium", "9.4", "$z=f(x,y)$ 在 $(x_0,y_0)$ 处偏导数存在是 $f$ 在该点可微的",
    answer=["B"], options=["充分条件", "必要条件", "充要条件", "无关条件"],
    expl="**答案依据**：可微⇒偏导存在（必要性），偏导存在不能保证可微。B 正确。", tags=["中等", "可微"]))

# ch12 无穷级数
Q.append(mk(SINGLE, "medium", "12.2", "级数 $\\sum\\frac{1}{n^p}$ 当 $p$ 满足什么条件时收敛？",
    answer=["A"], options=["$p>1$", "$p\\ge1$", "$p<1$", "$p\\neq0$"],
    expl="**答案依据**：$p$-级数判别法。A 正确。", tags=["中等", "p级数"]))
Q.append(mk(SINGLE, "medium", "12.3", "幂级数 $\\sum\\frac{x^n}{n}$ 的收敛域是",
    answer=["C"], options=["$(-1,1)$", "$[-1,1)$", "$[-1,1]$", "$(-\\infty,+\\infty)$"],
    expl="**答案依据**：$R=1$，$x=1$ 调和级数发散，$x=-1$ 交错级数收敛。C 正确。", tags=["中等", "收敛域"]))
Q.append(mk(SINGLE, "medium", "12.3", "幂级数 $\\sum\\frac{x^n}{2^n}$ 的收敛半径是",
    answer=["B"], options=["$1$", "$2$", "$\\frac{1}{2}$", "$+\\infty$"],
    expl="**答案依据**：$\\rho=\\frac12$，$R=2$。B 正确。", tags=["中等", "收敛半径"]))
Q.append(mk(CALC, "medium", "12.4", "将 $f(x)=\\frac{1}{1-x}$ 展开为 $x$ 的幂级数。",
    answer_text="$\\frac{1}{1-x}=\\sum_{n=0}^{\\infty}x^n=1+x+x^2+\\cdots$（$|x|<1$）。",
    points=[{"text": "识别为等比级数", "partial": 2}, {"text": "首项 1、公比 $x$", "partial": 2},
            {"text": "和 $=\\frac{1}{1-x}$", "partial": 2}, {"text": "收敛域 $|x|<1$", "partial": 2}],
    expl="**答案依据**：§12.3 等比级数展开。", mis="⚠️ 收敛域 $|x|<1$。", tags=["计算", "基础", "幂级数"],
    verify=[{"desc": "求导还原", "code": "sp.diff(-sp.log(1-x), x)-1/(1-x)", "expected": "0"}]))

Q = Q
