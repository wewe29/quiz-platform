# -*- coding: utf-8 -*-
"""第4章 不定积分 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：4.1 不定积分的概念与性质 / 4.2 换元积分法 / 4.3 分部积分法 / 4.4 有理函数的积分
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "4.1",
    "下列等式中正确的是",
    qid="c4-s1",
    answer=["B"],
    options=["$\\int f'(x)\\,dx=f(x)$",
             "$\\dfrac{d}{dx}\\int f(x)\\,dx=f(x)$",
             "$\\int \\mathrm{d}f(x)=f(x)$",
             "$\\mathrm{d}\\int f(x)\\,dx=f(x)$"],
    expl="**答案依据**：不定积分与微分（求导）互为逆运算时的关系（§4.1）：先积分后求导恰好还原——$\\left(\\int f(x)\\,dx\\right)'=f(x)$，故 B 正确。\n"
         "A 错：$\\int f'(x)\\,dx=f(x)+C$，丢掉了任意常数 $C$。\n"
         "C 错：$\\int \\mathrm{d}f(x)=\\int f'(x)\\,dx=f(x)+C$，同样丢 $C$。\n"
         "D 错：先积分后微分得的是微分 $\\mathrm{d}\\left(\\int f\\,dx\\right)=f(x)\\,dx$，右边缺少 $\\,dx$。",
    mis="⚠️易错点：记准口诀「先积后导，恰好还原；先导后积，差个常数」——是否相差 $C$ 是这类判断题的唯一定盘星。",
    tags=["不定积分性质", "必背"]))

Q_.append(Q(SINGLE, "medium", "4.2",
    "$\\int\\dfrac{dx}{1+\\sqrt{x}}=$",
    qid="c4-s2",
    answer=["A"],
    options=["$2\\sqrt{x}-2\\ln(1+\\sqrt{x})+C$",
             "$2\\sqrt{x}+2\\ln(1+\\sqrt{x})+C$",
             "$\\sqrt{x}-\\ln(1+\\sqrt{x})+C$",
             "$2\\sqrt{x}-\\ln(1+2\\sqrt{x})+C$"],
    expl="**答案依据**：令 $t=\\sqrt{x}$（$x=t^2$，$dx=2t\\,dt$），\n"
         "$$\\int\\frac{2t\\,dt}{1+t}=\\int\\left(2-\\frac{2}{1+t}\\right)dt=2t-2\\ln(1+t)+C=2\\sqrt{x}-2\\ln(1+\\sqrt{x})+C,$$\n"
         "故 A 正确。\n"
         "B 错：拆分 $\\dfrac{2t}{1+t}=2-\\dfrac{2}{1+t}$ 时符号写错。\n"
         "C 错：换元后忘记 $dx=2t\\,dt$ 中的因子 $2t$。\n"
         "D 错：对数内系数处理错误，$\\int\\dfrac{2}{1+t}dt=2\\ln|1+t|$ 系数在真数之外。",
    mis="⚠️易错点：第二类换元必须把 $dx$ 一并换成 $t$ 的表达式（含雅可比因子），回代时别漏平方根的限定（$x\\ge0$）。",
    tags=["第二类换元", "高频考点"],
    verify=[{"desc": "求导还原", "code": "xx=symbols('xx', positive=True); F=2*sqrt(xx)-2*log(1+sqrt(xx)); simplify(diff(F,xx) - 1/(1+sqrt(xx)))", "expected": "0"}]))

Q_.append(Q(SINGLE, "hard", "4.3",
    "$\\int x^2 e^x\\,dx=$",
    qid="c4-s3",
    answer=["D"],
    options=["$e^x(x^2+2x+2)+C$",
             "$e^x(x^2-2x)+C$",
             "$e^x(x^2-x+1)+C$",
             "$e^x(x^2-2x+2)+C$"],
    expl="**答案依据**：分部积分两次（§4.3，幂函数优先进 $u$）：\n"
         "$$\\int x^2e^x dx=x^2e^x-\\int 2xe^x dx=x^2e^x-\\left(2xe^x-\\int 2e^x dx\\right)=e^x(x^2-2x+2)+C,$$\n"
         "故 D 正确。\n"
         "A 错：第二次分部时 $\\int 2xe^xdx=2xe^x-2e^x$ 的符号取反。\n"
         "B 错：漏掉了 $\\int 2e^xdx=2e^x$ 这最后一项。\n"
         "C 错：系数与项都错，是「感觉化」答案。",
    mis="⚠️易错点：分部两次后会出现「循环」结构 $\\int xe^xdx$，第二次结果要**整体代入**并整理符号；正负号连错是最常见丢分点。",
    ext="引申：$\\int P_n(x)e^{ax}dx$ 型总可经 $n$ 次分部化为 $e^{ax}\\left(P_n-\\frac{P_n'}{a}+\\frac{P_n''}{a^2}-\\cdots\\right)+C$；同理 $\\int P_n(x)\\sin ax\\,dx$、$\\int P_n(x)\\cos ax\\,dx$。",
    tags=["分部积分", "高频考点"],
    verify=[{"desc": "求导还原", "code": "simplify(diff(exp(x)*(x**2-2*x+2), x) - x**2*exp(x))", "expected": "0"}]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "4.1",
    "关于原函数与不定积分，下列说法正确的有",
    qid="c4-m1",
    answer=["A", "B"],
    options=["区间上的连续函数必有原函数",
             "若 $F(x)$ 是 $f(x)$ 的一个原函数，则 $\\int f(x)\\,dx=F(x)+C$",
             "任何函数都有原函数",
             "初等函数的原函数一定还是初等函数"],
    expl="**答案依据**：原函数存在定理：连续函数必有原函数（变上限积分 $\\int_a^x f(t)dt$ 就是一个，§4.1/§5.2），A 正确；不定积分定义为全体原函数 $F(x)+C$，B 正确。\n"
         "C 错：含第一类间断点的函数在含该点的区间上不存在原函数（导函数无第一类间断点）。\n"
         "D 错：初等函数的原函数可能「积不出来」，如 $e^{-x^2}$、$\\dfrac{\\sin x}{x}$ 的原函数不是初等函数。",
    mis="⚠️易错点：「连续 $\\Rightarrow$ 有原函数」，但「有原函数」不要求连续；「初等函数的原函数存在」与「原函数是初等函数」是两回事。",
    ext="引申：$\\dfrac{\\sin x}{x}$、$e^{-x^2}$、$\\dfrac{1}{\\ln x}$ 的原函数都存在但非初等，它们分别定义了正弦积分 $\\mathrm{Si}(x)$、误差函数 $\\mathrm{erf}(x)$ 与对数积分 $\\mathrm{li}(x)$ 等特殊函数。",
    tags=["原函数", "概念辨析"]))

Q_.append(Q(MULTI, "hard", "4.2",
    "设 $\\int f(x)\\,dx=F(x)+C$，则下列等式成立的有",
    qid="c4-m2",
    answer=["B", "C", "D"],
    options=["$\\int f(2x)\\,dx=F(2x)+C$",
             "$\\int f(\\sin x)\\cos x\\,dx=F(\\sin x)+C$",
             "$\\int xf(x)\\,dx=xF(x)-\\int F(x)\\,dx$",
             "$\\int \\dfrac{f(\\ln x)}{x}\\,dx=F(\\ln x)+C$"],
    expl="**答案依据**：B：凑微分 $\\cos x\\,dx=d(\\sin x)$，再用 $\\int f(u)du=F(u)+C$，正确。C：对 $\\int xf(x)dx$ 用分部积分（$u=x,\\ dv=f(x)dx$）：$xF(x)-\\int F(x)dx$，正确。D：凑微分 $\\dfrac{dx}{x}=d(\\ln x)$，正确。\n"
         "A 错：$\\int f(2x)dx=\\dfrac12F(2x)+C$——线性换元要除以内的系数，遗漏 $\\dfrac12$。",
    mis="⚠️易错点：凑微分口诀「内的导数乘出来」：被积函数必须恰含内函数的导数因子才能直接凑；差一个常数因子也不行。",
    tags=["换元积分", "凑微分", "困难"],
    verify=[{"desc": "C项核验(取f=cosx)", "code": "xx=symbols('xx'); simplify(integrate(xx*cos(xx), xx) - (xx*sin(xx)+cos(xx)))", "expected": "0"}]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "4.1",
    "若 $F'(x)=f(x)$，则 $\\int f(x)\\,dx=F(x)$。",
    qid="c4-j1",
    answer=["B"],
    expl="**答案依据**：不定积分是**全体**原函数，必须带任意常数：$\\int f(x)\\,dx=F(x)+C$。漏写 $C$ 是不定积分计算题最常见的格式错误。命题错误（§4.1）。",
    mis="⚠️易错点：$F(x)$ 只是「一个」原函数；$F(x)+C$ 才是「一族」原函数。特别地两个原函数之间只差常数。",
    tags=["不定积分", "必背"]))

Q_.append(Q(JUDGE, "basic", "4.2",
    "$\\int 2x e^{x^2}\\,dx=e^{x^2}+C$。",
    qid="c4-j2",
    answer=["A"],
    expl="**答案依据**：凑微分 $2x\\,dx=d(x^2)$，故 $\\int 2xe^{x^2}dx=\\int e^{x^2}d(x^2)=e^{x^2}+C$；求导验证 $\\left(e^{x^2}\\right)'=2xe^{x^2}$ 吻合。命题正确（§4.2）。",
    mis="⚠️易错点：看见 $x$ 与 $x^2$ 共存，先想 $d(x^2)$；$e^{x^2}$ 的原函数是初等的，而 $e^{-x^2}$ 不是——两题对比记忆。",
    tags=["凑微分", "第一类换元"]))

Q_.append(Q(JUDGE, "medium", "4.3",
    "用分部积分法时，按「反、对、幂、指、三」的顺序，排在前面的函数优先选作 $u$。",
    qid="c4-j3",
    answer=["A"],
    expl="**答案依据**：分部积分 $\\int u\\,dv=uv-\\int v\\,du$ 的效果取决于 $\\int v\\,du$ 是否更易积。「反三角、对数」求导后变简单，优先作 $u$；「指数、三角」求导后不变复杂，宜作 $dv$。「反对幂指三」口诀与 §4.3 的例题选取一致。命题正确。",
    mis="⚠️易错点：口诀只是经验法则，最终标准是「$\\int v\\,du$ 比原积分更简单」；如 $\\int xe^x dx$ 中 $x$ 是「幂」，按口诀作 $u$ 正确。",
    tags=["分部积分", "必背"]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "4.2",
    "$\\int \\tan x\\,dx=$ ____。",
    qid="c4-b1",
    answer=["-ln|cosx|+C"],
    accept=["-ln|cosx|+C", "ln|secx|+C", "-lncosx+C", "ln|sec(x)|+C"],
    expl="**答案依据**：$\\tan x=\\dfrac{\\sin x}{\\cos x}=-\\dfrac{d(\\cos x)}{\\cos x}$，故 $\\int\\tan x\\,dx=-\\ln|\\cos x|+C=\\ln|\\sec x|+C$（§4.2 例题）。两种形式等价。",
    mis="⚠️易错点：$\\cos x$ 取绝对值与负号——$\\ln$ 的真数必须为正；「割化弦」后 $\\sec x=1/\\cos x$ 的负号进入对数。",
    tags=["基本积分", "凑微分"]))

Q_.append(Q(BLANK, "medium", "4.2",
    "$\\int \\dfrac{\\ln x}{x}\\,dx=$ ____。",
    qid="c4-b2",
    answer=["(1/2)ln^2x+C"],
    accept=["(1/2)ln^2x+C", "0.5*ln(x)^2+C", "(ln^2x)/2+C", "1/2*ln(x)**2+C", "(1/2)(lnx)^2+C"],
    expl="**答案依据**：凑微分 $\\dfrac{dx}{x}=d(\\ln x)$，故 $\\int\\dfrac{\\ln x}{x}dx=\\int \\ln x\\,d(\\ln x)=\\dfrac{\\ln^2 x}{2}+C$（把 $\\ln x$ 整体当新变量，幂函数积分）。",
    mis="⚠️易错点：结果平方的是 $\\ln x$ 整体，写成 $\\dfrac12\\ln(x^2)$ 就错了；也可用分部积分验证。",
    tags=["凑微分"],
    verify=[{"desc": "求导还原", "code": "xx=symbols('xx', positive=True); F=log(xx)**2/2; simplify(diff(F,xx) - log(xx)/xx)", "expected": "0"}]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "4.1",
    "名词解释：原函数。",
    qid="c4-t1",
    answer_text="设 $f(x)$ 在区间 $I$ 上有定义，若存在 $F(x)$ 使得对 $I$ 上任意 $x$ 都有 $F'(x)=f(x)$（或 $dF(x)=f(x)dx$），则称 $F(x)$ 为 $f(x)$ 在区间 $I$ 上的一个原函数；$f$ 的全体原函数 $F(x)+C$ 称为 $f$ 的不定积分。",
    points=["定义：在区间 $I$ 上满足 $F'(x)=f(x)$ 的函数 $F(x)$ 称为 $f(x)$ 的一个原函数。",
            "结构：任意两个原函数只相差常数，故全体原函数为 $F(x)+C$，即不定积分 $\\int f(x)dx=F(x)+C$；连续函数必有原函数。"],
    expl="**答案依据**：原函数与不定积分的定义、原函数族结构定理见 §4.1。\n"
         "**考点出处**：同济《高等数学》第七版 §4.1 不定积分的概念与性质。",
    mis="⚠️易错点：原函数是「区间」上的概念——$\\ln|x|$ 分别在 $(-\\infty,0)$ 与 $(0,+\\infty)$ 上是 $\\dfrac1x$ 的原函数，两个区间上常数可以不同。",
    tags=["原函数", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "4.3",
    "简答：写出分部积分公式，说明它适用的题型类型与 $u$、$dv$ 的选取原则。",
    qid="c4-t2",
    answer_text="分部积分公式：$\\int u\\,dv=uv-\\int v\\,du$（由乘积求导法则 $(uv)'=u'v+uv'$ 移项积分而得）。适用类型：两类不同函数的乘积，典型如幂函数 $\\times$ 指数/三角（$\\int xe^xdx$、$\\int x\\cos xdx$）、幂函数 $\\times$ 对数/反三角（$\\int x\\ln xdx$、$\\int x\\arctan xdx$）以及 $\\int e^x\\sin xdx$ 等循环型。选取原则：按「反、对、幂、指、三」次序，排前者取 $u$，余者凑成 $dv$，目标是让 $\\int v\\,du$ 比原积分简单。",
    points=["公式及来源：$\\int u\\,dv=uv-\\int v\\,du$，由乘积求导法则移项、两边积分得到。",
            "适用题型：两类不同函数之积（幂×指/三、幂×对/反）与循环型（$e^x\\sin x$，分部两次后原式重现需移项解方程）。",
            "选取原则：「反对幂指三」排前者取 $u$（求导后变简单），余下部分凑 $dv$；判定标准是 $\\int v\\,du$ 更易积。"],
    expl="**答案依据**：分部积分公式、例题类型与 $u$ 的选取规则均见 §4.3。\n"
         "**考点出处**：同济《高等数学》第七版 §4.3 分部积分法。",
    mis="⚠️易错点：$dv$ 要连 $dx$ 一起凑；两次分部后第二次必须与第一次「同类型」地选 $u$（否则恒等还原、白忙一场）。",
    tags=["分部积分", "简答", "高频考点"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "4.2",
    "求 $\\int x\\cos x^2\\,dx$。",
    qid="c4-c1",
    answer=["(1/2)sin(x^2)+C"],
    answer_text="凑微分：$x\\,dx=\\dfrac12\\,d(x^2)$，故\n$$\\int x\\cos x^2\\,dx=\\frac12\\int\\cos(x^2)\\,d(x^2)=\\frac12\\sin(x^2)+C.$$\n验证：$\\left(\\dfrac12\\sin x^2\\right)'=\\dfrac12\\cos(x^2)\\cdot 2x=x\\cos x^2$。",
    points=["凑微分 $x\\,dx=\\dfrac12 d(x^2)$（内的导数乘出来）。",
            "视 $x^2$ 为新变量，用基本公式 $\\int\\cos u\\,du=\\sin u+C$。",
            "得 $\\dfrac12\\sin(x^2)+C$，并对结果求导验证。",
            "注意：$\\int\\cos x^2 dx$（无 $x$ 因子）才是积不出的非初等积分，勿混淆。"],
    expl="**答案依据**：第一类换元（凑微分）法，见 §4.2。\n"
         "**考点出处**：同济《高等数学》第七版 §4.2 换元积分法。",
    tags=["凑微分", "高频考点"],
    verify=[{"desc": "积分", "code": "integrate(x*cos(x**2), x)", "expected": "sin(x**2)/2"}]))

Q_.append(Q(CALC, "medium", "4.3",
    "求 $\\int x\\ln x\\,dx$。",
    qid="c4-c2",
    answer=["(x^2/2)lnx-x^2/4+C"],
    answer_text="按「反对幂指三」取 $u=\\ln x$，$dv=x\\,dx$（$v=\\dfrac{x^2}{2}$）：\n"
                "$$\\int x\\ln x\\,dx=\\frac{x^2}{2}\\ln x-\\int\\frac{x^2}{2}\\cdot\\frac1x\\,dx=\\frac{x^2}{2}\\ln x-\\frac12\\int x\\,dx=\\frac{x^2}{2}\\ln x-\\frac{x^2}{4}+C.$$\n"
                "验证：求导得 $x\\ln x+\\dfrac{x}{2}-\\dfrac{x}{2}=x\\ln x$。",
    points=["选 $u=\\ln x$、$dv=x\\,dx$，则 $du=\\dfrac{dx}{x}$、$v=\\dfrac{x^2}{2}$。",
            "代入公式 $uv-\\int v\\,du$ 得 $\\dfrac{x^2}{2}\\ln x-\\dfrac12\\int x\\,dx$。",
            "算出 $\\dfrac{x^2}{2}\\ln x-\\dfrac{x^2}{4}+C$。",
            "求导验证最终结果。"],
    expl="**答案依据**：分部积分法标准例题（§4.3 中 $\\int x\\ln x dx$ 同型）。\n"
         "**考点出处**：同济《高等数学》第七版 §4.3 分部积分法。",
    tags=["分部积分", "高频考点"],
    verify=[{"desc": "积分", "code": "integrate(x*log(x), x)", "expected": "x**2*log(x)/2 - x**2/4"}]))

Q_.append(Q(CALC, "hard", "4.4",
    "求 $\\int \\dfrac{dx}{1+e^x}$。",
    qid="c4-c3",
    answer=["x-ln(1+e^x)+C"],
    answer_text="法一（凑项拆分）：分子分母同乘 $e^{-x}$：\n$$\\int\\frac{dx}{1+e^x}=\\int\\frac{e^{-x}}{1+e^{-x}}\\,dx=-\\int\\frac{d(1+e^{-x})}{1+e^{-x}}=-\\ln(1+e^{-x})+C,$$\n"
                "再化简：$-\\ln(1+e^{-x})=x-\\ln(1+e^x)$（提出 $e^{-x}$：$1+e^{-x}=e^{-x}(1+e^x)$）。\n"
                "法二（部分分式）：令 $t=e^x$，$\\dfrac{1}{1+t}=1-\\dfrac{t}{1+t}$，积分后回代同样得 $x-\\ln(1+e^x)+C$。\n"
                "验证：$\\left[x-\\ln(1+e^x)\\right]'=1-\\dfrac{e^x}{1+e^x}=\\dfrac{1}{1+e^x}$。",
    points=["思路一：分子分母同乘 $e^{-x}$，凑微分 $-d(1+e^{-x})$。",
            "积分得 $-\\ln(1+e^{-x})+C$，并利用 $1+e^{-x}=e^{-x}(1+e^x)$ 化简为 $x-\\ln(1+e^x)+C$。",
            "思路二：令 $t=e^x$ 化为有理函数积分 $\\int\\dfrac{dt}{t(1+t)}$，用部分分式 $\\dfrac1{t(1+t)}=\\dfrac1t-\\dfrac1{1+t}$。",
            "求导验证：$1-\\dfrac{e^x}{1+e^x}=\\dfrac{1}{1+e^x}$。"],
    expl="**答案依据**：指数函数有理式的积分是 §4.4 有理函数积分与 §4.2 换元法的综合例题。\n"
         "**考点出处**：同济《高等数学》第七版 §4.2、§4.4。",
    mis="⚠️易错点：化简 $-\\ln(1+e^{-x})$ 时提出 $e^{-x}$ 后对数外要**补回 $+x$**（$-\\ln e^{-x}=+x$），这一步最易丢；部分分式 $\\dfrac{1}{t(1+t)}$ 的拆分系数也易错。",
    tags=["有理函数", "综合", "困难"],
    verify=[{"desc": "积分", "code": "integrate(1/(1+exp(x)), x)", "expected": "x - log(exp(x) + 1)"},
             {"desc": "求导还原", "code": "simplify(diff(x-log(1+exp(x)), x) - 1/(1+exp(x)))", "expected": "0"}]))

Q = Q_
