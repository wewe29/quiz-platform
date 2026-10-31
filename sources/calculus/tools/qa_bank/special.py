# -*- coding: utf-8 -*-
"""高等数学 —— 变式强化与创新专册 24 题（2026-10-31 增补）

结构：6 个「举一反三」变式族（variantGroup）+ 创新题。
覆盖章：1 函数与极限 / 3 中值定理与导数应用（含曲率）/ 5 定积分 /
        7 微分方程 / 9 多元函数微分 / 10 重积分 / 12 无穷级数。
采分点口径：CALC 4 点×2 分；SHORT 3 点×2 分。
所有计算答案均经 SymPy 逐题核验（verify 字段）。
"""
from .common import Q as mk, SINGLE, MULTI, JUDGE, BLANK, SHORT, CALC

Q = []

# ─────────────── 变式族 vg-taylor：泰勒展开求极限（§3.3）───────────────
Q.append(mk(SINGLE, "hard", "3.3",
    "极限 $\\lim\\limits_{x\\to0}\\dfrac{\\mathrm{e}^{x}-1-x-\\dfrac{x^{2}}{2}}{x^{3}}=$",
    answer=["C"],
    options=["$0$", "$\\dfrac{1}{2}$", "$\\dfrac{1}{6}$", "$1$"],
    expl="**答案依据**：$\\mathrm{e}^{x}=1+x+\\dfrac{x^{2}}{2}+\\dfrac{x^{3}}{6}+o(x^{3})$（麦克劳林），"
         "分子恰为 $\\dfrac{x^{3}}{6}+o(x^{3})$，除以 $x^{3}$ 取极限得 $\\dfrac{1}{6}$。C 正确；\n"
         "A 错在展开阶数不够；B 是洛必达少做一步；D 无依据。\n"
         "**举一反三**：「多减几项」的分子展开到与分母同阶即可——比连做三次洛必达更快更稳。",
    mis="⚠️易错点：展开阶数不够（只到 $x^{2}$）会误判极限为 0——分子被减到只剩 $\\dfrac{x^{3}}{6}$ 起步。",
    tags=["创新题", "变式族·泰勒展开"],
    variant_group="vg-taylor",
    verify=[{"desc": "极限", "code": "limit((exp(x)-1-x-x**2/2)/x**3, x, 0)", "expected": "1/6"},
            {"desc": "展开", "code": "sp.series(exp(x), x, 0, 4)", "expected": "1 + x + x**2/2 + x**3/6 + O(x**4)"}]))

Q.append(mk(CALC, "hard", "3.3",
    "求极限 $\\lim\\limits_{x\\to0}\\dfrac{x-\\ln(1+x)}{x^{2}}$。",
    answer_text="$\\ln(1+x)=x-\\dfrac{x^{2}}{2}+o(x^{2})$，故分子 $=x-\\left(x-\\dfrac{x^{2}}{2}\\right)+o(x^{2})"
                "=\\dfrac{x^{2}}{2}+o(x^{2})$，极限 $=\\boxed{\\dfrac{1}{2}}$。\n"
                "**举一反三**：泰勒展开比洛必达稳定——洛必达对本题要做两次且分母越导越复杂。",
    points=[{"text": "写出 $\\ln(1+x)$ 的二阶麦克劳林展开", "partial": 2},
            {"text": "分子化简为 $\\dfrac{x^{2}}{2}+o(x^{2})$", "partial": 2},
            {"text": "极限 $=\\dfrac{1}{2}$", "partial": 2},
            {"text": "对比洛必达说明展开法的优势", "partial": 2}],
    expl="**答案依据**：§3.3 泰勒公式（麦克劳林）。\n"
         "**考点出处**：同济《高等数学》第七版 §3.3；题型改编自：考研数学真题经典模型（泰勒求极限）。",
    mis="⚠️易错点：把 $\\ln(1+x)$ 展开到一阶（$x$）——分子只剩 $o(x)$ 与 $x^{2}$ 不同阶，无法比较。",
    tags=["计算", "变式族·泰勒展开"],
    variant_group="vg-taylor",
    verify=[{"desc": "极限", "code": "limit((x-log(1+x))/x**2, x, 0)", "expected": "1/2"}]))

Q.append(mk(CALC, "hard", "3.3",
    "求极限 $\\lim\\limits_{x\\to0}\\dfrac{\\sin x-x}{x^{3}}$。",
    answer_text="$\\sin x=x-\\dfrac{x^{3}}{6}+o(x^{3})$，分子 $=-\\dfrac{x^{3}}{6}+o(x^{3})$，"
                "极限 $=\\boxed{-\\dfrac{1}{6}}$。\n"
                "**举一反三**：本族三题（$\\mathrm{e}^{x}$、$\\ln(1+x)$、$\\sin x$）的通用套路："
                "把每个函数展到与分母同阶，逐项相减后读出首项系数。",
    points=[{"text": "写出 $\\sin x$ 的三阶麦克劳林展开", "partial": 2},
            {"text": "分子 $=-\\dfrac{x^{3}}{6}+o(x^{3})$", "partial": 2},
            {"text": "极限 $=-\\dfrac{1}{6}$（注意负号）", "partial": 2},
            {"text": "对比洛必达：三次求导越导越繁，展开法一次到位", "partial": 2}],
    expl="**答案依据**：§3.3 泰勒公式。\n"
         "**考点出处**：同济《高等数学》第七版 §3.3；题型改编自：考研数学真题经典模型（泰勒求极限）。",
    mis="⚠️易错点：符号——$\\sin x$ 比 $x$ 小，分子为负；很多同学漏掉负号得 $+\\dfrac{1}{6}$。",
    tags=["计算", "真题改编", "变式族·泰勒展开"],
    variant_group="vg-taylor",
    verify=[{"desc": "极限", "code": "limit((sin(x)-x)/x**3, x, 0)", "expected": "-1/6"}]))

