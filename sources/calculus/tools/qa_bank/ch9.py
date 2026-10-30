# -*- coding: utf-8 -*-
"""第9章 多元函数微分法及其应用 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：9.1 多元函数的基本概念 / 9.2 偏导数 / 9.3 全微分 / 9.4 多元复合函数的求导法则
        9.5 隐函数的求导公式 / 9.7 方向导数与梯度 / 9.8 多元函数的极值及其求法
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "9.2",
    "设 $z=x^2y+\\sin(xy)$，则 $\\dfrac{\\partial z}{\\partial x}=$",
    qid="c9-s1",
    answer=["A"],
    options=["$2xy+y\\cos(xy)$", "$x^2+y\\cos(xy)$", "$2xy-y\\cos(xy)$", "$x^2y+y\\cos(xy)$"],
    expl="**答案依据**：对 $x$ 求偏导时把 $y$ 视为常数（§9.2）：$\\dfrac{\\partial}{\\partial x}(x^2y)=2xy$；$\\dfrac{\\partial}{\\partial x}\\sin(xy)=\\cos(xy)\\cdot y$。故 $\\dfrac{\\partial z}{\\partial x}=2xy+y\\cos(xy)$，A 正确。\n"
         "B 错：第一项对 $x$ 求导出错。\n"
         "C 错：链式因子符号弄反。\n"
         "D 错：第一项未求导。",
    mis="⚠️易错点：偏导数「只对 $x$ 求、$y$ 冻结」，但 $\\sin(xy)$ 内的 $y$ 冻结后仍有系数 $y$ 作为链式因子。",
    tags=["偏导数", "高频考点"]))

Q_.append(Q(SINGLE, "medium", "9.4",
    "设 $z=f(u,v)$ 可微，$u=x^2-y^2$，$v=xy$，则 $\\dfrac{\\partial z}{\\partial x}=$",
    qid="c9-s2",
    answer=["B"],
    options=["$2x\\dfrac{\\partial f}{\\partial u}-2y\\dfrac{\\partial f}{\\partial v}$",
             "$2x\\dfrac{\\partial f}{\\partial u}+y\\dfrac{\\partial f}{\\partial v}$",
             "$2x\\dfrac{\\partial f}{\\partial u}+x\\dfrac{\\partial f}{\\partial v}$",
             "$\\dfrac{\\partial f}{\\partial u}\\cdot 2x\\cdot\\dfrac{\\partial f}{\\partial v}\\cdot y$"],
    expl="**答案依据**：链式法则（§9.4）：$\\dfrac{\\partial z}{\\partial x}=\\dfrac{\\partial z}{\\partial u}\\cdot\\dfrac{\\partial u}{\\partial x}+\\dfrac{\\partial z}{\\partial v}\\cdot\\dfrac{\\partial v}{\\partial x}$。其中 $\\dfrac{\\partial u}{\\partial x}=2x$，$\\dfrac{\\partial v}{\\partial x}=y$，故 $\\dfrac{\\partial z}{\\partial x}=2xf_u+yf_v$，B 正确。\n"
         "A 错：把 $v$ 对 $x$ 的偏导误为 $-2y$（那是 $u$ 对 $y$ 的导数）。\n"
         "C 错：$v=xy$ 对 $x$ 求导得 $y$ 不是 $x$。\n"
         "D 错：把「链式相加」写成了「相乘」。",
    mis="⚠️易错点：画链式图「$z$ 分叉到 $u,v$、各自连到 $x$」——分线相加、沿线相乘；$u=x^2-y^2$ 对 $y$ 的导数才是 $-2y$。",
    tags=["链式法则", "高频考点"]))

Q_.append(Q(SINGLE, "hard", "9.3",
    "二元函数 $z=f(x,y)$ 在点 $(x_0,y_0)$ 处可微的一个**充分**条件是",
    qid="c9-s3",
    answer=["C"],
    options=["$f$ 在该点连续",
             "$f$ 在该点的两个偏导数都存在",
             "$f$ 的两个偏导数在该点的某邻域内存在且在该点连续",
             "$f$ 在该点沿任意方向的方向导数都存在"],
    expl="**答案依据**：可微的充分条件（§9.3 定理）：偏导数存在且连续 $\\Rightarrow$ 可微，C 正确。\n"
         "A 错：连续推不出可微（一元、二元皆然）。\n"
         "B 错：偏导存在推不出可微，经典反例 $f(x,y)=\\dfrac{xy}{x^2+y^2}$（补充定义 $f(0,0)=0$）在原点两个偏导均为 $0$ 但不连续，更不可微。\n"
         "D 错：方向导数都存在也推不出可微（同上反例沿坐标轴方向导数存在）。",
    mis="⚠️易错点：二元函数中「偏导存在」是比一元「导数存在」弱得多的条件——只涉及两条坐标线上的信息；可微才能保证各方向导数存在且 $d z=f_xdx+f_ydy$。",
    ext="引申：可微的充要条件是 $\\Delta z-[f_x\\Delta x+f_y\\Delta y]=o(\\rho)$（$\\rho=\\sqrt{\\Delta x^2+\\Delta y^2}$），判定可微直接用它，比「偏导连续」更本质（那只是充分条件）。",
    tags=["可微性", "充分条件", "高频考点", "困难"]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "9.3",
    "若 $z=f(x,y)$ 在点 $P$ 处可微，则下列结论必然成立的有",
    qid="c9-m1",
    answer=["A", "B", "C"],
    options=["$f$ 在点 $P$ 处连续",
             "$f$ 在点 $P$ 处的两个偏导数都存在",
             "$f$ 在点 $P$ 处沿任意方向 $\\vec l$ 的方向导数都存在",
             "$f$ 在点 $P$ 处的两个偏导数都连续"],
    expl="**答案依据**：可微 $\\Rightarrow$ 连续、偏导存在、沿任意方向的方向导数存在且 $\\dfrac{\\partial f}{\\partial\\vec l}=f_x\\cos\\alpha+f_y\\cos\\beta$（§9.3、§9.7），A、B、C 正确。\n"
         "D 错：「偏导连续 $\\Rightarrow$ 可微」，反向不成立，可微不能保证偏导连续。",
    mis="⚠️易错点：关系链「偏导连续 $\\Rightarrow$ 可微 $\\Rightarrow$ 连续、偏导存在、方向导数存在」是单向的；逆命题全部不成立。",
    tags=["可微性", "关系链", "必背"]))

Q_.append(Q(MULTI, "hard", "9.8",
    "设 $z=f(x,y)$ 在点 $P_0(x_0,y_0)$ 的某邻域内有直到二阶的连续偏导数，记 $A=f_{xx}(P_0)$，$B=f_{xy}(P_0)$，$C=f_{yy}(P_0)$，下列说法正确的有",
    qid="c9-m2",
    answer=["A", "C", "D"],
    options=["若 $f$ 可微且 $P_0$ 是极值点，则 $f_x(P_0)=f_y(P_0)=0$",
             "若 $AC-B^2>0$ 且 $A>0$，则 $P_0$ 是极大值点",
             "若 $AC-B^2=0$，则不能判定 $P_0$ 是否为极值点",
             "若 $AC-B^2<0$，则 $P_0$ 不是极值点"],
    expl="**答案依据**：二元函数极值的必要条件与 AC−B² 判别法（§9.8 定理）：极值必要条件 $f_x=f_y=0$（可微时），A 正确；$AC-B^2=0$ 时判别法失效（如 $z=x^4+y^4$ 在原点取极小、$z=x^3y$? 用 $z=x^3$ 型例子说明不确定），C 正确；$AC-B^2<0$ 时不是极值（鞍点），D 正确。\n"
         "B 错：$AC-B^2>0$ 且 $A>0$ 是**极小**值点（抛物面开口向上），$A<0$ 才是极大。",
    mis="⚠️易错点：$A>0$ 对应「碗口朝上」的极小；与一元 $f''>0$ 极小一致，可类比记忆；$AC-B^2\\le0$ 的点一律不是极值点（$=0$ 是失效待判）。",
    tags=["二元极值", "AC-B^2 判别法", "高频考点", "困难"]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "9.1",
    "若二重极限 $\\lim\\limits_{(x,y)\\to(0,0)}f(x,y)=A$，则点 $(x,y)$ 沿任何路径趋于原点时 $f(x,y)$ 都趋于 $A$。",
    qid="c9-j1",
    answer=["A"],
    expl="**答案依据**：二元极限定义要求「任意方式」趋近时函数值都趋于同一常数（§9.1），这正是二重极限与一元极限（只有左右两个方向）的本质区别。命题正确。",
    mis="⚠️易错点：证明二重极限**不存在**只需找两条路径极限不同（如 $y=kx$）；但要证明极限**存在**必须用定义或夹逼，逐路径验证无效。",
    tags=["二重极限", "必背"]))

Q_.append(Q(JUDGE, "basic", "9.2",
    "若 $f(x,y)$ 在点 $(0,0)$ 处的两个偏导数都存在，则 $f(x,y)$ 在 $(0,0)$ 处必连续。",
    qid="c9-j2",
    answer=["B"],
    expl="**答案依据**：偏导数只反映函数沿两条坐标轴直线的变化，控制不住其他路径。反例：$f(x,y)=\\dfrac{xy}{x^2+y^2}$（$f(0,0)=0$）在原点 $f_x=f_y=0$ 存在，但沿 $y=x$ 趋于原点时 $f\\to\\dfrac12\\ne f(0,0)$，不连续。命题错误（§9.2）。",
    mis="⚠️易错点：一元「可导必连续」不能平移到多元的「偏导存在必连续」——多元与连续挂钩的是「可微」。",
    tags=["偏导与连续", "高频考点"]))

Q_.append(Q(JUDGE, "medium", "9.8",
    "可微函数的极值点必是驻点。",
    qid="c9-j3",
    answer=["A"],
    expl="**答案依据**：二元极值必要条件：若 $f$ 在 $P_0$ 可微（有偏导）且取极值，则 $f_x(P_0)=f_y(P_0)=0$，即 $P_0$ 为驻点（§9.8）。命题正确。注意逆命题不真，驻点未必是极值点（如 $z=xy$ 的原点是鞍点）。",
    mis="⚠️易错点：与一元一样，「极值点 $\\subseteq$ 驻点 $\\cup$ 偏导不存在点」；本题有「可微」前提故极值点必为驻点。",
    tags=["极值必要条件"]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "9.2",
    "设 $z=\\ln(x^2+y^2)$，则 $\\dfrac{\\partial z}{\\partial x}=$ ____。",
    qid="c9-b1",
    answer=["2x/(x^2+y^2)"],
    accept=["2x/(x^2+y^2)", "2x/(x^2+y^2)", "2*x/(x^2+y^2)", "2x/(x*x+y*y)"],
    expl="**答案依据**：链式法则（§9.2）：$\\dfrac{\\partial z}{\\partial x}=\\dfrac{1}{x^2+y^2}\\cdot 2x=\\dfrac{2x}{x^2+y^2}$（$y$ 冻结，内层导数为 $2x$）。",
    mis="⚠️易错点：内层是 $x^2+y^2$ 而非 $x^2$，链式因子是 $2x$。",
    tags=["偏导数"]))

Q_.append(Q(BLANK, "medium", "9.2",
    "设 $z=x^2y^3$，则 $\\dfrac{\\partial z}{\\partial x}\\Big|_{(1,-1)}=$ ____。",
    qid="c9-b2",
    answer=["-2"],
    accept=["-2", "−2"],
    expl="**答案依据**：$\\dfrac{\\partial z}{\\partial x}=2xy^3$，代 $(1,-1)$：$2\\cdot1\\cdot(-1)^3=-2$（§9.2）。",
    mis="⚠️易错点：$(-1)^3=-1$ 的符号；$\\dfrac{\\partial z}{\\partial y}=3x^2y^2$ 在该点为 $3$，别与 $z_x$ 混淆。",
    tags=["偏导数求值"]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "9.3",
    "名词解释：全微分。",
    qid="c9-t1",
    answer_text="若函数 $z=f(x,y)$ 在点 $(x,y)$ 的全增量 $\\Delta z=f(x+\\Delta x,y+\\Delta y)-f(x,y)$ 可表示为 $\\Delta z=A\\Delta x+B\\Delta y+o(\\rho)$（$\\rho=\\sqrt{\\Delta x^2+\\Delta y^2}$，$A,B$ 不依赖于 $\\Delta x,\\Delta y$），则称 $f$ 在该点可微，线性主部 $A\\Delta x+B\\Delta y$ 称为全微分，记作 $dz=A\\,dx+B\\,dy$；可微时 $A=f_x$，$B=f_y$，故 $dz=f_x\\,dx+f_y\\,dy$。",
    points=["定义：全增量可写成线性主部加高阶无穷小 $\\Delta z=A\\Delta x+B\\Delta y+o(\\rho)$，线性主部即全微分 $dz$。",
            "系数与运算：可微时 $A=f_x$、$B=f_y$，$dz=f_xdx+f_ydy$；近似计算与误差估计以 $\\Delta z\\approx dz$ 为基础。"],
    expl="**答案依据**：全微分定义与可微条件见 §9.3。\n"
         "**考点出处**：同济《高等数学》第七版 §9.3 全微分。",
    mis="⚠️易错点：$\\rho$ 是两点距离而非 $\\Delta x$；「偏导存在」不等于「可微」，$A,B$ 的存在性由可微性保证。",
    tags=["全微分", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "9.1",
    "简答：二重极限 $\\lim\\limits_{(x,y)\\to(0,0)}f(x,y)$ 与一元函数极限有何本质区别？如何判定二重极限不存在？",
    qid="c9-t2",
    answer_text="本质区别：一元函数 $x\\to x_0$ 只有左右两个方向，而 $(x,y)\\to(0,0)$ 要求点以**任意方式**（任意路径、任意速度）趋近时函数值都趋于同一极限。因此二重极限更难存在。判定不存在的方法：找两条特殊路径（如 $y=kx$、$y=x^2$、沿坐标轴）使函数趋于不同极限；或沿某路径极限不存在（如含振荡因子），则原二重极限不存在。",
    points=["定义差异：一元极限只有左右两方向；二重极限要求任意路径趋近时极限都存在且相同。",
            "判定不存在的常用手法：取 $y=kx$ 得极限随 $k$ 变化（如 $\\dfrac{xy}{x^2+y^2}$ 沿 $y=kx$ 趋于 $\\dfrac{k}{1+k^2}$ → 极限不存在）；注意沿一切直线极限相同仍不够，还要检查曲线路径（如 $y=x^2$）。",
            "与连续、偏导的关系：二重极限存在且等于该点函数值 $\\iff$ 连续；偏导存在推不出连续。"],
    expl="**答案依据**：二重极限的定义、路径法判定不存在及经典反例见 §9.1。\n"
         "**考点出处**：同济《高等数学》第七版 §9.1 多元函数的基本概念。",
    mis="⚠️易错点：「沿任意直线极限相同」不等于二重极限存在（$\\dfrac{x^2y}{x^4+y^2}$ 沿一切直线极限为 0，沿 $y=x^2$ 极限为 $\\dfrac12$）。",
    ext="引申：$\\dfrac{x^2y}{x^4+y^2}$ 沿直线全为 0 而沿抛物线 $y=kx^2$ 趋于 $\\dfrac{k}{1+k^2}$，是「直线检验不足够」的招牌反例。",
    tags=["二重极限", "简答", "高频考点"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "9.2",
    "设 $z=x^2y+\\sin(xy)$，求 $\\dfrac{\\partial^2 z}{\\partial x\\partial y}$。",
    qid="c9-c1",
    answer=["2*x+cos(x*y)-x*y*sin(x*y)"],
    answer_text="先对 $x$ 求偏导：$\\dfrac{\\partial z}{\\partial x}=2xy+y\\cos(xy)$。\n"
                "再对 $y$ 求偏导：\n$$\\dfrac{\\partial^2 z}{\\partial x\\partial y}=2x+\\cos(xy)-xy\\sin(xy).$$\n"
                "（$\\cos(xy)$ 对 $y$ 求导为 $-x\\sin(xy)$，与 $y$ 相乘得 $-xy\\sin(xy)$。）\n"
                "由混合偏导连续定理（§9.2），$\\dfrac{\\partial^2z}{\\partial y\\partial x}$ 与之相等。",
    points=["先求 $z_x=2xy+y\\cos(xy)$（$y$ 冻结）。",
            "再对 $y$ 求导：$2xy\\to 2x$；$y\\cos(xy)\\to\\cos(xy)+y\\cdot[-x\\sin(xy)]$。",
            "合并得 $2x+\\cos(xy)-xy\\sin(xy)$。",
            "指出混合偏导在此（连续条件下）与求导次序无关。"],
    expl="**答案依据**：二阶混合偏导与求导次序无关定理（§9.2）。\n"
         "**考点出处**：同济《高等数学》第七版 §9.2 偏导数。",
    tags=["二阶偏导", "高频考点"],
    verify=[{"desc": "混合偏导", "code": "z=x**2*y+sin(x*y); simplify(diff(z, x, y) - (2*x+cos(x*y)-x*y*sin(x*y)))", "expected": "0"}]))

Q_.append(Q(CALC, "medium", "9.4",
    "设 $z=\\dfrac{x^2}{y^2}\\ln(xy)$，求 $\\dfrac{\\partial z}{\\partial x}$。",
    qid="c9-c2",
    answer=["(x/y^2)*(2*ln(x*y)+1)"],
    answer_text="令 $u=\\dfrac{x}{y}$，$v=xy$，则 $z=u^2\\ln v$。链式法则：\n$$\\frac{\\partial z}{\\partial x}=\\frac{\\partial z}{\\partial u}\\cdot\\frac{\\partial u}{\\partial x}+\\frac{\\partial z}{\\partial v}\\cdot\\frac{\\partial v}{\\partial x}=2u\\ln v\\cdot\\frac1y+\\frac{u^2}{v}\\cdot y=\\frac{2x}{y^2}\\ln(xy)+\\frac{x^2/y^2}{xy}\\cdot y=\\frac{x}{y^2}\\left[2\\ln(xy)+1\\right].$$",
    points=["设中间变量 $u=\\dfrac{x}{y}$、$v=xy$，则 $z=u^2\\ln v$。",
            "链式法则：$z_x=z_u\\cdot u_x+z_v\\cdot v_x=2u\\ln v\\cdot\\dfrac1y+\\dfrac{u^2}{v}\\cdot y$。",
            "代回并化简得 $\\dfrac{x}{y^2}\\left[2\\ln(xy)+1\\right]$。",
            "直接把 $z$ 写成 $\\dfrac{x^2}{y^2}\\ln(xy)$ 用乘积与链式法则求导可交叉验证。"],
    expl="**答案依据**：多元复合函数链式法则（§9.4）。\n"
         "**考点出处**：同济《高等数学》第七版 §9.4 多元复合函数的求导法则。",
    tags=["链式法则", "高频考点"],
    verify=[{"desc": "偏导核验", "code": "z=(x/y)**2*log(x*y); simplify(diff(z, x) - (x/y**2)*(2*log(x*y)+1))", "expected": "0"}]))

Q_.append(Q(CALC, "hard", "9.8",
    "求函数 $z=x^3-y^3+3x^2+3y^2-9x$ 的极值。",
    qid="c9-c3",
    answer=["极小值 f(1,0)=-5，极大值 f(-3,2)=31"],
    answer_text="解方程组 $\\begin{cases}z_x=3x^2+6x-9=0\\\\z_y=-3y^2+6y=0\\end{cases}$，得驻点 $(1,0),(1,2),(-3,0),(-3,2)$。\n"
                "$A=z_{xx}=6x+6$，$B=z_{xy}=0$，$C=z_{yy}=-6y+6$。\n"
                "逐点判别（$AC-B^2$）：\n"
                "$(1,0)$：$A=12,C=6$，$AC-B^2=72>0$ 且 $A>0$ → 极小值 $z=-5$；\n"
                "$(1,2)$：$C=-6$，$AC=-72<0$ → 非极值；\n"
                "$(-3,0)$：$A=-12$，$AC=-72<0$ → 非极值；\n"
                "$(-3,2)$：$A=-12,C=-6$，$AC-B^2=72>0$ 且 $A<0$ → 极大值 $z=31$。\n"
                "故极小值 $f(1,0)=-5$，极大值 $f(-3,2)=31$。",
    points=["解驻点方程组 $z_x=0,z_y=0$，得四个驻点。",
            "写出 $A=z_{xx}=6x+6$、$B=z_{xy}=0$、$C=z_{yy}=-6y+6$。",
            "逐点计算 $AC-B^2$ 并结合 $A$ 的符号判别：$(1,0)$ 极小 $-5$，$(-3,2)$ 极大 $31$，其余两点不是极值点。",
            "结论按「点 + 值 + 类型」三要素完整表述。"],
    expl="**答案依据**：二元极值的必要条件与 AC−B² 充分条件判别法（§9.8）。\n"
         "**考点出处**：同济《高等数学》第七版 §9.8 多元函数的极值及其求法。",
    tags=["二元极值", "困难", "高频考点"],
    verify=[{"desc": "驻点x", "code": "solve(3*x**2 + 6*x - 9, x)", "expected": "[-3, 1]"},
             {"desc": "极值", "code": "z=x**3-y**3+3*x**2+3*y**2-9*x; [z.subs({x:1,y:0}), z.subs({x:-3,y:2})]", "expected": "[-5, 31]"}]))

Q = Q_
