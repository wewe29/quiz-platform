# -*- coding: utf-8 -*-
"""第10章 重积分 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：10.1 二重积分的概念与性质 / 10.2 二重积分的计算法 / 10.3 三重积分 / 10.4 重积分的应用
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "10.1",
    "设 $D=\\{(x,y)\\,|\\,|x|\\le1,\\ |y|\\le1\\}$，则 $\\displaystyle\\iint_D \\mathrm{d}\\sigma=$",
    qid="c10-s1",
    answer=["C"],
    options=["$1$", "$2$", "$4$", "$8$"],
    expl="**答案依据**：被积函数为 $1$ 的二重积分等于积分区域的面积（§10.1 性质）。$D$ 是边长为 $2$ 的正方形，面积 $4$，故 C 正确。\n"
         "A、B、D 错：分别是把边长、半边长、体积概念混入。",
    mis="⚠️易错点：$\\iint_D d\\sigma=\\text{面积}(D)$、$\\iiint_\\Omega dV=\\text{体积}(\\Omega)$ 是最常用的「秒杀」性质。",
    tags=["二重积分性质"]))

Q_.append(Q(SINGLE, "medium", "10.2",
    "交换积分次序：$\\displaystyle\\int_0^1 dx\\int_0^{x^2} f(x,y)\\,dy=$",
    qid="c10-s2",
    answer=["D"],
    options=["$\\displaystyle\\int_0^1 dy\\int_0^{\\sqrt y} f(x,y)\\,dx$",
             "$\\displaystyle\\int_0^1 dy\\int_y^1 f(x,y)\\,dx$",
             "$\\displaystyle\\int_0^1 dy\\int_1^{\\sqrt y} f(x,y)\\,dx$",
             "$\\displaystyle\\int_0^1 dy\\int_{\\sqrt y}^{1} f(x,y)\\,dx$"],
    expl="**答案依据**：原积分区域为 $0\\le x\\le1$，$0\\le y\\le x^2$，即抛物线 $y=x^2$ 下方、$[0,1]\\times[0,1]$ 内的部分。改为先 $x$ 后 $y$：$y\\in[0,1]$，对固定 $y$，$x$ 从曲线 $x=\\sqrt y$ 到直线 $x=1$，故 $\\displaystyle\\int_0^1dy\\int_{\\sqrt y}^{1}f(x,y)dx$，D 正确。\n"
         "A 错：积分限方向颠倒（对固定 $y$，$x$ 的下限是 $\\sqrt y$）。\n"
         "B 错：把区域取成了 $y\\ge x^2$ 的部分。\n"
         "C 错：下限大于上限，积分号方向错误。",
    mis="⚠️易错点：交换次序必须先把区域图画出来、用「穿线法」定限；曲线 $y=x^2$（$x\\ge0$）的反函数是 $x=\\sqrt y$。",
    tags=["交换积分次序", "高频考点"]))

Q_.append(Q(SINGLE, "hard", "10.2",
    "$\\displaystyle\\iint_{x^2+y^2\\le1} e^{x^2+y^2}\\,\\mathrm{d}\\sigma=$",
    qid="c10-s3",
    answer=["D"],
    options=["$\\pi(e+1)$", "$2\\pi(e-1)$", "$\\dfrac{e-1}{2}$", "$\\pi(e-1)$"],
    expl="**答案依据**：极坐标变换（§10.2）：$x^2+y^2=r^2$，$d\\sigma=r\\,dr\\,d\\theta$，\n"
         "$$\\iint_D e^{x^2+y^2}d\\sigma=\\int_0^{2\\pi}d\\theta\\int_0^1 e^{r^2}r\\,dr=2\\pi\\cdot\\left[\\frac{e^{r^2}}{2}\\right]_0^1=\\pi(e-1),$$\n"
         "D 正确。\n"
         "A 错：$e^{r^2}$ 的原函数在 $r=1$ 处代值 $e$、$r=0$ 处为 $1$，差是 $e-1$ 不是 $e+1$。\n"
         "B 错：$\\int_0^1e^{r^2}r\\,dr=\\dfrac{e-1}{2}$，多乘了 $2$。\n"
         "C 错：漏了 $2\\pi$ 因子。",
    mis="⚠️易错点：极坐标下 $d\\sigma=r\\,dr\\,d\\theta$ 的**雅可比因子 $r$** 是第一易错点；被积函数含 $x^2+y^2$ 或区域为圆域时优先极坐标。",
    tags=["极坐标", "高频考点", "困难"],
    verify=[{"desc": "integral", "code": "rr,th=symbols('rr th', positive=True); I=integrate(exp(rr**2)*rr, (rr, 0, 1), (th, 0, 2*pi)); simplify(I - pi*(exp(1)-1))", "expected": "0"}]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "10.2",
    "关于二重积分的极坐标计算 $\\iint_D f(x,y)\\,d\\sigma=\\iint f(r\\cos\\theta,r\\sin\\theta)\\,r\\,dr\\,d\\theta$，下列说法正确的有",
    qid="c10-m1",
    answer=["A", "B", "D"],
    options=["区域 $D$ 为圆域、环域或扇形域时优先考虑极坐标",
             "被积函数含 $x^2+y^2$（或 $\\dfrac{y}{x}$）时优先考虑极坐标",
             "只有直角坐标下次序交换困难时才能用极坐标",
             "面积元素变换为 $d\\sigma=r\\,dr\\,d\\theta$"],
    expl="**答案依据**：§10.2 给出的两类典型适用情形——圆域/环域/扇形域（边界方程 $r=$ 常数简单）与被积函数含 $x^2+y^2$、$\\dfrac yx$（代入极坐标后变量分离），A、B 正确；$d\\sigma=r\\,dr\\,d\\theta$，D 正确。\n"
         "C 错：极坐标与交换次序是两个独立的化简手段，选择坐标系的依据是「区域形状 + 被积函数结构」，并非只有交换次序困难时才用。",
    mis="⚠️易错点：极坐标积分限：过极点的区域 $r\\in[0,r(\\theta)]$、环域 $r_1(\\theta)\\le r\\le r_2(\\theta)$；被积函数与 $d\\sigma$ 中**都要**把 $r$ 因子带上。",
    tags=["极坐标", "适用条件"]))

Q_.append(Q(MULTI, "hard", "10.3",
    "关于三重积分的计算，下列说法正确的有",
    qid="c10-m2",
    answer=["A", "B", "C"],
    options=["柱面坐标下 $dV=r\\,dz\\,dr\\,d\\theta$，适合区域含圆柱面、旋转抛物面的情形",
             "被积函数只含 $z$ 且截面面积易求时，可用「先二后一」（截面法）：$\\iiint_\\Omega f(z)\\,dV=\\int_{z_1}^{z_2}f(z)\\,S(z)\\,dz$",
             "球面坐标下 $dV=r^2\\sin\\varphi\\,dr\\,d\\varphi\\,d\\theta$",
             "若区域 $\\Omega$ 关于 $y$ 轴对称，则 $\\iiint_\\Omega f\\,dV=0$"],
    expl="**答案依据**：柱面坐标与球面坐标的体积元素及「先二后一」法均为 §10.3 的标准内容，A、B、C 正确。\n"
         "D 错：利用对称性须同时要求**被积函数具有相应奇偶性**——区域关于 $yOz$ 面对称且 $f$ 关于 $x$ 为奇函数时积分才为零；仅区域对称推不出积分为零。",
    mis="⚠️易错点：对称性简化口诀「域对称 + 函数奇（偶）」两个条件缺一不可；球面坐标中 $\\varphi$ 是与 $z$ 轴正向的夹角，$\\sin\\varphi$ 因子勿丢。",
    tags=["三重积分", "对称性", "困难"]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "10.1",
    "当 $f(x,y)\\ge0$ 时，$\\displaystyle\\iint_D f(x,y)\\,\\mathrm{d}\\sigma$ 在几何上表示以 $D$ 为底、$z=f(x,y)$ 为顶的曲顶柱体的体积。",
    qid="c10-j1",
    answer=["A"],
    expl="**答案依据**：二重积分的几何意义（§10.1）：被积函数非负时积分为曲顶柱体体积；一般情形是「上正下负」体积的代数和。命题正确。",
    mis="⚠️易错点：与定积分「带符号面积」类似，$f$ 变号时积分不是体积本身。",
    tags=["几何意义"]))

Q_.append(Q(JUDGE, "basic", "10.2",
    "$\\displaystyle\\iint_{x^2+y^2\\le R^2}\\sqrt{R^2-x^2-y^2}\\,\\mathrm{d}\\sigma=\\dfrac{2}{3}\\pi R^3$。",
    qid="c10-j2",
    answer=["A"],
    expl="**答案依据**：被积函数 $z=\\sqrt{R^2-x^2-y^2}$ 是上半球面，积分区域是其在 $xOy$ 面上的投影圆域，故积分等于半径 $R$ 的半球体积 $\\dfrac12\\cdot\\dfrac43\\pi R^3=\\dfrac23\\pi R^3$（§10.1 几何意义）。命题正确。",
    mis="⚠️易错点：看到 $\\sqrt{R^2-x^2-y^2}$ 应立即联想上半球面，用几何意义秒算，不必硬积。",
    tags=["几何意义", "半球体积"],
    verify=[{"desc": "R=1核验", "code": "rr,th=symbols('rr th', positive=True); I=integrate(sqrt(1-rr**2)*rr, (rr, 0, 1), (th, 0, 2*pi)); simplify(I - Rational(2,3)*pi)", "expected": "0"}]))

Q_.append(Q(JUDGE, "medium", "10.2",
    "若区域 $D$ 关于 $y$ 轴对称，则 $\\displaystyle\\iint_D f(x,y)\\,\\mathrm{d}\\sigma=0$。",
    qid="c10-j3",
    answer=["B"],
    expl="**答案依据**：对称性简化需要两个条件同时满足：区域对称 + 被积函数关于对称变量为**奇**函数。本题只给了区域对称，$f$ 任意，例如 $f\\equiv1$ 时积分等于区域面积 $\\ne0$。命题错误（§10.2）。",
    mis="⚠️易错点：正确表述——$D$ 关于 $y$ 轴对称时，$f$ 关于 $x$ 为奇函数则积分为 $0$，为偶函数则等于半区域积分的两倍。",
    tags=["对称性", "易错点"]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "10.2",
    "$\\displaystyle\\iint_{x^2+y^2\\le1} x\\,\\mathrm{d}\\sigma=$ ____。",
    qid="c10-b1",
    answer=["0"],
    accept=["0"],
    expl="**答案依据**：区域关于 $y$ 轴对称且 $f(x,y)=x$ 关于 $x$ 为奇函数，积分为 $0$（§10.2 对称性）。",
    mis="⚠️易错点：本题两点齐全（域对称 + 函数奇）才能秒判零；只背口诀不查条件会误用。",
    tags=["对称性"]))

Q_.append(Q(BLANK, "medium", "10.2",
    "$\\displaystyle\\iint_{x^2+y^2\\le4} (x^2+y^2)\\,\\mathrm{d}\\sigma=$ ____。",
    qid="c10-b2",
    answer=["8*pi"],
    accept=["8pi", "8*pi", "8π", "8*pi"],
    expl="**答案依据**：极坐标：$\\displaystyle\\int_0^{2\\pi}d\\theta\\int_0^2 r^2\\cdot r\\,dr=2\\pi\\cdot\\left[\\frac{r^4}{4}\\right]_0^2=2\\pi\\cdot4=8\\pi$。",
    mis="⚠️易错点：$d\\sigma$ 的 $r$ 因子与被积函数的 $r^2$ 合并为 $r^3$；上限是 $2$（半径），$2^4/4=4$。",
    tags=["极坐标", "高频考点"],
    verify=[{"desc": "integral", "code": "rr,th=symbols('rr th', positive=True); I=integrate(rr**2*rr, (rr, 0, 2), (th, 0, 2*pi)); simplify(I - 8*pi)", "expected": "0"}]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "10.1",
    "名词解释：二重积分。",
    qid="c10-t1",
    answer_text="设 $f(x,y)$ 是有界闭区域 $D$ 上的有界函数，将 $D$ 任意分成 $n$ 个小闭区域 $\\Delta\\sigma_i$，在每个 $\\Delta\\sigma_i$ 上任取一点 $(\\xi_i,\\eta_i)$，作和式 $\\sum_{i=1}^n f(\\xi_i,\\eta_i)\\Delta\\sigma_i$；若各小区域直径的最大值 $\\lambda\\to0$ 时该和式的极限存在，则称 $f$ 在 $D$ 上可积，极限值称为 $f$ 在 $D$ 上的二重积分，记作 $\\displaystyle\\iint_D f(x,y)\\,d\\sigma$。",
    points=["定义核心：分割、取点、求和、取极限，$\\iint_D f\\,d\\sigma=\\lim\\limits_{\\lambda\\to0}\\sum\\limits_{i=1}^n f(\\xi_i,\\eta_i)\\Delta\\sigma_i$。",
            "几何与存在性：$f\\ge0$ 时为曲顶柱体体积；有界闭区域上的连续函数必可积。"],
    expl="**答案依据**：二重积分的定义与可积条件见 §10.1。\n"
         "**考点出处**：同济《高等数学》第七版 §10.1 二重积分的概念与性质。",
    mis="⚠️易错点：$\\Delta\\sigma_i$ 表示小区域面积；极限过程是「最大直径 $\\lambda\\to0$」而非「块数 $n\\to\\infty$」。",
    tags=["二重积分定义", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "10.2",
    "简答：二重积分化为二次积分的一般步骤是什么？如何选择坐标系与积分次序？",
    qid="c10-t2",
    answer_text="步骤：①画区域 $D$ 的草图并求边界交点；②选坐标系——区域为圆域/环域/扇形或被积函数含 $x^2+y^2$ 时用极坐标（$d\\sigma=r\\,dr\\,d\\theta$），否则用直角坐标；③定次序——按「穿线法」看先固定一个变量时另一变量的进入线与穿出线是否分段，尽量选择不分段或少分段的次序（如 $Y$ 型区域先 $x$ 后 $y$）；④写出内外层积分限并逐次积分。",
    points=["画图与交点：确定区域形状是化限的前提；坐标系选择——圆域/环域/扇形或被积函数含 $x^2+y^2$、$\\dfrac yx$ 时用极坐标（$d\\sigma=r\\,dr\\,d\\theta$），否则直角坐标。",
            "次序选择：以「穿线不分段、内层原函数好求」为标准；交换次序时用反函数（如 $y=x^2$ ↔ $x=\\sqrt y$）改写边界。",
            "极坐标定限：射线从极点出发时 $r$ 从 $0$（或内边界）到 $r(\\theta)$，$\\theta$ 扫过整个区域的张角范围。"],
    expl="**答案依据**：直角坐标、极坐标计算法与次序选择的依据见 §10.2。\n"
         "**考点出处**：同济《高等数学》第七版 §10.2 二重积分的计算法。",
    mis="⚠️易错点：极坐标别忘了 $r$ 因子；直角坐标内外层限必须「外层常数、内层随变量」。",
    tags=["二次积分", "简答", "高频考点"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "10.2",
    "计算 $\\displaystyle\\iint_D (x+y)\\,\\mathrm{d}\\sigma$，其中 $D$ 由直线 $x=0$、$y=0$ 及 $x+y=1$ 围成。",
    qid="c10-c1",
    answer=["1/3"],
    answer_text="把 $D$ 视为 $X$ 型区域：$0\\le x\\le1$，$0\\le y\\le1-x$。\n"
                "$$\\iint_D(x+y)\\,d\\sigma=\\int_0^1dx\\int_0^{1-x}(x+y)\\,dy=\\int_0^1\\left[x(1-x)+\\frac{(1-x)^2}{2}\\right]dx.$$\n"
                "分别计算：$\\int_0^1(x-x^2)dx=\\dfrac16$，$\\int_0^1\\dfrac{(1-x)^2}{2}dx=\\dfrac16$，合计 $\\dfrac13$。",
    points=["写出 $X$ 型区域不等式 $0\\le x\\le1$，$0\\le y\\le1-x$。",
            "先积内层 $\\int_0^{1-x}(x+y)dy=x(1-x)+\\dfrac{(1-x)^2}{2}$。",
            "再积外层得 $\\dfrac16+\\dfrac16=\\dfrac13$。",
            "或用对称性：$\\iint_Dx\\,d\\sigma=\\iint_Dy\\,d\\sigma=\\dfrac16$，相加即 $\\dfrac13$。"],
    expl="**答案依据**：直角坐标下 $X$ 型区域的二次积分（§10.2）。\n"
         "**考点出处**：同济《高等数学》第七版 §10.2 二重积分的计算法。",
    tags=["二次积分", "高频考点"],
    verify=[{"desc": "integral", "code": "integrate(x + y, (y, 0, 1 - x), (x, 0, 1))", "expected": "1/3"}]))

Q_.append(Q(CALC, "medium", "10.2",
    "计算 $\\displaystyle\\iint_D xy\\,\\mathrm{d}\\sigma$，其中 $D$ 为 $x^2+y^2\\le1$ 在第一象限的部分。",
    qid="c10-c2",
    answer=["1/8"],
    answer_text="极坐标：$x=r\\cos\\theta$，$y=r\\sin\\theta$，$d\\sigma=r\\,dr\\,d\\theta$，$D$ 上 $0\\le r\\le1$，$0\\le\\theta\\le\\dfrac\\pi2$。\n"
                "$$\\iint_D xy\\,d\\sigma=\\int_0^{\\pi/2}\\cos\\theta\\sin\\theta\\,d\\theta\\int_0^1 r^3\\,dr=\\frac12\\cdot\\frac14=\\frac18.$$\n",
    points=["写出极坐标范围 $0\\le r\\le1$、$0\\le\\theta\\le\\dfrac\\pi2$，被积函数化为 $r^2\\cos\\theta\\sin\\theta$，并带 $r$ 因子得 $r^3$。",
            "变量分离：$\\int_0^{\\pi/2}\\sin\\theta\\cos\\theta\\,d\\theta=\\dfrac12$。",
            "$\\int_0^1r^3dr=\\dfrac14$，相乘得 $\\dfrac18$。",
            "本题被积函数与区域都「圆对称友好」，是极坐标的标准应用。"],
    expl="**答案依据**：极坐标计算二重积分（§10.2）。\n"
         "**考点出处**：同济《高等数学》第七版 §10.2 二重积分的计算法。",
    tags=["极坐标", "高频考点"],
    verify=[{"desc": "integral", "code": "rr,th=symbols('rr th', positive=True); integrate(rr**2*cos(th)*sin(th)*rr, (rr, 0, 1), (th, 0, pi/2))", "expected": "1/8"}]))

Q_.append(Q(CALC, "hard", "10.3",
    "计算 $\\displaystyle\\iiint_\\Omega z\\,\\mathrm{d}V$，其中 $\\Omega$ 为上半球体 $x^2+y^2+z^2\\le1$（$z\\ge0$）。",
    qid="c10-c3",
    answer=["pi/4"],
    answer_text="法一（先二后一）：固定 $z\\in[0,1]$，截面 $D_z$ 为半径 $\\sqrt{1-z^2}$ 的圆，面积 $S(z)=\\pi(1-z^2)$，\n"
                "$$\\iiint_\\Omega z\\,dV=\\int_0^1 z\\cdot\\pi(1-z^2)\\,dz=\\pi\\left(\\frac12-\\frac14\\right)=\\frac{\\pi}{4}.$$\n"
                "法二（球面坐标）：$z=r\\cos\\varphi$，$dV=r^2\\sin\\varphi\\,dr\\,d\\varphi\\,d\\theta$，\n"
                "$$\\int_0^{2\\pi}d\\theta\\int_0^{\\pi/2}\\sin\\varphi\\cos\\varphi\\,d\\varphi\\int_0^1 r^3\\,dr=2\\pi\\cdot\\frac12\\cdot\\frac14=\\frac{\\pi}{4}.$$\n",
    points=["「先二后一」：截面 $S(z)=\\pi(1-z^2)$，化为 $\\int_0^1 z\\pi(1-z^2)dz$。",
            "球面坐标：$dV=r^2\\sin\\varphi\\,dr\\,d\\varphi\\,d\\theta$，上半球 $\\varphi\\in[0,\\dfrac\\pi2]$。",
            "三个单积分分别算出 $2\\pi$、$\\dfrac12$、$\\dfrac14$，乘积 $\\dfrac\\pi4$。",
            "被积函数只含 $z$ 且截面面积易求时，先二后一最快。"],
    expl="**答案依据**：三重积分的「先二后一」与球面坐标（§10.3）。\n"
         "**考点出处**：同济《高等数学》第七版 §10.3 三重积分。",
    mis="⚠️易错点：球面坐标中 $\\varphi$ 从极轴（$z$ 正向）量起，上半球是 $[0,\\dfrac\\pi2]$ 而非 $[\\dfrac\\pi2,\\pi]$；先二后一中截面面积是 $\\pi(1-z^2)$ 不是 $2\\pi(1-z^2)$。",
    tags=["三重积分", "先二后一", "困难", "高频考点"],
    verify=[{"desc": "integral", "code": "rr,ph,th=symbols('rr ph th', positive=True); integrate(rr*cos(ph)*rr**2*sin(ph), (rr, 0, 1), (ph, 0, pi/2), (th, 0, 2*pi))", "expected": "pi/4"}]))

Q = Q_