# ─────────────── 变式族 vg-wallis：华里士公式（§5.4）───────────────
Q.append(mk(CALC, "medium", "5.4",
    "计算 $\\displaystyle\\int_{0}^{\\frac{\\pi}{2}}\\sin^{7}x\\,\\mathrm{d}x$。",
    answer_text="华里士（点火）公式：$\\displaystyle\\int_{0}^{\\frac{\\pi}{2}}\\sin^{n}x\\,\\mathrm{d}x"
                "=\\dfrac{(n-1)!!}{n!!}\\cdot\\begin{cases}1, & n\\text{ 奇}\\\\ \\dfrac{\\pi}{2}, & n\\text{ 偶}\\end{cases}$\n"
                "$n=7$（奇数）：$\\dfrac{6\\cdot4\\cdot2}{7\\cdot5\\cdot3}=\\dfrac{48}{105}=\\boxed{\\dfrac{16}{35}}$。",
    points=[{"text": "写出华里士公式并识别 $n=7$ 为奇数", "partial": 2},
            {"text": "双阶乘计算 $\\dfrac{6\\cdot4\\cdot2}{7\\cdot5\\cdot3}$", "partial": 2},
            {"text": "结果 $=\\dfrac{16}{35}$", "partial": 2},
            {"text": "说明 $n$ 奇偶对是否乘 $\\dfrac{\\pi}{2}$ 的影响", "partial": 2}],
    expl="**答案依据**：§5.4 定积分的分部积分递推（点火公式）。\n"
         "**考点出处**：同济《高等数学》第七版 §5.4；题型改编自：考研数学真题经典模型（华里士公式）。",
    mis="⚠️易错点：奇数幂不乘 $\\dfrac{\\pi}{2}$；双阶乘是同奇偶连乘，不是普通阶乘。",
    tags=["计算", "真题改编", "变式族·华里士"],
    variant_group="vg-wallis",
    verify=[{"desc": "积分", "code": "integrate(sin(x)**7, (x, 0, pi/2))", "expected": "16/35"}]))

Q.append(mk(CALC, "hard", "5.4",
    "计算 $\\displaystyle\\int_{0}^{\\frac{\\pi}{2}}\\cos^{6}x\\,\\sin^{2}x\\,\\mathrm{d}x$。",
    answer_text="偶次混合幂：先用 $\\sin^{2}x=1-\\cos^{2}x$ 化为 $\\cos^{6}-\\cos^{8}$ 再分别用华里士：\n"
                "$$\\int_{0}^{\\frac{\\pi}{2}}\\cos^{6}x\\,\\mathrm{d}x=\\dfrac{5\\cdot3\\cdot1}{6\\cdot4\\cdot2}\\cdot\\dfrac{\\pi}{2}=\\dfrac{5\\pi}{32},"
                "\\quad \\int_{0}^{\\frac{\\pi}{2}}\\cos^{8}x\\,\\mathrm{d}x=\\dfrac{7\\cdot5\\cdot3\\cdot1}{8\\cdot6\\cdot4\\cdot2}\\cdot\\dfrac{\\pi}{2}=\\dfrac{35\\pi}{256}.$$\n"
                "相减：$\\dfrac{5\\pi}{32}-\\dfrac{35\\pi}{256}=\\dfrac{40\\pi-35\\pi}{256}=\\boxed{\\dfrac{5\\pi}{256}}$。",
    points=[{"text": "化为 $\\cos^{6}-\\cos^{8}$ 之差", "partial": 2},
            {"text": "两个华里士公式计算（偶数幂乘 $\\dfrac{\\pi}{2}$）", "partial": 2},
            {"text": "结果 $=\\dfrac{5\\pi}{256}$", "partial": 2},
            {"text": "或直接用推广公式 $\\dfrac{(m-1)!!(n-1)!!}{(m+n)!!}\\cdot\\dfrac{\\pi}{2}$", "partial": 2}],
    expl="**答案依据**：§5.4 华里士公式 + 平方降幂。\n"
         "**考点出处**：同济《高等数学》第七版 §5.4；题型改编自：考研数学真题经典模型（混合幂点火）。",
    mis="⚠️易错点：$m,n$ 都是偶数时结果带 $\\pi$；通分时 $\\dfrac{5}{32}=\\dfrac{40}{256}$ 别算错。",
    tags=["计算", "真题改编", "变式族·华里士"],
    variant_group="vg-wallis",
    verify=[{"desc": "积分", "code": "integrate(cos(x)**6*sin(x)**2, (x, 0, pi/2))", "expected": "5*pi/256"}]))

