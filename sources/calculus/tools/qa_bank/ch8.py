# -*- coding: utf-8 -*-
"""第8章 向量代数与空间解析几何 —— 15 题（单选3/多选2/判断3/填空2/简答2/计算3）
难度：基础7 中等5 困难3
知识点：8.1 向量及其线性运算 / 8.2 数量积 向量积 *混合积 / 8.3 平面及其方程
        8.4 空间直线及其方程 / 8.5 曲面及其方程 / 8.6 空间曲线及其方程
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────── 单选 3（基础1 中等1 困难1）
Q_.append(Q(SINGLE, "basic", "8.2",
    "设 $\\vec a=(1,2,3)$，$\\vec b=(2,-1,1)$，则 $\\vec a\\times\\vec b=$",
    qid="c8-s1",
    answer=["A"],
    options=["$(5,5,-5)$", "$(5,-5,5)$", "$(-5,-5,5)$", "$(1,1,-1)$"],
    expl="**答案依据**：按行列式展开（§8.2）：\n"
         "$$\\vec a\\times\\vec b=\\begin{vmatrix}\\vec i&\\vec j&\\vec k\\\\1&2&3\\\\2&-1&1\\end{vmatrix}=(2\\cdot1-3\\cdot(-1),\\ 3\\cdot2-1\\cdot1,\\ 1\\cdot(-1)-2\\cdot2)=(5,5,-5),$$\n"
         "A 正确。\n"
         "B、C 错：行列式某行（或列）符号处理错误；注意 $\\vec b\\times\\vec a=(-5,-5,5)$。\n"
         "D 错：方向虽同但模长不对。",
    mis="⚠️易错点：三个分量的符号依次来自 $i,j,k$ 的代数余子式，$j$ 分量前有负号；用点积验算：$(5,5,-5)\\cdot(1,2,3)=0$ 且 $\\cdot(2,-1,1)=0$。",
    tags=["向量积", "高频考点"],
    verify=[{"desc": "cross", "code": "Matrix([1,2,3]).cross(Matrix([2,-1,1]))", "expected": "Matrix([[5], [5], [-5]])"}]))

Q_.append(Q(SINGLE, "medium", "8.3",
    "过点 $(1,2,-1)$ 且以 $\\vec n=(2,1,3)$ 为法向量的平面方程是",
    qid="c8-s2",
    answer=["C"],
    options=["$2x+y+3z+1=0$", "$2x-y+3z-1=0$", "$2x+y+3z-1=0$", "$x+2y+3z-1=0$"],
    expl="**答案依据**：点法式（§8.3）：$2(x-1)+(y-2)+3(z+1)=0$，展开得 $2x+y+3z-1=0$，C 正确。\n"
         "A 错：常数项符号错（$-2-2+3=-1$ 应移项为 $-1$）。\n"
         "B 错：$y$ 的系数符号错。\n"
         "D 错：把点的坐标与法向量分量错位。",
    mis="⚠️易错点：点法式代入后常数项 $-Ax_0-By_0-Cz_0=-(2+2-3)=-1$；代回点坐标可快速验算：$2+2-3-1=0$。",
    tags=["平面方程", "高频考点"]))

Q_.append(Q(SINGLE, "hard", "8.4",
    "直线 $L:\\dfrac{x-1}{1}=\\dfrac{y}{1}=\\dfrac{z+1}{2}$ 与平面 $\\pi:2x-2y+z=0$ 的夹角为",
    qid="c8-s3",
    answer=["D"],
    options=["$\\arccos\\dfrac{\\sqrt6}{9}$", "$\\arcsin\\dfrac13$", "$\\arccos\\dfrac23$", "$\\arcsin\\dfrac{\\sqrt6}{9}$"],
    expl="**答案依据**：直线方向向量 $\\vec s=(1,1,2)$，平面法向量 $\\vec n=(2,-2,1)$（§8.4）。夹角公式 $\\sin\\varphi=\\dfrac{|\\vec s\\cdot\\vec n|}{|\\vec s|\\,|\\vec n|}=\\dfrac{|2-2+2|}{\\sqrt6\\cdot3}=\\dfrac{2}{3\\sqrt6}=\\dfrac{\\sqrt6}{9}$，故 $\\varphi=\\arcsin\\dfrac{\\sqrt6}{9}$，D 正确。\n"
         "A 错：线面夹角用 $\\sin$（与法向量夹角互余），不能用 $\\arccos$ 直接套点积。\n"
         "B、C 错：分子分母计算错误。",
    mis="⚠️易错点：线面夹角 $\\varphi$ 与「直线与法向量夹角」互余，公式里是 $\\sin\\varphi=\\dfrac{|\\vec s\\cdot\\vec n|}{|\\vec s||\\vec n|}$；$\\vec s\\cdot\\vec n=0$ 时直线与平面平行。",
    tags=["线面夹角", "困难"],
    verify=[{"desc": "sinφ", "code": "s=Matrix([1,1,2]); n=Matrix([2,-2,1]); simplify(Abs(s.dot(n))/(sqrt(6)*3) - sqrt(6)/9)", "expected": "0"}]))

# ─────────────────────────── 多选 2（中等1 困难1）
Q_.append(Q(MULTI, "medium", "8.2",
    "对于非零向量 $\\vec a,\\vec b$，下列说法正确的有",
    qid="c8-m1",
    answer=["A", "B", "C"],
    options=["$\\vec a\\cdot\\vec b=|\\vec a|\\,|\\vec b|\\cos\\theta$（$\\theta$ 为夹角）",
             "$\\vec a\\times\\vec b$ 的方向按右手法则垂直于 $\\vec a$ 与 $\\vec b$ 所决定的平面",
             "$|\\vec a\\times\\vec b|=|\\vec a|\\,|\\vec b|\\sin\\theta$，等于以 $\\vec a,\\vec b$ 为邻边的平行四边形面积",
             "$\\vec a\\cdot\\vec b=0\\iff\\vec a\\parallel\\vec b$"],
    expl="**答案依据**：数量积与向量积的定义及几何意义见 §8.2，A、B、C 正确。\n"
         "D 错：$\\vec a\\cdot\\vec b=0\\iff\\vec a\\perp\\vec b$（垂直）；平行的等价条件是 $\\vec a\\times\\vec b=\\vec 0$。",
    mis="⚠️易错点：「点积零 ⇔ 垂直」「叉积零 ⇔ 平行」两句话别对调；数量积是数量，向量积是向量。",
    tags=["数量积", "向量积", "必背"]))

Q_.append(Q(MULTI, "hard", "8.3",
    "设平面 $\\pi_1:x+y+z=1$ 与 $\\pi_2:x+2y+2z=1$，下列说法正确的有",
    qid="c8-m2",
    answer=["A", "B", "C"],
    options=["两平面的夹角满足 $\\cos\\theta=\\dfrac{5\\sqrt3}{9}$",
             "两平面相交于一条直线",
             "点 $(1,0,0)$ 在平面 $\\pi_1$ 上",
             "两平面互相垂直"],
    expl="**答案依据**：法向量 $\\vec n_1=(1,1,1)$，$\\vec n_2=(1,2,2)$。$\\cos\\theta=\\dfrac{\\vec n_1\\cdot\\vec n_2}{|\\vec n_1||\\vec n_2|}=\\dfrac{5}{\\sqrt3\\cdot3}=\\dfrac{5\\sqrt3}{9}$，A 正确；两法向量不平行（分量不成比例），两平面必相交，B 正确；$1+0+0=1$ 成立，C 正确。\n"
         "D 错：垂直要求 $\\vec n_1\\cdot\\vec n_2=0$，而此处 $=5$。",
    mis="⚠️易错点：两平面夹角取 $[0,\\dfrac\\pi2]$，用 $|\\cos\\theta|$（本题点积为正无需取绝对值）；判断平行看法向量是否成比例。",
    tags=["平面夹角", "困难"],
    verify=[{"desc": "cosθ", "code": "n1=Matrix([1,1,1]); n2=Matrix([1,2,2]); simplify(n1.dot(n2)/(sqrt(3)*3) - Rational(5,3)/sqrt(3))", "expected": "0"},
             {"desc": "点在π1", "code": "1+0+0-1", "expected": "0"}]))

# ─────────────────────────── 判断 3（基础2 中等1）
Q_.append(Q(JUDGE, "basic", "8.1",
    "$\\vec a\\perp\\vec b$ 的充要条件是 $\\vec a\\cdot\\vec b=0$。",
    qid="c8-j1",
    answer=["A"],
    expl="**答案依据**：$\\vec a\\cdot\\vec b=|\\vec a||\\vec b|\\cos\\theta=0\\iff\\cos\\theta=0\\iff\\theta=\\dfrac{\\pi}{2}$（$\\vec a,\\vec b$ 均非零）。命题正确（§8.2）。零向量与任何向量都视为垂直（也视为平行），作为约定情形。",
    mis="⚠️易错点：判垂直用点积，判平行用叉积或坐标成比例；零向量是特殊约定情形。",
    tags=["数量积", "垂直"]))

Q_.append(Q(JUDGE, "basic", "8.2",
    "$\\vec a\\times\\vec b=\\vec b\\times\\vec a$。",
    qid="c8-j2",
    answer=["B"],
    expl="**答案依据**：向量积满足反交换律 $\\vec a\\times\\vec b=-\\vec b\\times\\vec a$（右手法则方向相反），一般不等于 $\\vec b\\times\\vec a$。命题错误（§8.2）。",
    mis="⚠️易错点：向量积不满足交换律与结合律，但满足分配律；只有 $\\vec a\\parallel\\vec b$ 时两者才同为零向量。",
    tags=["向量积", "运算律", "易错点"]))

Q_.append(Q(JUDGE, "medium", "8.5",
    "方程 $x^2+y^2=4$ 在空间直角坐标系中表示球面。",
    qid="c8-j3",
    answer=["B"],
    expl="**答案依据**：方程 $x^2+y^2=4$ 中不含 $z$，表示母线平行于 $z$ 轴的**圆柱面**（准线为 $xOy$ 面上的圆，§8.5）。球面方程应为 $x^2+y^2+z^2=4$。命题错误。",
    mis="⚠️易错点：同一方程在平面与空间中意义不同——「缺哪个变量，母线就平行于哪条轴」；$F(x,y)=0$ 型都是柱面。",
    ext="引申：常见二次曲面口诀——椭球面、抛物面、双曲面（单叶/双叶）、锥面；判定方法是截痕法（用平面去截看交线形状）。",
    tags=["二次曲面", "柱面", "易错点"]))

# ─────────────────────────── 填空 2（基础1 中等1）
Q_.append(Q(BLANK, "basic", "8.1",
    "向量 $\\vec a=(1,-2,2)$ 的模 $|\\vec a|=$ ____。",
    qid="c8-b1",
    answer=["3"],
    accept=["3"],
    expl="**答案依据**：$|\\vec a|=\\sqrt{1^2+(-2)^2+2^2}=\\sqrt9=3$（§8.1）。相应单位向量 $\\vec a^{\\,0}=\\pm\\dfrac13(1,-2,2)$。",
    mis="⚠️易错点：负分量平方后为正；$(3,4,0)$ 型勾股数要熟。",
    tags=["向量模"],
    verify=[{"desc": "norm", "code": "Matrix([1,-2,2]).norm()", "expected": "3"}]))

Q_.append(Q(BLANK, "medium", "8.2",
    "设 $\\vec a=(1,1,0)$，$\\vec b=(0,1,1)$，则 $\\vec a\\times\\vec b=$ ____（写成坐标形式）。",
    qid="c8-b2",
    answer=["(1,-1,1)"],
    accept=["(1,-1,1)", "(1, -1, 1)", "i-j+k", "(1，-1，1)"],
    expl="**答案依据**：$\\vec a\\times\\vec b=\\begin{vmatrix}\\vec i&\\vec j&\\vec k\\\\1&1&0\\\\0&1&1\\end{vmatrix}=(1\\cdot1-0\\cdot1,\\ 0\\cdot0-1\\cdot1,\\ 1\\cdot1-1\\cdot0)=(1,-1,1)$（§8.2）。",
    mis="⚠️易错点：中间分量前有负号（代数余子式符号）；验算 $(1,-1,1)\\cdot(1,1,0)=0$、$(1,-1,1)\\cdot(0,1,1)=0$。",
    tags=["向量积"],
    verify=[{"desc": "cross", "code": "Matrix([1,1,0]).cross(Matrix([0,1,1]))", "expected": "Matrix([[1], [-1], [1]])"}]))

# ─────────────────────────── 简答与名词解释 2（基础2）
Q_.append(Q(TERM, "basic", "8.2",
    "名词解释：向量积（叉积）。",
    qid="c8-t1",
    answer_text="两向量 $\\vec a$ 与 $\\vec b$ 的向量积 $\\vec a\\times\\vec b$ 是一个向量：其模 $|\\vec a\\times\\vec b|=|\\vec a||\\vec b|\\sin\\theta$（$\\theta$ 为夹角），方向垂直于 $\\vec a$ 与 $\\vec b$ 所决定的平面，且按右手法则从 $\\vec a$ 转向 $\\vec b$。坐标运算按三阶行列式展开；$|\\vec a\\times\\vec b|$ 等于以 $\\vec a,\\vec b$ 为邻边的平行四边形面积。",
    points=["定义：模为 $|\\vec a||\\vec b|\\sin\\theta$、方向由右手法则确定且垂直于 $\\vec a,\\vec b$ 平面的向量，记 $\\vec a\\times\\vec b$。",
            "性质与意义：$\\vec a\\times\\vec b=-\\vec b\\times\\vec a$（反交换）；$\\vec a\\times\\vec b=\\vec0\\iff\\vec a\\parallel\\vec b$；模长等于平行四边形面积，是求三角形面积与法向量的工具。"],
    expl="**答案依据**：向量积的定义、坐标表达式与几何意义见 §8.2。\n"
         "**考点出处**：同济《高等数学》第七版 §8.2 数量积 向量积 *混合积。",
    mis="⚠️易错点：向量积是**向量**不是数；方向由「右手法则」而不是左手法则。",
    tags=["向量积", "概念", "必背"]))

Q_.append(Q(SHORT, "basic", "8.3",
    "简答：写出平面方程的三种常见形式（点法式、一般式、截距式）及各自的关键要素。",
    qid="c8-t2",
    answer_text="点法式：$A(x-x_0)+B(y-y_0)+C(z-z_0)=0$，要素是平面上一点 $(x_0,y_0,z_0)$ 与法向量 $\\vec n=(A,B,C)$。一般式：$Ax+By+Cz+D=0$（$A,B,C$ 不全为零），其法向量为 $(A,B,C)$。截距式：$\\dfrac{x}{a}+\\dfrac{y}{b}+\\dfrac{z}{c}=1$（$abc\\ne0$），$a,b,c$ 为平面在三轴上的截距，便于画图。",
    points=["点法式 $A(x-x_0)+B(y-y_0)+C(z-z_0)=0$：点 + 法向量，是推导其他形式的起点。",
            "一般式 $Ax+By+Cz+D=0$：法向量为 $(A,B,C)$；特别地 $xOy$ 面为 $z=0$。",
            "截距式 $\\dfrac{x}{a}+\\dfrac{y}{b}+\\dfrac{z}{c}=1$（$abc\\ne0$）：三个截距直接给出与三轴的交点；求平面的一般思路是「几何条件 → 点与法向量 → 点法式」。"],
    expl="**答案依据**：平面方程的各种形式见 §8.3。\n"
         "**考点出处**：同济《高等数学》第七版 §8.3 平面及其方程。",
    mis="⚠️易错点：截距式要求截距非零且平面不过原点；两平面平行 $\\iff$ 法向量成比例且常数项不成比例。",
    tags=["平面方程", "简答", "必背"]))

# ─────────────────────────── 计算 3（基础1 中等1 困难1）
Q_.append(Q(CALC, "basic", "8.3",
    "求过点 $M(2,-1,1)$ 且以 $\\vec n=(1,-2,3)$ 为法向量的平面方程。",
    qid="c8-c1",
    answer=["x-2y+3z-7=0"],
    answer_text="点法式：$1\\cdot(x-2)-2\\cdot(y+1)+3\\cdot(z-1)=0$，展开整理得\n$$x-2y+3z-7=0.$$\n验算：$2-2\\cdot(-1)+3\\cdot1-7=2+2+3-7=0$，点在平面上。",
    points=["点法式代入：$(x-2)-2(y+1)+3(z-1)=0$。",
            "展开整理得 $x-2y+3z-7=0$。",
            "代回点 $M$ 验证常数为 $-7$。",
            "注意：法向量各系数与点坐标对应相乘，符号逐项处理。"],
    expl="**答案依据**：平面的点法式方程（§8.3）。\n"
         "**考点出处**：同济《高等数学》第七版 §8.3 平面及其方程。",
    tags=["平面方程", "高频考点"],
    verify=[{"desc": "点在平面上", "code": "xx,yy,zz=symbols('xx yy zz'); (xx - 2*yy + 3*zz - 7).subs({xx: 2, yy: -1, zz: 1})", "expected": "0"},
             {"desc": "法向量模核验", "code": "Matrix([1,-2,3]).norm().evalf()", "expected": "3.74165738677394"}]))


Q_.append(Q(CALC, "medium", "8.4",
    "将直线 $\\begin{cases}x+y+z=1,\\\\ x-y+2z=3\\end{cases}$ 化为对称式（点向式）方程。",
    qid="c8-c2",
    answer=["(x-2)/3=(y+1)/(-1)=z/(-2)"],
    answer_text="方向向量取两平面法向量的向量积：\n$$\\vec s=\\vec n_1\\times\\vec n_2=\\begin{vmatrix}\\vec i&\\vec j&\\vec k\\\\1&1&1\\\\1&-1&2\\end{vmatrix}=(3,-1,-2).$$\n"
                "再找直线上一点：取 $z=0$，解 $\\begin{cases}x+y=1\\\\x-y=3\\end{cases}$ 得 $(x,y)=(2,-1)$，即点 $(2,-1,0)$。\n"
                "对称式：$\\dfrac{x-2}{3}=\\dfrac{y+1}{-1}=\\dfrac{z}{-2}$。",
    points=["方向向量 $\\vec s=\\vec n_1\\times\\vec n_2=(3,-1,-2)$。",
            "令 $z=0$ 解两平面方程得直线上一点 $(2,-1,0)$。",
            "写对称式 $\\dfrac{x-2}{3}=\\dfrac{y+1}{-1}=\\dfrac{z}{-2}$。",
            "验算：点代入两平面方程均成立；$\\vec s$ 与 $\\vec n_1,\\vec n_2$ 点积为零。"],
    expl="**答案依据**：直线的一般式化对称式：方向向量 = 两法向量之叉积（§8.4）。\n"
         "**考点出处**：同济《高等数学》第七版 §8.4 空间直线及其方程。",
    tags=["直线方程", "高频考点"],
    verify=[{"desc": "方向向量", "code": "Matrix([1,1,1]).cross(Matrix([1,-1,2]))", "expected": "Matrix([[3], [-1], [-2]])"},
             {"desc": "点在线上", "code": "[2 + (-1) + 0 - 1, 2 - (-1) + 0 - 3]", "expected": "[0, 0]"}]))

Q_.append(Q(CALC, "hard", "8.4",
    "求直线 $L:\\dfrac{x-2}{1}=\\dfrac{y-3}{1}=\\dfrac{z-4}{2}$ 与平面 $\\pi:x+y+z-3=0$ 的交点。",
    qid="c8-c3",
    answer=["(1/2,3/2,1)"],
    answer_text="把直线写成参数式：$x=2+t,\\ y=3+t,\\ z=4+2t$。代入平面方程：\n"
                "$$(2+t)+(3+t)+(4+2t)-3=6+4t=0\\ \\Rightarrow\\ t=-\\dfrac{3}{2}.$$\n"
                "代回参数式得交点 $\\left(\\dfrac12,\\ \\dfrac32,\\ 1\\right)$。",
    points=["直线化参数式 $x=2+t,\\ y=3+t,\\ z=4+2t$。",
            "代入平面方程得 $6+4t=0$，解出 $t=-\\dfrac32$。",
            "代回得交点 $\\left(\\dfrac12,\\dfrac32,1\\right)$。",
            "讨论：若代入口得 $t$ 无解（系数为零且常数非零）则直线平行于平面；恒成立则直线在平面内。"],
    expl="**答案依据**：直线与平面的交点用参数式代入法（§8.4）。\n"
         "**考点出处**：同济《高等数学》第七版 §8.4 空间直线及其方程。",
    mis="⚠️易错点：参数代入时三个坐标都要带 $t$（$z$ 是 $2t$）；判断「平行/在面内」与「相交」要靠 $t$ 的解的个数。",
    tags=["线面交点", "困难"],
    verify=[{"desc": "交点", "code": "tt=symbols('tt'); s0=solve(2+tt+3+tt+4+2*tt-3, tt)[0]; [simplify(2+s0), simplify(3+s0), simplify(4+2*s0)]", "expected": "[1/2, 3/2, 1]"}]))

Q = Q_
