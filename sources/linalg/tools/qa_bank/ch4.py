# -*- coding: utf-8 -*-
"""第4章 向量组与线性方程组的解的结构 —— 36 题
（单选5 / 多选6 / 判断6 / 填空6 / 简答与名词解释6 / 计算与分析7）
难度：基础16 中等14 困难6
知识点：4.1 向量组及其线性组合 / 4.2 向量组的线性相关性 / 4.3 向量组的秩
        4.4 线性方程组的解的结构 / 4.5 向量空间
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────────────────────────── 单选 5（基础2 中等2 困难1）
Q_.append(Q(SINGLE, "basic", "4.1",
    "设 $\\boldsymbol{\\alpha}_1=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，则 $2\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2=$",
    answer=["A"],
    options=["$(2,-1,2)^{\\mathsf T}$", "$(2,1,2)^{\\mathsf T}$", "$(-2,-1,2)^{\\mathsf T}$", "$(0,-1,2)^{\\mathsf T}$"],
    expl="**答案依据**：§4.1 线性组合是**逐分量**的加减运算。\n"
          "$$2\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2=2(1,0,1)^{\\mathsf T}-(0,1,0)^{\\mathsf T}=(2,0,2)^{\\mathsf T}-(0,1,0)^{\\mathsf T}=(2,-1,2)^{\\mathsf T}.$$\n"
          "B 错：相当于算成 $2\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，第二个分量漏了负号；\n"
          "C 错：相当于算成 $-2\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2$，整个系数的符号取反；\n"
          "D 错：第一个分量误按 $2\\times0-1\\times0=0$ 计算，实为 $2\\times1-0=2$。",
    mis="⚠️易错点：系数 $2$ 作用在 $\\boldsymbol{\\alpha}_1$ 的**每一个**分量上，不是只作用在第一个分量；负号要分配到被减向量 $\\boldsymbol{\\alpha}_2$ 的所有分量。",
    tags=["重点", "计算"],
    verify=[{"desc": "2α1-α2 的三个分量", "code": "str(list(2*M([1,0,1]) - M([0,1,0])))", "expected": "[2, -1, 2]"}]))

Q_.append(Q(SINGLE, "basic", "4.2",
    "已知 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,0)^{\\mathsf T}$，则向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$",
    answer=["B"],
    options=["线性无关",
             "线性相关，且 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$",
             "线性无关，因为三个向量都非零",
             "线性相关，但 $\\boldsymbol{\\alpha}_3$ 不能由 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性表示"],
    expl="**答案依据**：§4.2 线性相关的定义——存在**不全为零**的系数使线性组合为零向量。此处\n"
          "$$1\\cdot\\boldsymbol{\\alpha}_1+1\\cdot\\boldsymbol{\\alpha}_2-1\\cdot\\boldsymbol{\\alpha}_3=\\boldsymbol{0},$$\n"
          "系数 $(1,1,-1)$ 不全为零，故线性相关，且关系式恰好给出 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$。\n"
          "A 错：把三向量作列构成矩阵，秩为 $2<3$，故线性相关；\n"
          "C 错：向量非零是线性相关的**必要**条件之一，与「无关」无关（$(1,0,0)^{\\mathsf T},(0,1,0)^{\\mathsf T},(1,1,0)^{\\mathsf T}$ 每个都非零却相关）；\n"
          "D 错：事实恰好相反，$\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$ 正是可表示。",
    mis="⚠️易错点：把「每个向量都非零」当作线性无关的充分条件。判定相关与否只看是否存在**不全为零**的系数组合。",
    tags=["重点", "易错"],
    verify=[{"desc": "三向量构成的矩阵秩为 2（<3，故相关）", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(SINGLE, "medium", "4.3",
    "设向量组 $\\boldsymbol{\\alpha}_1=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,2)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_4=(1,0,0)^{\\mathsf T}$，则向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$ 的秩是",
    answer=["C"],
    options=["$1$", "$2$", "$3$", "$4$"],
    expl="**答案依据**：§4.3 向量组的秩 $=$ 以该向量组为列构成矩阵的秩（§3.2）。\n"
          "第一步：$\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，故这四个向量的秩 $\\le 3$；\n"
          "第二步：设 $\\boldsymbol{\\alpha}_4=k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2$，即 $(k_1,k_2,k_1+k_2)^{\\mathsf T}=(1,0,0)^{\\mathsf T}$，前两式给出 $k_1=1,k_2=0$，而第三式 $k_1+k_2=1\\neq0$ 矛盾，故 $\\boldsymbol{\\alpha}_4$ 不在 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 的张成空间内，秩 $\\ge3$。\n"
          "于是秩 $=3$。\n"
          "A、B 错：都漏掉了 $\\boldsymbol{\\alpha}_4$ 带来的第三个独立方向；\n"
          "D 错：四个向量都在 $R^3$ 中，秩最多为 $3$。",
    mis="⚠️易错点：只看 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$ 就下结论，忘了把 $\\boldsymbol{\\alpha}_4$ 一起放进矩阵算秩。",
    tags=["计算", "高频"],
    verify=[{"desc": "四向量作列的矩阵的秩", "code": "M([[1,0,1,1],[0,1,1,0],[1,1,2,0]]).rank()", "expected": "3"}]))

Q_.append(Q(SINGLE, "medium", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵且 $r(A)=m<n$，则齐次线性方程组 $A\\boldsymbol{x}=0$ 的解空间的维数是",
    answer=["D"],
    options=["$m$", "$n$", "$0$", "$n-m$"],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构——解空间是 $R^n$ 的一个子空间，**维数等于自由未知量的个数 $n-r(A)$**。本题 $r(A)=m$，故维数 $=n-m$。\n"
          "A 错：$m$ 是系数矩阵的**行数**（此时满行秩），与解空间维数无关；\n"
          "B 错：$n$ 是未知量个数，只有 $r(A)=0$ 时解空间维数才等于 $n$；\n"
          "C 错：因 $r(A)=m>0$ 且 $r(A)<n$，方程组有非零解，解空间不是零空间。",
    mis="⚠️易错点：把「系数矩阵的行数 $m$」当成解空间的维数。维数是**自由未知量个数** $n-r(A)$，与 $m$ 无关。",
    tags=["重点", "高频"],
    verify=[{"desc": "示例：3 元 2 阶系数阵的秩", "code": "M([[1,1,1],[1,2,3]]).rank()", "expected": "2"},
            {"desc": "示例：解空间维数 n-r", "code": "3 - M([[1,1,1],[1,2,3]]).rank()", "expected": "1"}]))

Q_.append(Q(SINGLE, "hard", "4.5",
    "设 $K$ 是数域，$V$ 是由 $K$ 上向量组成的非空集合。下列条件中，**足以**判定 $V$ 是 $K$ 上的向量空间的是",
    answer=["A"],
    options=["对任意 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in V$ 有 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\in V$，且对任意 $k\\in K$ 与 $\\boldsymbol{\\alpha}\\in V$ 有 $k\\boldsymbol{\\alpha}\\in V$",
             "对任意 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in V$ 有 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\in V$，且对任意 $\\boldsymbol{\\alpha}\\in V$ 有 $2\\boldsymbol{\\alpha}\\in V$",
             "对任意 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in V$ 有 $\\boldsymbol{\\alpha}-\\boldsymbol{\\beta}\\in V$，且对任意 $\\boldsymbol{\\alpha}\\in V$ 有 $2\\boldsymbol{\\alpha}\\in V$",
             "对任意 $\\boldsymbol{\\alpha}\\in V$ 有 $2\\boldsymbol{\\alpha}\\in V$，且对任意 $k\\in K$ 有 $k\\boldsymbol{\\alpha}\\in V$"],
    expl="**答案依据**：§4.5 向量空间的定义——非空集合 $V$ 中的向量对**加法**和**数乘**都封闭时，$V$ 是 $K$ 上的向量空间。A 逐字给出了这两条封闭性，故充分且必要。\n"
          "B 错：只要求对标量 $2$ 封闭不够。反例 $V=\\{(x,y)^{\\mathsf T}\\mid x+y\\ge0\\}$：对加法封闭、对 $2$ 倍封闭，但 $-\\boldsymbol{\\alpha}$（分量和为负）不在 $V$ 中，故 $V$ 不是向量空间。\n"
          "C 错：减法封闭与 $2$ 倍封闭也不足以保证对任意标量封闭。反例 $V=\\{(x)^{\\mathsf T}\\mid x\\in\\mathbb{Z}\\}\\subset R$：对减法与倍加封闭，但 $\\frac12\\cdot(1)^{\\mathsf T}\\notin V$。\n"
          "D 错：缺少对**加法**的封闭性。反例 $V=\\{(x,0)^{\\mathsf T}\\}\\cup\\{(0,y)^{\\mathsf T}\\}$：对任意标量封闭，但 $(1,0)^{\\mathsf T}+(0,1)^{\\mathsf T}=(1,1)^{\\mathsf T}\\notin V$。",
    mis="⚠️易错点：以为「对 $2$ 倍封闭」就等于「对任意数乘封闭」。数乘封闭要求 $k$ 取遍**整个数域**，$2$ 只是一个数。",
    tags=["难点", "重点", "易错"],
    verify=[{"desc": "反例 B：α=(1,0,1) 的分量和", "code": "sum(M([1,0,1]))", "expected": "2"},
            {"desc": "反例 B：-α 的分量和为负，故 -α 不在 V 中", "code": "sum(M([1,0,1])*-1)", "expected": "-2"},
            {"desc": "反例 D：e1+e2 不在两条坐标轴的并集中", "code": "str(list(M([1,0,0]) + M([0,1,0])))", "expected": "[1, 1, 0]"}]))

# ─────────────────────────────────────────────── 多选 6（基础1 中等4 困难1）
Q_.append(Q(MULTI, "basic", "4.1",
    "关于向量的线性组合，下列说法正确的有",
    answer=["A", "C"],
    options=["若 $\\boldsymbol{\\beta}=\\sum_{i=1}^{m} k_i\\boldsymbol{\\alpha}_i$，则称 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示",
             "若 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示，则表示系数 $k_1,\\dots,k_m$ 必唯一",
             "若 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示，则 $\\boldsymbol{\\beta}$ 属于由这些向量张成的子空间",
             "若 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示，则 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 必线性相关"],
    expl="**答案依据**：§4.1 线性组合与线性表示的定义。A 就是定义本身；C 由「张成的子空间 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m)=\\{\\sum_{i=1}^{m}k_i\\boldsymbol{\\alpha}_i\\}$」直接得到——能线性表示的向量当然落在张成空间里。\n"
          "B 错：系数的**唯一性**要求该向量组**线性无关**。向量组线性相关时同一向量有无穷多种表示，例如 $\\boldsymbol{\\alpha}_1=(1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(2,0)^{\\mathsf T}$，则 $(1,0)^{\\mathsf T}=1\\boldsymbol{\\alpha}_1+0\\boldsymbol{\\alpha}_2=0\\boldsymbol{\\alpha}_1+\\tfrac12\\boldsymbol{\\alpha}_2$。\n"
          "D 错：方向反了。由「$\\boldsymbol{\\beta}$ 可被表示」推不出「原来的向量组相关」；反例：$\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性无关时 $\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}_1$ 仍可由它们表示。",
    mis="⚠️易错点：把「系数唯一」当成线性组合的必然要求。唯一性是**线性无关**才带来的性质，相关向量组的表示系数有无穷多组。",
    tags=["重点", "必背"]))

Q_.append(Q(MULTI, "medium", "4.2",
    "设向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性无关，则下列结论正确的有",
    answer=["B", "C", "D"],
    options=["在它后面添加任意一个向量 $\\boldsymbol{\\beta}$ 后，所得向量组仍线性无关",
             "每个 $\\boldsymbol{\\alpha}_i$ 都不能由其余向量的线性组合表示",
             "它的任意部分组（如 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_3$）也线性无关",
             "若 $\\boldsymbol{\\beta}=\\sum_{i=1}^{s}k_i\\boldsymbol{\\alpha}_i$，则 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s,\\boldsymbol{\\beta}$ 线性相关"],
    expl="**答案依据**：§4.2 线性相关性的基本定理与推论。\n"
          "B：若某个 $\\boldsymbol{\\alpha}_i$ 能由其余向量表示，移项即得一组不全为零的系数使线性组合为 $\\boldsymbol{0}$，与无关矛盾；\n"
          "C：无关组的任一部分组必无关——否则把该部分组的系数关系中其余系数补零，就得到原组的一组不全为零的系数关系；\n"
          "D：$\\boldsymbol{\\beta}$ 已落在原向量组张成的空间内，加入后向量数增加而秩不变，故必相关。\n"
          "A 错：添加 $\\boldsymbol{\\beta}$ 后**可能**相关，例如取 $\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$（$s\\ge2$），则 $\\boldsymbol{\\beta}-\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2=\\boldsymbol{0}$。",
    mis="⚠️易错点：以为「原来无关就加什么都无关」。无关性很脆弱，加入一个落在原张成空间里的向量立刻被破坏。",
    tags=["高频", "重点"]))

Q_.append(Q(MULTI, "hard", "4.2",
    "设 $\\boldsymbol{\\alpha}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(0,k,1)^{\\mathsf T}$，则下列结论正确的有",
    answer=["A", "C"],
    options=["三向量线性相关 $\\iff$ $k=-1$",
             "三向量线性相关 $\\iff$ $k=0$",
             "$k=1$ 时三向量线性无关",
             "$k=-2$ 时三向量线性相关"],
    expl="**答案依据**：以三向量为列作矩阵\n$$A=\\begin{pmatrix}1&1&0\\\\1&0&k\\\\0&1&1\\end{pmatrix}.$$\n"
          "由 §4.2 与 §3.2，它们线性相关 $\\iff r(A)<3\\iff|A|=0$。\n"
          "$$|A|=1\\cdot(0\\cdot1-k\\cdot1)-1\\cdot(1\\cdot1-k\\cdot0)+0=-k-1.$$\n"
          "故 $|A|=0\\iff k=-1$，即 A 正确、B 错误。\n"
          "再逐个代入其余选项验证：$k=1$ 时 $|A|=-2\\neq0$，三向量线性**无关**，故 C 正确；$k=-2$ 时 $|A|=1\\neq0$，三向量同样线性**无关**，故 D 错误。\n"
          "（$k=-1$ 时 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_2-\\boldsymbol{\\alpha}_1=(0,-1,1)^{\\mathsf T}$，确实线性相关。）",
    mis="⚠️易错点：含参讨论只验证「某个 $k$ 使相关」就收工，**不验证**其余 $k$ 值下都无关。充分必要条件必须两头都证。",
    tags=["计算", "高频", "含参", "难点"],
    verify=[{"desc": "行列式展开式", "code": "expand(M([[1,1,0],[1,0,symbols('k')],[0,1,1]]).det())", "expected": "-k - 1"},
            {"desc": "k=-1 时的行列式", "code": "M([[1,1,0],[1,0,-1],[0,1,1]]).det()", "expected": "0"},
            {"desc": "k=1 时的行列式", "code": "M([[1,1,0],[1,0,1],[0,1,1]]).det()", "expected": "-2"},
            {"desc": "k=-2 时的行列式", "code": "M([[1,1,0],[1,0,-2],[0,1,1]]).det()", "expected": "1"}]))

Q_.append(Q(MULTI, "medium", "4.3",
    "设 $n$ 维向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 的秩为 $r$，则下列结论正确的有",
    answer=["B", "C", "D"],
    options=["它的任意 $r$ 个向量都线性无关",
             "它存在由 $r$ 个向量构成的极大线性无关组",
             "它的任意 $r+1$ 个向量都线性相关",
             "它的任意线性无关子向量组所含向量个数都不超过 $r$"],
    expl="**答案依据**：§4.3 极大线性无关组与秩的定义。\n"
          "B：秩 $r$ 的定义就是极大线性无关组所含向量的个数（存在性可由初等行变换后取有主元的列得到）；\n"
          "C：若某 $r+1$ 个向量线性无关，则秩 $\\ge r+1$，与秩为 $r$ 矛盾；\n"
          "D：秩 $r$ 是线性无关向量个数的**最大值**，任何线性无关子组都不可能超过 $r$。\n"
          "A 错：秩为 $r$ 只保证**存在**一个含 $r$ 个向量的极大无关组，不保证**任意** $r$ 个都无关。反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(2,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_3=(0,1,0)^{\\mathsf T}$ 的秩为 $2$，但 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性相关。",
    mis="⚠️易错点：把「秩是极大无关组的大小」偷换成「任意 $r$ 个向量都无关」。**存在性 ≠ 任意性**。",
    tags=["重点", "易错", "高频"],
    verify=[{"desc": "反例 A：该向量组的秩为 2", "code": "M([[1,2,0],[0,0,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(MULTI, "medium", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵且 $r(A)=r<n$，则关于齐次线性方程组 $A\\boldsymbol{x}=0$，下列说法正确的有",
    answer=["A", "B", "C"],
    options=["它的解集是 $n$ 维向量空间 $R^n$ 的一个子空间",
             "它的基础解系含有 $n-r$ 个线性无关的解向量",
             "它的任意两个解之和仍是它的解",
             "它只有零解"],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构。\n"
          "A：零空间 $\\{\\boldsymbol{x}\\mid A\\boldsymbol{x}=0\\}$ 对加法与数乘封闭，故是 $R^n$ 的子空间（§4.5）；\n"
          "B：基础解系由 $n-r(A)$ 个线性无关的解向量构成，并张成整个解空间；\n"
          "C：$A(\\boldsymbol{x}_1+\\boldsymbol{x}_2)=A\\boldsymbol{x}_1+A\\boldsymbol{x}_2=\\boldsymbol{0}$，由矩阵乘法的分配律；\n"
          "D 错：$r(A)=r<n$ 说明存在自由未知量，方程组有**无穷多**解，不止零解。",
    mis="⚠️易错点：把「$r(A)<n$」误当成「无解」或「只有零解」。对**齐次**方程组而言，$r(A)<n$ 恰恰意味着有无穷多解。",
    tags=["重点", "高频"],
    verify=[{"desc": "示例：3 元 2 阶系数阵的秩", "code": "M([[1,1,1],[1,2,3]]).rank()", "expected": "2"},
            {"desc": "示例：基础解系向量个数 n-r", "code": "len(M([[1,1,1],[1,2,3]]).nullspace())", "expected": "1"}]))

Q_.append(Q(MULTI, "medium", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵，非齐次线性方程组 $A\\boldsymbol{x}=b$ 有解，则下列结论正确的有",
    answer=["A", "C", "D"],
    options=["$r(A)=r(A\\mid b)$ 是它有解的**充分必要条件**",
             "它的解集是 $R^n$ 的一个线性子空间",
             "若 $\\boldsymbol{x}_1,\\boldsymbol{x}_2$ 都是它的解，则 $\\boldsymbol{x}_1-\\boldsymbol{x}_2$ 满足 $A\\boldsymbol{x}=0$",
             "它的通解可写成「某个特解 $\\boldsymbol{x}_0$ + 齐次方程组 $A\\boldsymbol{x}=0$ 通解的任意线性组合」"],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构，配合 §3.3 的秩判别定理。\n"
          "A：由 §3.3 的定理，$A\\boldsymbol{x}=b$ 有解 $\\iff r(A)=r(A\\mid b)$；\n"
          "C：$A(\\boldsymbol{x}_1-\\boldsymbol{x}_2)=b-b=\\boldsymbol{0}$；\n"
          "D：设 $\\boldsymbol{x}_0$ 是任一特解，则任一解都可写成 $\\boldsymbol{x}=\\boldsymbol{x}_0+\\boldsymbol{\\eta}$，其中 $\\boldsymbol{\\eta}$ 是 $A\\boldsymbol{x}=0$ 的解；反之式中任取值都满足 $A\\boldsymbol{x}=b$。\n"
          "B 错：非齐次方程组的解集**不含零向量**（若 $\\boldsymbol{0}$ 是解则 $b=A\\boldsymbol{0}=\\boldsymbol{0}$，与非齐次矛盾），而线性子空间必含零向量，故它不是线性子空间。\n"
          "**引申**：非齐次解集恰好是「零空间的一个平移」，抽象代数中称为子空间的**陪集**——这是 §4.4 与 §4.5 的接口。",
    mis="⚠️易错点：非齐次方程组的解集**不是**线性空间——它没有零向量。这是 §4.4 最常被答错的辨析点。",
    tags=["重点", "易错", "高频"],
    verify=[{"desc": "示例一致系统：r(A)", "code": "M([[1,1,1],[1,2,3],[1,3,5]]).rank()", "expected": "2"},
            {"desc": "示例一致系统：r(A|b)", "code": "M([[1,1,1,1],[1,2,3,2],[1,3,5,3]]).rank()", "expected": "2"}]))

# ─────────────────────────────────────────────── 判断 6（基础3 中等2 困难1）
Q_.append(Q(JUDGE, "basic", "4.1",
    "零向量 $\\boldsymbol{0}$ 可以由任意一个向量组线性表示。",
    answer=["A"],
    expl="**答案依据**：§4.1 线性组合的定义——取所有系数 $k_1=\\dots=k_m=0$ 即可得 $\\boldsymbol{0}=0\\cdot\\boldsymbol{\\alpha}_1+\\cdots+0\\cdot\\boldsymbol{\\alpha}_m$。\n"
          "由此得到两个重要推论：① 含零向量的向量组**一定线性相关**（系数取 $1,0,\\dots,0$ 即得非平凡关系）；② 零向量能被表示，但**不能被唯一**表示。",
    mis="⚠️易错点：以为「零向量不在线性组合里」。恰恰相反，取全零系数即可。反过来，「含零向量必线性相关」才需要特别小心。",
    tags=["基础", "易错"],
    verify=[{"desc": "0 = 0·α 的结果", "code": "str(M([1,2,3])*0)", "expected": "Matrix([[0], [0], [0]])"}]))

Q_.append(Q(JUDGE, "basic", "4.2",
    "两个向量 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}$ 线性相关，当且仅当 $\\boldsymbol{\\alpha}=\\boldsymbol{\\beta}$。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。§4.2 中两个向量线性相关的充要条件是二者**成比例**（存在 $k$ 使 $\\boldsymbol{\\beta}=k\\boldsymbol{\\alpha}$，其中一个为零向量时也包含在内），而不是相等。\n"
          "反例：$\\boldsymbol{\\alpha}=(1,2,3)^{\\mathsf T}$，$\\boldsymbol{\\beta}=(2,4,6)^{\\mathsf T}$，二者成比例故线性相关（秩为 1），但显然 $\\boldsymbol{\\alpha}\\neq\\boldsymbol{\\beta}$。",
    mis="⚠️易错点：把「线性相关」误解成「两个向量相等」。相关是**成比例**关系；只有当 $\\boldsymbol{\\beta}=k\\boldsymbol{\\alpha}$ 中恰好 $k=1$ 时才相等。",
    tags=["重点", "易错"],
    verify=[{"desc": "成比例的两个向量的秩为 1（故相关）", "code": "M([[1,2],[2,4],[3,6]]).rank()", "expected": "1"}]))

Q_.append(Q(JUDGE, "basic", "4.3",
    "若向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 的秩为 $r$，则该向量组可以由其中 $r$ 个向量线性表示。",
    answer=["A"],
    expl="**答案依据**：§4.3。秩 $r$ 的定义就是极大线性无关组所含向量的个数，而这个极大线性无关组本身就是原向量组的一个子集；由于原向量组的每个向量都能由极大线性无关组线性表示，故原向量组可由其中 $r$ 个向量线性表示。\n"
          "等价说法：向量组的秩 $=$ 以该向量组为列构成的矩阵的秩 $=$ 列空间的维数。",
    mis="⚠️易错点：以为「秩为 $r$」意味着必须**恰好**找出 $r$ 个无关向量才算数。其实只要找出的线性无关向量个数不超过 $r$，它们就能张成整个向量组。",
    tags=["基础", "重点"],
    verify=[{"desc": "示例：秩为 2 的向量组", "code": "M([[1,2],[0,1],[1,1]]).rank()", "expected": "2"}]))

Q_.append(Q(JUDGE, "medium", "4.4",
    "齐次线性方程组 $A\\boldsymbol{x}=0$ 的任意两个解的任意线性组合仍是它的解。",
    answer=["A"],
    expl="**答案依据**：§4.4。若 $A\\boldsymbol{x}_1=\\boldsymbol{0}$，$A\\boldsymbol{x}_2=\\boldsymbol{0}$，则对任意 $\\lambda,\\mu\\in R$，\n"
          "$$A(\\lambda\\boldsymbol{x}_1+\\mu\\boldsymbol{x}_2)=\\lambda A\\boldsymbol{x}_1+\\mu A\\boldsymbol{x}_2=\\boldsymbol{0},$$\n"
          "由矩阵乘法的线性性可知。这正是「齐次方程组的解集构成 $R^n$ 的线性子空间」的来源，也是 §4.5 子空间定义的直接应用。",
    mis="⚠️易错点：把齐次与非齐次混为一谈——**非齐次**方程组的两个解相加一般不再是解（$b+b\\neq b$），只有作**差**才回到齐次方程组。",
    tags=["重点", "高频"],
    verify=[{"desc": "示例：解向量代入系数阵得零向量", "code": "str(M([[1,1,1],[1,2,3]])*M([[1],[-2],[1]]))", "expected": "Matrix([[0], [0]])"}]))

Q_.append(Q(JUDGE, "medium", "4.2",
    "若向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性相关，则它的任意部分组都线性相关。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。「相关」只说明**整体**存在一组不全为零的系数使线性组合为零向量，并不能保证每个部分组都相关。\n"
          "反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,0)^{\\mathsf T}$。因 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，三者线性相关（秩为 2）；但部分组 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2\\}$ 线性无关。\n"
          "正确的方向是：**无关**组的任意部分组必**无关**。",
    mis="⚠️易错点：把「无关 ⇒ 部分组无关」的方向反过来说成「相关 ⇒ 部分组相关」。方向一错，结论全错。",
    tags=["重点", "易错", "高频"],
    verify=[{"desc": "反例中三向量的秩为 2（<3，相关）", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(JUDGE, "hard", "4.3",
    "两个向量组等价的充分必要条件是它们的秩相等。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。「等价」的定义是两组向量**互相可以线性表示**（§4.1），它**蕴含**秩相等，但**反之不成立**。\n"
          "反例（在 $R^3$ 中）：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$ 与 $\\boldsymbol{\\beta}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\beta}_2=(0,0,1)^{\\mathsf T}$，两组的秩都是 $2$，但 $\\boldsymbol{\\alpha}_2$ 不在 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2$ 张成的子空间内，故不等价。\n"
          "正确表述：等价 $\\Rightarrow$ 秩相等；秩相等只说明两组张成的子空间**维数相同**，未必是同一个子空间。\n"
          "**引申**：这正是「同维子空间」与「同一子空间」的区别——前者只比维数，后者还要求位置一致。",
    mis="⚠️易错点：把「秩相等」当成「等价」的判据。判据是**互相可线性表示**（或秩相等且两组张成同一个子空间）。",
    tags=["难点", "易错", "跨章"],
    verify=[{"desc": "反例中第一组向量的秩", "code": "M([[1,0],[0,1],[0,0]]).rank()", "expected": "2"},
            {"desc": "反例中第二组向量的秩（相等但不等价）", "code": "M([[1,0],[0,0],[0,1]]).rank()", "expected": "2"}]))

# ─────────────────────────────────────────────── 填空 6（基础4 中等1 困难1）
Q_.append(Q(BLANK, "basic", "4.1",
    "设 $\\boldsymbol{\\alpha}=(2,1,-1)^{\\mathsf T}$，$\\boldsymbol{\\beta}=(1,-1,3)^{\\mathsf T}$，则 $3\\boldsymbol{\\alpha}-2\\boldsymbol{\\beta}=$ ______。",
    answer=["(4,5,-9)"],
    accept=["(4,5,-9)", "(4, 5, -9)", "4,5,-9", "(4,5,-9)^T", "(4,5,-9)^{\\mathsf T}"],
    expl="**答案依据**：线性组合是逐分量的加减：$3\\boldsymbol{\\alpha}=(6,3,-3)^{\\mathsf T}$，$2\\boldsymbol{\\beta}=(2,-2,6)^{\\mathsf T}$，相减得\n"
          "$$3\\boldsymbol{\\alpha}-2\\boldsymbol{\\beta}=(6-2,\\;3-(-2),\\;-3-6)^{\\mathsf T}=(4,5,-9)^{\\mathsf T}.$$",
    mis="⚠️易错点：把 $3\\boldsymbol{\\alpha}-2\\boldsymbol{\\beta}$ 拆成 $3(\\boldsymbol{\\alpha}-\\boldsymbol{\\beta})$ 或 $(3-2)(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})$——系数不能这样凑。",
    tags=["基础", "计算"],
    verify=[{"desc": "3α-2β 的三个分量", "code": "str(list(3*M([2,1,-1]) - 2*M([1,-1,3])))", "expected": "[4, 5, -9]"}]))

Q_.append(Q(BLANK, "basic", "4.2",
    "设 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,0)^{\\mathsf T}$，则这三个向量中线性无关的向量最多有 ______ 个。",
    answer=["2"],
    accept=["2", "2个", "2 个", "两"],
    expl="**答案依据**：由 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$ 知三者的秩为 $2$，故线性无关的向量个数最多为 $2$（取 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 即可达到）。\n"
          "（§4.3：线性无关向量的最大个数 $=$ 向量组的秩。）",
    mis="⚠️易错点：答成 3。线性无关向量的**个数**受秩限制，秩为 2 时最多只能取 2 个。",
    tags=["基础", "重点"],
    verify=[{"desc": "三向量作列的矩阵的秩", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(BLANK, "basic", "4.3",
    "向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 的秩，等于它的 ______ 中所含向量的个数。",
    answer=["极大线性无关组"],
    accept=["极大线性无关组", "极大无关组", "极大线性无关向量组", "极大无关向量组"],
    expl="**答案依据**：§4.3 的定义——向量组的秩就是它的**极大线性无关组**所含向量的个数。极大线性无关组的含义是：本身线性无关，而向量组中任何 $r+1$ 个向量都线性相关。\n"
          "配套定理（§4.3）：向量组的秩 $=$ 以该向量组为列构成的矩阵的秩。",
    mis="⚠️易错点：术语要写全——教材原文是「**极大线性无关组**」，漏掉「线性」二字虽意思相近，但不是标准表述。",
    tags=["基础", "必背"],
    verify=[{"desc": "示例：秩（= 极大线性无关组个数）为 2", "code": "M([[1,2],[0,1],[1,1]]).rank()", "expected": "2"}]))

Q_.append(Q(BLANK, "basic", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵且 $r(A)=r$，则齐次线性方程组 $A\\boldsymbol{x}=0$ 的基础解系含有 ______ 个线性无关的解向量。",
    answer=["n-r"],
    accept=["n-r", "n-r个", "n - r", "n－r", "n-r(个)"],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构——基础解系由 $n-r(A)$ 个线性无关的解向量构成，它们恰好张成整个解空间，故解空间的维数也是 $n-r(A)$。\n"
          "（当 $r(A)=n$ 时基础解系为空，只有零解，维数为 $0$。）",
    mis="⚠️易错点：写成 $r$ 或 $n$。正确答案是**自由未知量的个数** $n-r(A)$。",
    tags=["基础", "重点", "必背"],
    verify=[{"desc": "示例：n-r（3 元 2 阶系数阵）", "code": "3 - M([[1,1,1],[1,2,3]]).rank()", "expected": "1"}]))

Q_.append(Q(BLANK, "medium", "4.5",
    "在 $R^3$ 中，$W_1=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=0\\}$ 是 $R^3$ 的子空间，而 $W_2=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=1\\}$ 不是子空间。判断 $W_2$ 不是子空间的依据是：$W_2$ 中不含 ______ 向量。",
    answer=["零"],
    accept=["零", "零向量", "0", "零向量(0,0,0)", "(0,0,0)", "零（0）"],
    expl="**答案依据**：§4.5——子空间必含零向量（由封闭性推出：取任一 $\\boldsymbol{\\alpha}\\in W$，则 $0\\boldsymbol{\\alpha}=\\boldsymbol{0}\\in W$）。\n"
          "$W_2$ 中每个向量满足 $x+y+z=1$，而零向量的分量和为 $0\\neq1$，故 $\\boldsymbol{0}\\notin W_2$，$W_2$ 不是子空间。\n"
          "相对地，$W_1$ 由**齐次**线性方程给出，对加法与数乘都封闭，故是子空间——这与 §4.4「齐次方程组的解集是子空间、非齐次方程组的解集不是子空间」完全对应。",
    mis="⚠️易错点：以为「集合里都是实数坐标所以是向量空间」。判据是**含零向量 + 对加法与数乘封闭**，缺一不可。",
    tags=["重点", "跨章"],
    verify=[{"desc": "零向量的分量和为 0，不等于 1，故零向量∉W2", "code": "sum(M([0,0,0]))", "expected": "0"}]))

Q_.append(Q(BLANK, "hard", "4.3",
    "若向量组 $\\boldsymbol{\\alpha}_1=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,2)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_4=(1,0,0)^{\\mathsf T}$，则这四个向量的极大线性无关组含有的向量个数是 ______。",
    answer=["3"],
    accept=["3", "3个", "3 个", "三"],
    expl="**答案依据**：§4.3——极大线性无关组所含向量的个数即该向量组的秩。\n"
          "第一步：$\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，故这四个向量的秩 $\\le 3$；\n"
          "第二步：$\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_4$ 的行列式为 $-1\\neq0$，故三者线性无关，秩 $\\ge3$；\n"
          "综合得秩 $=3$，即极大线性无关组含 $3$ 个向量。",
    mis="⚠️易错点：只做到 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$ 就写「秩为 2」，漏掉了 $\\boldsymbol{\\alpha}_4$ 这个新的独立方向。",
    tags=["难点", "计算", "高频"],
    verify=[{"desc": "四向量作列的矩阵的秩", "code": "M([[1,0,1,1],[0,1,1,0],[1,1,2,0]]).rank()", "expected": "3"},
            {"desc": "α1,α2,α4 的行列式（非零，故线性无关）", "code": "M([[1,0,1],[0,1,0],[1,1,0]]).det()", "expected": "-1"}]))

# ─────────────────────────────────────────────── 简答与名词解释 6（基础3 中等2 困难1）
Q_.append(Q(TERM, "basic", "4.2",
    "名词解释：**线性相关**（linearly dependent）与**线性无关**（linearly independent）。",
    answer_text="设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 是 $R^n$ 中的 $s$ 个向量。若存在**不全为零**的实数 $k_1,\\dots,k_s$，使得\n"
                "$$k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0},$$\n"
                "则称向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ **线性相关**；若上式只有 $k_1=\\dots=k_s=0$ 这一种解，则称该向量组**线性无关**。\n\n"
                "**关键理解**：线性相关 $\\iff$ 存在一个**非平凡的**系数组合把向量组「压」成零向量；线性无关 $\\iff$ 不存在这样的组合。\n\n"
                "**基本推论**：\n"
                "① 含零向量的向量组一定线性相关；\n"
                "② $s>n$（向量个数超过维数）时必然线性相关；\n"
                "③ 线性无关组的任意部分组仍线性无关；\n"
                "④ 向量组线性相关 $\\iff$ 以该向量组为列构成的矩阵的秩小于向量个数 $s$。",
    points=[{"text": "写清线性相关的定义：存在不全为零的系数 $k_1,\\dots,k_s$ 使 $\\sum k_i\\boldsymbol{\\alpha}_i=\\boldsymbol{0}$", "partial": 2},
            {"text": "指出线性无关是「只有全零系数解」的情形，并补充「含零向量必相关」「$s>n$ 必相关」等推论", "partial": 2}],
    expl="**答案依据**：§4.2 向量组的线性相关性的定义及其基本推论。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性。",
    mis="⚠️易错点：把定义里的「**不全为零**」漏掉——若允许全零系数，任何向量组都会「线性相关」，定义就失效了。",
    tags=["名词解释", "必背", "重点"],
    verify=[{"desc": "示例：三向量秩为 2（<3，故相关）", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(TERM, "basic", "4.3",
    "名词解释：**极大线性无关组**与向量组的**秩**。",
    answer_text="设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 是 $R^n$ 中的 $s$ 个向量。如果其中的一部分向量 $\\boldsymbol{\\alpha}_{i_1},\\dots,\\boldsymbol{\\alpha}_{i_r}$ **线性无关**，而向量组中**任何** $r+1$ 个向量都线性相关，则称 $\\boldsymbol{\\alpha}_{i_1},\\dots,\\boldsymbol{\\alpha}_{i_r}$ 是该向量组的一个**极大线性无关组**。\n\n"
                "向量组的**秩**就是它的极大线性无关组所含向量的个数，记作 $r(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)$。极大线性无关组本身**不唯一**（可以换），但**个数唯一**——都等于秩。\n\n"
                "**重要定理（§4.3）**：\n"
                "① 向量组的秩 $=$ 以该向量组为列向量构成的矩阵的秩；\n"
                "② 向量组的任一向量都可由任取的一个极大线性无关组线性表示；\n"
                "③ 线性无关向量的最大个数就是该向量组的秩。",
    points=[{"text": "写出极大线性无关组的定义：本身线性无关，且向量组中任何 $r+1$ 个向量都线性相关", "partial": 2},
            {"text": "写出秩的定义（极大线性无关组所含向量个数）并指出个数唯一、与矩阵的秩相等", "partial": 2}],
    expl="**答案依据**：§4.3 向量组的秩与极大线性无关组。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：以为「极大线性无关组是唯一的」。它**不唯一**（可换底），唯一的是它的**个数**即秩。",
    tags=["名词解释", "必背"],
    verify=[{"desc": "示例：秩（= 极大线性无关组个数）为 3", "code": "M([[1,0,1,1],[0,1,1,0],[1,1,2,0]]).rank()", "expected": "3"}]))

Q_.append(Q(SHORT, "basic", "4.1",
    "写出向量组等价的定义，并说明向量组等价与「秩相等」之间的关系。",
    answer_text="**定义（§4.1）**：设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 是两组向量。若 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 中每一个向量都可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性表示，**且** $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 中每一个向量都可由 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 线性表示，则称这两个向量组**等价**。\n\n"
                "**几何意义**：两组向量**张成同一个子空间**。记 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)$ 为由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 张成的子空间，则\n"
                "$$L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)=L(\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t).$$\n\n"
                "**与秩的关系**：等价 $\\Rightarrow$ 秩相等（张成同一子空间，维数自然相同）；但**反之不成立**。\n"
                "反例（$R^3$ 中）：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$ 与 $\\boldsymbol{\\beta}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\beta}_2=(0,0,1)^{\\mathsf T}$ 的秩都是 $2$，但二者张成的子空间不同，故不等价。\n\n"
                "**注**：若两组向量不仅秩相等，而且都是同一个子空间的基（如都取自 $L$ 中的极大线性无关组），则它们等价——这正是「秩相等 + 同处一个空间」的用法。",
    points=[{"text": "写出等价定义：两个方向的线性表示都能成立", "partial": 2},
            {"text": "指出等价即两组向量张成同一个子空间", "partial": 2},
            {"text": "说明「等价推出秩相等，但秩相等推不出等价」，并举出秩相等而不等价的反例", "partial": 2}],
    expl="**答案依据**：§4.1 向量组等价；配合 §4.3 的秩。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：把「秩相等」当作「等价」的充要条件——它只是必要条件。",
    tags=["重点", "必背"],
    verify=[{"desc": "反例中第一组向量的秩", "code": "M([[1,0],[0,1],[0,0]]).rank()", "expected": "2"},
            {"desc": "反例中第二组向量的秩（相等但不等价）", "code": "M([[1,0],[0,0],[0,1]]).rank()", "expected": "2"}]))

Q_.append(Q(SHORT, "medium", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵且 $r(A)<n$。说明齐次线性方程组 $A\\boldsymbol{x}=0$ 的解的结构：基础解系是什么？通解如何写出？解空间的维数是多少？",
    answer_text="**基础解系**：把系数矩阵 $A$ 用初等行变换化为行阶梯形，再继续化为**最简阶梯形**（每列的首个非零元素上方与下方全为零），找出**自由未知量** $x_{r+1},\\dots,x_n$（其中 $r=r(A)$）。令自由未知量依次取 $1$、其余自由未知量取 $0$，解出对应的 $n-r$ 个线性无关的解向量\n"
                "$$\\boldsymbol{\\eta}_1,\\boldsymbol{\\eta}_2,\\dots,\\boldsymbol{\\eta}_{n-r},$$\n"
                "它们就构成该方程组的**基础解系**。\n\n"
                "**通解**：齐次方程组的全部解恰为基础解系的任意线性组合\n"
                "$$\\boldsymbol{x}=c_1\\boldsymbol{\\eta}_1+c_2\\boldsymbol{\\eta}_2+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r},\\qquad c_1,\\dots,c_{n-r}\\in R.$$\n\n"
                "**解空间**：全部解构成 $R^n$ 的一个 $n-r(A)$ 维线性子空间，维数为 $n-r(A)$；当 $r(A)=n$ 时基础解系为空、只有零解、维数为 $0$。\n\n"
                "**要点**：基础解系**不唯一**（取法不同则结果不同），但**个数唯一**，等于 $n-r(A)$，也就是解空间的维数；基础解系必须由原方程组**解出**，不能任意取。",
    points=[{"text": "说明基础解系的求法：化为最简阶梯形、令自由未知量取单位列求基本解", "partial": 2},
            {"text": "写出通解形式：$\\boldsymbol{x}=\\sum c_i\\boldsymbol{\\eta}_i$，共 $n-r(A)$ 个自由参数", "partial": 2},
            {"text": "指出解空间是 $n-r(A)$ 维子空间，基础解系个数等于解空间维数", "partial": 2}],
    expl="**答案依据**：§4.4 线性方程组的解的结构（齐次方程组）；求基础解系要配合 §3.1 初等变换。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：化到行阶梯形就停下，忘了继续化成**最简阶梯形**（或忘了「每列挑一个自由未知量」），结果自由未知量选错、方程解错。",
    tags=["重点", "高频"],
    verify=[{"desc": "示例：基础解系含 n-r=1 个向量", "code": "len(M([[1,1,1],[1,2,3]]).nullspace())", "expected": "1"},
            {"desc": "示例：基础解系的三个分量", "code": "str(list(M([[1,1,1],[1,2,3]]).nullspace()[0]))", "expected": "[1, -2, 1]"}]))

Q_.append(Q(SHORT, "medium", "4.4",
    "设非齐次线性方程组 $A\\boldsymbol{x}=b$ 有解。说明它的解集的结构：特解与通解的关系是什么？解集是不是线性空间？",
    answer_text="**前提**：$A\\boldsymbol{x}=b$ 有解 $\\iff r(A)=r(A\\mid b)$（§3.3 秩判别定理）。此时先求出一个**特解** $\\boldsymbol{x}_0$（把常数项换成 $0$ 再解齐次方程组即可；等价地把增广矩阵化为阶梯形后读出自由未知量取 $0$ 的那一组解）。\n\n"
                "**通解**：非齐次方程组的全部解为\n"
                "$$\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r},$$\n"
                "其中 $\\boldsymbol{\\eta}_1,\\dots,\\boldsymbol{\\eta}_{n-r}$ 是齐次方程组 $A\\boldsymbol{x}=0$ 的基础解系，$c_i$ 为任意实数。反之，式中任取值都满足原方程组，因为 $A\\boldsymbol{x}_0=b$ 而 $A\\boldsymbol{\\eta}_i=\\boldsymbol{0}$。\n\n"
                "**解集的几何结构**：解集**不是**线性空间，而是「一个特解 $\\boldsymbol{x}_0$ 加上零空间（齐次解空间）」的**平移**：\n"
                "$$\\{\\boldsymbol{x}\\mid A\\boldsymbol{x}=b\\}=\\boldsymbol{x}_0+Z(A),$$\n"
                "其中 $Z(A)=\\{\\boldsymbol{\\eta}\\mid A\\boldsymbol{\\eta}=0\\}$ 是齐次解空间，维数为 $n-r(A)$。理由：解集不含零向量（若 $\\boldsymbol{0}$ 是解则 $b=A\\boldsymbol{0}=\\boldsymbol{0}$，与非齐次矛盾），而线性子空间必含零向量。\n\n"
                "**要点**：特解不唯一（任取一个即可），但不同特解之差必是齐次方程组的解。\n\n"
                "**引申**：把解集看成「零空间的一个平移」，正是抽象代数中**陪集**的标准模型；§4.5 的子空间概念在这里与 §4.4 的解结构接上了。",
    points=[{"text": "说明有解条件 $r(A)=r(A|b)$ 并先求出一个特解", "partial": 2},
            {"text": "写出通解 = 特解 + 齐次通解的线性组合，并说明其正确性", "partial": 2},
            {"text": "指出解集是「特解 + 零空间」的平移，不是线性空间（不含零向量）", "partial": 2}],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构，配合 §3.3 秩判别定理与 §4.5 子空间。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：非齐次方程组的解集**不是**线性子空间（不含零向量），这是本节最常被答错的辨析点。",
    tags=["重点", "易错", "高频"],
    verify=[{"desc": "示例：r(A)", "code": "M([[1,1,1],[1,2,3]]).rank()", "expected": "2"},
            {"desc": "示例：r(A|b)（与 r(A) 相等，故有解）", "code": "M([[1,1,1,1],[1,2,3,2]]).rank()", "expected": "2"},
            {"desc": "示例：特解 x0=(0,1,0) 代入系数阵的结果", "code": "str(list(M([[1,1,1],[1,2,3]])*M([[0],[1],[0]])))", "expected": "[1, 2]"}]))

Q_.append(Q(SHORT, "hard", "4.5",
    "写出向量空间与子空间的定义，说明 $W$ 是 $V$ 的子空间的判定定理，并解释「$W$ 非空且含零向量」为什么还不够。",
    answer_text="**向量空间（§4.5）**：设 $K$ 是数域，$V$ 是由 $K$ 上向量组成的非空集合。若对任意 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in V$ 及任意 $k,l\\in K$，都有 $k\\boldsymbol{\\alpha}+l\\boldsymbol{\\beta}\\in V$（即对向量的**加法**和**数乘**都封闭），则称 $V$ 是 $K$ 上的**向量空间**（线性空间）。\n\n"
                "**子空间**：设 $V$ 是数域 $K$ 上的向量空间，$W$ 是 $V$ 的非空子集。若 $W$ 本身也是 $K$ 上的向量空间，则称 $W$ 是 $V$ 的**子空间**。\n\n"
                "**判定定理**：设 $W$ 是 $V$ 的非空子集，则\n"
                "$$W\\text{ 是 }V\\text{ 的子空间}\\iff W\\text{ 对向量的加法与数乘封闭}\\iff \\forall\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in W,\\;\\forall k,l\\in K:\\;k\\boldsymbol{\\alpha}+l\\boldsymbol{\\beta}\\in W.$$\n"
                "**推论**：若 $W$ 是子空间，则 $\\boldsymbol{0}\\in W$，且对任意 $\\boldsymbol{\\alpha}\\in W$ 有 $-\\boldsymbol{\\alpha}\\in W$（分别取 $k=0$ 与 $k=-1$）。\n\n"
                "**为什么「非空 + 含零向量」还不够**：这两个条件只说明 $W$ 里有 $\\boldsymbol{0}$，却**不能**保证 $W$ 对运算封闭。\n"
                "反例：在 $R^3$ 中取 $W=\\{\\boldsymbol{0},\\boldsymbol{e}_1\\}=\\{(0,0,0)^{\\mathsf T},(1,0,0)^{\\mathsf T}\\}$。它非空且含零向量，但 $\\boldsymbol{e}_1+\\boldsymbol{e}_1=(2,0,0)^{\\mathsf T}\\notin W$，对加法不封闭，故不是子空间。\n"
                "另一个反例：$W=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=1\\}$ 不含零向量，直接被排除。\n\n"
                "**引申**：把 §4.3 的极大线性无关组与本节的子空间结合起来，就得到「子空间的基与维数」——极大线性无关组即子空间的一组基，其个数即该子空间的维数（教材第 6 章选学部分）。",
    points=[{"text": "写出向量空间的定义（$K$ 上向量集合对线性组合封闭）与子空间的定义（非空子集且本身是向量空间）", "partial": 2},
            {"text": "写出子空间判定定理（非空 + 对加法与数乘封闭）及零向量、负向量的推论", "partial": 2},
            {"text": "举出「非空且含零向量但对加法不封闭」的反例并说明其不是子空间", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间的定义及判定定理。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：把「含零向量」当成子空间的充分条件。子空间要求对加法、数乘**封闭**，零向量只是封闭性的推论之一。",
    ext="引申：子空间的基与维数见教材第 6 章（选学）——§4.3 的极大线性无关组即子空间的一组基。",
    tags=["难点", "重点", "跨章"],
    verify=[{"desc": "反例：e1+e1=(2,0,0) 不在 W={0,e1} 中", "code": "str(list(M([1,0,0]) + M([1,0,0])))", "expected": "[2, 0, 0]"}]))

# ─────────────────────────────────────────────── 计算与分析 7（基础3 中等3 困难1）
Q_.append(Q(CALC, "basic", "4.2",
    "判断向量组 $\\boldsymbol{\\alpha}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(2,2,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,1)^{\\mathsf T}$ 是否线性相关；若是，求出一组不全为零的系数 $k_1,k_2,k_3$ 使 $k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+k_3\\boldsymbol{\\alpha}_3=\\boldsymbol{0}$。",
    answer_text="以三个向量为列构成矩阵\n$$A=\\begin{pmatrix}1&2&1\\\\1&2&1\\\\0&1&1\\end{pmatrix}.$$\n"
                "由 §4.2 与 §3.2，向量组线性相关 $\\iff r(A)<3\\iff|A|=0$。\n\n"
                "$$|A|=1\\cdot\\begin{vmatrix}2&1\\\\1&1\\end{vmatrix}-2\\cdot\\begin{vmatrix}1&1\\\\0&1\\end{vmatrix}+1\\cdot\\begin{vmatrix}1&2\\\\0&1\\end{vmatrix}=1\\cdot(2-1)-2\\cdot(1-0)+1\\cdot(1-0)=1-2+1=0.$$\n"
                "故向量组**线性相关**。\n\n"
                "**求系数**：由 $k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+k_3\\boldsymbol{\\alpha}_3=\\boldsymbol{0}$ 得方程组\n"
                "$$\\begin{cases}k_1+2k_2+k_3=0\\\\k_1+2k_2+k_3=0\\\\k_2+k_3=0\\end{cases}\\Longrightarrow\\begin{cases}k_1=-k_2\\\\k_3=-k_2\\end{cases}.$$\n"
                "取 $k_2=1$，得 $k_1=-1,\\;k_3=-1$，即\n$$1\\cdot\\boldsymbol{\\alpha}_1+1\\cdot\\boldsymbol{\\alpha}_2+(-1)\\cdot\\boldsymbol{\\alpha}_3=\\boldsymbol{0},$$\n"
                "等价地 $\\boldsymbol{\\alpha}_2=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_3$。\n\n"
                "**验证**：$(1,1,0)^{\\mathsf T}-(2,2,1)^{\\mathsf T}+(1,1,1)^{\\mathsf T}=(0,0,0)^{\\mathsf T}$ ✓",
    points=[{"text": "写出以三向量为列的矩阵，并用 $|A|=0$ 判定线性相关", "partial": 2},
            {"text": "正确算出 $|A|=0$（行列式展开无误）", "partial": 2},
            {"text": "解出系数关系 $k_1=-k_2,\\;k_3=-k_2$ 并给出一组具体系数", "partial": 2},
            {"text": "写出关系式并回代验证为零向量", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的判定（以向量为列的矩阵秩小于列数）+ §1.5 行列式按行展开。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性。",
    mis="⚠️易错点：算出 $|A|=0$ 后**不求系数**就收工。判定相关只是第一步，本题还要求写出那组「不全为零」的系数。",
    tags=["计算", "重点", "高频"],
    verify=[{"desc": "三向量作列的矩阵的秩为 2（<3，故相关）", "code": "M([[1,2,1],[1,2,1],[0,1,1]]).rank()", "expected": "2"},
            {"desc": "关系式 α1-α2+α3=0 的验证结果", "code": "str(M([1,1,0]) - M([2,2,1]) + M([1,1,1]))", "expected": "Matrix([[0], [0], [0]])"}]))

Q_.append(Q(CALC, "basic", "4.3",
    "求向量组 $\\boldsymbol{\\alpha}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,2,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_4=(2,3,1)^{\\mathsf T}$ 的秩，并求出一个极大线性无关组。",
    answer_text="以四个向量为列作矩阵\n$$A=\\begin{pmatrix}1&0&1&2\\\\1&1&2&3\\\\0&1&1&1\\end{pmatrix}.$$\n"
                "作初等行变换（§3.1）：\n"
                "$$R_2\\leftarrow R_2-R_1\\;\\Longrightarrow\\;\\begin{pmatrix}1&0&1&2\\\\0&1&1&1\\\\0&1&1&1\\end{pmatrix}\\xrightarrow{\\;R_3\\leftarrow R_3-R_2\\;}\\;\\begin{pmatrix}1&0&1&2\\\\0&1&1&1\\\\0&0&0&0\\end{pmatrix}.$$\n"
                "非零行数为 $2$，故 $r(A)=2$；由 §4.3，向量组的秩为 $\\boxed{2}$。\n\n"
                "非零行对应的列是第 1、2 列，故取 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$。验证它们线性无关：\n"
                "$$\\begin{vmatrix}1&0\\\\1&1\\end{vmatrix}=1\\neq0,$$\n"
                "即取前两行所得二阶子式非零，故 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性无关。\n\n"
                "又 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，$\\boldsymbol{\\alpha}_4=2\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，其余两个向量都在 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 张成的子空间内，故 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2\\}$ 是一个**极大线性无关组**。\n\n"
                "**答案**：秩为 $2$，极大线性无关组可取 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2\\}$。",
    points=[{"text": "写出以四个向量为列的矩阵并作初等行变换", "partial": 2},
            {"text": "由非零行数读出秩 $r(A)=2$", "partial": 2},
            {"text": "指出 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性无关（二阶子式非零）", "partial": 2},
            {"text": "写出极大线性无关组并说明 $\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$ 可由它表示", "partial": 2}],
    expl="**答案依据**：§4.3 向量组的秩 $=$ 矩阵的秩（§3.2）；极大线性无关组由初等行变换后有主元的列给出（§3.1）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：行变换后随手取前两列——必须取**有主元（首列非零）**的那些列，并回到**原矩阵**去取对应的列向量。",
    tags=["计算", "基础", "高频"],
    verify=[{"desc": "四向量作列的矩阵的秩", "code": "M([[1,0,1,2],[1,1,2,3],[0,1,1,1]]).rank()", "expected": "2"},
            {"desc": "α1,α2 的二阶子式（非零，故线性无关）", "code": "M([[1,0],[1,1]]).det()", "expected": "1"}]))

Q_.append(Q(CALC, "basic", "4.1",
    "判断向量 $\\boldsymbol{\\beta}=(1,2,3)^{\\mathsf T}$ 能否由向量组 $\\boldsymbol{\\alpha}_1=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$ 线性表示；若能，求出表示式。",
    answer_text="设 $\\boldsymbol{\\beta}=k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2$，按分量列出方程：\n"
                "$$k_1\\begin{pmatrix}1\\\\0\\\\1\\end{pmatrix}+k_2\\begin{pmatrix}0\\\\1\\\\1\\end{pmatrix}=\\begin{pmatrix}1\\\\2\\\\3\\end{pmatrix}\\Longleftrightarrow\\begin{cases}k_1=1\\\\k_2=2\\\\k_1+k_2=3\\end{cases}.$$\n"
                "第一个方程给出 $k_1=1$，第二个方程给出 $k_2=2$；代回第三个方程检验：$1+2=3$ 成立，方程组相容，故 $\\boldsymbol{\\beta}$ **可以**由 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性表示，且\n"
                "$$\\boxed{\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2}.$$\n\n"
                "（由于 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性无关——其前两行组成的二阶子式为 $\\begin{vmatrix}1&0\\\\0&1\\end{vmatrix}=1\\neq0$——该表示式是**唯一**的。）",
    points=[{"text": "设出待定系数并列出三个分量方程", "partial": 2},
            {"text": "解出 $k_1=1,\\;k_2=2$ 并检验第三个方程相容", "partial": 2},
            {"text": "给出表示式 $\\boldsymbol{\\beta}=\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2$", "partial": 2},
            {"text": "指出该向量组线性无关故表示式唯一", "partial": 2}],
    expl="**答案依据**：§4.1 线性组合与线性表示；唯一性由 §4.2 线性无关给出。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：只解出两个方程就下结论，**不检验第三个方程**。三个分量方程必须同时成立，否则该向量不能被表示。",
    tags=["计算", "基础"],
    verify=[{"desc": "α1+2α2 的结果（应等于 β）", "code": "str(M([1,0,1]) + 2*M([0,1,1]))", "expected": "Matrix([[1], [2], [3]])"}]))

Q_.append(Q(CALC, "medium", "4.4",
    "求齐次线性方程组 $\\begin{cases}x_1+x_2+x_3=0\\\\x_1+2x_2+3x_3=0\\end{cases}$ 的基础解系，并写出它的通解。",
    answer_text="系数矩阵作初等行变换：\n"
                "$$\\begin{pmatrix}1&1&1\\\\1&2&3\\end{pmatrix}\\xrightarrow{\\;R_2\\leftarrow R_2-R_1\\;}\\begin{pmatrix}1&1&1\\\\0&1&2\\end{pmatrix}\\xrightarrow{\\;R_1\\leftarrow R_1-R_2\\;}\\begin{pmatrix}1&0&-1\\\\0&1&2\\end{pmatrix}.$$\n"
                "最简阶梯形中 $x_3$ 是自由未知量，第一行给出 $x_1-x_3=0$，第二行给出 $x_2+2x_3=0$，即 $x_1=x_3,\\;x_2=-2x_3$。\n\n"
                "令自由未知量 $x_3=1$（其余自由未知量取 $0$），得基本解\n$$\\boldsymbol{\\eta}_1=\\begin{pmatrix}1\\\\-2\\\\1\\end{pmatrix}.$$\n"
                "**检验**：$1+(-2)+1=0$ ✓；$1+2\\times(-2)+3\\times1=0$ ✓。\n\n"
                "由于 $r(A)=2$，$n-r(A)=3-2=1$，故基础解系只含 $1$ 个向量：$\\left\\{\\begin{pmatrix}1\\\\-2\\\\1\\end{pmatrix}\\right\\}$。\n\n"
                "**通解**为\n$$\\boldsymbol{x}=c\\begin{pmatrix}1\\\\-2\\\\1\\end{pmatrix},\\qquad c\\in R,$$\n即 $x_1=c,\\;x_2=-2c,\\;x_3=c$。",
    points=[{"text": "对系数矩阵作初等行变换得到最简阶梯形", "partial": 2},
            {"text": "识别自由未知量并求出基本解向量 $(1,-2,1)^{\\mathsf T}$", "partial": 2},
            {"text": "写出基础解系并说明其个数为 $n-r(A)=1$", "partial": 2},
            {"text": "写出通解 $\\boldsymbol{x}=c\\boldsymbol{\\eta}_1$ 并回代检验", "partial": 2}],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构，配合 §3.1 初等行变换求基础解系。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：化到行阶梯形就停下，忘了继续化成**最简阶梯形**（或忘了「每列挑一个自由未知量」），结果自由未知量选错、方程解错。",
    tags=["计算", "重点", "高频"],
    verify=[{"desc": "基础解系含 n-r=1 个向量", "code": "len(M([[1,1,1],[1,2,3]]).nullspace())", "expected": "1"},
            {"desc": "基础解系的三个分量", "code": "str(list(M([[1,1,1],[1,2,3]]).nullspace()[0]))", "expected": "[1, -2, 1]"}]))

Q_.append(Q(CALC, "medium", "4.4",
    "求非齐次线性方程组 $\\begin{cases}x_1+x_2+x_3=1\\\\x_1+2x_2+3x_3=2\\end{cases}$ 的通解。",
    answer_text="增广矩阵作初等行变换：\n"
                "$$\\begin{pmatrix}1&1&1&1\\\\1&2&3&2\\end{pmatrix}\\xrightarrow{\\;R_2\\leftarrow R_2-R_1\\;}\\begin{pmatrix}1&1&1&1\\\\0&1&2&1\\end{pmatrix}\\xrightarrow{\\;R_1\\leftarrow R_1-R_2\\;}\\begin{pmatrix}1&0&-1&0\\\\0&1&2&1\\end{pmatrix}.$$\n"
                "第二行给出 $x_2+2x_3=1$，第一行给出 $x_1-x_3=0$，故 $x_1=x_3$，$x_2=1-2x_3$。令自由未知量 $x_3=t$，则\n"
                "$$x_1=t,\\qquad x_2=1-2t,\\qquad x_3=t.$$\n\n"
                "**求特解**：取 $t=0$，得一个特解 $\\boldsymbol{x}_0=\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}$（检验：$0+1+0=1$ ✓，$0+2\\times1+0=2$ ✓）。\n\n"
                "**求齐次部分**：对应齐次方程组 $x_1+x_2+x_3=0,\\;x_1+2x_2+3x_3=0$ 的基础解系为 $\\boldsymbol{\\eta}_1=\\begin{pmatrix}1\\\\-2\\\\1\\end{pmatrix}$（$r(A)=2$，故 $n-r=1$）。\n\n"
                "**通解**（§4.4 的「特解 + 齐次通解」）：\n"
                "$$\\boldsymbol{x}=\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}+t\\begin{pmatrix}1\\\\-2\\\\1\\end{pmatrix},\\qquad t\\in R.$$\n"
                "检验：$A\\begin{pmatrix}t\\\\1-2t\\\\t\\end{pmatrix}=\\begin{pmatrix}t+1-2t+t\\\\t+2(1-2t)+3t\\end{pmatrix}=\\begin{pmatrix}1\\\\2\\end{pmatrix}$ ✓",
    points=[{"text": "对增广矩阵作初等行变换并解出 $x_1,x_2$ 与自由未知量 $x_3$ 的关系", "partial": 2},
            {"text": "求出一个特解 $\\boldsymbol{x}_0=(0,1,0)^{\\mathsf T}$", "partial": 2},
            {"text": "写出齐次方程组的基础解系 $\\boldsymbol{\\eta}_1=(1,-2,1)^{\\mathsf T}$", "partial": 2},
            {"text": "写出通解「特解 + $t\\boldsymbol{\\eta}_1$」并回代检验", "partial": 2}],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构（特解 + 齐次通解）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：把特解与齐次基础解系**混着写**（在特解上再加参数项）。记住：特解是一个**固定的向量**，带参数的是齐次解。",
    tags=["计算", "重点", "高频"],
    verify=[{"desc": "示例：r(A)=r(A|b)，故有解", "code": "M([[1,1,1,1],[1,2,3,2]]).rank()", "expected": "2"},
            {"desc": "特解 x0=(0,1,0) 代入系数阵的结果", "code": "str(list(M([[1,1,1],[1,2,3]])*M([[0],[1],[0]])))", "expected": "[1, 2]"},
            {"desc": "齐次基础解系的三个分量", "code": "str(list(M([[1,1,1],[1,2,3]]).nullspace()[0]))", "expected": "[1, -2, 1]"}]))

Q_.append(Q(CALC, "medium", "4.3",
    "求向量组 $\\boldsymbol{\\alpha}_1=(1,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(1,2,4)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(2,3,5)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_4=(1,1,2)^{\\mathsf T}$ 的秩，并求出一个极大线性无关组。",
    answer_text="以四个向量为列作矩阵\n$$A=\\begin{pmatrix}1&1&2&1\\\\1&2&3&1\\\\1&4&5&2\\end{pmatrix}.$$\n"
                "作初等行变换：\n"
                "$$R_3\\leftarrow R_3-R_1\\;\\Longrightarrow\\;\\begin{pmatrix}1&1&2&1\\\\1&2&3&1\\\\0&3&3&1\\end{pmatrix}\\xrightarrow{\\;R_2\\leftarrow R_2-R_1\\;}\\begin{pmatrix}1&1&2&1\\\\0&1&1&0\\\\0&3&3&1\\end{pmatrix}\\xrightarrow{\\;R_3\\leftarrow R_3-3R_2\\;}\\begin{pmatrix}1&1&2&1\\\\0&1&1&0\\\\0&0&0&1\\end{pmatrix}.$$\n"
                "非零行数为 $3$，故 $r(A)=3$，向量组的秩为 $\\boxed{3}$。\n\n"
                "有主元（首列非零）的列是第 1、2、4 列，故取 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_4$。验证它们线性无关：\n"
                "$$\\begin{vmatrix}1&1&1\\\\1&2&1\\\\1&4&2\\end{vmatrix}=1\\cdot(2\\cdot2-1\\cdot4)-1\\cdot(1\\cdot2-1\\cdot1)+1\\cdot(1\\cdot4-2\\cdot1)=0-1+2=1\\neq0,$$\n"
                "故三者线性无关；又 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，所以 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_4$ 正是极大线性无关组。\n\n"
                "**答案**：秩为 $3$，极大线性无关组可取 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_4\\}$。",
    points=[{"text": "写出以四个向量为列的矩阵并作初等行变换", "partial": 2},
            {"text": "由非零行数读出秩 $r(A)=3$", "partial": 2},
            {"text": "指出极大线性无关组为 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_4\\}$ 并验证行列式非零", "partial": 2},
            {"text": "说明 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，其余向量可由该组表示", "partial": 2}],
    expl="**答案依据**：§4.3 向量组的秩 $=$ 矩阵的秩（§3.2）；极大线性无关组由初等行变换后有主元的列确定（§3.1）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：行变换后随手取前几列——必须取**有主元（该列首非零）**的那些列，且要回到**原矩阵**取对应的列向量。",
    tags=["计算", "重点", "高频"],
    verify=[{"desc": "四向量作列的矩阵的秩", "code": "M([[1,1,2,1],[1,2,3,1],[1,4,5,2]]).rank()", "expected": "3"},
            {"desc": "α1,α2,α4 的行列式（非零，故线性无关）", "code": "M([[1,1,1],[1,2,1],[1,4,2]]).det()", "expected": "1"}]))

Q_.append(Q(CALC, "hard", "4.5",
    "在 $R^3$ 中判断下列集合是否为 $R^3$ 的子空间，并说明理由：(1) $W_1=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=0\\}$；(2) $W_2=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=1\\}$；(3) $W_3=\\{(x,y,z)^{\\mathsf T}\\mid x\\cdot y=0\\}$。",
    answer_text="**判定依据（§4.5）**：设 $W$ 是 $V$ 的非空子集，则 $W$ 是 $V$ 的子空间 $\\iff W$ 非空且对向量的加法与数乘封闭。\n\n"
                "**(1) $W_1$ 是子空间**：非空（含 $\\boldsymbol{0}=(0,0,0)^{\\mathsf T}$）。设 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in W_1$，其分量和均为 $0$；则 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}$ 的分量和为 $0+0=0$，故 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\in W_1$；对任意 $k\\in R$，$k\\boldsymbol{\\alpha}$ 的分量和为 $k\\cdot0=0$，故 $k\\boldsymbol{\\alpha}\\in W_1$。所以 $W_1$ 是子空间。\n"
                "（从方程角度看：$W_1$ 是**齐次**线性方程 $x+y+z=0$ 的解集，与 §4.4 一致。）\n\n"
                "**(2) $W_2$ 不是子空间**：$\\boldsymbol{0}$ 的分量和为 $0\\neq1$，故 $\\boldsymbol{0}\\notin W_2$，而子空间必含零向量。（对应 §4.4：非齐次方程组的解集不是子空间。）\n\n"
                "**(3) $W_3$ 不是子空间**：取 $\\boldsymbol{\\alpha}=(1,0,0)^{\\mathsf T}$ 与 $\\boldsymbol{\\beta}=(0,1,0)^{\\mathsf T}$，二者都满足 $x\\cdot y=0$，故都属于 $W_3$；但\n"
                "$$\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}=(1,1,0)^{\\mathsf T},$$\n"
                "其分量乘积为 $1\\cdot1=1\\neq0$，故 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\notin W_3$，$W_3$ 对加法不封闭，所以不是子空间。\n\n"
                "**引申**：$W_3$ 的几何意义是平面 $x=0$ 与平面 $y=0$ 的**并集**（两个子空间之并一般不再是子空间）；一般地，由**非线性**（或非齐次一次）条件给出的集合通常不是子空间，判定时必须回到「加法、数乘封闭」这两条硬指标。",
    points=[{"text": "写出子空间判定定理（非空 + 对加法与数乘封闭）作为统一依据", "partial": 2},
            {"text": "判定 $W_1$ 是子空间：非空，且证明其对加法与数乘封闭", "partial": 2},
            {"text": "判定 $W_2$ 不是子空间：$W_2$ 不含零向量", "partial": 2},
            {"text": "判定 $W_3$ 不是子空间：举出反例 $(1,0,0)^{\\mathsf T}+(0,1,0)^{\\mathsf T}=(1,1,0)^{\\mathsf T}$，说明对加法不封闭", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间的判定定理；与 §4.4「齐次解集是子空间、非齐次解集不是子空间」相互印证。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：把「$xy=0$ 里含 $0$」当成子空间。只看**是否含零向量**不够，必须验证**对加法与数乘封闭**——$W_3$ 含零向量却对加法不封闭。",
    ext="引申：$W_3$ 是平面 $x=0$ 与平面 $y=0$ 的并集；两个子空间之并一般不再是子空间。",
    tags=["难点", "重点", "跨章"],
    verify=[{"desc": "W1 中向量 (1,2,-3) 的分量和为 0", "code": "sum(M([1,2,-3]))", "expected": "0"},
            {"desc": "数乘封闭：3(1,2,-3) 的分量和仍为 0", "code": "sum(M([1,2,-3])*3)", "expected": "0"},
            {"desc": "W2 中零向量的分量和为 0，不等于 1", "code": "sum(M([0,0,0]))", "expected": "0"},
            {"desc": "W3 反例：(1,0,0)+(0,1,0)", "code": "str(list(M([1,0,0]) + M([0,1,0])))", "expected": "[1, 1, 0]"},
            {"desc": "该向量的 x·y = 1 ≠ 0，故不在 W3 中", "code": "M([1,1,0])[0]*M([1,1,0])[1]", "expected": "1"}]))

Q = Q_