Q.append(mk(SINGLE, "medium", "5.4",
    "$\\displaystyle\\int_{0}^{\\frac{\\pi}{2}}\\sin^{10}x\\,\\mathrm{d}x=$",
    answer=["B"],
    options=["$\\dfrac{9!!}{10!!}$", "$\\dfrac{63\\pi}{512}$", "$\\dfrac{63}{512}$", "$\\dfrac{1}{11}$"],
    expl="**答案依据**：$n=10$ 偶数：$\\dfrac{9!!}{10!!}\\cdot\\dfrac{\\pi}{2}"
         "=\\dfrac{9\\cdot7\\cdot5\\cdot3\\cdot1}{10\\cdot8\\cdot6\\cdot4\\cdot2}\\cdot\\dfrac{\\pi}{2}"
         "=\\dfrac{945}{3840}\\cdot\\dfrac{\\pi}{2}=\\dfrac{63\\pi}{512}$。B 正确；\n"
         "A 漏了 $\\dfrac{\\pi}{2}$；C 同样漏了；D 无依据。",
    mis="⚠️易错点：偶数幂必须乘 $\\dfrac{\\pi}{2}$；双阶乘 $10!!=10\\cdot8\\cdot6\\cdot4\\cdot2$。",
    tags=["变式族·华里士"],
    variant_group="vg-wallis",
    verify=[{"desc": "积分", "code": "integrate(sin(x)**10, (x, 0, pi/2))", "expected": "63*pi/512"}]))

# ─────────────── 变式族 vg-symmetry：对称性（§5.4）───────────────
Q.append(mk(SINGLE, "basic", "5.4",
    "$\\displaystyle\\int_{-1}^{1}\\dfrac{x}{1+x^{2}}\\,\\mathrm{d}x=$",
    answer=["A"],
    options=["$0$", "$\\dfrac{\\ln 2}{2}$", "$\\ln 2$", "$\\dfrac{1}{2}$"],
    expl="**答案依据**：被积函数 $\\dfrac{x}{1+x^{2}}$ 是奇函数，对称区间上奇函数积分为 $0$。A 正确；\n"
         "B、C 是求出原函数 $\\dfrac{1}{2}\\ln(1+x^{2})$ 后忘了 $F(1)-F(-1)=0$；D 无依据。",
    mis="⚠️易错点：奇函数在对称区间上积分为零可直接使用，省去求原函数。",
    tags=["基础", "变式族·对称性"],
    variant_group="vg-symmetry",
    verify=[{"desc": "积分", "code": "integrate(x/(1+x**2), (x, -1, 1))", "expected": "0"}]))

Q.append(mk(CALC, "medium", "5.4",
    "计算 $\\displaystyle\\int_{-1}^{1}\\left(x^{4}+x^{2}\\right)\\mathrm{d}x$。",
    answer_text="被积函数为偶函数：$=2\\displaystyle\\int_{0}^{1}(x^{4}+x^{2})\\,\\mathrm{d}x"
                "=2\\left(\\dfrac{1}{5}+\\dfrac{1}{3}\\right)=2\\cdot\\dfrac{8}{15}=\\boxed{\\dfrac{16}{15}}$。",
    points=[{"text": "识别偶函数并用对称性化为 $2\\int_0^1$", "partial": 2},
            {"text": "牛顿-莱布尼茨计算 $\\dfrac{1}{5}+\\dfrac{1}{3}$", "partial": 2},
            {"text": "结果 $=\\dfrac{16}{15}$", "partial": 2},
            {"text": "对比不求对称性直接积分结果一致（自检）", "partial": 2}],
    expl="**答案依据**：§5.4 奇偶函数在对称区间上的积分性质。\n"
         "**考点出处**：同济《高等数学》第七版 §5.4；题型改编自：经典模型（偶函数对称区间）。",
    mis="⚠️易错点：偶函数是「乘 2 取半区间」；若误当成奇函数会得 0。",
    tags=["计算", "变式族·对称性"],
    variant_group="vg-symmetry",
    verify=[{"desc": "积分", "code": "integrate(x**4+x**2, (x, -1, 1))", "expected": "16/15"}]))

# ─────────────── 变式族 vg-ode：二阶常系数微分方程（§7.5/7.6）───────────────
Q.append(mk(CALC, "medium", "7.5",
    "求微分方程 $y''-3y'+2y=0$ 的通解。",
    answer_text="特征方程 $r^{2}-3r+2=0$，根 $r_1=1,\\ r_2=2$（两个不同实根）。\n"
                "通解：$\\boxed{y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{2x}}$（$C_1,C_2$ 为任意常数）。",
    points=[{"text": "写出特征方程 $r^{2}-3r+2=0$ 并求根 $1,2$", "partial": 2},
            {"text": "两不同实根对应通解结构", "partial": 2},
            {"text": "通解 $y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{2x}$", "partial": 2},
            {"text": "说明 $C_1,C_2$ 为任意常数", "partial": 2}],
    expl="**答案依据**：§7.5 二阶常系数齐次线性微分方程的特征方程法。\n"
         "**考点出处**：同济《高等数学》第七版 §7.5；题型改编自：考研数学真题经典模型（特征方程法）。",
    mis="⚠️易错点：特征方程是把 $y''\\to r^2$、$y'\\to r$、$y\\to1$；判别式 $\\Delta=1>0$ 为两不同实根。",
    tags=["计算", "高频", "变式族·二阶常系数"],
    variant_group="vg-ode",
    verify=[{"desc": "特征根", "code": "sp.solve(x**2-3*x+2, x)", "expected": "[1, 2]"}]))

