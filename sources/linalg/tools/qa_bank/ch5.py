# -*- coding: utf-8 -*-
"""第5章 特征值与二次型 —— 36 题（单选5/多选6/判断4/填空6/简答7/计算8）
难度：基础15 中等15 困难6
知识点：5.1 向量的内积、长度及正交性 / 5.2 方阵的特征值与特征向量
        5.3 相似矩阵 / 5.4 对称矩阵的对角化 / 5.5 二次型及其标准形
        5.6 用配方法化二次型成标准形 / 5.7 正定二次型
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────────────────────────── 单选 5（基础1 中等2 困难2）
Q_.append(Q(SINGLE, "basic", "5.2",
    "设 $A=\\begin{pmatrix}1&2\\\\0&3\\end{pmatrix}$，则 $A$ 的特征值为",
    answer=["A"],
    options=["$1$ 与 $3$", "$1$ 与 $-3$", "$2$ 与 $2$", "$-1$ 与 $3$"],
    expl="**答案依据**：特征值是使 $|\\lambda E-A|=0$ 成立的 $\\lambda$（§5.2）。\n"
         "$$|\\lambda E-A|=\\begin{vmatrix}\\lambda-1&-2\\\\0&\\lambda-3\\end{vmatrix}=(\\lambda-1)(\\lambda-3)=0,$$\n"
         "故特征值为 $1$ 与 $3$。\n"
         "B 错：$|-3E-A|=\\begin{vmatrix}-4&-2\\\\0&-6\\end{vmatrix}=24\\neq0$，$-3$ 不是特征值；\n"
         "C 错：$|2E-A|=\\begin{vmatrix}1&-2\\\\0&-1\\end{vmatrix}=-1\\neq0$，$2$ 不是特征值（虽然 $2+2=4$ 恰好等于主对角线元素之和，但「特征值之和等于迹」只是必要条件）；\n"
         "D 错：$|-E-A|=\\begin{vmatrix}-2&-2\\\\0&-4\\end{vmatrix}=8\\neq0$，$-1$ 不是特征值。",
    mis="⚠️易错点：把「特征值之和等于主对角线元素之和」当成充分条件来「凑」特征值。迹相同不能保证特征值相同，必须解特征方程 $|\\lambda E-A|=0$。",
    tags=["计算", "高频"],
    verify=[{"desc": "特征值", "code": "M([[1,2],[0,3]]).eigenvals()", "expected": "{3: 1, 1: 1}"}]))

Q_.append(Q(SINGLE, "medium", "5.1",
    "设 $\\alpha=(1,1,0)^{\\mathsf T}$，$\\beta=(1,0,1)^{\\mathsf T}$，则 $\\alpha$ 与 $\\beta$ 的夹角 $\\theta$ 为",
    answer=["B"],
    options=["$\\dfrac{\\pi}{4}$", "$\\dfrac{\\pi}{3}$", "$\\dfrac{\\pi}{2}$", "$\\dfrac{\\pi}{6}$"],
    expl="**答案依据**：实空间两向量的夹角由内积给出（§5.1）\n"
         "$$\\cos\\theta=\\frac{(\\alpha,\\beta)}{\\|\\alpha\\|\\,\\|\\beta\\|}.$$\n"
         "其中 $(\\alpha,\\beta)=1\\times1+1\\times0+0\\times1=1$，$\\|\\alpha\\|=\\sqrt{1^2+1^2+0^2}=\\sqrt2$，$\\|\\beta\\|=\\sqrt{1^2+0^2+1^2}=\\sqrt2$，\n"
         "故 $\\cos\\theta=\\dfrac{1}{\\sqrt2\\cdot\\sqrt2}=\\dfrac12$，即 $\\theta=\\dfrac{\\pi}{3}$。\n"
         "A 错：$\\cos\\dfrac{\\pi}{4}=\\dfrac{\\sqrt2}{2}\\neq\\dfrac12$；\n"
         "C 错：$\\cos\\dfrac{\\pi}{2}=0$ 对应 $(\\alpha,\\beta)=0$，本题内积为 $1\\neq0$，两向量**不正交**；\n"
         "D 错：$\\cos\\dfrac{\\pi}{6}=\\dfrac{\\sqrt3}{2}>\\dfrac12$。\n"
         "**引申**：内积 $(\\alpha,\\beta)$ 的两个重要用途是判别正交（$=0$）与计算夹角；夹角公式也正是 Cauchy 不等式 $|(\\alpha,\\beta)|\\le\\|\\alpha\\|\\|\\beta\\|$ 的几何解释。",
    mis="⚠️易错点：把「长度」与「长度的平方」混用——$\\|\\alpha\\|^2=(\\alpha,\\alpha)=2$，而 $\\|\\alpha\\|=\\sqrt2$；夹角公式的分母是两个长度之积，不能漏掉开方。",
    tags=["计算", "高频"],
    verify=[{"desc": "内积", "code": "M([[1,1,0]]).dot(M([[1,0,1]]))", "expected": "1"},
            {"desc": "alpha 长度平方", "code": "M([[1,1,0]]).dot(M([[1,1,0]]))", "expected": "2"},
            {"desc": "cos theta", "code": "expand(M([[1,1,0]]).dot(M([[1,0,1]]))/(sqrt(2)*sqrt(2)))", "expected": "1/2"}]))

Q_.append(Q(SINGLE, "medium", "5.6",
    "用**配方法**把二次型 $f(x_1,x_2)=x_1^2-2x_1x_2+3x_2^2$ 化为标准形，所得结果为",
    answer=["C"],
    options=["$y_1^2+3y_2^2$", "$-y_1^2+4y_2^2$", "$y_1^2+2y_2^2$", "$y_1^2+y_2^2$"],
    expl="**答案依据**：§5.6 配方法。先把含 $x_1$ 的项配成完全平方：\n"
         "$$f=(x_1^2-2x_1x_2)+3x_2^2=(x_1-x_2)^2+3x_2^2-x_2^2=(x_1-x_2)^2+2x_2^2.$$\n"
         "令 $y_1=x_1-x_2$，$y_2=x_2$，得标准形 $y_1^2+2y_2^2$。\n"
         "（用合同验算：$A=\\begin{pmatrix}1&-1\\\\-1&3\\end{pmatrix}$，取 $C=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$，则 $C^{\\mathsf T}AC=\\begin{pmatrix}1&0\\\\0&2\\end{pmatrix}$，与配方结果一致。）\n"
         "A 错：配方后 $x_2^2$ 的系数应为 $3-1=2$，不是 $3$——把 $(x_1-x_2)^2$ 中的 $x_2^2$ 漏算了一次；\n"
         "B 错：$A$ 满足 $a_{11}=1>0$ 且 $|A|=2>0$，故 $f$ 正定，标准形的系数必须全为正，不可能出现 $-y_1^2$；\n"
         "D 错：合同变换保持迹不变，$\\operatorname{tr}A=1+3=4$，而标准形 $y_1^2+y_2^2$ 的系数之和为 $2\\neq4$。",
    mis="⚠️易错点：配方时把 $(x_1-x_2)^2$ 展开后**漏掉** $x_2^2$ 项，或忘记从 $3x_2^2$ 中扣掉这 $1$，误得 $y_1^2+3y_2^2$。",
    tags=["计算", "高频"],
    verify=[{"desc": "合同变换结果", "code": "C=M([[1,1],[0,1]]); A=M([[1,-1],[-1,3]]); str(expand(C.T*A*C))", "expected": "Matrix([[1, 0], [0, 2]])"},
            {"desc": "正定性", "code": "M([[1,-1],[-1,3]]).is_positive_definite", "expected": "True"}]))

Q_.append(Q(SINGLE, "hard", "5.4",
    "设 $A=\\begin{pmatrix}1&1&1\\\\1&1&1\\\\1&1&1\\end{pmatrix}$，则 $A$ 的特征值及可对角化性为",
    answer=["D"],
    options=["特征值全为 $1$，且 $A$ 可对角化",
             "特征值为 $3,0,0$，且 $A$ **不可**对角化",
             "特征值全为 $0$，且 $A$ 可对角化",
             "特征值为 $3,0,0$，且 $A$ 可对角化"],
    expl="**答案依据**：$A=\\mathbf{1}\\mathbf{1}^{\\mathsf T}$（$\\mathbf{1}=(1,1,1)^{\\mathsf T}$），故 $A\\mathbf{1}=3\\mathbf{1}$，$3$ 是特征值；又 $\\operatorname{tr}A=3$、$|A|=0$，故另外两个特征值为 $0,0$，特征值为 $3,0,0$。\n"
         "可对角化性：$A$ 是**实对称矩阵**，由 §5.4，对称矩阵一定可以用正交变换对角化（重特征值的几何重数等于代数重数）。直接验证：$r(A)=1$，故零特征值对应的特征子空间维数为 $3-1=2$，等于其重数 $2$；$r(A-3E)=2$，故 $3$ 的特征子空间维数为 $3-2=1$，等于其重数 $1$。两种特征值的维数都等于重数，故 $A$ 可对角化。\n"
         "A 错：$A$ 不是单位矩阵，$3$ 是特征值（$A\\mathbf{1}=3\\mathbf{1}\\neq0$），特征值不全为 $1$；\n"
         "B 错：「有重特征值就不可对角化」只对一般矩阵成立，实对称矩阵必可对角化；\n"
         "C 错：$|A|=0$ 只说明有零特征值，$3$ 同样是特征值。",
    mis="⚠️易错点：把「有重特征值」等同于「不可对角化」。对一般矩阵重根可能导致不可对角化，但**实对称矩阵必可对角化**——这是本章最高频的辨析陷阱。",
    tags=["重点", "难点", "高频"],
    verify=[{"desc": "特征值", "code": "M([[1,1,1],[1,1,1],[1,1,1]]).eigenvals()", "expected": "{3: 1, 0: 2}"},
            {"desc": "r(A)", "code": "M([[1,1,1],[1,1,1],[1,1,1]]).rank()", "expected": "1"},
            {"desc": "r(A-3E)", "code": "(M([[1,1,1],[1,1,1],[1,1,1]])-3*eye(3)).rank()", "expected": "2"}]))

Q_.append(Q(SINGLE, "hard", "5.5",
    "设二次型 $f(x)=x^{\\mathsf T}Ax$ 的矩阵为 $A=\\begin{pmatrix}1&1&0\\\\1&1&0\\\\0&0&-1\\end{pmatrix}$，则下列结论**正确**的是",
    answer=["D"],
    options=["$f$ 的秩为 $1$",
             "$f$ 的正、负惯性指数分别为 $2,0$",
             "$f$ 的规范形为 $z_1^2+z_2^2$",
             "$f$ 的秩为 $2$，正惯性指数为 $1$，负惯性指数为 $1$"],
    expl="**答案依据**：§5.5 二次型的秩与惯性指数。$A$ 的前两行前两列构成的子块 $\\begin{pmatrix}1&1\\\\1&1\\end{pmatrix}$ 的特征值为 $2$ 与 $0$，第三个特征值为 $-1$，故 $A$ 的特征值为 $2,0,-1$。\n"
         "于是非零特征值有 $2$ 个，故 $r(A)=2$（$A$ 对称，秩等于非零特征值的个数）；正特征值只有 $2$ 这一个，故正惯性指数 $p=1$；负特征值只有 $-1$ 这一个，故负惯性指数 $q=1$；零特征值 $0$ 对应零变量。规范形为 $z_1^2-z_2^2$。\n"
         "A 错：$r(A)=2$（不是 $1$）——$A$ 的前两行相同，故 $|A|=0$，但第三行 $(0,0,-1)$ 与前两行不共线，故 $r(A)=2$ 而不是 $1$；\n"
         "B 错：正惯性指数为 $1$（不是 $2$），且负惯性指数为 $1$（不是 $0$）；\n"
         "C 错：存在负特征值 $-1$，故 $f$ 不是正定的，规范形应为 $z_1^2-z_2^2$ 而不是 $z_1^2+z_2^2$。",
    mis="⚠️易错点：把「秩」与「非零特征值的个数」以及「惯性指数」混为一谈。$r(A)=p+q$ 是**对称矩阵**才有的等式；一般矩阵的秩是线性无关列（行）数。",
    tags=["重点", "难点", "高频"],
    verify=[{"desc": "特征值", "code": "M([[1,1,0],[1,1,0],[0,0,-1]]).eigenvals()", "expected": "{2: 1, 0: 1, -1: 1}"},
            {"desc": "r(A)", "code": "M([[1,1,0],[1,1,0],[0,0,-1]]).rank()", "expected": "2"},
            {"desc": "|A|（前两行相同故为 0）", "code": "M([[1,1,0],[1,1,0],[0,0,-1]]).det()", "expected": "0"}]))

# ─────────────────────────────────────────────── 多选 6（基础2 中等3 困难1）
Q_.append(Q(MULTI, "basic", "5.1",
    "关于实向量的内积与正交，下列说法正确的有",
    answer=["A", "B", "C"],
    options=["内积满足对称性：$(\\alpha,\\beta)=(\\beta,\\alpha)$",
             "非零向量 $\\alpha$ 与 $\\beta$ 正交，当且仅当 $(\\alpha,\\beta)=0$",
             "若 $\\alpha,\\beta$ 都非零且 $\\alpha\\perp\\beta$，则 $\\alpha,\\beta$ 线性无关",
             "正交关系具有传递性：若 $\\alpha\\perp\\beta$ 且 $\\beta\\perp\\gamma$，则 $\\alpha\\perp\\gamma$"],
    expl="**答案依据**：§5.1。实数域上 $(\\alpha,\\beta)=\\sum_{i=1}^n x_iy_i$，满足 $(\\alpha,\\beta)=(\\beta,\\alpha)$（A）；$(\\alpha,\\beta)=0$ 即定义为正交（B）；若 $\\alpha\\perp\\beta$ 且两者非零，设 $k_1\\alpha+k_2\\beta=0$，两边与 $\\alpha$ 作内积得 $k_2(\\beta,\\alpha)=0$，故 $k_2=0$，同理 $k_1=0$，故线性无关（C）。\n"
         "D 错：正交关系**没有传递性**。反例：$\\alpha=(1,0,0)^{\\mathsf T}$，$\\beta=(0,1,0)^{\\mathsf T}$，$\\gamma=(1,0,1)^{\\mathsf T}$，则 $(\\alpha,\\beta)=0$、$(\\beta,\\gamma)=0$，但 $(\\alpha,\\gamma)=1\\neq0$，即 $\\alpha$ 与 $\\gamma$ 不正交。",
    mis="⚠️易错点：默认「垂直于垂直就垂直」。正交只对同一对向量成立，没有传递性；也不要把正交与「线性无关」记混——非零向量正交 $\\iff$ 线性无关。",
    tags=["重点", "高频"],
    verify=[{"desc": "反例内积 alpha.gamma", "code": "M([[1,0,0]]).dot(M([[1,0,1]]))", "expected": "1"},
            {"desc": "反例内积 beta.gamma", "code": "M([[0,1,0]]).dot(M([[1,0,1]]))", "expected": "0"}]))

Q_.append(Q(MULTI, "basic", "5.2",
    "设 $A$ 为 $n$ 阶方阵，关于 $A$ 的特征值与特征向量，下列说法正确的有",
    answer=["A", "B", "C"],
    options=["$\\lambda$ 是 $A$ 的特征值 $\\iff$ $|\\lambda E-A|=0$",
             "若 $\\lambda$ 是 $A$ 的特征值，则齐次方程组 $(\\lambda E-A)x=0$ 的解空间是由属于 $\\lambda$ 的特征向量生成的线性子空间",
             "$A$ 的全部特征值（按重数计）之和等于 $A$ 的主对角线元素之和",
             "$A$ 的全部特征值之积等于 $A$ 的秩"],
    expl="**答案依据**：§5.2。特征值定义为使 $|\\lambda E-A|=0$ 成立的 $\\lambda$（A）；属于 $\\lambda$ 的特征向量正是 $(\\lambda E-A)x=0$ 的非零解，连同零向量构成解空间 $N(A-\\lambda E)$（特征子空间）（B）；特征多项式 $|\\lambda E-A|=\\lambda^n-a_{11}\\lambda^{n-1}+\\cdots+(-1)^n|A|$ 由韦达定理给出「特征值之和 $=$ 主对角线元素之和、特征值之积 $=$ $|A|$」（C）。\n"
         "D 错：特征值之积等于行列式 $|A|$，而不是秩。例如 $A=\\begin{pmatrix}1&0\\\\0&1\\end{pmatrix}$，特征值之积为 $1$，而 $r(A)=2$；又如 $A=\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix}$，特征值之积为 $0$ 而 $r(A)=1$。",
    mis="⚠️易错点：把「特征值之积」记成行列式是对的，但记成秩就错了；另外「特征值之和 $=$ 迹」必须**按重数计**。",
    tags=["重点", "高频"],
    verify=[{"desc": "反例1 特征值", "code": "M([[1,0],[0,1]]).eigenvals()", "expected": "{1: 2}"},
            {"desc": "反例1 秩", "code": "M([[1,0],[0,1]]).rank()", "expected": "2"},
            {"desc": "反例2 特征值", "code": "M([[0,1],[0,0]]).eigenvals()", "expected": "{0: 2}"},
            {"desc": "反例2 秩", "code": "M([[0,1],[0,0]]).rank()", "expected": "1"}]))

Q_.append(Q(MULTI, "medium", "5.3",
    "设 $A,B$ 均为 $n$ 阶方阵，且 $B=P^{-1}AP$（$P$ 可逆）。则下列结论正确的有",
    answer=["A", "B", "C"],
    options=["$A$ 与 $B$ 有相同的特征多项式，从而有相同的特征值",
             "$|A|=|B|$",
             "$r(A)=r(B)$",
             "$A$ 与 $B$ 有相同的特征向量"],
    expl="**答案依据**：§5.3 相似矩阵的基本性质。\n"
         "A：$|\\lambda E-B|=|P^{-1}(\\lambda E-A)P|=|P^{-1}|\\,|\\lambda E-A|\\,|P|=|\\lambda E-A|$，故特征多项式与特征值都相同；\n"
         "B：在 A 中令 $\\lambda=0$ 即得 $|B|=|A|$（也可由 $|P^{-1}||P|=1$ 直接算出）；\n"
         "C：$B=P^{-1}AP$，由 §3.2 的秩的乘法规律 $r(PA)=r(AP)$ 得 $r(B)=r(A)$。\n"
         "D 错：相似变换把特征向量**一并变换**——若 $A\\alpha=\\lambda\\alpha$，则 $B(P^{-1}\\alpha)=P^{-1}A\\alpha=\\lambda(P^{-1}\\alpha)$，即 $A$ 的特征向量 $\\alpha$ 对应的是 $B$ 的特征向量 $P^{-1}\\alpha$，二者一般不是同一个向量。",
    mis="⚠️易错点：认为相似矩阵「连特征向量都一样」。相似保持的是**特征值**这一层不变量，特征向量会被 $P^{-1}$ 改写。",
    tags=["重点", "高频"],
    verify=[{"desc": "B=P^-1AP", "code": "P=M([[1,0],[0,2]]); A=M([[1,2],[0,3]]); str(P.inv()*A*P)", "expected": "Matrix([[1, 4], [0, 3]])"},
            {"desc": "特征值不变", "code": "P=M([[1,0],[0,2]]); A=M([[1,2],[0,3]]); str((P.inv()*A*P).eigenvals())", "expected": "{3: 1, 1: 1}"}]))

Q_.append(Q(MULTI, "medium", "5.7",
    "设 $A$ 为 $n$ 阶实对称矩阵，关于 $A$ 的正定性，下列结论正确的有",
    answer=["A", "B", "D"],
    options=["$A$ 正定 $\\iff$ $A$ 的全部特征值都为正数",
             "$A$ 正定 $\\iff$ $A$ 的各阶顺序主子式全大于零",
             "若 $A$ 正定，则 $-A$ 也正定",
             "若 $A$ 正定，则 $A$ 的主对角线元素 $a_{ii}$ 全大于零"],
    expl="**答案依据**：§5.7 正定二次型的判别法。实对称矩阵 $A$ 正定 $\\iff$ $A$ 的特征值全为正数（A，这是 §5.4 正交对角化的直接推论）；正定 $\\iff$ 各阶顺序主子式全大于零（Sylvester 判据）（B）；正定时对任意 $x\\neq0$ 有 $x^{\\mathsf T}Ax>0$，取 $x=e_i$ 即得 $a_{ii}=e_i^{\\mathsf T}Ae_i>0$（D）。\n"
         "C 错：$-A$ 的特征值是 $A$ 的特征值的相反数，若 $A$ 正定则 $-A$ 的特征值全为负，$-A$ 是**负定**而不是正定。",
    mis="⚠️易错点：以为「正定」对取负号封闭。$-A$ 是负定的；只有当 $A$ 奇异（$f$ 半正定）时才可能同时有零特征值，但 $-A$ 仍然不是正定矩阵。",
    tags=["重点", "高频"],
    verify=[{"desc": "正定矩阵", "code": "M([[2,1],[1,2]]).is_positive_definite", "expected": "True"},
            {"desc": "其特征值", "code": "M([[2,1],[1,2]]).eigenvals()", "expected": "{3: 1, 1: 1}"},
            {"desc": "取负后不正定", "code": "M([[-2,-1],[-1,-2]]).is_positive_definite", "expected": "False"}]))

Q_.append(Q(MULTI, "medium", "5.4",
    "设 $A$ 为 $n$ 阶实对称矩阵，下列结论正确的有",
    answer=["A", "B", "C"],
    options=["$A$ 的特征值全为实数",
             "属于 $A$ 的不同特征值的特征向量相互正交",
             "存在正交矩阵 $Q$，使 $Q^{\\mathsf T}AQ=\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_n)$，其中 $\\lambda_i$ 为 $A$ 的特征值",
             "若 $\\lambda$ 是 $A$ 的 $r$ 重特征值，则属于 $\\lambda$ 的线性无关特征向量只有 $n-r$ 个"],
    expl="**答案依据**：§5.4 实对称矩阵的对角化定理：① 特征值全为实数（A）；② 属于不同特征值的特征向量相互正交（B）；③ 存在正交矩阵 $Q$ 使 $Q^{\\mathsf T}AQ=\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_n)$，$Q$ 的列向量构成 $A$ 的标准正交特征向量组（C）；④ 每个特征值的**重数等于其特征子空间的维数**，即 $r$ 重特征值恰有 $r$ 个线性无关的特征向量。\n"
         "D 错：个数应是 $r$ 而不是 $n-r$。例如 $A=\\begin{pmatrix}2&0\\\\0&2\\end{pmatrix}$，$2$ 是 $2$ 重特征值，属于 $2$ 的线性无关特征向量有 $2$ 个（如 $(1,0)^{\\mathsf T},(0,1)^{\\mathsf T}$），而不是 $n-r=0$ 个。",
    mis="⚠️易错点：把「不同特征值的特征向量正交」扩大到「同一特征值的特征向量也正交」，或者把重数 $r$ 与 $n-r$ 记混。",
    tags=["重点", "高频"],
    verify=[{"desc": "反例内积", "code": "M([[1,0]]).dot(M([[0,1]]))", "expected": "0"},
            {"desc": "同特征值两向量内积", "code": "M([[1,0]]).dot(M([[2,0]]))", "expected": "2"}]))

Q_.append(Q(MULTI, "hard", "5.5",
    "关于二次型、合同变换与规范形，下列说法正确的有",
    answer=["A", "B", "D"],
    options=["每个 $n$ 元实二次型都有唯一确定的**对称**矩阵 $A$，使 $f(x)=x^{\\mathsf T}Ax$",
             "作可逆线性变换 $x=Cy$（$C$ 可逆）后，二次型的矩阵由 $A$ 变为 $C^{\\mathsf T}AC$，这称为**合同**变换",
             "任意两个 $n$ 阶实对称矩阵都合同",
             "$A$ 与 $B$（均为实对称阵）合同 $\\iff$ 它们有相同的秩和相同的正惯性指数"],
    expl="**答案依据**：§5.5。二次型 $f(x)=\\sum_{i,j}a_{ij}x_ix_j$ 的矩阵取对称形式：$a_{ii}$ 为 $x_i^2$ 的系数，$a_{ij}=a_{ji}$ 取交叉项系数的一半，故对称阵 $A$ 唯一（A）；变量变换 $x=Cy$ 使 $f=x^{\\mathsf T}Ax=y^{\\mathsf T}C^{\\mathsf T}ACy$，矩阵由 $A$ 变为 $C^{\\mathsf T}AC$，这正是合同变换（B）；由惯性定理，$A,B$ 合同 $\\iff$ 秩相同且正惯性指数相同（D）。\n"
         "C 错：合同保持**惯性指数**（正特征值个数与负特征值个数），并非任意两个实对称矩阵都合同。反例 $A=\\begin{pmatrix}1&0\\\\0&0\\end{pmatrix}$（$p=1,q=0$，正定）与 $B=\\begin{pmatrix}-1&0\\\\0&0\\end{pmatrix}$（$p=0,q=1$，负定）：二者秩都是 $1$，但惯性指数不同，故**不合同**。\n"
         "**引申**：合同变换要求 $C$ 可逆但形式为 $C^{\\mathsf T}AC$（作用在矩阵两边），而相似变换是 $P^{-1}AP$（形式为共轭）。对**实对称矩阵**而言，由「特征值决定惯性」可知相似与合同恰好一致；但对一般矩阵二者毫不相干。",
    mis="⚠️易错点：把合同与相似混为一谈，或者认为「秩相同就合同」。合同要同时看秩和正惯性指数。",
    tags=["重点", "难点", "跨章"],
    verify=[{"desc": "A 的特征值", "code": "M([[1,0],[0,0]]).eigenvals()", "expected": "{1: 1, 0: 1}"},
            {"desc": "B 的特征值", "code": "M([[-1,0],[0,0]]).eigenvals()", "expected": "{-1: 1, 0: 1}"},
            {"desc": "A 的秩", "code": "M([[1,0],[0,0]]).rank()", "expected": "1"},
            {"desc": "B 的秩", "code": "M([[-1,0],[0,0]]).rank()", "expected": "1"}]))

# ─────────────────────────────────────────────── 判断 4（基础1 中等3 困难0）
Q_.append(Q(JUDGE, "basic", "5.2",
    "若 $\\lambda_0$ 是方阵 $A$ 的特征值，则齐次线性方程组 $(A-\\lambda_0E)x=0$ 必有非零解。",
    answer=["A"],
    expl="**答案依据**：特征值的定义（§5.2）：$\\lambda_0$ 是 $A$ 的特征值，当且仅当 $|A-\\lambda_0E|=0$，即 $A-\\lambda_0E$ 奇异；由 §3.3 线性方程组解的判定，齐次方程组 $(A-\\lambda_0E)x=0$ 有非零解，其非零解就是属于 $\\lambda_0$ 的特征向量。\n"
         "反过来说，若该方程组只有零解，则 $\\lambda_0$ **不是** $A$ 的特征值。",
    mis="⚠️易错点：把特征向量与任意非零解混为一谈——非零解必须与特征值 $\\lambda_0$ 绑定才有意义；且零向量对任何 $\\lambda$ 都满足 $A0=\\lambda0$，故不能作特征向量。",
    tags=["基础", "定义"]))

Q_.append(Q(JUDGE, "medium", "5.1",
    "任意两个非零向量 $\\alpha,\\beta$ 线性相关，当且仅当 $\\alpha\\perp\\beta$。",
    answer=["B"],
    expl="**答案依据**：命题错误（§5.1 与 §4.2）。\n"
         "正方向不成立：若 $\\alpha\\perp\\beta$ 且两者非零，则 $\\alpha,\\beta$ 必然**线性无关**（设 $k_1\\alpha+k_2\\beta=0$，与 $\\alpha$ 作内积得 $k_2(\\beta,\\alpha)=0$，故 $k_2=0$，同理 $k_1=0$），这与「线性相关」正相反。\n"
         "逆方向也不成立：线性相关的两个非零向量互相平行（$\\beta=k\\alpha$，$k\\neq0$），此时 $(\\alpha,\\beta)=k\\|\\alpha\\|^2\\neq0$，**不**正交。\n"
         "故这个充要关系两头都不成立，正确说法是「两个非零向量正交 $\\iff$ 它们线性无关」。",
    mis="⚠️易错点：把「正交」与「线性相关／线性无关」的关系记反。正确结论是：两个非零向量正交 $\\iff$ 线性无关。",
    tags=["易错", "高频"]))

Q_.append(Q(JUDGE, "medium", "5.7",
    "设 $A$ 为实对称矩阵，则 $A$ 正定的充要条件是 $A$ 的各阶顺序主子式都大于零。",
    answer=["A"],
    expl="**答案依据**：§5.7 的 Sylvester 判别法（正定判别法）：实对称矩阵 $A$ 正定 $\\iff$ $A$ 的**各阶顺序主子式** $A_k$（取前 $k$ 行前 $k$ 列所得子式）全大于零。\n"
         "要点：① 前提是 $A$ 为**实对称矩阵**，非对称矩阵不能用此判据；② 判据用的是**顺序**主子式 $A_1,A_2,\\dots,A_n$（前导主子式），不是任意挑选的主子式；③ 这与「特征值全为正」的判据等价。",
    mis="⚠️易错点：忘记「实对称」这个前提，或者把「顺序主子式」写成「任意主子式」。",
    tags=["必背", "高频"],
    verify=[{"desc": "正定矩阵的顺序主子式", "code": "M([[2,1],[1,2]])[0,0]", "expected": "2"},
            {"desc": "二阶顺序主子式", "code": "M([[2,1],[1,2]]).det()", "expected": "3"}]))

Q_.append(Q(JUDGE, "medium", "5.4",
    "实对称矩阵 $A$ 的任意两个特征向量都相互正交。",
    answer=["B"],
    expl="**答案依据**：命题错误（§5.4）。正交定理说的是：**属于不同特征值的**特征向量相互正交，而不是任意两个特征向量都正交。\n"
         "反例：$A=\\begin{pmatrix}2&0\\\\0&2\\end{pmatrix}$ 的特征值只有 $2$（二重），$(1,0)^{\\mathsf T}$ 与 $(2,0)^{\\mathsf T}$ 都是属于 $2$ 的特征向量，但它们共线，内积为 $2\\neq0$，并不正交。\n"
         "只有当两个特征向量属于**不同**特征值时才保证正交；同一特征值的特征向量之间要另外设法（如用施密特正交化）才能得到正交组。",
    mis="⚠️易错点：把「不同特征值的特征向量正交」扩大成「任意两个特征向量正交」。",
    tags=["易错", "高频"],
    verify=[{"desc": "同特征值两向量内积", "code": "M([[1,0]]).dot(M([[2,0]]))", "expected": "2"}]))

# ─────────────────────────────────────────────── 填空 6（基础2 中等3 困难1）
Q_.append(Q(BLANK, "basic", "5.1",
    "设 $\\alpha=(1,2,2)^{\\mathsf T}$，则 $\\|\\alpha\\|=$ ______ 。",
    answer=["3"],
    accept=["3"],
    expl="**答案依据**：向量的长度（§5.1）$\\|\\alpha\\|=\\sqrt{(\\alpha,\\alpha)}$，故\n"
         "$\\|\\alpha\\|=\\sqrt{1^2+2^2+2^2}=\\sqrt9=3$。",
    mis="⚠️易错点：把长度写成 $\\|\\alpha\\|^2=9$（那是平方范数），或忘记开方。",
    tags=["计算"],
    verify=[{"desc": "长度", "code": "sqrt(M([[1,2,2]]).dot(M([[1,2,2]])))", "expected": "3"},
            {"desc": "长度平方", "code": "M([[1,2,2]]).dot(M([[1,2,2]]))", "expected": "9"}]))

Q_.append(Q(BLANK, "basic", "5.2",
    "设 $A=\\begin{pmatrix}1&1\\\\0&2\\end{pmatrix}$，则 $A$ 的两个特征值中**较大**的那个是 ______ 。",
    answer=["2"],
    accept=["2"],
    expl="**答案依据**：$|\\lambda E-A|=\\begin{vmatrix}\\lambda-1&-1\\\\0&\\lambda-2\\end{vmatrix}=(\\lambda-1)(\\lambda-2)$，故特征值为 $1$ 与 $2$，较大者是 $2$（§5.2）。",
    mis="⚠️易错点：把特征方程写成 $|A-\\lambda E|$ 时把根的符号搞乱；本题两种写法同解，但 $n$ 为奇数时 $|A-\\lambda E|=-|\\lambda E-A|$。",
    tags=["计算", "高频"],
    verify=[{"desc": "特征值", "code": "M([[1,1],[0,2]]).eigenvals()", "expected": "{2: 1, 1: 1}"}]))

Q_.append(Q(BLANK, "medium", "5.5",
    "二次型 $f(x_1,x_2,x_3)=x_1^2+2x_2^2+3x_3^2-2x_1x_2$ 的矩阵的**秩**为 ______ 。",
    answer=["3"],
    accept=["3"],
    expl="**答案依据**：二次型的矩阵取对称形式：$x_1^2$ 的系数为 $a_{11}=1$，交叉项 $-2x_1x_2$ 的系数为 $-2$，故 $a_{12}=a_{21}=-1$（交叉项系数取一半），$a_{22}=2$，$a_{33}=3$，无 $x_1x_3$、$x_2x_3$ 项，故\n"
         "$$A=\\begin{pmatrix}1&-1&0\\\\-1&2&0\\\\0&0&3\\end{pmatrix}.$$\n"
         "按第一行展开：$|A|=1\\cdot\\begin{vmatrix}2&0\\\\0&3\\end{vmatrix}-(-1)\\cdot\\begin{vmatrix}-1&0\\\\0&3\\end{vmatrix}=1\\cdot6+1\\cdot(-3)=3\\neq0$，故 $r(A)=3$，即二次型 $f$ 的秩为 $3$（§5.5）。",
    mis="⚠️易错点：交叉项 $-2x_1x_2$ 的系数取成 $-2$（忘记取一半），会得到错误的对角元；二次型的秩就是其矩阵的秩。",
    tags=["计算", "高频"],
    verify=[{"desc": "rank", "code": "M([[1,-1,0],[-1,2,0],[0,0,3]]).rank()", "expected": "3"},
            {"desc": "det", "code": "M([[1,-1,0],[-1,2,0],[0,0,3]]).det()", "expected": "3"}]))

Q_.append(Q(BLANK, "medium", "5.7",
    "设 $A=\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}$，则 $A$ 的二阶顺序主子式为 ______ 。",
    answer=["3"],
    accept=["3"],
    expl="**答案依据**：二阶顺序主子式即取 $A$ 的前两行、前两列所得的子式：\n"
         "$$A_2=\\begin{vmatrix}2&1\\\\1&2\\end{vmatrix}=2\\times2-1\\times1=3>0,$$\n"
         "且一阶顺序主子式 $A_1=2>0$，由 Sylvester 判据（§5.7）知 $A$ 正定。",
    mis="⚠️易错点：把「顺序主子式」误算成「由任意两行两列取出的子式」；本题所有二阶主子式恰好都等于 $3$，容易掩盖这一差别。",
    tags=["高频"],
    verify=[{"desc": "二阶顺序主子式", "code": "M([[2,1],[1,2]]).det()", "expected": "3"},
            {"desc": "一阶顺序主子式", "code": "M([[2,1],[1,2]])[0,0]", "expected": "2"}]))

Q_.append(Q(BLANK, "medium", "5.6",
    "用配方法把二次型 $f(x_1,x_2)=x_1^2+2x_1x_2+3x_2^2$ 化为标准形 $y_1^2+k\\,y_2^2$，则 $k=$ ______ 。",
    answer=["2"],
    accept=["2"],
    expl="**答案依据**：配方（§5.6）：\n"
         "$$f=(x_1^2+2x_1x_2)+3x_2^2=(x_1+x_2)^2+3x_2^2-x_2^2=(x_1+x_2)^2+2x_2^2.$$\n"
         "令 $y_1=x_1+x_2$，$y_2=x_2$，得标准形 $y_1^2+2y_2^2$，故 $k=2$。\n"
         "（合同验算：$A=\\begin{pmatrix}1&1\\\\1&3\\end{pmatrix}$，取 $C=\\begin{pmatrix}1&-1\\\\0&1\\end{pmatrix}$，则 $C^{\\mathsf T}AC=\\begin{pmatrix}1&0\\\\0&2\\end{pmatrix}$。）",
    mis="⚠️易错点：配方时忘了把展开 $(x_1+x_2)^2$ 带来的 $x_2^2$ 从 $3x_2^2$ 中扣掉，误得 $k=3$。",
    tags=["计算", "高频"],
    verify=[{"desc": "合同变换结果", "code": "C=M([[1,-1],[0,1]]); A=M([[1,1],[1,3]]); str(expand(C.T*A*C))", "expected": "Matrix([[1, 0], [0, 2]])"},
            {"desc": "正定性", "code": "M([[1,1],[1,3]]).is_positive_definite", "expected": "True"}]))

Q_.append(Q(BLANK, "hard", "5.4",
    "设实对称矩阵 $A=\\begin{pmatrix}0&1&0\\\\1&0&0\\\\0&0&1\\end{pmatrix}$，则 $A$ 的三个特征值（从小到大排列，用逗号分隔）是 ______ 。",
    answer=["-1,1,1"],
    accept=["-1,1,1", "-1, 1, 1", "(-1,1,1)", "-1，1，1"],
    expl="**答案依据**：由 §5.4，实对称矩阵的特征值全为实数。前两行前两列构成的子块 $\\begin{pmatrix}0&1\\\\1&0\\end{pmatrix}$ 的特征值为 $1$ 与 $-1$，第三个特征值为 $1$，故特征值为 $-1,1,1$。\n"
         "相应的特征子空间：$\\lambda=1$ 时 $Ax=x\\iff x=y$，解空间 $\\{(t,t,s)^{\\mathsf T}\\}$（二维，对应二重特征值 $1$）；$\\lambda=-1$ 时 $Ax=-x\\iff x=-y$，解空间 $\\{(t,-t,0)^{\\mathsf T}\\}$（一维）。",
    mis="⚠️易错点：把实对称矩阵的零特征值或重特征值的个数数错；本题特征值 $-1$ 为一重、$1$ 为二重，顺序按从小到大写。",
    tags=["难点", "高频"],
    verify=[{"desc": "特征值", "code": "M([[0,1,0],[1,0,0],[0,0,1]]).eigenvals()", "expected": "{-1: 1, 1: 2}"},
            {"desc": "特征多项式", "code": "lam=symbols('lam'); expand(M([[0,1,0],[1,0,0],[0,0,1]]).charpoly(lam).as_expr())", "expected": "lam**3 - lam**2 - lam + 1"}]))

# ─────────────────────────────────────────────── 名词解释 3（基础3）
Q_.append(Q(TERM, "basic", "5.1",
    "名词解释：**内积**与**向量的长度**（数量积与模）。",
    answer_text="**内积（数量积，§5.1）**：设 $\\alpha=(x_1,x_2,\\dots,x_n)^{\\mathsf T}$，$\\beta=(y_1,y_2,\\dots,y_n)^{\\mathsf T}$ 是实数空间 $\\mathbf R^n$ 中的两个向量，把它们的对应分量相乘再求和所得的实数\n"
                "$$(\\alpha,\\beta)=x_1y_1+x_2y_2+\\cdots+x_ny_n=\\sum_{i=1}^n x_iy_i$$\n"
                "称为 $\\alpha$ 与 $\\beta$ 的**内积**，记作 $(\\alpha,\\beta)$ 或 $\\alpha^{\\mathsf T}\\beta$；它满足 $(\\alpha,\\beta)=(\\beta,\\alpha)$、$(\\lambda\\alpha,\\beta)=\\lambda(\\alpha,\\beta)$、$(\\alpha+\\beta,\\gamma)=(\\alpha,\\gamma)+(\\beta,\\gamma)$。\n\n"
                "**长度（模）**：非负实数\n$$\\|\\alpha\\|=\\sqrt{(\\alpha,\\alpha)}=\\sqrt{x_1^2+x_2^2+\\cdots+x_n^2}$$\n"
                "称为向量 $\\alpha$ 的**长度**；且 $\\|\\alpha\\|=0$ 当且仅当 $\\alpha=0$，$\\|\\alpha\\|>0$ 当且仅当 $\\alpha\\neq0$。\n\n"
                "**正交**：若 $(\\alpha,\\beta)=0$，称 $\\alpha$ 与 $\\beta$ **正交**（记作 $\\alpha\\perp\\beta$）；若向量组中任意两个向量都正交，则称其为**正交向量组**；长度都为 $1$ 的正交向量组称为**标准正交向量组**。",
    points=[{"text": "写出内积的定义 $(\\alpha,\\beta)=\\sum_{i=1}^n x_iy_i$（是一个实数），并指出它满足对称性等内积公理", "partial": 2},
            {"text": "写出长度的定义 $\\|\\alpha\\|=\\sqrt{(\\alpha,\\alpha)}$，并给出正交的定义 $(\\alpha,\\beta)=0$ 以及标准正交向量组的含义", "partial": 2}],
    expl="**答案依据**：§5.1 向量的内积、长度及正交性。\n"
         "**考点出处**：同济《线性代数》第六版 §5.1 向量的内积、长度及正交性。",
    mis="⚠️易错点：把内积与 $\\alpha^{\\mathsf T}\\beta$ 写成矩阵乘法却不说明结果是**数**；把「长度」与「长度的平方」混淆。",
    tags=["名词解释", "必背"]))

Q_.append(Q(TERM, "basic", "5.2",
    "名词解释：**特征值**与**特征向量**。",
    answer_text="设 $A$ 是 $n$ 阶方阵。如果数 $\\lambda$ 使齐次方程组 $(\\lambda E-A)x=0$ 有非零解 $x$，即存在 $\\alpha\\neq0$ 使得\n"
                "$$A\\alpha=\\lambda\\alpha,$$\n"
                "那么称数 $\\lambda$ 是方阵 $A$ 的一个**特征值**，称非零向量 $\\alpha$ 是 $A$ 的属于（对应于）特征值 $\\lambda$ 的**特征向量**，$\\lambda$ 可以是实数也可以是复数。\n\n"
                "等价说法：$\\lambda$ 是 $A$ 的特征值 $\\iff$ $|\\lambda E-A|=0$，即 $\\lambda$ 是**特征多项式** $p(\\lambda)=|\\lambda E-A|$ 的根。\n\n"
                "要点：① 特征向量必须是**非零**向量（零向量对任意 $\\lambda$ 都满足 $A0=\\lambda0$，故不能充当特征向量）；② 属于同一特征值 $\\lambda$ 的全部特征向量连同零向量构成线性空间 $N(A-\\lambda E)$，称为 $A$ 的**特征子空间**，其维数称为该特征值的**几何重数**。",
    points=[{"text": "给出特征值的定义：存在非零向量 $\\alpha$ 使 $A\\alpha=\\lambda\\alpha$，或等价地 $\\lambda$ 是 $|\\lambda E-A|=0$ 的根", "partial": 2},
            {"text": "给出特征向量的定义并强调它必须非零，指出属于同一特征值的特征向量全体与零向量构成特征子空间", "partial": 2}],
    expl="**答案依据**：§5.2 方阵的特征值与特征向量。\n"
         "**考点出处**：同济《线性代数》第六版 §5.2 方阵的特征值与特征向量。",
    mis="⚠️易错点：漏掉「非零」这一限定；以及把「几何重数」（特征子空间维数）与「代数重数」（特征多项式中根的重数）混为一谈。",
    tags=["名词解释", "必背"]))

Q_.append(Q(TERM, "basic", "5.7",
    "名词解释：**正定二次型**与**正定矩阵**。",
    answer_text="设 $f(x_1,x_2,\\dots,x_n)=\\sum_{i,j}a_{ij}x_ix_j$ 是 $n$ 元实二次型，$A$ 是与它对应的对称矩阵，即 $f(x)=x^{\\mathsf T}Ax$。如果\n"
                "$$f(x)>0\\qquad\\text{对一切非零向量 }x,$$\n"
                "即对任意 $x\\neq0$ 都有 $x^{\\mathsf T}Ax>0$，就称 $f$ 是**正定二次型**，并称对称矩阵 $A$ 是**正定矩阵**。\n\n"
                "等价说法（§5.7）：实对称矩阵 $A$ 正定 $\\iff$ $A$ 的特征值全为正数 $\\iff$ $A$ 的各阶顺序主子式全大于零 $\\iff$ 存在可逆矩阵 $C$ 使 $C^{\\mathsf T}AC=E$。\n\n"
                "相对地：若对一切 $x\\neq0$ 有 $f(x)<0$，称 $f$ 为**负定**；若对一切 $x\\neq0$ 有 $f(x)\\ge0$，称 $f$ 为**半正定**（另有半负定、不定）。",
    points=[{"text": "给出正定二次型的定义：对一切非零 $x$ 有 $f(x)=x^{\\mathsf T}Ax>0$，并说明此时称矩阵 $A$ 为正定矩阵（$A$ 为实对称阵）", "partial": 2},
            {"text": "写出正定的等价判别（特征值全为正、顺序主子式全大于零中至少一种），并指出负定、半正定、不定的区分", "partial": 2}],
    expl="**答案依据**：§5.7 正定二次型。\n"
         "**考点出处**：同济《线性代数》第六版 §5.7 正定二次型。",
    mis="⚠️易错点：只写「$f(x)>0$」而不加「对一切非零 $x$」这个量词——在 $x=0$ 处 $f(0)=0$，$f$ 只能是半正定的。",
    tags=["名词解释", "重点"]))

# ─────────────────────────────────────────────── 简答 4（基础1 中等1 困难2）
Q_.append(Q(SHORT, "basic", "5.1",
    "写出施密特正交化方法的完整步骤，并说明它的作用。",
    answer_text="**步骤（§5.1）**：设 $\\alpha_1,\\alpha_2,\\dots,\\alpha_s$ 是 $\\mathbf R^n$ 中线性无关的向量组。先逐个去投影：\n"
                "$$\\beta_1=\\alpha_1,\\qquad \\beta_i=\\alpha_i-\\sum_{j=1}^{i-1}\\frac{(\\alpha_i,\\beta_j)}{(\\beta_j,\\beta_j)}\\beta_j\\quad(i=2,3,\\dots,s).$$\n"
                "再作标准化：\n$$\\gamma_i=\\frac{\\beta_i}{\\|\\beta_i\\|}=\\frac{\\beta_i}{\\sqrt{(\\beta_i,\\beta_i)}}\\quad(i=1,2,\\dots,s).$$\n\n"
                "**结论**：$\\beta_1,\\dots,\\beta_s$ 是与 $\\alpha_1,\\dots,\\alpha_s$ 等价（可互相线性表出）的**正交向量组**；$\\gamma_1,\\dots,\\gamma_s$ 是**标准正交向量组**。\n\n"
                "**作用与易错点**：① 它把一组线性无关向量变成标准正交向量组而不改变它们张成的子空间，是求正交基的通用方法，也是 §5.4 正交对角化、§5.5 合同变换的共同工具；② 被投影的内积 $(\\alpha_i,\\beta_j)$ 中必须用**已经正交化**的 $\\beta_j$，若误用原来的 $\\alpha_j$ 会算错；③ 分母 $(\\beta_j,\\beta_j)=\\|\\beta_j\\|^2$ 是 $\\beta_j$ 的长度平方，不是 $\\alpha_j$ 的。",
    points=[{"text": "写出递推式 $\\beta_1=\\alpha_1$、$\\beta_i=\\alpha_i-\\sum_{j<i}\\frac{(\\alpha_i,\\beta_j)}{(\\beta_j,\\beta_j)}\\beta_j$", "partial": 2},
            {"text": "写出标准化 $\\gamma_i=\\beta_i/\\|\\beta_i\\|$ 并说明所得为标准正交向量组、与原向量组等价", "partial": 2},
            {"text": "指出要点：内积中必须用正交化后的 $\\beta_j$、分母是 $\\|\\beta_j\\|^2$，并说明该方法的作用", "partial": 2}],
    expl="**答案依据**：§5.1 施密特正交化方法；与 §5.4、§5.5 联用。\n"
         "**考点出处**：同济《线性代数》第六版 §5.1 向量的内积、长度及正交性。",
    mis="⚠️易错点：递推式里把 $\\beta_j$ 写成 $\\alpha_j$；或者分母写成 $\\|\\alpha_j\\|^2$。",
    tags=["重点", "必背"]))

Q_.append(Q(SHORT, "medium", "5.3",
    "写出方阵 $A$ 可相似对角化的充要条件，并给出一个不可对角化的矩阵例子。",
    answer_text="**充要条件（§5.3）**：$n$ 阶方阵 $A$ 可相似对角化（存在可逆矩阵 $P$ 使 $P^{-1}AP=\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_n)$）的充要条件是：$A$ 有 $n$ 个**线性无关的特征向量**；等价地说，$A$ 的每个特征值的**几何重数等于其代数重数**。\n\n"
                 "**充分性**：若 $\\alpha_1,\\dots,\\alpha_n$ 是 $A$ 的 $n$ 个线性无关特征向量，分别属于 $\\lambda_1,\\dots,\\lambda_n$，令 $P=(\\alpha_1,\\dots,\\alpha_n)$，则 $AP=P\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_n)$，左乘 $P^{-1}$ 即得 $P^{-1}AP=\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_n)$。\n\n"
                 "**必要性**：若 $P^{-1}AP=\\Lambda$，则 $AP=P\\Lambda$，即 $P$ 的各列都是 $A$ 的特征向量，且分属不同的对角元对应的特征值，故线性无关。\n\n"
                 "**反例**：$A=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$。特征方程 $|\\lambda E-A|=(\\lambda-1)^2=0$，只有特征值 $\\lambda=1$（二重）。但\n"
                 "$$(A-E)=\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix},\\qquad r(A-E)=1,$$\n"
                 "故齐次方程组 $(A-E)x=0$ 的解空间维数为 $2-1=1$，属于 $\\lambda=1$ 的线性无关特征向量只有 $1$ 个（少于 $n=2$），几何重数 $1<2$ 不等于代数重数 $2$，所以 $A$ **不可对角化**。",
    points=[{"text": "给出充要条件：$A$ 有 $n$ 个线性无关的特征向量（等价于每个特征值几何重数等于代数重数）", "partial": 2},
            {"text": "证明充分性与必要性（利用 $AP=P\\Lambda$，$P$ 的列即特征向量）", "partial": 2},
            {"text": "给出反例 $A=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$，算出 $r(A-E)=1$、特征子空间维数为 1，说明其不可对角化", "partial": 2}],
    expl="**答案依据**：§5.3 相似对角化；与 §5.4「实对称矩阵必可对角化」对照。\n"
         "**考点出处**：同济《线性代数》第六版 §5.3 相似矩阵。\n"
         "**引申**：本条件与「对称」无关——实对称矩阵之所以一定可对角化，正是因为对实对称矩阵每个特征值的几何重数恒等于代数重数。",
    mis="⚠️易错点：以为「特征方程有 $n$ 个根（按重数）就能对角化」。必要条件是**特征向量**有 $n$ 个，重根存在时未必够。",
    tags=["重点", "高频"],
    verify=[{"desc": "反例的特征值", "code": "M([[1,1],[0,1]]).eigenvals()", "expected": "{1: 2}"},
            {"desc": "r(A-E)", "code": "(M([[1,1],[0,1]])-eye(2)).rank()", "expected": "1"}]))

Q_.append(Q(SHORT, "hard", "5.4",
    "证明：实对称矩阵属于**不同**特征值的两个特征向量相互正交，并说明该结论的适用范围。",
    answer_text="**证明（§5.4）**：设 $A$ 是实对称矩阵，$\\alpha,\\beta$ 分别是属于不同特征值 $\\lambda_1\\neq\\lambda_2$ 的特征向量，即\n"
                 "$$A\\alpha=\\lambda_1\\alpha,\\qquad A\\beta=\\lambda_2\\beta.$$\n"
                 "由于 $A^{\\mathsf T}=A$，且实向量的内积就是 $\\alpha^{\\mathsf T}\\beta$，故\n"
                 "$$(\\alpha,\\beta)=(A\\alpha)^{\\mathsf T}\\beta=(\\lambda_1\\alpha)^{\\mathsf T}\\beta=\\lambda_1\\alpha^{\\mathsf T}\\beta=\\lambda_1(\\alpha,\\beta),$$\n"
                 "$$(\\alpha,\\beta)=\\alpha^{\\mathsf T}A\\beta=\\alpha^{\\mathsf T}(\\lambda_2\\beta)=\\lambda_2\\alpha^{\\mathsf T}\\beta=\\lambda_2(\\alpha,\\beta).$$\n"
                 "两式相减得 $(\\lambda_1-\\lambda_2)(\\alpha,\\beta)=0$。因 $\\lambda_1\\neq\\lambda_2$，必有 $(\\alpha,\\beta)=0$，即 $\\alpha\\perp\\beta$。$\\qquad\\blacksquare$\n\n"
                 "**适用范围与说明**：① 关键一步用了 $A^{\\mathsf T}=A$，对一般矩阵不成立；② 结论只适用于**不同**特征值，同一特征值的两个特征向量未必正交；③ 由本定理可知实对称矩阵有 $n$ 个线性无关的特征向量，故一定可相似对角化，而且可取 $Q$ 为正交矩阵，这正是 §5.4 对角化定理的证明基础。",
    points=[{"text": "设 $\\alpha,\\beta$ 分属不同特征值 $\\lambda_1\\neq\\lambda_2$，写出 $A\\alpha=\\lambda_1\\alpha$、$A\\beta=\\lambda_2\\beta$", "partial": 2},
            {"text": "利用 $A^{\\mathsf T}=A$ 分别推出 $(\\alpha,\\beta)=\\lambda_1(\\alpha,\\beta)$ 与 $(\\alpha,\\beta)=\\lambda_2(\\alpha,\\beta)$", "partial": 2},
            {"text": "由 $(\\lambda_1-\\lambda_2)(\\alpha,\\beta)=0$ 且 $\\lambda_1\\neq\\lambda_2$ 得出 $\\alpha\\perp\\beta$，并指出结论只对不同特征值成立", "partial": 2}],
    expl="**答案依据**：§5.4 实对称矩阵特征值与特征向量的性质；用到 $A^{\\mathsf T}=A$ 与内积的转置不变性。\n"
         "**考点出处**：同济《线性代数》第六版 §5.4 对称矩阵的对角化。",
    mis="⚠️易错点：证明中漏掉 $A^{\\mathsf T}=A$ 这一步，直接写 $(\\alpha,\\beta)=(A\\alpha)^{\\mathsf T}\\beta$——这一步对一般矩阵不成立，是本题的关键条件。",
    tags=["难点", "证明", "高频"]))

Q_.append(Q(SHORT, "hard", "5.5",
    "设 $A$ 为 $n$ 阶实对称矩阵，二次型 $f(x)=x^{\\mathsf T}Ax$ 的秩为 $r$，正惯性指数为 $p$，负惯性指数为 $q$。① 说明 $r=p+q$ 的理由；② 写出 $f$ 的标准形与规范形；③ 说明为什么只给出秩不足以判别两个二次型是否合同。",
    answer_text="**① $r=p+q$（§5.5）**：由惯性定理，实对称矩阵 $A$ 经合同变换可化为对角阵\n"
                 "$$\\mathrm{diag}(\\lambda_1,\\dots,\\lambda_p,-\\mu_1,\\dots,-\\mu_q,0,\\dots,0),\\qquad \\lambda_i>0,\\ \\mu_j>0,$$\n"
                 "其对角元非零的个数恰为 $p+q$；而合同变换不改变矩阵的秩（$C$ 可逆，$C^{\\mathsf T}AC$ 与 $A$ 的秩相同），故 $r(A)=p+q$，即二次型的秩等于正、负惯性指数之和。\n\n"
                 "**② 标准形与规范形**：**标准形**（用合同变换或正交变换化成的对角形）为\n"
                 "$$\\lambda_1y_1^2+\\cdots+\\lambda_py_p^2-\\mu_1y_{p+1}^2-\\cdots-\\mu_qy_{p+q}^2,$$\n"
                 "其中系数是具体数值（合同变换下是配方所得的正数，正交变换下是 $A$ 的特征值）；**规范形**为\n"
                 "$$z_1^2+\\cdots+z_p^2-z_{p+1}^2-\\cdots-z_{p+q}^2,$$\n"
                 "只保留非零项，其余 $n-r$ 个变量不出现。规范形由 $(p,q)$ 唯一确定，故同一次二次型的规范形是唯一的。\n\n"
                 "**③ 只给秩不够**：$r$ 只反映非零项的个数，不区分正负。例如\n"
                 "$$A_1=\\begin{pmatrix}1&0\\\\0&0\\end{pmatrix},\\qquad A_2=\\begin{pmatrix}-1&0\\\\0&0\\end{pmatrix},$$\n"
                 "二者的秩都是 $1$，但 $A_1$ 的正惯性指数为 $1$、$A_2$ 的正惯性指数为 $0$；对应的二次型一个正定、一个负定，规范形分别是 $z_1^2$ 与 $-z_1^2$，二者**不合同**。所以判别两个二次型是否合同，必须同时给出秩和正惯性指数（这正是惯性定理的结论）。",
    points=[{"text": "说明 $r=p+q$ 的理由：合同化为对角阵后非零对角元个数为 $p+q$，且合同保持矩阵的秩", "partial": 2},
            {"text": "写出标准形与规范形的表达式，指出规范形由 $(p,q)$ 唯一确定、零变量个数为 $n-r$", "partial": 2},
            {"text": "举出秩相同但正惯性指数不同的反例（正定与负定），说明只给秩不足以判别合同", "partial": 2}],
    expl="**答案依据**：§5.5 二次型的秩、惯性指数、标准形与规范形；惯性定理。\n"
         "**考点出处**：同济《线性代数》第六版 §5.5 二次型及其标准形。",
    mis="⚠️易错点：把「标准形」与「规范形」混为一谈（标准形的系数是具体数值，规范形的系数只有 $\\pm1$）；以及误以为秩相同就合同。",
    tags=["难点", "重点", "高频"],
    verify=[{"desc": "反例1 特征值", "code": "M([[1,0],[0,0]]).eigenvals()", "expected": "{1: 1, 0: 1}"},
            {"desc": "反例2 特征值", "code": "M([[-1,0],[0,0]]).eigenvals()", "expected": "{-1: 1, 0: 1}"}]))

# ─────────────────────────────────────────────── 计算与分析 8（基础5 中等3 困难0）
Q_.append(Q(CALC, "basic", "5.2",
    "求方阵 $A=\\begin{pmatrix}1&2\\\\0&3\\end{pmatrix}$ 的特征值与对应的特征向量。",
    answer_text="**第一步 求特征值**：特征方程为 $|\\lambda E-A|=0$，\n"
                "$$|\\lambda E-A|=\\begin{vmatrix}\\lambda-1&-2\\\\0&\\lambda-3\\end{vmatrix}=(\\lambda-1)(\\lambda-3)=0.$$\n"
                "故 $A$ 的特征值为 $\\lambda_1=1$，$\\lambda_2=3$。\n\n"
                "**第二步 求属于 $\\lambda_1=1$ 的特征向量**：\n"
                "$$(A-E)x=0\\ \\Longleftrightarrow\\ \\begin{pmatrix}0&2\\\\0&2\\end{pmatrix}\\begin{pmatrix}x_1\\\\x_2\\end{pmatrix}=0\\ \\Longleftrightarrow\\ 2x_2=0\\ \\Longleftrightarrow\\ x_2=0,$$\n"
                "$x_1$ 任意。取 $x_1=1$，得属于特征值 $1$ 的特征向量 $\\alpha_1=\\begin{pmatrix}1\\\\0\\end{pmatrix}$（特征子空间为 $\\{(t,0)^{\\mathsf T}\\}$）。\n\n"
                "**第三步 求属于 $\\lambda_2=3$ 的特征向量**：\n"
                "$$(A-3E)x=0\\ \\Longleftrightarrow\\ \\begin{pmatrix}-2&2\\\\0&0\\end{pmatrix}\\begin{pmatrix}x_1\\\\x_2\\end{pmatrix}=0\\ \\Longleftrightarrow\\ x_1=x_2,$$\n"
                "$x_2$ 任意。取 $x_2=1$，得属于特征值 $3$ 的特征向量 $\\alpha_2=\\begin{pmatrix}1\\\\1\\end{pmatrix}$（特征子空间为 $\\{(t,t)^{\\mathsf T}\\}$）。\n\n"
                "**结论**：$A$ 有两个线性无关的特征向量，故 $A$ 可对角化；取 $P=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ 时 $P^{-1}AP=\\mathrm{diag}(1,3)$。",
    points=[{"text": "写出特征方程 $|\\lambda E-A|=(\\lambda-1)(\\lambda-3)=0$，求出特征值 $1$ 与 $3$", "partial": 2},
            {"text": "对 $\\lambda=1$ 解 $(A-E)x=0$ 得 $x_2=0$，给出特征向量 $(1,0)^{\\mathsf T}$", "partial": 2},
            {"text": "对 $\\lambda=3$ 解 $(A-3E)x=0$ 得 $x_1=x_2$，给出特征向量 $(1,1)^{\\mathsf T}$", "partial": 2},
            {"text": "指出两个特征向量线性无关、$A$ 可对角化，并写出 $P^{-1}AP=\\mathrm{diag}(1,3)$", "partial": 2}],
    expl="**答案依据**：§5.2 特征值与特征向量的求法（特征方程 + 解齐次方程组）。\n"
         "**考点出处**：同济《线性代数》第六版 §5.2 方阵的特征值与特征向量。",
    mis="⚠️易错点：解 $(A-\\lambda E)x=0$ 时把 $\\lambda$ 代入后算错元素；以及把零向量 $\\begin{pmatrix}0\\\\0\\end{pmatrix}$ 写成特征向量。",
    tags=["计算", "高频"],
    verify=[{"desc": "特征值", "code": "M([[1,2],[0,3]]).eigenvals()", "expected": "{3: 1, 1: 1}"},
            {"desc": "A·(1,0)", "code": "str(M([[1,2],[0,3]])*M([1,0]))", "expected": "Matrix([[1], [0]])"},
            {"desc": "A·(1,1)", "code": "str(M([[1,2],[0,3]])*M([1,1]))", "expected": "Matrix([[3], [3]])"}]))

Q_.append(Q(CALC, "basic", "5.1",
    "用施密特正交化方法把向量组 $\\alpha_1=(1,1,0)^{\\mathsf T}$，$\\alpha_2=(1,0,1)^{\\mathsf T}$，$\\alpha_3=(1,1,1)^{\\mathsf T}$ 化为标准正交向量组。",
    answer_text="**第一步** $\\beta_1=\\alpha_1=(1,1,0)^{\\mathsf T}$，$(\\beta_1,\\beta_1)=2$，$\\|\\beta_1\\|=\\sqrt2$，故\n"
                "$$\\gamma_1=\\frac{1}{\\sqrt2}(1,1,0)^{\\mathsf T}.$$\n\n"
                "**第二步** $\\beta_2=\\alpha_2-\\dfrac{(\\alpha_2,\\beta_1)}{(\\beta_1,\\beta_1)}\\beta_1$。因 $(\\alpha_2,\\beta_1)=1\\times1+0\\times1+1\\times0=1$，$(\\beta_1,\\beta_1)=2$，\n"
                "$$\\beta_2=(1,0,1)^{\\mathsf T}-\\frac12(1,1,0)^{\\mathsf T}=\\frac12(1,-1,2)^{\\mathsf T},$$\n"
                "$(\\beta_2,\\beta_2)=\\frac{1+1+4}{4}=\\frac32$，$\\|\\beta_2\\|=\\frac{\\sqrt6}{2}$，故\n"
                "$$\\gamma_2=\\frac{1}{\\sqrt6}(1,-1,2)^{\\mathsf T}.$$\n\n"
                "**第三步** $\\beta_3=\\alpha_3-\\dfrac{(\\alpha_3,\\beta_1)}{(\\beta_1,\\beta_1)}\\beta_1-\\dfrac{(\\alpha_3,\\beta_2)}{(\\beta_2,\\beta_2)}\\beta_2$。由 $(\\alpha_3,\\beta_1)=2$、$(\\alpha_3,\\beta_2)=\\frac12-\\frac12+1=1$、$(\\beta_2,\\beta_2)=\\frac32$ 得\n"
                "$$\\beta_3=(1,1,1)^{\\mathsf T}-(1,1,0)^{\\mathsf T}-\\frac23\\cdot\\frac12(1,-1,2)^{\\mathsf T}=\\frac13(-1,1,1)^{\\mathsf T},$$\n"
                "$(\\beta_3,\\beta_3)=\\frac{1+1+1}{9}=\\frac13$，$\\|\\beta_3\\|=\\frac{1}{\\sqrt3}$，故\n"
                "$$\\gamma_3=\\frac{1}{\\sqrt3}(-1,1,1)^{\\mathsf T}.$$\n\n"
                "**结果与检验**：\n$$\\gamma_1=\\frac{(1,1,0)^{\\mathsf T}}{\\sqrt2},\\qquad \\gamma_2=\\frac{(1,-1,2)^{\\mathsf T}}{\\sqrt6},\\qquad \\gamma_3=\\frac{(-1,1,1)^{\\mathsf T}}{\\sqrt3}.$$\n"
                "检验：$(1,1,0)\\cdot(1,-1,2)=0$，$(1,1,0)\\cdot(-1,1,1)=0$，$(1,-1,2)\\cdot(-1,1,1)=-1-1+2=0$，三组内积皆为零；且各向量长度平方分别为 $2,6,3$，归一化后长度均为 $1$，故 $\\gamma_1,\\gamma_2,\\gamma_3$ 确为标准正交向量组。",
    points=[{"text": "算出 $\\beta_1=(1,1,0)^{\\mathsf T}$ 并给出 $\\gamma_1=\\frac{1}{\\sqrt2}(1,1,0)^{\\mathsf T}$", "partial": 2},
            {"text": "算出 $\\beta_2=\\frac12(1,-1,2)^{\\mathsf T}$ 与 $\\gamma_2=\\frac{1}{\\sqrt6}(1,-1,2)^{\\mathsf T}$", "partial": 2},
            {"text": "算出 $\\beta_3=\\frac13(-1,1,1)^{\\mathsf T}$ 与 $\\gamma_3=\\frac{1}{\\sqrt3}(-1,1,1)^{\\mathsf T}$", "partial": 2},
            {"text": "验证两两正交且长度均为 $1$，说明所得为标准正交向量组", "partial": 2}],
    expl="**答案依据**：§5.1 施密特正交化方法。\n"
         "**考点出处**：同济《线性代数》第六版 §5.1 向量的内积、长度及正交性。",
    mis="⚠️易错点：第二步以后内积 $(\\alpha_i,\\beta_j)$ 中的 $\\beta_j$ 必须换成**已正交化**的向量；若沿用 $\\alpha_j$ 就会算错，且分母要用 $(\\beta_j,\\beta_j)$。",
    tags=["计算", "难点", "高频"],
    verify=[{"desc": "beta1 长度平方", "code": "M([[1,1,0]]).dot(M([[1,1,0]]))", "expected": "2"},
            {"desc": "beta2 长度平方", "code": "M([[1,-1,2]]).dot(M([[1,-1,2]]))", "expected": "6"},
            {"desc": "beta3 长度平方", "code": "M([[-1,1,1]]).dot(M([[-1,1,1]]))", "expected": "3"},
            {"desc": "正交 1·2", "code": "M([[1,1,0]]).dot(M([[1,-1,2]]))", "expected": "0"},
            {"desc": "正交 1·3", "code": "M([[1,1,0]]).dot(M([[-1,1,1]]))", "expected": "0"},
            {"desc": "正交 2·3", "code": "M([[1,-1,2]]).dot(M([[-1,1,1]]))", "expected": "0"}]))

Q_.append(Q(CALC, "basic", "5.3",
    "设 $A=\\begin{pmatrix}1&4\\\\0&3\\end{pmatrix}$，求可逆矩阵 $P$，使 $P^{-1}AP=\\mathrm{diag}(1,3)$。",
    answer_text="**思路**：若 $P^{-1}AP=\\Lambda$，则 $AP=P\\Lambda$，即 $P$ 的各列是 $A$ 的特征向量，且按 $\\Lambda$ 的对角元顺序排列。\n\n"
                "**第一步 求特征值**：\n"
                "$$|\\lambda E-A|=\\begin{vmatrix}\\lambda-1&-4\\\\0&\\lambda-3\\end{vmatrix}=(\\lambda-1)(\\lambda-3)=0,$$\n"
                "故特征值为 $\\lambda_1=1$，$\\lambda_2=3$。\n\n"
                "**第二步 求特征向量**：\n"
                "- 属于 $\\lambda_1=1$：$(A-E)x=0\\Longleftrightarrow\\begin{pmatrix}0&4\\\\0&2\\end{pmatrix}x=0\\Longleftrightarrow x_2=0$，取 $\\alpha_1=\\begin{pmatrix}1\\\\0\\end{pmatrix}$；\n"
                "- 属于 $\\lambda_2=3$：$(A-3E)x=0\\Longleftrightarrow\\begin{pmatrix}-2&4\\\\0&0\\end{pmatrix}x=0\\Longleftrightarrow x_1=2x_2$，取 $\\alpha_2=\\begin{pmatrix}2\\\\1\\end{pmatrix}$。\n\n"
                "**第三步 构造 $P$ 并验证**：令\n$$P=(\\alpha_1,\\alpha_2)=\\begin{pmatrix}1&2\\\\0&1\\end{pmatrix},\\qquad P^{-1}=\\begin{pmatrix}1&-2\\\\0&1\\end{pmatrix},\\qquad |P|=1\\neq0,$$\n"
                "则\n$$P^{-1}AP=\\begin{pmatrix}1&-2\\\\0&1\\end{pmatrix}\\begin{pmatrix}1&4\\\\0&3\\end{pmatrix}\\begin{pmatrix}1&2\\\\0&1\\end{pmatrix}=\\begin{pmatrix}1&0\\\\0&3\\end{pmatrix}.$$\n"
                "故所求 $P=\\begin{pmatrix}1&2\\\\0&1\\end{pmatrix}$（把特征向量换成其任意非零倍数仍可，所得 $P$ 不同但对角化结果相同）。",
    points=[{"text": "写出特征方程 $(\\lambda-1)(\\lambda-3)=0$，求出特征值 $1,3$", "partial": 2},
            {"text": "求出属于 $1$ 的特征向量 $(1,0)^{\\mathsf T}$ 与属于 $3$ 的特征向量 $(2,1)^{\\mathsf T}$", "partial": 2},
            {"text": "以特征向量为列构造 $P=\\begin{pmatrix}1&2\\\\0&1\\end{pmatrix}$ 并算出 $P^{-1}$、验证 $|P|\\neq0$", "partial": 2},
            {"text": "验证 $P^{-1}AP=\\mathrm{diag}(1,3)$，结论正确", "partial": 2}],
    expl="**答案依据**：§5.3 相似对角化——$P$ 的列取 $A$ 的特征向量。\n"
         "**考点出处**：同济《线性代数》第六版 §5.3 相似矩阵。",
    mis="⚠️易错点：把 $P$ 的列按**非**特征值顺序排列，那样得到的对角阵对角元会与特征值错位；另外别忘了 $P$ 必须可逆（本题 $|P|=1$）。",
    tags=["计算", "高频"],
    verify=[{"desc": "P^-1AP", "code": "P=M([[1,2],[0,1]]); A=M([[1,4],[0,3]]); str(P.inv()*A*P)", "expected": "Matrix([[1, 0], [0, 3]])"},
            {"desc": "|P|", "code": "M([[1,2],[0,1]]).det()", "expected": "1"},
            {"desc": "特征值", "code": "M([[1,4],[0,3]]).eigenvals()", "expected": "{3: 1, 1: 1}"}]))

Q_.append(Q(CALC, "basic", "5.4",
    "设实对称矩阵 $A=\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}$，用正交变换把 $A$ 化为标准形，并求正交矩阵 $Q$。",
    answer_text="**第一步 求特征值**：\n"
                "$$|\\lambda E-A|=\\begin{vmatrix}\\lambda-2&-1\\\\-1&\\lambda-2\\end{vmatrix}=(\\lambda-2)^2-1=(\\lambda-3)(\\lambda-1)=0,$$\n"
                "故 $\\lambda_1=3$，$\\lambda_2=1$。\n\n"
                "**第二步 求特征向量并单位化**：\n"
                "- $\\lambda_1=3$：$(A-3E)x=0\\Longleftrightarrow\\begin{pmatrix}-1&1\\\\1&-1\\end{pmatrix}x=0\\Longleftrightarrow x_1=x_2$，取 $\\alpha_1=\\begin{pmatrix}1\\\\1\\end{pmatrix}$，$\\|\\alpha_1\\|=\\sqrt2$，$\\gamma_1=\\dfrac{1}{\\sqrt2}\\begin{pmatrix}1\\\\1\\end{pmatrix}$；\n"
                "- $\\lambda_2=1$：$(A-E)x=0\\Longleftrightarrow\\begin{pmatrix}1&1\\\\1&1\\end{pmatrix}x=0\\Longleftrightarrow x_1=-x_2$，取 $\\alpha_2=\\begin{pmatrix}1\\\\-1\\end{pmatrix}$，$\\|\\alpha_2\\|=\\sqrt2$，$\\gamma_2=\\dfrac{1}{\\sqrt2}\\begin{pmatrix}1\\\\-1\\end{pmatrix}$。\n\n"
                "**第三步 构造正交矩阵**：$(\\gamma_1,\\gamma_2)=0$，且二者长度均为 $1$，故取\n"
                "$$Q=(\\gamma_1,\\gamma_2)=\\frac{1}{\\sqrt2}\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix},$$\n"
                "则 $Q^{\\mathsf T}Q=E$，$Q$ 是正交矩阵。于是\n"
                "$$Q^{\\mathsf T}AQ=\\begin{pmatrix}3&0\\\\0&1\\end{pmatrix},$$\n"
                "即 $A$ 的正交标准形为 $3y_1^2+y_2^2$。",
    points=[{"text": "写出特征方程 $(\\lambda-3)(\\lambda-1)=0$，求出特征值 $3,1$", "partial": 2},
            {"text": "求出特征向量 $(1,1)^{\\mathsf T}$ 与 $(1,-1)^{\\mathsf T}$ 并分别单位化", "partial": 2},
            {"text": "写出正交矩阵 $Q=\\frac{1}{\\sqrt2}\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix}$ 并验证 $Q^{\\mathsf T}Q=E$", "partial": 2},
            {"text": "得到 $Q^{\\mathsf T}AQ=\\mathrm{diag}(3,1)$，写出标准形 $3y_1^2+y_2^2$", "partial": 2}],
    expl="**答案依据**：§5.4 实对称矩阵的正交对角化（用施密特正交化把特征向量单位化即可得 $Q$）。\n"
         "**考点出处**：同济《线性代数》第六版 §5.4 对称矩阵的对角化。",
    mis="⚠️易错点：$Q$ 的列向量顺序与对角元顺序必须对应（第一列对应 $\\lambda_1=3$）；另外别忘了除以长度，$Q$ 的列必须是**单位**向量。",
    tags=["计算", "高频"],
    verify=[{"desc": "特征值", "code": "M([[2,1],[1,2]]).eigenvals()", "expected": "{3: 1, 1: 1}"},
            {"desc": "Q^T A Q", "code": "Q=M([[sqrt(2)/2,sqrt(2)/2],[sqrt(2)/2,-sqrt(2)/2]]); A=M([[2,1],[1,2]]); str(expand(Q.T*A*Q))", "expected": "Matrix([[3, 0], [0, 1]])"},
            {"desc": "Q^T Q", "code": "Q=M([[sqrt(2)/2,sqrt(2)/2],[sqrt(2)/2,-sqrt(2)/2]]); str(expand(Q.T*Q))", "expected": "Matrix([[1, 0], [0, 1]])"}]))

Q_.append(Q(CALC, "basic", "5.5",
    "求二次型 $f(x_1,x_2,x_3)=x_1^2+2x_2^2+3x_3^2+2x_1x_2-2x_2x_3$ 的矩阵 $A$，并求 $|A|$。",
    answer_text="**第一步 求矩阵**：二次型的矩阵取**对称**形式：$x_i^2$ 的系数为 $a_{ii}$，交叉项 $x_ix_j$ 的系数为 $2a_{ij}$（即交叉项系数取一半）。\n"
                "由 $x_1^2$ 的系数得 $a_{11}=1$；$2x_1x_2$ 的系数为 $2$，故 $a_{12}=a_{21}=1$；$x_2^2$ 的系数得 $a_{22}=2$；$-2x_2x_3$ 的系数为 $-2$，故 $a_{23}=a_{32}=-1$；$x_3^2$ 的系数得 $a_{33}=3$；无 $x_1x_3$ 项，故 $a_{13}=a_{31}=0$。\n\n"
                "$$A=\\begin{pmatrix}1&1&0\\\\1&2&-1\\\\0&-1&3\\end{pmatrix},\\qquad f(x)=x^{\\mathsf T}Ax.$$\n\n"
                "**第二步 求行列式**（按第一行展开）：\n"
                "$$|A|=1\\cdot\\begin{vmatrix}2&-1\\\\-1&3\\end{vmatrix}-1\\cdot\\begin{vmatrix}1&-1\\\\0&3\\end{vmatrix}+0\\cdot\\begin{vmatrix}1&2\\\\0&-1\\end{vmatrix}$$\n"
                "$$=\\bigl(2\\times3-(-1)(-1)\\bigr)-\\bigl(1\\times3-(-1)\\times0\\bigr)=(6-1)-(3-0)=5-3=2.$$\n"
                "故 $|A|=2\\neq0$，二次型 $f$ **非退化**，其秩 $r(A)=3$（§5.5）。",
    points=[{"text": "指出二次型矩阵取对称形式、交叉项系数取一半的规则", "partial": 2},
            {"text": "写出矩阵 $A=\\begin{pmatrix}1&1&0\\\\1&2&-1\\\\0&-1&3\\end{pmatrix}$", "partial": 2},
            {"text": "用展开法正确算出 $|A|=2$", "partial": 2},
            {"text": "得出结论：$|A|\\neq0$，$f$ 非退化、秩为 3", "partial": 2}],
    expl="**答案依据**：§5.5 二次型的矩阵与秩。\n"
         "**考点出处**：同济《线性代数》第六版 §5.5 二次型及其标准形。",
    mis="⚠️易错点：把交叉项 $2x_1x_2$ 的系数 $2$ 直接填进 $a_{12}$（应取一半为 $1$）；以及展开时第二项的符号漏掉负号。",
    tags=["计算", "高频"],
    verify=[{"desc": "det", "code": "M([[1,1,0],[1,2,-1],[0,-1,3]]).det()", "expected": "2"},
            {"desc": "rank", "code": "M([[1,1,0],[1,2,-1],[0,-1,3]]).rank()", "expected": "3"}]))

Q_.append(Q(CALC, "medium", "5.6",
    "用配方法把二次型 $f(x_1,x_2,x_3)=x_1^2+2x_2^2+3x_3^2+2x_1x_2-2x_2x_3$ 化为标准形，并写出所作的可逆线性变换。",
    answer_text="**第一步 写矩阵并作第一次配方**（就含 $x_1$ 的项配平方）：\n"
                "$$f=(x_1^2+2x_1x_2)+2x_2^2-2x_2x_3+3x_3^2=(x_1+x_2)^2+x_2^2-2x_2x_3+3x_3^2.$$\n\n"
                "**第二步 作第二次配方**（就含 $x_2$ 的项配平方）：\n"
                "$$f=(x_1+x_2)^2+\\bigl(x_2^2-2x_2x_3+x_3^2\\bigr)+2x_3^2=(x_1+x_2)^2+(x_2-x_3)^2+2x_3^2.$$\n\n"
                "**第三步 换元**：令\n$$y_1=x_1+x_2,\\qquad y_2=x_2-x_3,\\qquad y_3=x_3,$$\n"
                "则反解得 $x_3=y_3$，$x_2=y_2+y_3$，$x_1=y_1-y_2-y_3$，即\n"
                "$$x=Cy,\\qquad C=\\begin{pmatrix}-1&-1&-1\\\\0&1&1\\\\0&0&1\\end{pmatrix},\\qquad |C|=-1\\neq0,$$\n"
                "变换可逆。代入即得**标准形**\n$$f=y_1^2+y_2^2+2y_3^2.$$\n\n"
                "**第四步 惯性指数与规范形**：标准形中三个系数全为正，故正惯性指数 $p=3$，负惯性指数 $q=0$，零惯性指数 $0$，$r=p+q=3$；**规范形**为 $z_1^2+z_2^2+z_3^2$。\n\n"
                "**验算**（合同）：取 $A=\\begin{pmatrix}1&1&0\\\\1&2&-1\\\\0&-1&3\\end{pmatrix}$，直接计算得 $C^{\\mathsf T}AC=\\mathrm{diag}(1,1,2)$，与标准形一致。",
    points=[{"text": "写出矩阵 $A$ 并完成第一次配方 $f=(x_1+x_2)^2+x_2^2-2x_2x_3+3x_3^2$", "partial": 2},
            {"text": "完成第二次配方 $f=(x_1+x_2)^2+(x_2-x_3)^2+2x_3^2$", "partial": 2},
            {"text": "作换元并写出可逆矩阵 $C=\\begin{pmatrix}-1&-1&-1\\\\0&1&1\\\\0&0&1\\end{pmatrix}$，验证 $|C|=-1\\neq0$", "partial": 2},
            {"text": "得到标准形 $y_1^2+y_2^2+2y_3^2$，并给出正惯性指数 $p=3$、负惯性指数 $q=0$、秩 $r=3$", "partial": 2}],
    expl="**答案依据**：§5.6 用配方法化二次型成标准形 + §5.5 惯性指数。\n"
         "**考点出处**：同济《线性代数》第六版 §5.6 用配方法化二次型成标准形。\n"
         "**引申**：同一二次型若改用**正交变换**，标准形的系数是矩阵 $A$ 的特征值，本题 $A$ 的特征值为 $2,\\ 2-\\sqrt3,\\ 2+\\sqrt3$（三者皆正）；配方法与正交变换给出的标准形系数**不同**，但二者惯性指数相同，故规范形相同（都是三个正平方项）。",
    mis="⚠️易错点：配方时只配一次就收尾（$x_2^2-2x_2x_3+3x_3^2$ 还要再配一次）；以及把换元矩阵的行列写反（应为 $x=Cy$ 中的 $C$，可由 $y=Cx$ 反解得到）。",
    tags=["计算", "难点", "高频"],
    verify=[{"desc": "C^T A C", "code": "C=M([[-1,-1,-1],[0,1,1],[0,0,1]]); A=M([[1,1,0],[1,2,-1],[0,-1,3]]); str(expand(C.T*A*C))", "expected": "Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 2]])"},
            {"desc": "|C|", "code": "M([[-1,-1,-1],[0,1,1],[0,0,1]]).det()", "expected": "-1"},
            {"desc": "A 的特征值", "code": "M([[1,1,0],[1,2,-1],[0,-1,3]]).eigenvals()", "expected": "{2: 1, 2 - sqrt(3): 1, sqrt(3) + 2: 1}"}]))

Q_.append(Q(CALC, "medium", "5.7",
    "判断二次型 $f(x_1,x_2,x_3)=x_1^2+2x_2^2+3x_3^2-2x_1x_2+2x_2x_3-2x_1x_3$ 是否正定，并说明理由。",
    answer_text="**第一步 写出对称矩阵**（交叉项系数取一半）：\n"
                "$$A=\\begin{pmatrix}1&-1&-1\\\\-1&2&1\\\\-1&1&3\\end{pmatrix},\\qquad f(x)=x^{\\mathsf T}Ax.$$\n\n"
                "**第二步 用顺序主子式判别**（§5.7 Sylvester 判据）：\n"
                "$$A_1=1>0,$$\n"
                "$$A_2=\\begin{vmatrix}1&-1\\\\-1&2\\end{vmatrix}=1\\times2-(-1)(-1)=2-1=1>0,$$\n"
                "$$A_3=|A|=1\\cdot\\begin{vmatrix}2&1\\\\1&3\\end{vmatrix}-(-1)\\cdot\\begin{vmatrix}-1&1\\\\-1&3\\end{vmatrix}+(-1)\\cdot\\begin{vmatrix}-1&2\\\\-1&1\\end{vmatrix}.$$\n"
                "其中 $\\begin{vmatrix}2&1\\\\1&3\\end{vmatrix}=6-1=5$，$\\begin{vmatrix}-1&1\\\\-1&3\\end{vmatrix}=-3+1=-2$，$\\begin{vmatrix}-1&2\\\\-1&1\\end{vmatrix}=-1+2=1$，故\n"
                "$$|A|=1\\times5+1\\times(-2)+(-1)\\times1=5-2-1=2>0.$$\n"
                "各阶顺序主子式全大于零，故 $f$ **正定**，$A$ 是正定矩阵。\n\n"
                "**第三步 其他等价判据（§5.4 + §5.7）**：实对称矩阵 $A$ 正定 $\\iff$ 它的特征值全为正数 $\\iff$ 存在可逆矩阵 $C$ 使 $C^{\\mathsf T}AC=E$。由 $|A|=2>0$ 及各顺序主子式为正也可得同一结论。",
    points=[{"text": "写出对称矩阵 $A=\\begin{pmatrix}1&-1&-1\\\\-1&2&1\\\\-1&1&3\\end{pmatrix}$", "partial": 2},
            {"text": "算出一阶、二阶顺序主子式 $A_1=1>0$，$A_2=1>0$", "partial": 2},
            {"text": "算出三阶顺序主子式 $|A|=2>0$", "partial": 2},
            {"text": "由 Sylvester 判据得出 $f$ 正定的结论", "partial": 2}],
    expl="**答案依据**：§5.7 正定二次型的判别法（顺序主子式判据）。\n"
         "**考点出处**：同济《线性代数》第六版 §5.7 正定二次型。",
    mis="⚠️易错点：算三阶行列式时符号出错（三项分别是 $+,-,+$）；以及用「非顺序主子式」去套 Sylvester 判据。",
    tags=["计算", "高频"],
    verify=[{"desc": "A1", "code": "M([[1,-1,-1],[-1,2,1],[-1,1,3]])[0,0]", "expected": "1"},
            {"desc": "A2", "code": "M([[1,-1,-1],[-1,2,1],[-1,1,3]])[:2,:2].det()", "expected": "1"},
            {"desc": "|A|", "code": "M([[1,-1,-1],[-1,2,1],[-1,1,3]]).det()", "expected": "2"},
            {"desc": "正定性", "code": "M([[1,-1,-1],[-1,2,1],[-1,1,3]]).is_positive_definite", "expected": "True"}]))

Q_.append(Q(CALC, "medium", "5.4",
    "设实对称矩阵 $A=\\begin{pmatrix}2&1&1\\\\1&2&1\\\\1&1&2\\end{pmatrix}$，求它的特征值与一组标准正交特征向量，并求正交矩阵 $Q$ 使 $Q^{\\mathsf T}AQ$ 为对角阵。",
    answer_text="**第一步 求特征值**：$A$ 可写成 $A=E+J$，其中 $J$ 是元素全为 $1$ 的 $3$ 阶矩阵，$J\\mathbf{1}=3\\mathbf{1}$ 而 $J$ 在 $\\mathbf{1}^{\\perp}$ 上为 $0$，故 $A$ 的特征值为 $1+3=4$（一重）与 $1+0=1$（二重）。直接计算：\n"
                "$$|\\lambda E-A|=(\\lambda-4)(\\lambda-1)^2=0,$$\n"
                "故 $\\lambda_1=4$，$\\lambda_2=\\lambda_3=1$。\n\n"
                "**第二步 求特征向量并正交化**：\n"
                "- 属于 $\\lambda_1=4$：$(A-4E)x=0\\Longleftrightarrow x_1=x_2=x_3$，取 $\\alpha_1=\\begin{pmatrix}1\\\\1\\\\1\\end{pmatrix}$，$\\|\\alpha_1\\|=\\sqrt3$，$\\gamma_1=\\dfrac{1}{\\sqrt3}(1,1,1)^{\\mathsf T}$；\n"
                "- 属于 $\\lambda_2=\\lambda_3=1$：$(A-E)x=0\\Longleftrightarrow x_1+x_2+x_3=0$，其解空间是二维平面，取 $\\alpha_2=\\begin{pmatrix}1\\\\-1\\\\0\\end{pmatrix}$、$\\alpha_3=\\begin{pmatrix}1\\\\1\\\\-2\\end{pmatrix}$。用施密特正交化：$(1,-1,0)\\cdot(1,1,-2)=1-1+0=0$，两向量已正交，且长度分别为 $\\sqrt2$ 与 $\\sqrt6$，故\n"
                "$\\gamma_2=\\dfrac{1}{\\sqrt2}(1,-1,0)^{\\mathsf T}$，$\\gamma_3=\\dfrac{1}{\\sqrt6}(1,1,-2)^{\\mathsf T}$。\n\n"
                "**第三步 构造正交矩阵**：\n"
                "$$Q=(\\gamma_1,\\gamma_2,\\gamma_3)=\\begin{pmatrix}\\frac{1}{\\sqrt3}&\\frac{1}{\\sqrt2}&\\frac{1}{\\sqrt6}\\\\\\frac{1}{\\sqrt3}&-\\frac{1}{\\sqrt2}&\\frac{1}{\\sqrt6}\\\\\\frac{1}{\\sqrt3}&0&-\\frac{2}{\\sqrt6}\\end{pmatrix}.$$\n"
                "三列向量两两正交（$(1,1,1)\\cdot(1,-1,0)=0$，$(1,1,1)\\cdot(1,1,-2)=0$，$(1,-1,0)\\cdot(1,1,-2)=0$）且长度均为 $1$，故 $Q^{\\mathsf T}Q=E$，$Q$ 是正交矩阵。于是\n"
                "$$Q^{\\mathsf T}AQ=\\begin{pmatrix}4&0&0\\\\0&1&0\\\\0&0&1\\end{pmatrix},$$\n"
                "即 $A$ 的正交标准形为 $4y_1^2+y_2^2+y_3^2$。",
    points=[{"text": "求出特征方程 $(\\lambda-4)(\\lambda-1)^2=0$，得特征值 $4$ 与 $1$（二重）", "partial": 2},
            {"text": "求出属于 $4$ 的特征向量 $(1,1,1)^{\\mathsf T}$ 并单位化", "partial": 2},
            {"text": "在 $x_1+x_2+x_3=0$ 内取两个正交向量并单位化，得 $\\gamma_2,\\gamma_3$", "partial": 2},
            {"text": "写出正交矩阵 $Q$ 并得到 $Q^{\\mathsf T}AQ=\\mathrm{diag}(4,1,1)$", "partial": 2}],
    expl="**答案依据**：§5.4 实对称矩阵的正交对角化（重特征值时需在特征子空间内取正交基）+ §5.1 施密特正交化。\n"
         "**考点出处**：同济《线性代数》第六版 §5.4 对称矩阵的对角化。\n"
         "**引申**：实对称矩阵有重特征值时，仍能在对应的特征子空间内取出一组标准正交基，从而「重数 $=$ 几何重数」并保证正交对角化一定做得到——这正是一般矩阵做不到的地方。",
    mis="⚠️易错点：重特征值 $1$ 对应的特征子空间是二维的，只取一个向量就拼不成 $Q$ 的三列；且 $Q$ 的列必须**单位化**并两两正交。",
    tags=["计算", "难点", "高频"],
    verify=[{"desc": "特征值", "code": "M([[2,1,1],[1,2,1],[1,1,2]]).eigenvals()", "expected": "{4: 1, 1: 2}"},
            {"desc": "Q^T A Q", "code": "Q=M([[1/sqrt(3),1/sqrt(2),1/sqrt(6)],[1/sqrt(3),-1/sqrt(2),1/sqrt(6)],[1/sqrt(3),0,-2/sqrt(6)]]); A=M([[2,1,1],[1,2,1],[1,1,2]]); str(expand(Q.T*A*Q))", "expected": "Matrix([[4, 0, 0], [0, 1, 0], [0, 0, 1]])"},
            {"desc": "Q^T Q", "code": "Q=M([[1/sqrt(3),1/sqrt(2),1/sqrt(6)],[1/sqrt(3),-1/sqrt(2),1/sqrt(6)],[1/sqrt(3),0,-2/sqrt(6)]]); str(expand(Q.T*Q))", "expected": "Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])"}]))

Q = Q_
