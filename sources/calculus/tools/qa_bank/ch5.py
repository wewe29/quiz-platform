# -*- coding: utf-8 -*-
"""第5章 定积分 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：5.1 定积分的概念与性质 / 5.2 微积分基本公式 / 5.3 定积分的换元法和分部积分法 / 5.4 反常积分
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "5.1",
    "由定积分的几何意义，$\\int_0^{2\\pi}\\sin x\\,dx=$",
    qid="c5-s1",
    answer=["A"],
    options=["$0$", "$1$", "$2\\pi$", "$4\\pi$"],
    expl="**答案依据**：$\\sin x$ 在 $[0,\\pi]$ 上的图象与 $[\\pi,2\\pi]$ 上的图象关于点 $(\\pi,0)$ 中心对称，$x$ 轴上方面积与下方面积相等、符号相反，代数和为零（§5.1 几何意义）。故 A 正确。\n"
         "B 错：是 $\\int_0^{\\pi}\\sin x\\,dx=2$ 的一半再误取。\n"
         "C、D 错：把「面积」当成了「积分值」——面积是 $\\int_0^{2\\pi}|\\sin x|dx=4$，且 $2\\pi$、$4\\pi$ 也不是面积。",
    mis="⚠️易错点：定积分的值是「带符号面积的代数和」，几何意义是面积的前提是被积函数非负；对称区间上奇函数积分为零是本题的另一种解释。",
    tags=["几何意义"],
    verify=[{"desc": "integral", "code": "integrate(sin(x), (x, 0, 2*pi))", "expected": "0"}]))

Q_.append(Q(SINGLE, "medium", "5.2",
    "设 $F(x)=\\displaystyle\\int_0^{x^2}\\sin t^2\\,dt$，则 $F'(x)=$",
    qid="c5-s2",
    answer=["C"],
    options=["$\\sin x^4$", "$x^2\\sin x^4$", "$2x\\sin x^4$", "$2x\\cos x^4$"],
    expl="**答案依据**：变上限积分求导的链式版本（§5.2）：$\\dfrac{d}{dx}\\int_0^{\\varphi(x)}f(t)dt=f(\\varphi(x))\\varphi'(x)$。这里 $\\varphi(x)=x^2$，故 $F'(x)=\\sin(x^2)^2\\cdot 2x=2x\\sin x^4$，C 正确。\n"
         "A 错：漏乘上限函数的导数 $2x$。\n"
         "B 错：把 $\\varphi'(x)$ 误写成 $x^2$。\n"
         "D 错：对被积函数 $\\sin t^2$ 也求了导（积分变量 $t$ 不是求导对象）。",
    mis="⚠️易错点：被积函数里的 $t$ 在求导时是「死变量」，只对上限 $x$ 复合求导；上限是 $x^2$ 时要多乘一个 $2x$。",
    tags=["变上限积分", "高频考点"],
    verify=[{"desc": "求导", "code": "xx=symbols('xx'); simplify(diff(Integral(sin(t**2), (t, 0, xx**2)), xx) - 2*xx*sin(xx**4))", "expected": "0"}]))

Q_.append(Q(SINGLE, "hard", "5.4",
    "反常积分 $\\int_0^1\\ln x\\,dx$ 的值是",
    qid="c5-s3",
    answer=["D"],
    options=["$0$", "$1$", "发散", "$-1$"],
    expl="**答案依据**：$x=0$ 是瑕点。$\\int_0^1\\ln x\\,dx=\\lim\\limits_{\\varepsilon\\to0^+}\\left[x\\ln x-x\\right]_\\varepsilon^1=(0-1)-\\lim\\limits_{\\varepsilon\\to0^+}(\\varepsilon\\ln\\varepsilon-\\varepsilon)=-1-0=-1$（$\\varepsilon\\ln\\varepsilon\\to0$，见第 1 章）。积分收敛且值为 $-1$，D 正确。\n"
         "A 错：以为瑕点处被积函数趋于 $-\\infty$ 就一定发散。\n"
         "B 错：符号与数值均错。\n"
         "C 错：瑕积分是否发散要看具体极限，此处收敛。",
    mis="⚠️易错点：瑕积分先写极限定义再计算；$x\\ln x\\to0$（$x\\to0^+$）这一结果要当作已知结论使用。",
    tags=["反常积分", "困难"],
    verify=[{"desc": "integral", "code": "integrate(log(x), (x, 0, 1))", "expected": "-1"}]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "5.3",
    "下列关于对称区间 $[-a,a]$ 上定积分的等式，成立的有（其中 $f$ 为连续函数）",
    qid="c5-m1",
    answer=["A", "B", "C"],
    options=["若 $f$ 为奇函数，则 $\\int_{-a}^{a}f(x)\\,dx=0$",
             "若 $f$ 为偶函数，则 $\\int_{-a}^{a}f(x)\\,dx=2\\int_0^{a}f(x)\\,dx$",
             "$\\int_{-\\pi/2}^{\\pi/2}x^3\\cos x\\,dx=0$",
             "$\\int_{-1}^{1}|x|\\,dx=0$"],
    expl="**答案依据**：对称区间上奇偶函数的积分性质（§5.3 换元法推论）：奇函数积分为零、偶函数积分为半区间两倍，A、B 正确；$x^3\\cos x$ 是奇函数（奇 $\\times$ 偶），积分为零，C 正确。\n"
         "D 错：$|x|$ 是偶函数且非负，$\\int_{-1}^{1}|x|\\,dx=2\\int_0^1x\\,dx=1$。",
    mis="⚠️易错点：先用对称性化简再计算可大幅减负；判断奇偶要先化简结构（如 $x^3\\sin x$ 是偶函数）。",
    tags=["对称性", "高频考点"],
    verify=[{"desc": "D项反例", "code": "integrate(Abs(x), (x, -1, 1))", "expected": "1"}]))

Q_.append(Q(MULTI, "hard", "5.1",
    "关于定积分的存在性（可积性），下列说法正确的有",
    qid="c5-m2",
    answer=["A", "B", "D"],
    options=["在 $[a,b]$ 上连续的函数必可积",
             "在 $[a,b]$ 上可积的函数必有界",
             "在 $[a,b]$ 上有界的函数必可积",
             "在 $[a,b]$ 上单调的函数必可积"],
    expl="**答案依据**：可积的充分条件（§5.1）：连续函数可积、单调函数可积、只有有限个第一类间断点的函数可积，A、D 正确；可积函数必有界（无界函数的黎曼和可任意大），B 正确。\n"
         "C 错：有界不可积的反例是狄利克雷函数 $D(x)$（有理处取 1、无理处取 0），其黎曼和的极限不存在。",
    mis="⚠️易错点：「连续 $\\Rightarrow$ 可积 $\\Rightarrow$ 有界」是一条单向链，反向都不成立；可积函数可以有无穷多个间断点（只要「面积」上不集中）。",
    ext="引申：更精细的勒贝格判据——$[a,b]$ 上的有界函数可积 $\\iff$ 其间断点集是零测度集（黎曼可积）；狄利克雷函数处处间断故不可积，而黎曼函数只在可数个点间断故可积。",
    tags=["可积性", "困难"]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "5.2",
    "牛顿-莱布尼茨公式 $\\int_a^b f(x)\\,dx=F(b)-F(a)$ 成立的一个常见条件是：$f(x)$ 在 $[a,b]$ 上连续，$F(x)$ 是 $f(x)$ 在 $[a,b]$ 上的一个原函数。",
    qid="c5-j1",
    answer=["A"],
    expl="**答案依据**：教材叙述的牛顿-莱布尼茨公式以「$f$ 在 $[a,b]$ 上连续」为条件（§5.2；更一般的条件是 $f$ 可积且 $F$ 为原函数）。命题正确。",
    mis="⚠️易错点：被积函数在区间内有瑕点（无界）时不能直接套 N-L 公式，如 $\\int_{-1}^{1}\\dfrac{dx}{x^2}$——先检查连续性条件。",
    tags=["牛顿-莱布尼茨公式", "必背"]))

Q_.append(Q(JUDGE, "basic", "5.3",
    "$\\int_{-1}^{1}\\dfrac{dx}{x^2}=\\left[-\\dfrac{1}{x}\\right]_{-1}^{1}=-2$。",
    qid="c5-j2",
    answer=["B"],
    expl="**答案依据**：$x=0$ 是被积函数的瑕点（无界），不满足牛顿-莱布尼茨公式的连续性条件，不能直接套用。按瑕积分定义 $\\int_{-1}^{1}\\dfrac{dx}{x^2}=\\int_{-1}^{0}+\\int_{0}^{1}$，而 $\\int_0^1\\dfrac{dx}{x^2}=\\lim\\limits_{\\varepsilon\\to0^+}\\left[-\\dfrac1x\\right]_\\varepsilon^1=+\\infty$，发散。命题错误（§5.4）。",
    mis="⚠️易错点：定积分计算前先扫一眼区间内有无瑕点；「套公式得出负的面积」这类荒谬结果正是违规使用 N-L 的信号。",
    tags=["瑕积分", "易错点"]))

Q_.append(Q(JUDGE, "medium", "5.4",
    "反常积分 $\\int_0^{+\\infty}e^{-x}\\,dx$ 收敛。",
    qid="c5-j3",
    answer=["A"],
    expl="**答案依据**：$\\int_0^{+\\infty}e^{-x}dx=\\lim\\limits_{b\\to+\\infty}\\left[-e^{-x}\\right]_0^b=\\lim\\limits_{b\\to+\\infty}(1-e^{-b})=1$，收敛于 $1$。命题正确（§5.4）。",
    mis="⚠️易错点：指数衰减是反常积分收敛的典型；对照 $\\int_0^{+\\infty}e^{x}dx$ 发散，记住「$p$ 指数上正负一变，敛散全变」。",
    tags=["反常积分"],
    verify=[{"desc": "integral", "code": "integrate(exp(-x), (x, 0, oo))", "expected": "1"}]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "5.2",
    "$\\dfrac{d}{dx}\\displaystyle\\int_0^x t\\sin t\\,dt=$ ____。",
    qid="c5-b1",
    answer=["x*sin(x)"],
    accept=["xsinx", "x*sin(x)", "xsin(x)"],
    expl="**答案依据**：变上限积分求导定理（§5.2）：$\\dfrac{d}{dx}\\int_0^x f(t)dt=f(x)$，被积函数中 $t$ 换成 $x$ 即得 $x\\sin x$。",
    mis="⚠️易错点：上限恰是 $x$（不是 $x^2$ 等），直接代入即可，无需链式因子。",
    tags=["变上限积分"],
    verify=[{"desc": "求导", "code": "xx=symbols('xx'); simplify(diff(Integral(t*sin(t), (t, 0, xx)), xx) - xx*sin(xx))", "expected": "0"}]))

Q_.append(Q(BLANK, "medium", "5.3",
    "$\\displaystyle\\int_0^{\\pi/2}\\sin^2 x\\,dx=$ ____。",
    qid="c5-b2",
    answer=["pi/4"],
    accept=["pi/4", "π/4", "0.7853981633974483"],
    expl="**答案依据**：降幂公式 $\\sin^2x=\\dfrac{1-\\cos2x}{2}$，故 $\\int_0^{\\pi/2}\\sin^2x\\,dx=\\dfrac12\\left[x-\\dfrac{\\sin2x}{2}\\right]_0^{\\pi/2}=\\dfrac{\\pi}{4}$。\n"
         "**引申**：华里士（Wallis）公式 $\\int_0^{\\pi/2}\\sin^nx\\,dx=\\dfrac{n-1}{n}\\cdot\\dfrac{n-3}{n-2}\\cdots$，$n=2$ 时直接得 $\\dfrac12\\cdot\\dfrac\\pi2=\\dfrac\\pi4$。",
    mis="⚠️易错点：忘记 $\\sin2x$ 在 $0$ 与 $\\dfrac\\pi2$ 处都为 $0$，或降幂公式系数 $\\dfrac12$ 丢失。",
    ext="引申：华里士公式（点火公式）对 $\\int_0^{\\pi/2}\\sin^nx\\,dx$ 与 $\\cos^nx\\,dx$ 通用，是期末与考研的高频速算工具。",
    tags=["降幂公式", "华里士公式"],
    verify=[{"desc": "integral", "code": "integrate(sin(x)**2, (x, 0, pi/2))", "expected": "pi/4"}]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "5.1",
    "名词解释：定积分。",
    qid="c5-t1",
    answer_text="设 $f(x)$ 在 $[a,b]$ 上有界，在 $[a,b]$ 中任意插入分点并取 $\\xi_i\\in[x_{i-1},x_i]$，作和式 $\\sum_{i=1}^{n}f(\\xi_i)\\Delta x_i$；若当分割细度 $\\lambda=\\max\\Delta x_i\\to0$ 时此和式的极限存在（与分割方式及 $\\xi_i$ 的取法无关），则称 $f(x)$ 在 $[a,b]$ 上可积，该极限值称为 $f(x)$ 在 $[a,b]$ 上的定积分，记作 $\\int_a^b f(x)\\,dx$。",
    points=["定义核心：分割、取点、求和、取极限——$\\int_a^b f(x)dx=\\lim\\limits_{\\lambda\\to0}\\sum\\limits_{i=1}^n f(\\xi_i)\\Delta x_i$，极限须与分割和取点方式无关。",
            "几何意义与存在性：$f\\ge0$ 时表示曲边梯形面积；连续函数、单调函数、仅有有限个第一类间断点的函数都可积。"],
    expl="**答案依据**：定积分的「和式极限」定义与几何意义见 §5.1。\n"
         "**考点出处**：同济《高等数学》第七版 §5.1 定积分的概念与性质。",
    mis="⚠️易错点：定义中的 $\\lambda\\to0$ 是「最大子区间长度趋于零」，不能换成 $n\\to\\infty$（均匀分割加细才行）；定积分是数，与积分变量用什么字母无关。",
    tags=["定积分定义", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "5.2",
    "简答：叙述微积分基本定理（含变上限积分的原函数存在定理与牛顿-莱布尼茨公式）的内容，并说明其意义。",
    qid="c5-t2",
    answer_text="①原函数存在定理：若 $f(x)$ 在 $[a,b]$ 上连续，则 $\\Phi(x)=\\int_a^x f(t)\\,dt$ 在 $[a,b]$ 上可导，且 $\\Phi'(x)=f(x)$——连续函数必有原函数。②牛顿-莱布尼茨公式：若 $F(x)$ 是 $f(x)$ 在 $[a,b]$ 上的一个原函数，则 $\\int_a^b f(x)\\,dx=F(b)-F(a)$。意义：它揭示了微分与积分的互逆关系，把定积分计算归结为求原函数的函数值之差，使定积分从「求和式极限」变为可操作的运算。",
    points=["原函数存在定理：$f$ 连续时变上限积分 $\\Phi(x)=\\int_a^xf(t)dt$ 可导且 $\\Phi'=f$，即连续函数必有原函数。",
            "牛顿-莱布尼茨公式：$\\int_a^bf(x)dx=F(b)-F(a)$（$F$ 为任一原函数）。",
            "意义与前提：沟通微分学与积分学，把定积分计算化为「找原函数、代端点」；使用前提是 $f$ 在 $[a,b]$ 上连续（教材条件），有瑕点时须改用反常积分。"],
    expl="**答案依据**：两个定理的表述与意义见 §5.2。\n"
         "**考点出处**：同济《高等数学》第七版 §5.2 微积分基本公式。",
    mis="⚠️易错点：$\\Phi(x)=\\int_a^x f(t)dt$ 中 $\\Phi(a)=0$；「$\\Phi$ 是 $f$ 的原函数」与「$\\int_a^bf=F(b)-F(a)$」是两条定理，别混成一条。",
    tags=["微积分基本定理", "简答", "必背"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "5.3",
    "求 $\\displaystyle\\int_1^{e}\\dfrac{\\ln x}{x}\\,dx$。",
    qid="c5-c1",
    answer=["1/2"],
    answer_text="凑微分 $\\dfrac{dx}{x}=d(\\ln x)$：\n$$\\int_1^{e}\\frac{\\ln x}{x}dx=\\int_1^{e}\\ln x\\,d(\\ln x)=\\left[\\frac{\\ln^2x}{2}\\right]_1^{e}=\\frac{1}{2}.$$\n（$\\ln e=1$，$\\ln 1=0$。）",
    points=["凑微分 $\\dfrac{dx}{x}=d(\\ln x)$，把 $\\ln x$ 视为新变量。",
            "直接用幂函数积分 $\\int u\\,du=\\dfrac{u^2}{2}$。",
            "代端点：$\\dfrac{1^2}{2}-0=\\dfrac12$。",
            "说明：定积分的凑微分不必回代原变量，直接换上下限。"],
    expl="**答案依据**：定积分换元法「换元同时换限」（§5.3）。\n"
         "**考点出处**：同济《高等数学》第七版 §5.3 定积分的换元法。",
    tags=["凑微分", "高频考点"],
    verify=[{"desc": "integral", "code": "integrate(log(x)/x, (x, 1, E))", "expected": "1/2"}]))

Q_.append(Q(CALC, "medium", "5.3",
    "求 $\\displaystyle\\int_0^{\\pi/2}x\\sin x\\,dx$。",
    qid="c5-c2",
    answer=["1"],
    answer_text="分部积分：取 $u=x$、$dv=\\sin x\\,dx$（$v=-\\cos x$）：\n"
                "$$\\int_0^{\\pi/2}x\\sin x\\,dx=\\left[-x\\cos x\\right]_0^{\\pi/2}+\\int_0^{\\pi/2}\\cos x\\,dx=0+\\left[\\sin x\\right]_0^{\\pi/2}=1.$$\n"
                "（注意 $[-x\\cos x]_0^{\\pi/2}=0-0=0$。）",
    points=["幂函数 $x$ 取 $u$、三角部分凑 $dv=\\sin x\\,dx$，$v=-\\cos x$。",
            "代入 $uv-\\int v\\,du$ 得 $\\left[-x\\cos x\\right]_0^{\\pi/2}+\\int_0^{\\pi/2}\\cos x\\,dx$。",
            "边界项 $\\dfrac\\pi2\\cos\\dfrac\\pi2=0$，积分项 $\\left[\\sin x\\right]_0^{\\pi/2}=1$。",
            "结论：原积分 $=1$。"],
    expl="**答案依据**：定积分的分部积分法（§5.3），边界项与积分项分别代限。\n"
         "**考点出处**：同济《高等数学》第七版 §5.3 定积分的分部积分法。",
    tags=["分部积分", "高频考点"],
    verify=[{"desc": "integral", "code": "integrate(x*sin(x), (x, 0, pi/2))", "expected": "1"}]))

Q_.append(Q(CALC, "hard", "5.4",
    "求反常积分 $\\displaystyle\\int_0^{+\\infty}e^{-x}\\sin x\\,dx$。",
    qid="c5-c3",
    answer=["1/2"],
    answer_text="先求 $\\int e^{-x}\\sin x\\,dx$：分部两次（都取 $u=\\sin x/\\cos x$ 型三角函数）：\n"
                "$$\\int e^{-x}\\sin x\\,dx=-e^{-x}\\sin x+\\int e^{-x}\\cos x\\,dx=-e^{-x}\\sin x-e^{-x}\\cos x-\\int e^{-x}\\sin x\\,dx.$$\n"
                "移项解出\n$$\\int e^{-x}\\sin x\\,dx=-\\frac{e^{-x}(\\sin x+\\cos x)}{2}+C.$$\n"
                "代限：$\\lim\\limits_{b\\to+\\infty}\\left[-\\dfrac{e^{-x}(\\sin x+\\cos x)}{2}\\right]_0^{b}=0-\\left(-\\dfrac{1}{2}\\right)=\\dfrac{1}{2}$（$e^{-b}$ 有界振荡因子趋于零）。故积分收敛于 $\\dfrac12$。",
    points=["两次分部积分（三角函数均取 $u$，指数部分凑 $dv$），出现循环结构。",
            "移项解出 $\\int e^{-x}\\sin x\\,dx=-\\dfrac{e^{-x}(\\sin x+\\cos x)}{2}+C$。",
            "写成反常积分极限：$\\lim\\limits_{b\\to+\\infty}F(b)-F(0)$。",
            "由 $|e^{-b}(\\sin b+\\cos b)|\\le2e^{-b}\\to0$ 得极限为 $\\dfrac12$，说明收敛。"],
    expl="**答案依据**：反常积分与分部积分综合（§5.3、§5.4）。\n"
         "**考点出处**：同济《高等数学》第七版 §5.3、§5.4。",
    ext="引申：拉普拉斯变换表 $\\int_0^{+\\infty}e^{-sx}\\sin x\\,dx=\\dfrac{1}{s^2+1}$（$s>0$）是本题的一般化，在信号与系统中是基本结论。",
    tags=["反常积分", "分部积分", "困难"],
    verify=[{"desc": "integral", "code": "integrate(exp(-x)*sin(x), (x, 0, oo))", "expected": "1/2"}]))

Q = Q_