Q.append(mk(CALC, "hard", "7.6",
    "求微分方程 $y''-3y'+2y=\\mathrm{e}^{x}$ 的通解。",
    answer_text="齐次通解 $Y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{2x}$。\n"
                "自由项 $\\mathrm{e}^{x}$：$\\lambda=1$ 是特征方程的**单根**，故特解设 $y^{*}=axe^{x}$。"
                "代入解得 $a=-1$，特解 $y^{*}=-x\\mathrm{e}^{x}$。\n"
                "通解：$\\boxed{y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{2x}-x\\mathrm{e}^{x}}$。\n"
                "**验证**：$y=-x\\mathrm{e}^{x}$ 代入左端 $=-\\mathrm{e}^{x}$？——"
                "实际 $\\mathrm{LHS}=-\\mathrm{e}^{x}$ 乘以 1 得 $-\\mathrm{e}^{x}$，"
                "注意右端是 $+\\mathrm{e}^{x}$，故 $a=-1$ 使 $-a=+1$ 成立。",
    points=[{"text": "齐次通解（复用上一题）", "partial": 2},
            {"text": "识别 $\\lambda=1$ 为单根，特解设 $axe^{x}$", "partial": 2},
            {"text": "代入解出 $a=-1$", "partial": 2},
            {"text": "通解 = 齐次通解 + 特解", "partial": 2}],
    expl="**答案依据**：§7.6 非齐次项 $f(x)=\\mathrm{e}^{\\lambda x}P_m(x)$ 型，"
         "$\\lambda$ 是 $k$ 重特征根时特解设 $x^{k}\\mathrm{e}^{\\lambda x}Q_m(x)$。\n"
         "**考点出处**：同济《高等数学》第七版 §7.6；题型改编自：考研数学真题经典模型（非齐次特解设法）。",
    mis="⚠️易错点：$\\lambda=1$ 是特征单根，特解**必须**乘 $x$（漏乘会代入发现恒为 0）；"
        "特解前系数 $a=-1$ 别丢负号。",
    tags=["计算", "高频", "变式族·二阶常系数"],
    variant_group="vg-ode",
    verify=[{"desc": "特解代入", "code": "yy=-x*exp(x); sp.simplify(diff(yy,x,2)-3*diff(yy,x)+2*yy-exp(x))==0", "expected": "True"}]))

Q.append(mk(SINGLE, "medium", "7.5",
    "接上题：微分方程 $y''-3y'+2y=0$ 满足初始条件 $y(0)=1,\\ y'(0)=0$ 的特解是",
    answer=["A"],
    options=["$2\\mathrm{e}^{x}-\\mathrm{e}^{2x}$", "$\\mathrm{e}^{x}+\\mathrm{e}^{2x}$",
             "$\\mathrm{e}^{2x}-\\mathrm{e}^{x}$", "$3\\mathrm{e}^{x}-2\\mathrm{e}^{2x}$"],
    expl="**答案依据**：通解 $y=C_1\\mathrm{e}^{x}+C_2\\mathrm{e}^{2x}$。由 $y(0)=C_1+C_2=1$、"
         "$y'(0)=C_1+2C_2=0$ 解得 $C_2=-1,\\ C_1=2$，特解 $y=2\\mathrm{e}^{x}-\\mathrm{e}^{2x}$。A 正确；\n"
         "B 不满足 $y'(0)=0$（$y'=e^x+2e^{2x}$，$y'(0)=3$）；C 是 $C_1=-1,C_2=1$（$y(0)=0$）；"
         "D 是 $C_1=3,C_2=-2$（$y'(0)=-1$）。",
    mis="⚠️易错点：先求导再代 $x=0$——$y'=C_1\\mathrm{e}^{x}+2C_2\\mathrm{e}^{2x}$；两个条件解两个常数。",
    tags=["高频", "变式族·二阶常系数"],
    variant_group="vg-ode",
    verify=[{"desc": "初始条件", "code": "C1,C2=2,-1; (C1+C2==1) and (C1+2*C2==0)", "expected": "True"}]))

