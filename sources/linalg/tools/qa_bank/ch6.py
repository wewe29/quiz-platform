# -*- coding: utf-8 -*-
"""第6章 线性空间与线性变换（选学）—— 6 题（每题型各 1 题）
难度：基础3 中等2 困难1
知识点：6.1 线性空间的定义与性质 / 6.2 维数、基与坐标 / 6.3 基变换与坐标变换
        6.4 线性变换 / 6.5 线性变换的矩阵表示式
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────────────────────────── 单选 1（基础1 中等0 困难0）
Q_.append(Q(SINGLE, "basic", "6.1",
    "设 $V$ 是数域 $F$ 上的线性空间。下列命题中，必为真的是",
    answer=["B"],
    options=["$V$ 中存在两个线性无关的非零向量",
             "$V$ 含零向量，且对向量的加法与数乘封闭",
             "$V$ 中每个向量都可唯一表示成有限多个基向量的线性组合",
             "$V$ 必为有限维空间"],
    expl="**答案依据**：线性空间的定义（§6.1）要求：$V$ 是 $F$ 上向量的**非空**集合，且对加法、数乘**封闭**——任取 $\\alpha,\\beta\\in V$ 有 $\\alpha+\\beta\\in V$，任取 $\\lambda\\in F$ 有 $\\lambda\\alpha\\in V$。取 $\\lambda=0$ 得 $0\\alpha=\\boldsymbol{0}\\in V$，故零向量必在 $V$ 中，这正是 B 的内容。\n"
          "A 不一定成立：平凡线性空间 $V=\\{\\boldsymbol{0}\\}$ 也是线性空间，但其中不存在两个线性无关的非零向量。\n"
          "C 错：只有**有限维**空间才有有限的一组基；无限维空间（如实系数多项式空间）的基是无限集，「有限多个基向量的线性组合」张不成整个 $V$。\n"
          "D 错：多项式空间、多项式矩阵空间都是无限维线性空间。",
    mis="⚠️易错点：默认「线性空间 = 有限维」。线性空间的定义**不要求有限维**，有限维只是附加条件。",
    tags=["重点", "易错"]))

# ─────────────────────────────────────────────── 多选 1（基础0 中等1 困难0）
Q_.append(Q(MULTI, "medium", "6.4",
    "设 $T$ 是线性空间 $V$ 到 $W$ 的一个映射。关于 $T$ 是否为线性变换，下列说法正确的有",
    answer=["A", "B", "D"],
    options=["$T(\\alpha+\\beta)=T(\\alpha)+T(\\beta)$（保持加法）",
             "$T(\\lambda\\alpha)=\\lambda T(\\alpha)$（保持数乘）",
             "$T$ 必为可逆映射",
             "零变换 $T(\\alpha)=0$ 是线性变换"],
    expl="**答案依据**：线性变换的定义（§6.4）恰好就是保持加法与数乘两条，故 A、B 正确；把 $\\alpha=\\boldsymbol{0}$ 或 $\\lambda=0$ 代入即可看出零变换满足这两条，D 正确。\n"
          "C 错：线性变换**未必可逆**。例如 $T:\\mathbb{R}^2\\to\\mathbb{R}^2$，$T(x,y)=(x,0)$ 是线性变换，但 $\\ker T\\neq\\{0\\}$，不可逆。",
    mis="⚠️易错点：把「线性」当成「可逆」。线性只约束加法与数乘的保持，与单射、满射无关。",
    tags=["高频", "易错"]))

# ─────────────────────────────────────────────── 判断 1（基础1 中等0 困难0）
Q_.append(Q(JUDGE, "basic", "6.2",
    "设 $\\alpha_1,\\dots,\\alpha_n$ 是线性空间 $V$ 的一组向量。则 $\\alpha_1,\\dots,\\alpha_n$ 是 $V$ 的一组基，当且仅当它们线性无关且能张成 $V$。",
    answer=["A"],
    expl="**答案依据**：§6.2 基的定义与判定定理——$V$ 的一组向量是 $V$ 的一组基，**当且仅当**它们线性无关并且张成 $V$。线性无关保证坐标表示的**唯一性**，张成保证坐标表示的**存在性**，两者缺一不可。\n"
          "若 $V$ 为 $n$ 维空间，则每组基恰含 $n$ 个向量，这个 $n$ 称为 $V$ 的**维数**。",
    mis="⚠️易错点：只强调其中一条——只线性无关张不成整个空间，只张成则坐标表示不唯一。",
    tags=["重点", "必背"]))

# ─────────────────────────────────────────────── 填空 1（基础1 中等0 困难0）
Q_.append(Q(BLANK, "basic", "6.3",
    "设 $\\alpha_1,\\alpha_2,\\alpha_3$ 是 $\\mathbb{R}^3$ 的一组基，则在基 $\\alpha_1,\\alpha_2,\\alpha_3$ 下，向量 $\\boldsymbol{\\beta}=\\alpha_1+2\\alpha_2+3\\alpha_3$ 的坐标是 ______。",
    answer=["(1,2,3)", "1,2,3", "(1,2,3)^T", "{1,2,3}"],
    accept=["(1,2,3)", "1,2,3", "(1,2,3)^T", "(1,2,3)^t", "{1,2,3}", "(1,2,3)T"],
    expl="**答案依据**：坐标的定义（§6.2）——向量在基 $\\alpha_1,\\alpha_2,\\alpha_3$ 下的坐标，就是把它写成基向量的线性组合时**各系数构成的有序数组**。\n"
          "这里 $\\boldsymbol{\\beta}=\\alpha_1+2\\alpha_2+3\\alpha_3$，系数依次为 $1,2,3$，故坐标为 $(1,2,3)^{\\mathsf T}$。\n"
          "**引申**：坐标依赖于所选的基；换成另一组基，同一个向量的坐标一般会变，这正是基变换与坐标变换要处理的问题（§6.3）。",
    mis="⚠️易错点：把 $\\alpha_1+2\\alpha_2+3\\alpha_3$ 当成答案——那是向量的**表示式**，坐标只是那三个**系数**。",
    tags=["高频", "概念"]))

# ─────────────────────────────────────────────── 简答与名词解释 1（基础0 中等1 困难0）
Q_.append(Q(SHORT, "medium", "6.3",
    "设 $\\alpha_1,\\alpha_2,\\alpha_3$ 与 $\\beta_1,\\beta_2,\\beta_3$ 是三维线性空间 $V$ 的两组基。说明基变换矩阵与坐标变换矩阵之间的关系。",
    answer_text="**答案（§6.3 基变换与坐标变换）**：记\n"
                "$$\\boldsymbol{\\alpha}=(\\alpha_1,\\alpha_2,\\alpha_3)^{\\mathsf T},\\qquad \\boldsymbol{\\beta}=(\\beta_1,\\beta_2,\\beta_3)^{\\mathsf T}.$$\n"
                "由基的定义，$\\boldsymbol{\\beta}$ 的每个向量都能唯一地表示成 $\\boldsymbol{\\alpha}$ 的线性组合，故存在**唯一**的矩阵 $P=(p_{ij})_{3\\times3}$ 使\n"
                "$$\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}P\\qquad(P\\text{ 为可逆矩阵，称 }P\\text{ 为基变换矩阵}).$$\n"
                "设向量 $\\boldsymbol{\\xi}$ 在基 $\\boldsymbol{\\alpha}$ 与基 $\\boldsymbol{\\beta}$ 下的坐标分别为 $\\boldsymbol{x}$ 与 $\\boldsymbol{y}$，即\n"
                "$$\\boldsymbol{\\xi}=\\boldsymbol{\\alpha}\\boldsymbol{x}=\\boldsymbol{\\beta}\\boldsymbol{y}.$$\n"
                "把 $\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}P$ 代入右端并约去 $\\boldsymbol{\\alpha}$（$\\boldsymbol{\\alpha}$ 的元素线性无关，可作左乘消去），得\n"
                "$$\\boldsymbol{x}=P\\boldsymbol{y}\\quad\\Longrightarrow\\quad \\boldsymbol{y}=P^{-1}\\boldsymbol{x}.$$\n"
                "**结论**：由旧基 $\\boldsymbol{\\alpha}$ 的坐标换到新基 $\\boldsymbol{\\beta}$ 的坐标要乘**基变换矩阵的逆矩阵** $P^{-1}$；反之从新基坐标换回旧基坐标要乘 $P$。两个方向的变换矩阵互为逆矩阵。\n"
                "**补充**：$P$ 的第 $j$ 列正是 $\\beta_j$ 在基 $\\boldsymbol{\\alpha}$ 下的坐标。",
    points=[{"text": "写出基变换矩阵的定义式 $\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}P$，并指出 $P$ 可逆且唯一", "partial": 2},
            {"text": "由 $\\boldsymbol{\\alpha}\\boldsymbol{x}=\\boldsymbol{\\beta}\\boldsymbol{y}$ 推出 $\\boldsymbol{x}=P\\boldsymbol{y}$，即 $\\boldsymbol{y}=P^{-1}\\boldsymbol{x}$", "partial": 2},
            {"text": "得出结论：坐标变换矩阵与基变换矩阵互为逆矩阵，并说明换基方向", "partial": 2}],
    expl="**答案依据**：§6.3 基变换与坐标变换。\n"
          "**考点出处**：同济《线性代数》第六版 §6.3 基变换与坐标变换（选学）。",
    mis="⚠️易错点：把方向搞反——用**旧基坐标换新基坐标**要乘 $P^{-1}$（过渡矩阵的逆），不是乘 $P$。",
    tags=["难点", "重点"]))

# ─────────────────────────────────────────────── 计算与分析 1（基础0 中等0 困难1）
Q_.append(Q(CALC, "hard", "6.5",
    "设 $T$ 是 $\\mathbb{R}^3$ 上的线性变换，已知\n"
    "$$T(\\boldsymbol{e}_1)=\\begin{pmatrix}2\\\\0\\\\1\\end{pmatrix},\\quad "
    "T(\\boldsymbol{e}_2)=\\begin{pmatrix}0\\\\1\\\\1\\end{pmatrix},\\quad "
    "T(\\boldsymbol{e}_3)=\\begin{pmatrix}1\\\\1\\\\0\\end{pmatrix},$$\n"
    "其中 $\\boldsymbol{e}_1,\\boldsymbol{e}_2,\\boldsymbol{e}_3$ 为 $\\mathbb{R}^3$ 的标准基。求 $T$ 的矩阵表示式 $A$；并判断 $T$ 是否为可逆变换，若可逆求出 $T^{-1}$ 的矩阵表示式。",
    answer_text="**第一步：求 $T$ 的矩阵表示式**。\n"
                "在标准基下，$T$ 的矩阵表示式的第 $j$ 列，就是 $T(\\boldsymbol{e}_j)$ 在该基下的坐标（§6.5）。故\n"
                "$$A=\\begin{pmatrix}2&0&1\\\\0&1&1\\\\1&1&0\\end{pmatrix}.$$\n"
                "即对任意 $\\boldsymbol{x}=(x_1,x_2,x_3)^{\\mathsf T}$，\n"
                "$$T(\\boldsymbol{x})=A\\boldsymbol{x}=\\begin{pmatrix}2x_1+x_3\\\\x_2+x_3\\\\x_1+x_2\\end{pmatrix}.$$\n\n"
                "**第二步：判断可逆性**。\n"
                "$$|A|=2\\begin{vmatrix}1&1\\\\1&0\\end{vmatrix}+1\\begin{vmatrix}0&1\\\\1&1\\end{vmatrix}"
                "=2\\times(-1)+1\\times(-1)=-3\\neq0,$$\n"
                "故 $A$ 可逆，从而 $T$ 是**可逆变换**。\n\n"
                "**第三步：求 $T^{-1}$ 的矩阵表示式**。\n"
                "由 $A^{-1}=\\dfrac{1}{|A|}A^*$，其中 $A^*$ 为 $A$ 的伴随矩阵。计算各代数余子式得\n"
                "$$A^*=\\begin{pmatrix}-1&1&-1\\\\1&-1&-2\\\\-1&-2&2\\end{pmatrix},$$\n"
                "于是\n"
                "$$A^{-1}=-\\dfrac13\\begin{pmatrix}-1&1&-1\\\\1&-1&-2\\\\-1&-2&2\\end{pmatrix}"
                "=\\begin{pmatrix}\\dfrac13&-\\dfrac13&\\dfrac13\\\\-\\dfrac13&\\dfrac13&\\dfrac23\\\\\\dfrac13&\\dfrac23&-\\dfrac23\\end{pmatrix}.$$\n"
                "即 $T^{-1}$ 的矩阵表示式为 $A^{-1}$。",
    points=[{"text": "写出 $T$ 的矩阵表示式 $A$（以 $T(\\boldsymbol{e}_j)$ 作为第 $j$ 列）", "partial": 2},
            {"text": "算出 $|A|=-3\\neq0$ 并据此判定 $T$ 为可逆变换", "partial": 2},
            {"text": "正确求出伴随矩阵 $A^*$ 并得出 $A^{-1}$ 的各个元素", "partial": 2},
            {"text": "结论完整：矩阵表示式 $A$、可逆性结论、逆变换的矩阵表示式 $A^{-1}$", "partial": 2}],
    expl="**答案依据**：§6.5 线性变换的矩阵表示式——$T$ 在基 $\\boldsymbol{e}_1,\\boldsymbol{e}_2,\\boldsymbol{e}_3$ 下的矩阵第 $j$ 列即 $T(\\boldsymbol{e}_j)$ 在该基下的坐标；可逆性归结为 $A$ 可逆（§2.3），逆矩阵用 $A^{-1}=\\dfrac{1}{|A|}A^*$（§2.3）。\n"
          "**考点出处**：同济《线性代数》第六版 §6.5 线性变换的矩阵表示式（选学）；次要考点 §2.3 逆矩阵。",
    mis="⚠️易错点：把 $T(\\boldsymbol{e}_j)$ 当成 $A$ 的**行**而不是**列**；以及算伴随矩阵时漏掉转置（$A^*=(A_{ji})$）。",
    tags=["计算", "难点", "高频"],
    verify=[{"desc": "|A|", "code": "M([[2,0,1],[0,1,1],[1,1,0]]).det()", "expected": "-3"},
            {"desc": "A^-1", "code": "str(M([[2,0,1],[0,1,1],[1,1,0]]).inv())",
             "expected": "Matrix([[1/3, -1/3, 1/3], [-1/3, 1/3, 2/3], [1/3, 2/3, -2/3]])"},
            {"desc": "伴随矩阵", "code": "str(M([[2,0,1],[0,1,1],[1,1,0]]).adjugate())",
             "expected": "Matrix([[-1, 1, -1], [1, -1, -2], [-1, -2, 2]])"}]))

Q = Q_
