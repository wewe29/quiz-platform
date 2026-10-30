# -*- coding: utf-8 -*-
"""第11章 曲线积分与曲面积分 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：11.1 对弧长的曲线积分 / 11.2 对坐标的曲线积分 / 11.3 格林公式及其应用
        11.4 对面积的曲面积分 / 11.5 对坐标的曲面积分 / 11.6 高斯公式
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "11.1",
    "$\\displaystyle\\oint_L x\\,\\mathrm{d}s=$，其中 $L$ 为圆周 $x^2+y^2=1$",
    qid="c11-s1",
    answer=["A"],
    options=["$0$", "$\\pi$", "$2\\pi$", "$1$"],
    expl="**答案依据**：第一类曲线积分利用对称性（§11.1）：积分曲线关于 $y$ 轴对称，被积函数 $x$ 关于 $x$ 为奇函数，故积分为 $0$，A 正确。\n"
         "B、C 错：是 $\\oint_L \\mathrm{d}s=2\\pi$（周长）及其中一半的混淆。\n"
         "D 错：无依据。",
    mis="⚠️易错点：第一类曲线积分的对称性与二重积分类似——「域对称 + 函数奇」才为零；参数法 $x=\\cos t$ 亦可验证 $\\int_0^{2\\pi}\\cos t\\,dt=0$。",
    tags=["第一类曲线积分", "对称性"]))

Q_.append(Q(SINGLE, "medium", "11.3",
    "$L$ 为圆周 $x^2+y^2=1$ 取正向（逆时针），则 $\\displaystyle\\oint_L x\\,\\mathrm{d}y-y\\,\\mathrm{d}x=$",
    qid="c11-s2",
    answer=["B"],
    options=["$\\pi$", "$2\\pi$", "$0$", "$4\\pi$"],
    expl="**答案依据**：格林公式（§11.3）：$P=-y$，$Q=x$，$\\dfrac{\\partial Q}{\\partial x}-\\dfrac{\\partial P}{\\partial y}=1-(-1)=2$，故\n"
         "$$\\oint_L x\\,dy-y\\,dx=\\iint_D 2\\,\\mathrm{d}\\sigma=2\\cdot\\pi=2\\pi,$$\n"
         "B 正确（也可由参数方程 $x=\\cos t,y=\\sin t$ 直接积分）。\n"
         "A 错：漏了因子 $2$（相当于只算了 $\\dfrac12\\oint x\\,dy-y\\,dx$，那才是面积）。\n"
         "C 错：把积分误判为奇对称零——第二类曲线积分与方向有关，不能用这种对称性。\n"
         "D 错：面积算成了 $2\\pi$。",
    mis="⚠️易错点：$\\dfrac{1}{2}\\oint_L x\\,dy-y\\,dx=A$ 是用曲线积分求面积的公式，本题乘 $2$ 得 $2\\pi$；方向取反向时结果变号。",
    tags=["格林公式", "高频考点"],
    verify=[{"desc": "integral", "code": "tt=symbols('tt'); I=integrate(cos(tt)**2 + sin(tt)**2, (tt, 0, 2*pi)); simplify(I - 2*pi)", "expected": "0"}]))

Q_.append(Q(SINGLE, "hard", "11.6",
    "用高斯公式计算曲面积分 $\\displaystyle\\oiint_\\Sigma x\\,\\mathrm{d}y\\mathrm{d}z+y\\,\\mathrm{d}z\\mathrm{d}x+z\\,\\mathrm{d}x\\mathrm{d}y$，其中 $\\Sigma$ 为球面 $x^2+y^2+z^2=a^2$ 的外侧，其值为",
    qid="c11-s3",
    answer=["A"],
    options=["$4\\pi a^3$", "$\\dfrac{4}{3}\\pi a^3$", "$\\pi a^3$", "$12\\pi a^3$"],
    expl="**答案依据**：高斯公式（§11.6）：$P=x,Q=y,R=z$，$\\dfrac{\\partial P}{\\partial x}+\\dfrac{\\partial Q}{\\partial y}+\\dfrac{\\partial R}{\\partial z}=3$，故原积分 $=\\displaystyle\\iiint_\\Omega 3\\,dV=3\\cdot\\dfrac43\\pi a^3=4\\pi a^3$，A 正确。\n"
         "B 错：球体体积没乘 $3$。\n"
         "C 错：三重积分算错。\n"
         "D 错：把 $\\dfrac{4}{3}$ 处理成了 $4$。",
    mis="⚠️易错点：高斯公式要求曲面**封闭且取外侧**；若取内侧须变号；不封闭时先补面再减去补面上的积分。",
    ext="引申：$\\dfrac{1}{3}\\oiint_\\Sigma x\\,dy\\,dz+y\\,\\,dz\\,dx+z\\,dx\\,dy=V$ 是用曲面积分求体积的公式（与格林公式求面积 $\\dfrac12\\oint x\\,dy-y\\,dx$ 对应）。",
    tags=["高斯公式", "困难", "高频考点"],
    verify=[{"desc": "高斯核验", "code": "aa=symbols('aa', positive=True); simplify(3*Rational(4,3)*pi*aa**3 - 4*pi*aa**3)", "expected": "0"}]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "11.3",
    "关于格林公式 $\\displaystyle\\oint_L P\\,dx+Q\\,dy=\\iint_D\\left(\\frac{\\partial Q}{\\partial x}-\\frac{\\partial P}{\\partial y}\\right)\\mathrm{d}\\sigma$，下列说法正确的有",
    qid="c11-m1",
    answer=["A", "B", "C"],
    options=["$L$ 必须是闭区域 $D$ 的**正向**边界曲线",
             "要求 $P(x,y)$、$Q(x,y)$ 在 $D$ 上具有一阶连续偏导数",
             "对非闭曲线，可添加辅助线使其封闭后使用格林公式",
             "对任意平面曲线（无论是否封闭）公式均成立"],
    expl="**答案依据**：格林公式的两个条件——$L$ 取正向边界、$P,Q$ 在 $D$ 上有一阶连续偏导（§11.3），A、B 正确；处理非闭曲线时「补线法」是标准技巧（补上从终点回起点的线段，用公式后减去补线上的积分），C 正确。\n"
         "D 错：曲线不封闭时没有「内部区域 $D$」，公式无从谈起。",
    mis="⚠️易错点：正向 = 沿该方向行走时区域 $D$ 始终在**左侧**；复连通区域的边界内圈要取顺时针。",
    tags=["格林公式", "必背"]))

Q_.append(Q(MULTI, "hard", "11.5",
    "关于两类曲面积分与高斯公式，下列说法正确的有",
    qid="c11-m2",
    answer=["A", "B", "C"],
    options=["第二类曲面积分（对坐标）与曲面所取的侧有关",
             "使用高斯公式要求闭曲面取外侧（内侧时公式差一个负号）",
             "$\\displaystyle\\oiint_\\Sigma z\\,\\mathrm{d}x\\mathrm{d}y=\\iiint_\\Omega\\mathrm{d}V=V_\\Omega$（$\\Sigma$ 为 $\\Omega$ 的边界外侧）",
             "第一类曲面积分（对面积）与曲面的侧有关"],
    expl="**答案依据**：第二类曲面积分的定向依赖性（§11.5）与高斯公式的侧向要求（§11.6），A、B 正确；由高斯公式 $\\dfrac{\\partial z}{\\partial z}=1$，积分等于区域体积，C 正确。\n"
         "D 错：第一类曲面积分定义在「面密度」型量上，与侧（方向）无关；换侧不改变其值。",
    mis="⚠️易错点：「第一类与侧无关、第二类与侧有关（换侧变号）」；两类曲面积分通过投影公式互相转化时，方向余弦的符号由侧决定。",
    tags=["曲面积分", "侧", "困难"]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "11.1",
    "第一类曲线积分（对弧长）$\\displaystyle\\int_L f(x,y)\\,\\mathrm{d}s$ 的值与曲线 $L$ 的方向无关。",
    qid="c11-j1",
    answer=["A"],
    expl="**答案依据**：第一类曲线积分以弧长 $ds$ 为元素，$ds$ 恒正、与走向无关，故 $\\int_{\\widehat{AB}}f\\,ds=\\int_{\\widehat{BA}}f\\,ds$（§11.1）。命题正确。这与第二类曲线积分（换方向变号）形成对照。",
    mis="⚠️易错点：两类曲线积分的方向依赖性正好相反——第一类无关、第二类反号。",
    tags=["第一类曲线积分", "必背"]))

Q_.append(Q(JUDGE, "basic", "11.3",
    "沿任何平面闭曲线的第二类曲线积分 $\\displaystyle\\oint_L P\\,dx+Q\\,dy$ 恒为零。",
    qid="c11-j2",
    answer=["B"],
    expl="**答案依据**：闭曲线积分为零需要「$\\dfrac{\\partial Q}{\\partial x}=\\dfrac{\\partial P}{\\partial y}$ 在 $D$ 内恒成立（单连通）」的条件。反例：$\\oint x\\,dy-y\\,dx=2A\\ne0$（$A$ 为所围面积）。命题错误（§11.3）。",
    mis="⚠️易错点：「积分与路径无关 $\\iff$ 闭曲线积分为零 $\\iff$ $Q_x=P_y$」都要求单连通区域 + 偏导连续；含奇点（如 $\\dfrac{1}{x^2+y^2}$ 型）时闭曲线包围奇点则不为零。",
    ext="引申：$\\displaystyle\\oint_L\\dfrac{x\\,dy-y\\,dx}{x^2+y^2}$ 沿包含原点的闭曲线恒为 $2\\pi$——原点是奇点，单连通条件被破坏，格林公式不能直接用。",
    tags=["路径无关", "易错点"]))

Q_.append(Q(JUDGE, "medium", "11.3",
    "格林公式中边界曲线的「正向」是指：沿该方向前进时，区域 $D$ 总在行进方向的左侧。",
    qid="c11-j3",
    answer=["A"],
    expl="**答案依据**：单连通区域正向边界的定义即「左侧规则」（外边界逆时针）；复连通区域中内边界取顺时针才能保证 $D$ 在左侧（§11.3）。命题正确。",
    mis="⚠️易错点：复连通区域的外圈与内圈方向相反，否则公式差符号；用「左手边」判断比死记逆/顺时针更可靠。",
    tags=["格林公式", "正向边界"]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "11.1",
    "$\\displaystyle\\int_L \\mathrm{d}s=$，其中 $L$ 为线段 $y=x$（$0\\le x\\le1$）：其值为 ____。",
    qid="c11-b1",
    answer=["sqrt(2)"],
    accept=["sqrt(2)", "√2", "1.4142135623730951", "根号2"],
    expl="**答案依据**：$\\int_L ds$ 就是曲线的弧长。$ds=\\sqrt{1+y‘^2}\\,dx=\\sqrt2\\,dx$，故值为 $\\sqrt2$（§11.1，弧长公式）。",
    mis="⚠️易错点：线段长可直接用两点距离 $\\sqrt{1^2+1^2}$ 验证。",
    tags=["弧长"]))

Q_.append(Q(BLANK, "medium", "11.3",
    "$L$ 为圆周 $x^2+y^2=1$ 取正向，则 $\\displaystyle\\oint_L y\\,\\mathrm{d}x-x\\,\\mathrm{d}y=$ ____。",
    qid="c11-b2",
    answer=["-2*pi"],
    accept=["-2pi", "-2*pi", "-2π", "-6.283185307179586"],
    expl="**答案依据**：格林公式：$P=y$，$Q=-x$，$Q_x-P_y=-1-1=-2$，积分 $=\\displaystyle\\iint_D(-2)d\\sigma=-2\\pi$（§11.3）。本题与 $\\oint x\\,dy-y\\,dx=2\\pi$ 恰差一个符号。",
    mis="⚠️易错点：$Q_x-P_y$ 的次序别写反；本题曲线是顺时针效果（相对上题），答案为负。",
    tags=["格林公式", "高频考点"],
    verify=[{"desc": "integral", "code": "tt=symbols('tt'); I=integrate(sin(tt)*(-sin(tt))-cos(tt)*cos(tt), (tt, 0, 2*pi)); simplify(I - (-2*pi))", "expected": "0"}]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "11.2",
    "名词解释：对坐标的曲线积分（第二类曲线积分）。",
    qid="c11-t1",
    answer_text="设 $L$ 为 $xOy$ 面上从 $A$ 到 $B$ 的有向光滑曲线，$P(x,y)$、$Q(x,y)$ 在 $L$ 上有界。将 $L$ 任意分割，记有向小弧段在 $x$ 轴、$y$ 轴上的投影近似分别为 $\\Delta x_i$、$\\Delta y_i$，作和 $\\sum\\left[P(\\xi_i,\\eta_i)\\Delta x_i+Q(\\xi_i,\\eta_i)\\Delta y_i\\right]$，若极限存在则称为 $P$、$Q$ 沿 $L$ 对坐标的曲线积分，记作 $\\displaystyle\\int_L P\\,dx+Q\\,dy$。它表示变力沿曲线做功等「方向性」量，交换曲线方向则积分变号。",
    points=["定义：在有向曲线上对坐标增量 $dx$、$dy$ 分别配权 $P,Q$ 作和取极限，$\\int_L Pdx+Qdy$。",
            "性质与意义：方向性——$\\int_{L^-}=-\\int_{L^+}$；物理意义为变力沿曲线做的功；两类曲线积分的联系 $\\int_L Pdx+Qdy=\\int_L(P\\cos\\alpha+Q\\cos\\beta)ds$。"],
    expl="**答案依据**：第二类曲线积分的定义、方向性与物理意义见 §11.2。\n"
         "**考点出处**：同济《高等数学》第七版 §11.2 对坐标的曲线积分。",
    mis="⚠️易错点：与第一类（对弧长）积分的区别在于「有没有方向」；参数化计算时积分下限对应曲线**起点**，上限对应**终点**（可以下限大于上限）。",
    tags=["第二类曲线积分", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "11.3",
    "简答：叙述格林公式的内容与条件，并说明它的两类典型应用。",
    qid="c11-t2",
    answer_text="内容：设闭区域 $D$ 由分段光滑的闭曲线 $L$ 围成，$P(x,y)$、$Q(x,y)$ 在 $D$ 上具有一阶连续偏导数，则有 $\\displaystyle\\oint_L P\\,dx+Q\\,dy=\\iint_D\\left(\\dfrac{\\partial Q}{\\partial x}-\\dfrac{\\partial P}{\\partial y}\\right)\\mathrm{d}\\sigma$，其中 $L$ 取正向。应用：①闭曲线或补线后的曲线积分化成二重积分计算；②取 $P=-y,Q=x$（或 $P=0,Q=x$ 等）得面积公式 $A=\\dfrac12\\oint_L x\\,dy-y\\,dx=\\oint_L x\\,dy=-\\oint_L y\\,dx$。",
    points=["条件：$D$ 由分段光滑闭曲线围成，$P,Q$ 在 $D$ 上一阶偏导连续，$L$ 取正向（外圈逆时针、内圈顺时针）；结论 $\\oint_LP\\,dx+Q\\,dy=\\iint_D(Q_x-P_y)\\,d\\sigma$。",
            "应用一：闭曲线（或补线）积分化为二重积分，特别是 $Q_x-P_y$ 为常数时。",
            "应用二：面积公式 $A=\\dfrac12\\oint_Lx\\,dy-y\\,dx$；路径无关的判定 $Q_x=P_y$（单连通）也源于此。"],
    expl="**答案依据**：格林公式的叙述、条件与面积公式均见 §11.3。\n"
         "**考点出处**：同济《高等数学》第七版 §11.3 格林公式及其应用。",
    mis="⚠️易错点：用面积公式时 $L$ 必须取正向，否则面积为负；复连通区域每个边界圈都要算入。",
    tags=["格林公式", "简答", "高频考点"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "11.1",
    "计算 $\\displaystyle\\int_L (x^2+y^2)\\,\\mathrm{d}s$，其中 $L$ 为上半圆周 $x^2+y^2=1$（$y\\ge0$）。",
    qid="c11-c1",
    answer=["pi"],
    answer_text="在 $L$ 上 $x^2+y^2=1$（被积函数可先化简），弧长元素 $ds=\\mathrm{d}t$ 对应参数 $t\\in[0,\\pi]$（$x=\\cos t,\\ y=\\sin t$，$ds=dt$）：\n"
                "$$\\int_L (x^2+y^2)\\,ds=\\int_0^{\\pi}1\\cdot\\mathrm{d}t=\\pi.$$\n"
                "（本质即上半圆的周长 $\\pi$，因为被积函数在曲线上恒为 $1$。）",
    points=["曲线方程代入化简：$x^2+y^2=1$ 在 $L$ 上恒成立。",
            "参数化 $x=\\cos t,\\ y=\\sin t$（$0\\le t\\le\\pi$），$ds=dt$。",
            "积分 $\\int_0^\\pi dt=\\pi$。",
            "说明：第一类曲线积分可将曲线方程代入被积函数「降维」。"],
    expl="**答案依据**：第一类曲线积分的计算法（曲线方程可代入被积函数，§11.1）。\n"
         "**考点出处**：同济《高等数学》第七版 §11.1 对弧长的曲线积分。",
    tags=["第一类曲线积分", "高频考点"],
    verify=[{"desc": "integral", "code": "tt=symbols('tt'); integrate(1, (tt, 0, pi))", "expected": "pi"}]))

Q_.append(Q(CALC, "medium", "11.2",
    "计算 $\\displaystyle\\int_L 2xy\\,\\mathrm{d}x+x^2\\,\\mathrm{d}y$，其中 $L$ 为抛物线 $y=x^2$ 上从 $(0,0)$ 到 $(1,1)$ 的一段。",
    qid="c11-c2",
    answer=["1"],
    answer_text="以 $x$ 为参数：$y=x^2$，$dy=2x\\,dx$，$x$ 从 $0$ 到 $1$：\n"
                "$$\\int_0^1\\left[2x\\cdot x^2+x^2\\cdot 2x\\right]dx=\\int_0^1 4x^3\\,dx=\\left[x^4\\right]_0^1=1.$$\n"
                "（另法：$2xy\\,dx+x^2\\,dy=\\mathrm{d}(x^2y)$ 是全微分，积分值 = 端点函数值差 $1^2\\cdot1-0=1$，与路径无关。）",
    points=["参数化：$y=x^2$、$dy=2x\\,dx$，化为对 $x$ 的定积分。",
            "被积函数合并为 $4x^3$，积得 $1$。",
            "识别全微分 $d(x^2y)$，用端点值差核验结果。",
            "第二类曲线积分下限对应起点参数 $0$、上限对应终点参数 $1$。"],
    expl="**答案依据**：对坐标的曲线积分的参数计算法与全微分判别（§11.2，结合 §11.3 路径无关）。\n"
         "**考点出处**：同济《高等数学》第七版 §11.2、§11.3。",
    tags=["第二类曲线积分", "高频考点"],
    verify=[{"desc": "integral", "code": "integrate(2*x*x**2 + x**2*2*x, (x, 0, 1))", "expected": "1"}]))

Q_.append(Q(CALC, "hard", "11.3",
    "计算 $\\displaystyle\\oint_L (e^x\\sin y-y)\\,\\mathrm{d}x+(e^x\\cos y-1)\\,\\mathrm{d}y$，其中 $L$ 为上半圆周 $x^2+y^2=1$（$y\\ge0$）与直线段 $y=0$（$-1\\le x\\le1$）围成的闭曲线，取逆时针方向。",
    qid="c11-c3",
    answer=["pi/2"],
    answer_text="记 $P=e^x\\sin y-y$，$Q=e^x\\cos y-1$，则 $\\dfrac{\\partial Q}{\\partial x}=e^x\\cos y$，$\\dfrac{\\partial P}{\\partial y}=e^x\\cos y-1$，\n"
                "$$\\frac{\\partial Q}{\\partial x}-\\frac{\\partial P}{\\partial y}=1.$$\n"
                "由格林公式（$L$ 正向，$D$ 为上半圆盘）：\n"
                "$$\\oint_LP\\,dx+Q\\,dy=\\iint_D 1\\,\\mathrm{d}\\sigma=\\frac{1}{2}\\pi\\cdot1^2=\\frac{\\pi}{2}.$$\n",
    points=["计算 $Q_x=e^x\\cos y$、$P_y=e^x\\cos y-1$，相减得常数 $1$。",
            "识别 $L$ 为上半圆盘的正向边界，应用格林公式。",
            "$\\displaystyle\\iint_Dd\\sigma=$ 上半圆面积 $=\\dfrac\\pi2$。",
            "说明本题妙处：$e^x\\sin y$、$e^x\\cos y$ 的偏导恰好相消，只剩 $-y$ 与 $-1$ 的贡献。"],
    expl="**答案依据**：格林公式对含指数三角混合被积函数的应用（§11.3 经典例题）。\n"
         "**考点出处**：同济《高等数学》第七版 §11.3 格林公式及其应用。",
    mis="⚠️易错点：$P_y$ 中 $\\sin y$ 求导为 $\\cos y$、常数 $-y$ 求导为 $-1$，两项都要算；若曲线不闭，须先补 $x$ 轴上的直径段（补线上的积分常因 $y=0$ 而为零，本题恰属此类）。",
    tags=["格林公式", "困难", "高频考点"],
    verify=[{"desc": "integral", "code": "xx,yy=symbols('xx yy'); P=exp(xx)*sin(yy)-yy; Q=exp(xx)*cos(yy)-1; integrate(integrate(diff(Q,xx)-diff(P,yy), (yy, 0, sqrt(1-xx**2))), (xx, -1, 1))", "expected": "pi/2"}]))

Q = Q_