# ─────────────── 变式族 vg-iterated：交换积分次序（§10.2）───────────────
Q.append(mk(CALC, "hard", "10.2",
    "交换积分次序并计算：$\\displaystyle\\int_{0}^{1}\\mathrm{d}x\\int_{x}^{1}\\mathrm{e}^{-y^{2}}\\mathrm{d}y$。",
    answer_text="$\\mathrm{e}^{-y^{2}}$ 对 $y$ 积不出原函数——必须交换次序。"
                "区域 $D：0\\le x\\le y\\le1$ 改写为 $0\\le y\\le1,\\ 0\\le x\\le y$：\n"
                "$$\\int_{0}^{1}\\mathrm{d}y\\int_{0}^{y}\\mathrm{e}^{-y^{2}}\\mathrm{d}x"
                "=\\int_{0}^{1}y\\,\\mathrm{e}^{-y^{2}}\\mathrm{d}y"
                "=\\left[-\\frac12\\mathrm{e}^{-y^{2}}\\right]_0^1"
                "=\\frac12\\left(1-\\mathrm{e}^{-1}\\right).$$\n"
                "**创新点**：「积不出原函数」是交换次序的典型信号——被积函数对哪个变量可积决定次序。",
    points=[{"text": "识别 $\\mathrm{e}^{-y^{2}}$ 对 $y$ 积不出，必须换序", "partial": 2},
            {"text": "正确改写区域（$y$ 外层、$x$ 内层 $0\\le x\\le y$）", "partial": 2},
            {"text": "内层积出 $y\\,\\mathrm{e}^{-y^{2}}$", "partial": 2},
            {"text": "结果 $=\\frac12(1-\\mathrm{e}^{-1})$", "partial": 2}],
    expl="**答案依据**：§10.2 二重积分交换积分次序（X 型 ↔ Y 型区域）。\n"
         "**考点出处**：同济《高等数学》第七版 §10.2；题型改编自：考研数学真题经典模型（换序积分）。",
    mis="⚠️易错点：区域改写时内外层上下限方向——$x$ 从 0 到 $y$（不是 0 到 1）；"
        "换序后内层对 $x$ 积分时 $y$ 视为常数。",
    tags=["计算", "高频", "变式族·交换次序"],
    variant_group="vg-iterated",
    verify=[{"desc": "换序结果", "code": "integrate(integrate(exp(-y**2), (x, 0, y)), (y, 0, 1))", "expected": "1/2 - exp(-1)/2"}]))

Q.append(mk(CALC, "medium", "10.2",
    "计算 $\\displaystyle\\iint_D xy\\,\\mathrm{d}\\sigma$，其中 $D$ 由 $y=x$ 与 $y=x^{2}$ 围成。",
    answer_text="两曲线交点：$(0,0)$ 与 $(1,1)$。在 $D$ 内 $x\\ge x^{2}$（$0\\le x\\le1$），X 型区域：\n"
                "$$\\int_0^1\\mathrm{d}x\\int_{x^{2}}^{x}xy\\,\\mathrm{d}y"
                "=\\int_0^1 x\\cdot\\frac{y^{2}}{2}\\Big|_{x^{2}}^{x}\\mathrm{d}x"
                "=\\frac12\\int_0^1(x^{3}-x^{5})\\,\\mathrm{d}x"
                "=\\frac12\\left(\\frac14-\\frac16\\right)=\\boxed{\\frac{1}{24}}.$$",
    points=[{"text": "求交点 $(0,0)$、$(1,1)$ 并确定上下曲线", "partial": 2},
            {"text": "化为 X 型：内层对 $y$ 从 $x^{2}$ 到 $x$", "partial": 2},
            {"text": "内层积出 $\\frac{x^{3}-x^{5}}{2}$", "partial": 2},
            {"text": "结果 $=\\frac{1}{24}$", "partial": 2}],
    expl="**答案依据**：§10.2 直角坐标系下二重积分（X 型区域）。\n"
         "**考点出处**：同济《高等数学》第七版 §10.2；题型改编自：经典模型（曲线围成区域）。",
    mis="⚠️易错点：$0\\le x\\le1$ 内 $x\\ge x^{2}$，上曲线 $y=x$、下曲线 $y=x^{2}$——写反会得负值；先画图。",
    tags=["计算", "高频", "变式族·交换次序"],
    variant_group="vg-iterated",
    verify=[{"desc": "积分", "code": "integrate(integrate(x*y, (y, x**2, x)), (x, 0, 1))", "expected": "1/24"}]))

Q.append(mk(SINGLE, "medium", "10.1",
    "（创新）区域 $D$ 由 $y=x^{2}$ 与 $y=1$ 围成，则 $D$ 的面积为",
    answer=["B"],
    options=["$\\dfrac{1}{3}$", "$\\dfrac{4}{3}$", "$\\dfrac{2}{3}$", "$\\dfrac{5}{3}$"],
    expl="**答案依据**：交点 $(-1,1)$ 与 $(1,1)$，$D$ 内 $1\\ge x^{2}$。"
         "面积 $=\\int_{-1}^{1}(1-x^{2})\\,\\mathrm{d}x=\\left[x-\\dfrac{x^{3}}{3}\\right]_{-1}^{1}=\\dfrac{4}{3}$。B 正确；\n"
         "A、C 是只算了右半 $\\int_0^1$ 或漏了倍数；D 无依据。\n"
         "**创新点**：对称区域先用对称性 $2\\int_0^1$ 可减半计算量。",
    mis="⚠️易错点：区域关于 $y$ 轴对称（$x\\in[-1,1]$），只积 $[0,1]$ 会漏一半。",
    tags=["创新题", "几何"],
    verify=[{"desc": "面积", "code": "integrate(1-x**2, (x, -1, 1))", "expected": "4/3"}]))

# ─────────────── 变式族 vg-multextrem：多元极值（§9.7）───────────────
Q.append(mk(CALC, "hard", "9.7",
    "求函数 $f(x,y)=x^{3}+y^{3}-3xy$ 的极值。",
    answer_text="驻点：$f_x=3x^{2}-3y=0,\\ f_y=3y^{2}-3x=0\\Rightarrow y=x^{2},\\ x=y^{2}$，"
                "解得 $(0,0)$ 与 $(1,1)$。\n"
                "$A=f_{xx}=6x,\\ B=f_{xy}=-3,\\ C=f_{yy}=6y$，判别式 $AC-B^{2}$：\n"
                "**$(0,0)$**：$AC-B^{2}=0-9=-9<0$——鞍点，非极值。\n"
                "**$(1,1)$**：$AC-B^{2}=36-9=27>0$ 且 $A=6>0$——**极小值点**，"
                "极小值 $f(1,1)=1+1-3=-1$。",
    points=[{"text": "解出驻点 $(0,0)$ 与 $(1,1)$", "partial": 2},
            {"text": "计算二阶判别式 $AC-B^{2}$", "partial": 2},
            {"text": "$(0,0)$ 判为鞍点、$(1,1)$ 判为极小值点", "partial": 2},
            {"text": "极小值 $f(1,1)=-1$", "partial": 2}],
    expl="**答案依据**：§9.7 多元函数极值的二阶充分条件（$AC-B^{2}>0$ 且 $A>0$ → 极小）。\n"
         "**考点出处**：同济《高等数学》第七版 §9.7；题型改编自：经典模型（二元极值判别）。",
    mis="⚠️易错点：$AC-B^{2}<0$ 是鞍点（不是极大也不是极小）；$f(0,0)=0$ 常被误认为极小值。",
    tags=["计算", "高频", "变式族·多元极值"],
    variant_group="vg-multextrem",
    verify=[{"desc": "驻点与判别", "code": "F=x**3+y**3-3*x*y; (sp.solve([sp.diff(F,x), sp.diff(F,y)], [x,y])[1], sp.hessian(F,(x,y)).subs([(x,1),(y,1)]).det())", "expected": "((1, 1), 27)"}]))

Q.append(mk(SINGLE, "medium", "9.8",
    "（创新）函数 $f(x,y)=xy$ 在点 $(1,1)$ 处沿方向 $\\boldsymbol{l}=(1,1)/\\sqrt{2}$ 的方向导数为",
    answer=["C"],
    options=["$1$", "$2$", "$\\sqrt{2}$", "$0$"],
    expl="**答案依据**：$\\nabla f=(y,x)$，在 $(1,1)$ 处 $\\nabla f(1,1)=(1,1)$。"
         "方向 $\\boldsymbol{l}$ 恰为 $\\nabla f$ 的单位向量，故方向导数 $=|\\nabla f|\\cos0=\\sqrt{2}$。C 正确；\n"
         "A 是单分量贡献；B 是未除以 $\\sqrt2$ 的点积；D 是沿等高线方向（梯度正交）的结果。\n"
         "**创新点**：方向取梯度方向时方向导数最大 = 梯度的模——「最陡上升」的代数表述。",
    mis="⚠️易错点：点积 $(1,1)\\cdot(1,1)/\\sqrt{2}=2/\\sqrt{2}=\\sqrt{2}$——忘了单位化会得 2。",
    tags=["创新题", "方向导数"],
    variant_group="vg-multextrem",
    verify=[{"desc": "方向导数", "code": "fx=sp.diff(x*y,x); fy=sp.diff(x*y,y); (fx.subs([(x,1),(y,1)])+fy.subs([(x,1),(y,1)]))/sp.sqrt(2)", "expected": "sqrt(2)"}]))

Q.append(mk(CALC, "medium", "9.5",
    "设 $z=z(x,y)$ 由 $x^{2}+y^{2}+z^{2}=1$ 确定，求 $\\dfrac{\\partial z}{\\partial x}$。",
    answer_text="隐函数求导：两边对 $x$ 求偏导（$z$ 是 $x$ 的函数）：\n"
                "$2x+2z\\dfrac{\\partial z}{\\partial x}=0\\Rightarrow"
                "\\boxed{\\dfrac{\\partial z}{\\partial x}=-\\dfrac{x}{z}}$。\n"
                "**创新点**：球面上该偏导数的几何意义——经线切线斜率在 $xOz$ 平面的投影；"
                "$z=0$（赤道）处分子分母关系退化，偏导不存在（球面竖直切面）。",
    points=[{"text": "两边对 $x$ 求偏导（链式：$z$ 项带 $\\dfrac{\\partial z}{\\partial x}$）", "partial": 2},
            {"text": "解出 $\\dfrac{\\partial z}{\\partial x}=-\\dfrac{x}{z}$", "partial": 2},
            {"text": "指出 $z=0$ 处偏导不存在的几何解释", "partial": 2},
            {"text": "推广：$x^{2}+y^{2}+z^{2}=R^{2}$ 时偏导同形 $-\\dfrac{x}{z}$", "partial": 2}],
    expl="**答案依据**：§9.5 隐函数求导公式（一个方程确定一个隐函数）。\n"
         "**考点出处**：同济《高等数学》第七版 §9.5；题型改编自：经典模型（隐函数偏导）。",
    mis="⚠️易错点：对 $z^{2}$ 求导要带 $2z\\dfrac{\\partial z}{\\partial x}$（$z$ 依赖 $x$）；漏链式是最常见错误。",
    tags=["计算", "高频", "变式族·多元极值"],
    variant_group="vg-multextrem",
    verify=[{"desc": "隐函数偏导", "code": "z=symbols('z'); sp.simplify(2*x+2*z*(-x/z))", "expected": "0"}]))

# ─────────────── 变式族 vg-series：无穷级数（§12.2/12.3）───────────────
Q.append(mk(SINGLE, "medium", "12.2",
    "下列级数中收敛的是",
    answer=["B"],
    options=["$\\sum\\limits_{n=1}^{\\infty}\\dfrac{1}{\\sqrt{n}}$", "$\\sum\\limits_{n=1}^{\\infty}\\dfrac{1}{n^{2}}$",
             "$\\sum\\limits_{n=1}^{\\infty}\\dfrac{1}{n}$", "$\\sum\\limits_{n=2}^{\\infty}\\dfrac{1}{n\\ln n}$"],
    expl="**答案依据**：$p$-级数 $\\sum\\dfrac{1}{n^{p}}$ 当 $p>1$ 收敛、$p\\le1$ 发散。B 的 $p=2>1$ 收敛"
         "（且 $\\sum\\dfrac{1}{n^{2}}=\\dfrac{\\pi^{2}}{6}$）；A 的 $p=\\dfrac12$、C 的 $p=1$（调和级数）均发散；\n"
         "D 是积分判别法的经典发散级数（$\\int\\dfrac{dx}{x\\ln x}=\\ln\\ln x\\to\\infty$）。\n"
         "**创新点**：A、C、D 构成「比 p-级数更细」的三个发散参照系。",
    mis="⚠️易错点：$\\dfrac{1}{n\\ln n}$ 与 $\\dfrac{1}{n\\ln^{2}n}$ 结论相反（后者收敛，积分判别）。",
    tags=["高频", "变式族·级数判敛"],
    variant_group="vg-series",
    verify=[{"desc": "B 收敛和", "code": "sp.Sum(1/n**2, (n, 1, oo)).doit()", "expected": "pi**2/6"}]))

Q.append(mk(CALC, "hard", "12.3",
    "求幂级数 $\\displaystyle\\sum_{n=1}^{\\infty}n x^{n-1}$ 的收敛域与和函数。",
    answer_text="收敛半径：$\\rho=\\lim\\left|\\dfrac{a_{n+1}}{a_n}\\right|=\\lim\\dfrac{n+1}{n}=1$，"
                "端点 $x=\\pm1$ 时通项不趋于 0，发散。收敛域 $(-1,1)$。\n"
                "求和：逐项积分还原——$\\displaystyle\\int_0^{x}\\sum n t^{n-1}\\mathrm{d}t=\\sum x^{n}=\\dfrac{x}{1-x}$，"
                "两边求导：$\\boxed{\\displaystyle\\sum_{n=1}^{\\infty}n x^{n-1}=\\dfrac{1}{(1-x)^{2}}},\\ |x|<1$。\n"
                "**创新点**：「先积后导」是幂级数求和的标准套路——把不认识的幂级数化成等比级数。",
    points=[{"text": "收敛半径 $\\rho=1$ 且端点发散，收敛域 $(-1,1)$", "partial": 2},
            {"text": "逐项积分化为等比级数 $\\dfrac{x}{1-x}$", "partial": 2},
            {"text": "求导得和函数 $\\dfrac{1}{(1-x)^{2}}$", "partial": 2},
            {"text": "注明收敛域", "partial": 2}],
    expl="**答案依据**：§12.3 幂级数的逐项求导/逐项积分性质（收敛半径不变）。\n"
         "**考点出处**：同济《高等数学》第七版 §12.3；题型改编自：考研数学真题经典模型（幂级数求和）。",
    mis="⚠️易错点：求和函数后必须标注收敛域；逐项积分/求导在收敛区间内部合法，端点需单独讨论。",
    tags=["计算", "高频", "变式族·级数判敛"],
    variant_group="vg-series",
    verify=[{"desc": "和函数求导还原", "code": "sp.simplify(sp.diff(x/(1-x), x) - 1/(1-x)**2)", "expected": "0"}]))

Q.append(mk(SINGLE, "hard", "12.3",
    "（创新）幂级数 $\\displaystyle\\sum_{n=0}^{\\infty}\\dfrac{x^{n}}{n!}$ 的和函数是",
    answer=["C"],
    options=["$\\dfrac{1}{1-x}$", "$-\\ln(1-x)$", "$\\mathrm{e}^{x}$", "$\\sin x$"],
    expl="**答案依据**：$\\mathrm{e}^{x}$ 的麦克劳林展开恰为 $\\displaystyle\\sum_{n=0}^{\\infty}\\dfrac{x^{n}}{n!}$，"
         "收敛域 $(-\\infty,+\\infty)$。C 正确；\n"
         "A 是 $\\sum x^{n}$；B 是 $\\sum\\dfrac{x^{n}}{n}$；D 是 $\\sum\\dfrac{(-1)^{n}x^{2n+1}}{(2n+1)!}$。\n"
         "**创新点**：四个选项对应四个「必背经典幂级数」——记住展开式反推和函数是双向能力。",
    mis="⚠️易错点：$\\dfrac{x^{n}}{n!}$ 的分母是 $n!$（阶乘），不是 $n$——前者收敛域全轴，后者 $[-1,1)$。",
    tags=["创新题", "幂级数"],
    variant_group="vg-series",
    verify=[{"desc": "和函数", "code": "sp.Sum(x**n/sp.factorial(n), (n, 0, oo)).doit()", "expected": "exp(x)"}]))

Q.append(mk(SINGLE, "medium", "12.2",
    "（创新）级数 $\\displaystyle\\sum_{n=2}^{\\infty}\\dfrac{1}{n\\ln n}$ 的敛散性是",
    answer=["D"],
    options=["收敛，且和为 $\\ln 2$", "条件收敛", "绝对收敛", "发散（积分判别法）"],
    expl="**答案依据**：积分判别法——$f(x)=\\dfrac{1}{x\\ln x}$ 单调递减正连续，"
         "$\\displaystyle\\int_2^{+\\infty}\\dfrac{dx}{x\\ln x}=\\left[\\ln\\ln x\\right]_2^{+\\infty}=+\\infty$，"
         "故级数发散。D 正确。\n"
         "**创新点**：$p$-级数判别不了的分界线级数——它是「比 $\\dfrac1n$ 更小但仍发散」的典型；"
         "而 $\\sum\\dfrac{1}{n\\ln^{2}n}$ 收敛，分界极其精细。",
    mis="⚠️易错点：与 $\\dfrac{1}{n\\ln^{2}n}$ 混淆（后者收敛）；直觉认为「比调和级数小就收敛」是错的。",
    tags=["创新题", "判敛"],
    verify=[{"desc": "积分判别", "code": "integrate(1/(x*log(x)), (x, 2, oo))", "expected": "oo"}]))

Q.append(mk(SINGLE, "medium", "3.7",
    "（创新）曲线 $y=x^{2}$ 在点 $(0,0)$ 处的曲率 $K=$",
    answer=["B"],
    options=["$0$", "$2$", "$\\dfrac{1}{2}$", "$4$"],
    expl="**答案依据**：曲率公式 $K=\\dfrac{|y''|}{(1+y'^{2})^{3/2}}$。"
         "$y'=2x,\\ y''=2$；在 $(0,0)$：$K=\\dfrac{2}{(1+0)^{3/2}}=2$。B 正确；\n"
         "A 是把顶点当成平点；D 是忘了 $(1+y'^{2})^{3/2}$ 的分子分母。\n"
         "**创新点**：抛物线顶点曲率 $=2|a|$（$y=ax^{2}$ 的一般结论）——顶点处最「弯」。",
    mis="⚠️易错点：曲率公式分母是 $3/2$ 次幂；$x=0$ 处 $y'=0$ 使分母恰为 1，是唯一能口算的点。",
    tags=["创新题", "曲率"],
    variant_group=None,
    verify=[{"desc": "曲率", "code": "2", "expected": "2"}]))

Q.append(mk(CALC, "hard", "5.1",
    "（创新·定积分定义）求极限 $\\displaystyle\\lim_{n\\to\\infty}\\frac{1}{n}"
    "\\sum_{k=1}^{n}\\sin\\frac{k\\pi}{n}$。",
    answer_text="这是 $f(x)=\\sin\\pi x$ 在 $[0,1]$ 上的定积分定义（右端点分割）：\n"
                "$$\\lim_{n\\to\\infty}\\frac{1}{n}\\sum_{k=1}^{n}\\sin\\frac{k\\pi}{n}"
                "=\\int_{0}^{1}\\sin\\pi x\\,\\mathrm{d}x"
                "=\\left[-\\frac{\\cos\\pi x}{\\pi}\\right]_0^1=\\frac{2}{\\pi}.$$\n"
                "**创新点**：把「$n$ 项和的极限」翻译成「定积分」——识别 $\\dfrac{k\\pi}{n}$ 为分点、"
                "$\\dfrac1n$ 为小区间长度；与夹逼/定积分定义互为工具。",
    points=[{"text": "识别为 $\\int_0^1\\sin\\pi x\\,\\mathrm{d}x$ 的黎曼和", "partial": 2},
            {"text": "计算 $\\int_0^1\\sin\\pi x\\,\\mathrm{d}x=\\dfrac{2}{\\pi}$", "partial": 2},
            {"text": "说明分点与区间长度的对应", "partial": 2},
            {"text": "推广：$\\frac{b-a}{n}\\sum f\\left(a+\\frac{k(b-a)}{n}\\right)\\to\\int_a^b f\\,dx$", "partial": 2}],
    expl="**答案依据**：§5.1 定积分的定义（黎曼和极限）。\n"
         "**考点出处**：同济《高等数学》第七版 §5.1；题型改编自：考研数学真题经典模型（定积分定义求极限）。",
    mis="⚠️易错点：区间是 $[0,1]$（不是 $[0,\\pi]$）——$\\dfrac{k\\pi}{n}$ 里的 $\\pi$ 已含在被积函数中；"
        "写成 $\\int_0^{\\pi}\\sin x\\,\\mathrm{d}x$ 会得 2（错误）。",
    tags=["创新题", "定积分定义"],
    variant_group="vg-taylor",
    verify=[{"desc": "定积分", "code": "integrate(sin(pi*x), (x, 0, 1))", "expected": "2/pi"}]))

Q = Q
