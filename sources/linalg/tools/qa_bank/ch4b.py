# -*- coding: utf-8 -*-
"""第4章 向量组与线性方程组的解的结构 —— 真题扩写 60 题
（单选10 / 多选10 / 判断10 / 填空10 / 简答10 / 计算与分析10）
难度：基础28 中等20 困难12
知识点：4.1 向量组及其线性组合 / 4.2 向量组的线性相关性 / 4.3 向量组的秩
        4.4 线性方程组的解的结构 / 4.5 向量空间
题型取材：中科大《线性代数》历年考题（循环和组抽象题、线性无关的证明模板、
        同解判据模型、张成子空间的维数与基模型）、考研数学真题经典模型。
"""
from .common import Q, SINGLE, MULTI, JUDGE, BLANK, TERM, SHORT, CALC

Q_ = []

# ─────────────────────────────────────────────── 单选 10（基础4 中等4 困难2）
Q_.append(Q(SINGLE, "basic", "4.1",
    "两组向量 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\beta}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\beta}_2=(1,0,0)^{\\mathsf T}$，则向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 与 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2$",
    answer=["A"],
    options=["等价，即它们互相可以线性表示",
             "不等价，但它们的秩相等",
             "不等价，且它们的秩也不相等",
             "只有当两个向量组的向量个数相同时，它们才可能等价"],
    expl="**答案依据**：§4.1 向量组等价的定义——两组向量互相可以线性表示时称等价，等价于它们**张成同一个子空间**。\n"
          "第一组张成的子空间：$L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)=\\{(x,y,0)^{\\mathsf T}\\mid x,y\\in R\\}$；\n"
          "第二组：取 $\\dfrac{\\boldsymbol{\\beta}_1+\\boldsymbol{\\beta}_2}{2}=(1,0,0)^{\\mathsf T}$、$\\dfrac{\\boldsymbol{\\beta}_1-\\boldsymbol{\\beta}_2}{2}=(0,1,0)^{\\mathsf T}$，可见 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 都能由 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2$ 表示；反之 $\\boldsymbol{\\beta}_1=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$、$\\boldsymbol{\\beta}_2=\\boldsymbol{\\alpha}_1$ 也能由第一组表示。故两组**等价**。\n"
          "B 错：这里不止秩相等，两组本身就是等价的（秩都等于 2，而等价是更强的结论）。\n"
          "C 错：两组秩都等于 2，并非不等。\n"
          "D 错：等价的向量组个数可以不同，例如 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 与 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$ 等价，而个数是 2 与 3。",
    mis="⚠️易错点：把「秩相等」当成「等价」的判据。等价要求**互相**可以线性表示；秩相等只说明两组张成的子空间维数相同，位置未必相同。",
    tags=["重点", "易错"],
    verify=[{"desc": "第一组向量为列的矩阵的秩", "code": "M([[1,0],[0,1],[0,0]]).rank()", "expected": "2"},
            {"desc": "第二组向量为列的矩阵的秩", "code": "M([[1,1],[1,0],[0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(SINGLE, "basic", "4.2",
    "设 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}$ 是 $R^n$ 中的两个向量，则 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}$ 线性相关的充分必要条件是",
    answer=["D"],
    options=["$\\boldsymbol{\\alpha}=\\boldsymbol{\\beta}$",
             "$\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}=\\boldsymbol{0}$",
             "$\\boldsymbol{\\alpha}$ 与 $\\boldsymbol{\\beta}$ 的内积为零",
             "其中一个向量是另一个向量的倍数"],
    expl="**答案依据**：§4.2 线性相关性的定义——存在不全为零的 $k_1,k_2$ 使 $k_1\\boldsymbol{\\alpha}+k_2\\boldsymbol{\\beta}=\\boldsymbol{0}$。\n"
          "若 $\\boldsymbol{\\beta}=k\\boldsymbol{\\alpha}$（$k\\neq0$），则 $\\boldsymbol{\\alpha}-k\\boldsymbol{\\beta}=\\boldsymbol{0}$ 是一组非平凡系数关系，故线性相关；反之若 $k_1\\boldsymbol{\\alpha}+k_2\\boldsymbol{\\beta}=\\boldsymbol{0}$ 且系数不全为零，取其中非零的那个解出另一个向量，即知其中一个是另一个的倍数。故两个向量线性相关 $\\iff$ 成比例，选项 D 说的正是这一条件。\n"
          "A 错：相等的两个向量确实线性相关，但这只是比例关系中 $k=1$ 的特例，并非充分必要条件；反例 $\\boldsymbol{\\alpha}=(1,0)^{\\mathsf T},\\boldsymbol{\\beta}=(2,0)^{\\mathsf T}$ 线性相关却不相等。\n"
          "B 错：$\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}=\\boldsymbol{0}$ 只是「倍数 $k=-1$」这一种特例。\n"
          "C 错：内积为零表示两个向量**正交**，而正交的非零向量恰好线性无关（如 $(1,0)^{\\mathsf T}$ 与 $(0,1)^{\\mathsf T}$）。",
    mis="⚠️易错点：把「成比例」记成「相等」。线性相关 $\\iff$ 成比例（$\\boldsymbol{\\beta}=k\\boldsymbol{\\alpha}$，$k$ 为任意实数，含 $k=1$、$k=-1$ 等各种情形）。",
    tags=["重点", "易错"]))

Q_.append(Q(SINGLE, "basic", "4.3",
    "设 $A$ 是 $3$ 阶方阵且 $r(A)=2$，则 $A$ 的列向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$ 的秩是",
    answer=["B"],
    options=["$1$", "$2$", "$3$", "由 $A$ 的具体元素决定"],
    expl="**答案依据**：§4.3 的定理——向量组的秩等于以该向量组为列向量构成的矩阵的秩。这里以列向量构成的矩阵正是 $A$，故秩 $=r(A)=2$。\n"
          "A 错：秩不会小于 $r(A)=2$；\n"
          "C 错：三个列向量虽然个数是 3，但它们线性相关，秩为 2 而不是 3；\n"
          "D 错：秩只由 $r(A)$ 决定，题中 $r(A)=2$ 已把结果完全确定。",
    mis="⚠️易错点：把「向量个数」当成「秩」。列向量有 3 个而秩是 2——秩是其中线性无关向量的**最大个数**。",
    tags=["重点", "高频"],
    verify=[{"desc": "示例：列向量组作列的矩阵的秩", "code": "M([[1,0,1],[0,1,1],[1,1,2]]).rank()", "expected": "2"}]))

Q_.append(Q(SINGLE, "basic", "4.4",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)=n-1$，则齐次线性方程组 $A\\boldsymbol{x}=0$ 的基础解系所含向量的个数是",
    answer=["D"],
    options=["$2$", "$n-1$", "$m-1$", "$n-r(A)$"],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构——基础解系由 $n-r(A)$ 个线性无关的解向量构成。本题 $r(A)=n-1$，故基础解系含 $n-(n-1)=1$ 个向量。\n"
          "A 错：基础解系只含 1 个向量；\n"
          "B 错：$n-1$ 是系数矩阵的秩，它说明的是主元变量的个数，不是基础解系的大小；\n"
          "C 错：$m$ 是方程（行）的个数，与解向量的个数无关。",
    mis="⚠️易错点：把 $r(A)=n-1$ 里的 $n-1$ 当成基础解系的个数。基础解系的大小是**自由未知量个数** $n-r(A)$。",
    tags=["重点", "必背", "高频"],
    verify=[{"desc": "示例：n-r 的值（4 元 3 阶系数阵）", "code": "4 - M([[1,0,1],[0,1,1],[0,0,1]]).rank()", "expected": "1"}]))

Q_.append(Q(SINGLE, "medium", "4.1",
    "已知向量组 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,1)^{\\mathsf T}$，则向量 $\\boldsymbol{\\beta}=(2,3,5)^{\\mathsf T}$ 可由它们线性表示为",
    answer=["D"],
    options=["$\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$",
             "$3\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$",
             "$-\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$",
             "$-3\\boldsymbol{\\alpha}_1-2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$"],
    expl="**答案依据**：§4.1 线性表示——设 $\\boldsymbol{\\beta}=k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+k_3\\boldsymbol{\\alpha}_3$，按分量列出方程：\n"
          "$$k_1+k_3=2,\\qquad k_2+k_3=3,\\qquad k_3=5.$$\n"
          "由第三式得 $k_3=5$，回代第一式得 $k_1=2-5=-3$，回代第二式得 $k_2=3-5=-2$，故 $\\boldsymbol{\\beta}=-3\\boldsymbol{\\alpha}_1-2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$。\n"
          "（因 $\\begin{vmatrix}1&0&1\\\\0&1&1\\\\0&0&1\\end{vmatrix}=1\\neq0$，三个向量线性无关，故该表示式唯一。）\n"
          "A 错：$\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3=(6,7,5)^{\\mathsf T}\\neq\\boldsymbol{\\beta}$；\n"
          "B 错：$3\\boldsymbol{\\alpha}_1+2\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3=(8,7,5)^{\\mathsf T}\\neq\\boldsymbol{\\beta}$；\n"
          "C 错：$-\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3=(4,4,5)^{\\mathsf T}\\neq\\boldsymbol{\\beta}$。",
    mis="⚠️易错点：三个分量方程只解两个就作答。必须三个方程同时成立（本题第三式先定出 $k_3$，再回代），否则得到的组合不等于 $\\boldsymbol{\\beta}$。",
    tags=["计算", "高频"],
    verify=[{"desc": "唯一表示系数", "code": "list(M([[1,0,1],[0,1,1],[0,0,1]]).inv()*M([[2],[3],[5]]))", "expected": "[-3, -2, 5]"},
            {"desc": "表示式的验证结果（应等于 β）", "code": "str(list(M([[1,0,1],[0,1,1],[0,0,1]])*M([[-3],[-2],[5]])))", "expected": "[2, 3, 5]"}]))

Q_.append(Q(SINGLE, "medium", "4.2",
    "设 $A$ 是 $m\\times n$ 矩阵，对 $A$ 作一次初等行变换得到矩阵 $B$，则 $B$ 的列向量组与 $A$ 的列向量组",
    answer=["B"],
    options=["秩不同，因而线性相关性也不同",
             "线性相关性完全相同",
             "只有当 $A$ 是方阵时该结论才成立",
             "只有当 $A$ 可逆时该结论才成立"],
    expl="**答案依据**：初等行变换可逆，故 $B=EA$（$E$ 为可逆的初等矩阵）。设 $A$ 的列向量组线性相关，则存在不全为零的 $k_1,\\dots,k_n$ 使 $A\\boldsymbol{k}=\\boldsymbol{0}$，于是 $B\\boldsymbol{k}=EA\\boldsymbol{k}=E\\boldsymbol{0}=\\boldsymbol{0}$，即 $B$ 的列向量组也线性相关；反之由 $B\\boldsymbol{k}=\\boldsymbol{0}$ 与 $E$ 可逆得 $A\\boldsymbol{k}=E^{-1}B\\boldsymbol{k}=\\boldsymbol{0}$，故 $A$ 的列向量组也线性相关。两者线性相关性相同（这是 §4.3「秩不随初等行变换改变」的应用）。\n"
          "A 错：初等行变换不改变矩阵的秩，秩相同则线性相关性必然相同；\n"
          "C 错：上述论证对任意 $m\\times n$ 矩阵都成立，不要求 $A$ 是方阵；\n"
          "D 错：初等行变换后的矩阵未必可逆（例如把一行的倍数加到另一行使其变成零行），但结论仍然成立。",
    mis="⚠️易错点：以为「行变换会改变列向量组的线性相关性」。行变换保持**列**向量组的线性相关性；与行向量组对应的是**列**变换。",
    tags=["真题改编", "高频"],
    src="同济《线性代数》第六版 §4.2 向量组的线性相关性；题型改编自：中科大《线性代数》历年考题（行变换与列相关性模型）"))

Q_.append(Q(SINGLE, "medium", "4.3",
    "考虑向量组 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,k)^{\\mathsf T}$，则其秩等于 $3$ 的充分必要条件是",
    answer=["C"],
    options=["$k=0$", "$k=1$", "$k\\neq0$", "$k\\neq1$"],
    expl="**答案依据**：以三向量为列作矩阵\n$$A=\\begin{pmatrix}1&0&1\\\\0&1&1\\\\0&0&k\\end{pmatrix},$$\n"
          "由 §4.3，秩 $=r(A)$；又 $A$ 是上三角矩阵，$|A|=1\\cdot1\\cdot k=k$，故 $r(A)=3\\iff|A|\\neq0\\iff k\\neq0$。\n"
          "A 错：$k=0$ 时 $\\boldsymbol{\\alpha}_3=(1,1,0)^{\\mathsf T}=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，秩为 2；\n"
          "B 错：$k=1$ 时 $|A|=1\\neq0$，秩恰为 3，条件写反了；\n"
          "D 错：$k=1$ 时秩也是 3，所以「$k\\neq1$」并非充分必要条件。",
    mis="⚠️易错点：只验一个方向。含参讨论必须两头都证：既证 $k\\neq0$ 时秩为 3，也证 $k=0$ 时秩小于 3。",
    tags=["含参", "计算", "高频"],
    verify=[{"desc": "含参行列式", "code": "expand(M([[1,0,1],[0,1,1],[0,0,symbols('k')]]).det())", "expected": "k"},
            {"desc": "k=0 时三向量作列的矩阵的秩", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"}]))

Q_.append(Q(SINGLE, "medium", "4.4",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)=r<n$，非齐次线性方程组 $A\\boldsymbol{x}=b$ 有解，则它的解集",
    answer=["C"],
    options=["是 $R^n$ 的一个 $r$ 维线性子空间",
             "是 $R^n$ 的一个 $(n-r)$ 维线性子空间",
             "是零空间 $N(A)$ 的一个陪集，维数为 $n-r$",
             "是空集"],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构——通解为\n$$\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r},$$\n"
          "其中 $\\boldsymbol{x}_0$ 是任一特解，$\\boldsymbol{\\eta}_1,\\dots,\\boldsymbol{\\eta}_{n-r}$ 是 $A\\boldsymbol{x}=0$ 的基础解系。故解集是零空间 $N(A)$ 的一个**平移（陪集）**，维数为 $n-r$。\n"
          "A 错：解集不含零向量（若 $\\boldsymbol{0}$ 是解则 $b=A\\boldsymbol{0}=\\boldsymbol{0}$，与非齐次矛盾），因而它不是一个线性子空间；\n"
          "B 错：维数确实是 $n-r$，但「线性子空间」错在解集不含零向量，它是一个陪集；\n"
          "D 错：题设已说明方程组有解。",
    mis="⚠️易错点：把非齐次方程组的解集当成线性子空间。判据是**含不含零向量**：齐次解集是子空间，非齐次解集是陪集。",
    tags=["重点", "高频", "易错"]))

Q_.append(Q(SINGLE, "hard", "4.2",
    "设向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$ 的秩为 $4$，记 $\\boldsymbol{\\beta}_1=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，$\\boldsymbol{\\beta}_2=\\boldsymbol{\\alpha}_2+\\boldsymbol{\\alpha}_3$，$\\boldsymbol{\\beta}_3=\\boldsymbol{\\alpha}_3+\\boldsymbol{\\alpha}_4$，$\\boldsymbol{\\beta}_4=\\boldsymbol{\\alpha}_4+\\boldsymbol{\\alpha}_1$，则向量组 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3,\\boldsymbol{\\beta}_4$ 的秩是",
    answer=["A"],
    options=["$3$", "$4$", "$2$", "不大于 $2$"],
    expl="**答案依据**：\n"
          "第一步（秩 $\\le3$）：注意到\n$$\\boldsymbol{\\beta}_1-\\boldsymbol{\\beta}_2+\\boldsymbol{\\beta}_3-\\boldsymbol{\\beta}_4=(\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2)-(\\boldsymbol{\\alpha}_2+\\boldsymbol{\\alpha}_3)+(\\boldsymbol{\\alpha}_3+\\boldsymbol{\\alpha}_4)-(\\boldsymbol{\\alpha}_4+\\boldsymbol{\\alpha}_1)=\\boldsymbol{0},$$\n"
          "这是一组不全为零的系数关系，故四个 $\\boldsymbol{\\beta}$ 线性相关，秩 $\\le3$。\n"
          "第二步（秩 $\\ge3$）：$\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3$ 关于 $\\boldsymbol{\\alpha}$ 的系数矩阵为\n$$C=\\begin{pmatrix}1&1&0\\\\0&1&1\\\\0&0&1\\end{pmatrix},\\qquad |C|=1\\neq0,$$\n"
          "而 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_4$ 的秩为 4（即它们线性无关），故 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3$ 线性无关，秩 $\\ge3$。综上秩 $=3$。\n"
          "B 错：存在上面的非平凡关系，四个 $\\boldsymbol{\\beta}$ 不可能线性无关，秩到不了 4；\n"
          "C 错：$\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3$ 线性无关，秩至少为 3；\n"
          "D 错：同理，秩不小于 3。",
    mis="⚠️易错点：只找到一组非平凡关系就写「秩 $\\le3$」并收工。要得到等号必须**两头都证**：再证出秩 $\\ge3$。",
    tags=["真题改编", "难点", "计算"],
    src="同济《线性代数》第六版 §4.3 向量组的秩；题型改编自：中科大《线性代数》历年考题（循环和组抽象题）",
    verify=[{"desc": "系数矩阵的行列式（为 0，说明四个 β 相关）", "code": "M([[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]).det()", "expected": "0"},
            {"desc": "系数矩阵的秩（为 3，故秩恰为 3）", "code": "M([[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]).rank()", "expected": "3"}]))

Q_.append(Q(SINGLE, "hard", "4.5",
    "在 $R^4$ 中，设 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$ 是四个线性无关的向量，$W_1=L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)$，$W_2=L(\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4)$（$L(\\cdot)$ 表示由这些向量张成的子空间），则 $\\dim(W_1\\cap W_2)+\\dim(W_1+W_2)$ 等于",
    answer=["C"],
    options=["$2$", "$3$", "$4$", "$5$"],
    expl="**答案依据**：有限维向量子空间的维数公式\n$$\\dim(W_1+W_2)+\\dim(W_1\\cap W_2)=\\dim W_1+\\dim W_2.$$\n"
          "本题 $\\dim W_1=2$、$\\dim W_2=2$（两个二元向量组各自线性无关），故左端 $=2+2=4$。\n"
          "也可直接验证：若 $\\boldsymbol{v}\\in W_1\\cap W_2$，则 $\\boldsymbol{v}=a\\boldsymbol{\\alpha}_1+b\\boldsymbol{\\alpha}_2=c\\boldsymbol{\\alpha}_3+d\\boldsymbol{\\alpha}_4$，即 $a\\boldsymbol{\\alpha}_1+b\\boldsymbol{\\alpha}_2-c\\boldsymbol{\\alpha}_3-d\\boldsymbol{\\alpha}_4=\\boldsymbol{0}$；由四个 $\\boldsymbol{\\alpha}$ 线性无关得 $a=b=c=d=0$，故 $W_1\\cap W_2=\\{\\boldsymbol{0}\\}$，$\\dim(W_1\\cap W_2)=0$；又 $W_1+W_2$ 由四个线性无关向量张成，$\\dim(W_1+W_2)=4$。\n"
          "A 错：交空间是零空间，维数是 0 而不是 2；\n"
          "B 错：和空间为四维，合计不是 3；\n"
          "D 错：两个二维子空间的交与和的维数之和等于 4，不会超过 4。",
    mis="⚠️易错点：把 $\\dim(W_1+W_2)$ 当成 $\\dim W_1+\\dim W_2$（那要两空间不交才成立）。一般情形用维数公式，且和空间的维数**不超过**两者之和。",
    tags=["难点", "重点", "计算"],
    verify=[{"desc": "四个 α 作列的矩阵的秩（为 4，即线性无关）", "code": "M([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]).rank()", "expected": "4"}]))

# ─────────────────────────────────────────────── 多选 10（基础4 中等4 困难2）
Q_.append(Q(MULTI, "basic", "4.1",
    "设 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}$ 是 $R^n$ 中的向量，$k,l$ 是常数。下列等式中恒成立的有",
    answer=["A", "B", "C"],
    options=["$k\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}=\\boldsymbol{\\beta}+k\\boldsymbol{\\alpha}$",
             "$k(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})=k\\boldsymbol{\\alpha}+k\\boldsymbol{\\beta}$",
             "$(k+l)\\boldsymbol{\\alpha}=k\\boldsymbol{\\alpha}+l\\boldsymbol{\\alpha}$",
             "$k(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})=k\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}$"],
    expl="**答案依据**：§4.1 向量的线性组合运算——加法的交换律、数乘对加法的分配律、数乘对加法的结合律这三条恒成立。\n"
          "A：向量加法可以交换次序；\n"
          "B：数乘对加法可分配，括号内的两项都要乘上 $k$；\n"
          "C：先把系数合并，再按分配律展开：$(k+l)\\boldsymbol{\\alpha}=k\\boldsymbol{\\alpha}+l\\boldsymbol{\\alpha}$。\n"
          "D 错：右边漏掉了 $k\\boldsymbol{\\beta}$ 这一项，只有 $k=1$ 时才成立；一般的分配律是 $k(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})=k\\boldsymbol{\\alpha}+k\\boldsymbol{\\beta}$。",
    mis="⚠️易错点：把数乘的分配律记成 $k(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})=k\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}$。系数 $k$ 必须同时分配给括号内的**每一项**。",
    tags=["基础", "必背"]))

Q_.append(Q(MULTI, "basic", "4.2",
    "关于向量组的线性相关性，下列结论正确的有",
    answer=["A", "B", "C"],
    options=["含零向量的向量组必定线性相关",
             "向量个数多于它所在空间的维数时，该向量组必定线性相关",
             "线性无关向量组的任意部分组都线性无关",
             "线性相关向量组的任意部分组都线性相关"],
    expl="**答案依据**：§4.2、§4.3 的基本推论。\n"
          "A：设零向量是第 $j$ 个，取系数 $k_j=1$、其余系数取 0，即得不全为零的系数组合使线性组合为零向量；\n"
          "B：线性无关向量的个数不超过所在空间的维数（§4.3 中秩 $\\le n$），故 $s>n$ 时必相关；\n"
          "C：若某部分组相关，把它的系数关系中其余系数补零，就得到原组的一组不全为零的系数关系，与原组无关矛盾。\n"
          "D 错：整体相关只说明**整体**存在非平凡关系，部分组未必相关。反例：$\\boldsymbol{\\alpha}_1=(2,1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(1,0,1)^{\\mathsf T},\\boldsymbol{\\alpha}_3=(3,1,1)^{\\mathsf T}$，因 $\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$ 三者相关，而部分组 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2\\}$ 的二阶子式为 $-1\\neq0$，线性无关。",
    mis="⚠️易错点：把「相关 ⇒ 部分组相关」说成定理。正确方向是**无关 ⇒ 部分组无关**。",
    tags=["重点", "易错", "高频"],
    verify=[{"desc": "反例中三向量作列的矩阵的秩为 2（<3，故相关）", "code": "M([[2,1,3],[1,0,1],[0,1,1]]).rank()", "expected": "2"},
            {"desc": "反例中部分组两向量作列的矩阵的二阶子式（非零，故无关）", "code": "M([[2,1],[1,0]]).det()", "expected": "-1"}]))

Q_.append(Q(MULTI, "basic", "4.3",
    "关于向量组的秩，下列说法正确的有",
    answer=["A", "C", "D"],
    options=["向量组的秩等于以该向量组为列向量构成的矩阵的秩",
             "秩为 $r$ 的向量组中任意 $r$ 个向量都线性无关",
             "向量组的秩也等于以该向量组为行向量构成的矩阵的秩",
             "向量组中每一个向量都可以由该组的任取的一个极大线性无关组线性表示"],
    expl="**答案依据**：§4.3 向量组的秩与极大线性无关组。\n"
          "A：以向量组为列构成矩阵，该矩阵的秩就是向量组的秩；\n"
          "C：行向量构成的矩阵是列向量构成的矩阵的转置，而 $r(A)=r(A^{T})$，故两者的秩相同；\n"
          "D：极大线性无关组的定义保证原向量组的任一向量都能由它线性表示，并且对**任取**的一个极大无关组都成立。\n"
          "B 错：秩为 $r$ 只保证**存在**一组含 $r$ 个向量的极大线性无关组。反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(3,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_3=(0,1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_4=(0,0,1)^{\\mathsf T}$ 的秩为 3，但 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性相关。",
    mis="⚠️易错点：把「秩是极大无关组的大小」偷换成「任意 $r$ 个向量都无关」。**存在性 ≠ 任意性**。",
    tags=["重点", "易错"],
    verify=[{"desc": "反例中四个向量作列的矩阵的秩", "code": "M([[1,3,0,0],[0,0,1,0],[0,0,0,1]]).rank()", "expected": "3"}]))

Q_.append(Q(MULTI, "basic", "4.4",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)<n$，关于齐次线性方程组 $A\\boldsymbol{x}=0$，下列说法正确的有",
    answer=["B", "C", "D"],
    options=["它的解集是 $R^n$ 的一个仿射子集",
             "它的基础解系所含向量的个数为 $n-r(A)$",
             "它的通解是基础解系中各向量的任意线性组合",
             "它有非零解当且仅当 $r(A)<n$"],
    expl="**答案依据**：§4.4 齐次线性方程组解的结构。\n"
          "B：自由未知量有 $n-r(A)$ 个，故基础解系含 $n-r(A)$ 个线性无关的解向量；\n"
          "C：通解 $\\boldsymbol{x}=c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r}$，其中 $c_i$ 为任意实数；\n"
          "D：$r(A)<n$ 表示存在自由未知量，令自由未知量不全为零即得非零解；$r(A)=n$ 时系数阵可逆，只有零解。\n"
          "A 错：齐次方程组的解集含零向量且对加法与数乘封闭，它是 $R^n$ 的**线性子空间**，而仿射子集一般不含零向量。",
    mis="⚠️易错点：把齐次与非齐次解集搞混。齐次解集是**子空间**（含零向量），非齐次解集才是仿射子集（陪集）。",
    tags=["重点", "高频"]))

Q_.append(Q(MULTI, "medium", "4.4",
    "设线性方程组 $A\\boldsymbol{x}=b$ 与 $C\\boldsymbol{x}=d$ 的系数矩阵与增广矩阵分别为 $A,C,(A\\mid b),(C\\mid d)$，下列说法正确的有",
    answer=["A", "B", "D"],
    options=["若两个方程组同解，则必有 $r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$",
             "方程组 $A\\boldsymbol{x}=b$ 有解的充分必要条件是 $r(A)=r(A\\mid b)$",
             "非齐次方程组 $A\\boldsymbol{x}=b$ 的解集是 $R^n$ 的一个线性子空间",
             "若 $A\\boldsymbol{x}=b$ 有解，则它的解集是零空间 $N(A)$ 的一个陪集"],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构，配合秩判别定理。\n"
          "A：同解意味着两个方程组都相容，且解集相同从而解空间的维数相同，故 $r(A)=r(A\\mid b)=r(C)=r(C\\mid d)$（这是同解的**必要**条件，反之不成立）；\n"
          "B：§3.3 的秩判别定理——有解 $\\iff r(A)=r(A\\mid b)$；\n"
          "D：通解 $\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r}$，即解集 $=Z(A)+\\boldsymbol{x}_0$，是零空间 $N(A)$ 的平移——陪集。\n"
          "C 错：非齐次解集不含零向量（若 $\\boldsymbol{0}$ 是解则 $b=A\\boldsymbol{0}=\\boldsymbol{0}$，与非齐次矛盾），故它不是一个线性子空间。",
    mis="⚠️易错点：把「同解」当成只由 $r(A)=r(C)$、$r(A\\mid b)=r(C\\mid d)$ 就能判定。这两条只是必要条件，反例：$x_1=0$ 与 $x_2=0$ 的相关秩都等于 1，但解集不同。",
    tags=["真题改编", "高频", "易错"],
    src="同济《线性代数》第六版 §4.4 线性方程组的解的结构；题型改编自：中科大《线性代数》历年考题（同解判据模型）"))

Q_.append(Q(MULTI, "medium", "4.1",
    "设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 是 $R^n$ 中的两组向量（$L(\\cdot)$ 表示由这些向量张成的子空间）。下列说法正确的有",
    answer=["B", "C", "D"],
    options=["若两组向量等价，则必有 $s=t$",
             "若两组向量等价，则它们的秩相等",
             "若 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性表示，则 $L(\\boldsymbol{\\beta})\\subseteq L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)$",
             "若 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)=L(\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t)$，则这两组向量等价"],
    expl="**答案依据**：§4.1 向量组等价；§4.3 秩。\n"
          "B：等价 $\\Rightarrow$ 两组张成同一子空间 $\\Rightarrow$ 秩（维数）相等；\n"
          "C：由张成的定义，$\\boldsymbol{\\beta}=k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s$ 本身就说明 $\\boldsymbol{\\beta}$ 落在第一组张成的子空间里；\n"
          "D：等价 $\\iff$ 两组张成同一个子空间，故由「张成同一子空间」反推等价成立。\n"
          "A 错：等价的向量组个数可以不同。反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$ 与 $\\boldsymbol{\\beta}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\beta}_2=(0,1,0)^{\\mathsf T}$ 互相可以线性表示，两组等价，但前者 1 个向量、后者 2 个向量。",
    mis="⚠️易错点：把「等价」误解成「向量个数相同」。等价只看**张成的子空间**是否相同，与个数无关。",
    tags=["重点", "易错", "高频"]))

Q_.append(Q(MULTI, "medium", "4.2",
    "设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 是 $R^n$ 中的 $s$ 个向量。下列命题中，与「向量组线性相关」等价的命题有",
    answer=["A", "C", "D"],
    options=["存在不全为零的常数 $k_1,\\dots,k_s$，使 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$",
             "存在唯一的一组不全为零的常数 $k_1,\\dots,k_s$，使 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$",
             "齐次方程组 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$ 有非零解",
             "至少有一个向量 $\\boldsymbol{\\alpha}_i$ 可以由其余向量线性表示"],
    expl="**答案依据**：§4.2 线性相关性的定义与等价刻画。\n"
          "A：这就是定义本身；\n"
          "C：把 $k_1,\\dots,k_s$ 看作未知量，「有非零解」正是 A 的另一种写法；\n"
          "D：若 $\\boldsymbol{\\alpha}_i$ 可由其余向量表示，把等式移项即得一组不全为零的系数使线性组合为零向量；反之由一组不全为零的系数关系中某个非零系数解出对应的向量即可。\n"
          "B 错：线性相关时非平凡的系数关系有**无穷多组**（可整体乘以任意非零常数），并非唯一。",
    mis="⚠️易错点：以为「相关的系数关系是唯一的」。相关只要求**存在**一组不全为零的系数；唯一性是线性无关组的性质。",
    tags=["重点", "高频", "必背"]))

Q_.append(Q(MULTI, "medium", "4.3",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)=r$。下列说法正确的有",
    answer=["A", "B", "D"],
    options=["$r(A)\\le\\min\\{m,n\\}$",
             "当 $A$ 是 $n$ 阶方阵时，$r(A)=n$ 与 $A$ 可逆等价",
             "秩为 $r$ 的向量组中任意 $r$ 个向量都线性无关",
             "向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 的秩为 $r$，添加任意向量 $\\boldsymbol{\\beta}$ 后新向量组的秩为 $r$ 或 $r+1$"],
    expl="**答案依据**：§4.3 秩的性质，配合 §2.3 逆矩阵、§3.2 矩阵的秩。\n"
          "A：矩阵的秩不超过行数也不超过列数；\n"
          "B：$n$ 阶方阵可逆 $\\iff |A|\\neq0\\iff r(A)=n$；\n"
          "D：添加一个向量后张成的空间最多增加一个独立方向，故秩只可能保持 $r$ 或变为 $r+1$。\n"
          "C 错：秩为 $r$ 只保证**存在**一组含 $r$ 个向量的极大线性无关组。反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(3,0,0)^{\\mathsf T},\\boldsymbol{\\alpha}_3=(0,1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_4=(0,0,1)^{\\mathsf T}$ 的秩为 3，但 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性相关。",
    mis="⚠️易错点：以为「秩是 $r$ 就随便挑 $r$ 个都无关」。挑出的无关向量个数不超过秩即可，但必须**恰好 $r$ 个**才构成极大线性无关组。",
    tags=["高频", "重点"]))

Q_.append(Q(MULTI, "hard", "4.4",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)=r$。关于齐次线性方程组 $A\\boldsymbol{x}=0$，下列说法正确的有",
    answer=["A", "C", "D"],
    options=["它有非零解当且仅当 $r(A)<n$",
             "它的解空间的维数为 $m-r(A)$",
             "它的解集是 $R^n$ 的一个 $n-r(A)$ 维线性子空间",
             "若非齐次方程组 $A\\boldsymbol{x}=b$ 有解且 $r(A)=n$，则它的解是唯一的"],
    expl="**答案依据**：§4.4 齐次与非齐次线性方程组解的结构。\n"
          "A：$r(A)<n$ 表示存在自由未知量，令自由未知量不全为零即得非零解；$r(A)=n$ 时系数阵可逆，只有零解；\n"
          "C：解空间是 $R^n$ 的线性子空间，维数为自由未知量个数 $n-r(A)$；\n"
          "D：$r(A)=n$ 时 $A$ 可逆，$A\\boldsymbol{x}=b$ 至多有一个解，有解即唯一。\n"
          "B 错：解空间的维数是 $n-r(A)$，其中 $n$ 是未知量的个数；$m$ 是方程的个数，与解空间的维数无关。",
    mis="⚠️易错点：把 $n$（未知量个数）记成 $m$（方程个数）。维数公式是 $n-r(A)$，其中 $n$ 来自未知量个数。",
    tags=["重点", "难点", "高频"]))

Q_.append(Q(MULTI, "hard", "4.5",
    "设 $V$ 是数域 $K$ 上的向量空间，$W_1,W_2$ 是 $V$ 的两个子空间。下列说法正确的有",
    answer=["B", "C", "D"],
    options=["$W_1\\cup W_2$ 一定是 $V$ 的子空间",
             "$W_1\\cap W_2$ 一定是 $V$ 的子空间",
             "若 $W$ 是 $V$ 的有限维子空间且 $\\dim W=\\dim V$，则 $W=V$",
             "$V$ 的每个子空间都含零向量"],
    expl="**答案依据**：§4.5 向量空间与子空间的判定定理与维数。\n"
          "B：交集中的元素相加、相乘仍在交集中，且零向量必在其中，故 $W_1\\cap W_2$ 是子空间；\n"
          "C：$W\\subseteq V$ 且两者维数相同，在有限维空间中只能有 $W=V$；\n"
          "D：由封闭性取标量 $k=0$ 即得 $k\\boldsymbol{\\alpha}=\\boldsymbol{0}\\in W$。\n"
          "A 错：两个子空间的并一般不再是子空间（除非其中一个包含另一个）。反例：在 $R^2$ 中 $W_1=\\{(x,0)^{\\mathsf T}\\}$、$W_2=\\{(0,y)^{\\mathsf T}\\}$，则 $(1,0)^{\\mathsf T}+(0,1)^{\\mathsf T}=(1,1)^{\\mathsf T}$ 不在 $W_1\\cup W_2$ 中。",
    mis="⚠️易错点：以为「两个子空间的并还是子空间」。只有当其中一个包含另一个时，并才是子空间。",
    tags=["难点", "重点", "易错"]))

# ─────────────────────────────────────────────── 判断 10（基础5 中等3 困难2）
Q_.append(Q(JUDGE, "basic", "4.1",
    "若向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性无关，则向量 $\\boldsymbol{\\beta}$ 可由它们线性表示时，表示系数是唯一的。",
    answer=["A"],
    expl="**答案依据**：§4.1 线性表示与 §4.2 线性无关。若 $\\boldsymbol{\\beta}=k_1\\boldsymbol{\\alpha}_1+\\cdots+k_m\\boldsymbol{\\alpha}_m=l_1\\boldsymbol{\\alpha}_1+\\cdots+l_m\\boldsymbol{\\alpha}_m$，则 $(k_1-l_1)\\boldsymbol{\\alpha}_1+\\cdots+(k_m-l_m)\\boldsymbol{\\alpha}_m=\\boldsymbol{0}$；由无关性得 $k_i-l_i=0$，故 $k_i=l_i$，表示系数唯一。",
    mis="⚠️易错点：忘了「线性无关」这个前提。若向量组线性相关，同一向量有无穷多种表示方式。",
    tags=["重点", "必背"]))

Q_.append(Q(JUDGE, "basic", "4.2",
    "含有零向量的向量组一定线性无关。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。§4.2 的基本推论是：含零向量的向量组一定**线性相关**——设零向量是第 $j$ 个，取 $k_j=1$、其余系数取 0，即得一组不全为零的系数使线性组合为零向量。",
    mis="⚠️易错点：把「含零向量」与「线性无关」挂上关系。零向量是**相关**的触发条件。",
    tags=["重点", "易错"],
    verify=[{"desc": "含零列的矩阵秩为 1（小于列数 2，故相关）", "code": "M([[1,0],[0,0]]).rank()", "expected": "1"}]))

Q_.append(Q(JUDGE, "basic", "4.3",
    "向量组的秩就是它的极大线性无关组所含向量的个数。",
    answer=["A"],
    expl="**答案依据**：§4.3 的定义。极大线性无关组本身**不唯一**（可以换底），但它们所含向量的个数唯一，这个唯一的个数就是向量组的秩。",
    mis="⚠️易错点：以为「极大线性无关组是唯一的」。唯一的是它的**个数**（秩）。",
    tags=["基础", "必背"]))

Q_.append(Q(JUDGE, "basic", "4.4",
    "设 $A$ 为 $m\\times n$ 矩阵且 $r(A)=r<n$，则非齐次线性方程组 $A\\boldsymbol{x}=b$ 的通解中所含自由参数的个数等于 $n-r(A)$。",
    answer=["A"],
    expl="**答案依据**：§4.4——通解为 $\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r}$，其中的自由参数正是齐次方程组基础解系对应的 $n-r(A)$ 个参数。",
    mis="⚠️易错点：把 $r$ 或 $m$ 当成自由参数个数。自由参数个数 $=$ 自由未知量个数 $=$ $n-r(A)$。",
    tags=["基础", "重点", "高频"]))

Q_.append(Q(JUDGE, "basic", "4.5",
    "任意非空集合都是 $R^3$ 的子空间。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。§4.5 的判定定理要求集合非空**且**对加法与数乘都封闭。反例：$W=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=1\\}$ 非空，但零向量的分量和为 0，零向量不在 $W$ 中，故 $W$ 不是子空间。",
    mis="⚠️易错点：只看到「非空」就下结论。子空间还要**含零向量**并对两种运算封闭。",
    tags=["基础", "易错"]))

Q_.append(Q(JUDGE, "medium", "4.1",
    "若向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 等价，则必有 $s=t$。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。§4.1 中「等价」只要求两组向量**互相可以线性表示**（等价于张成同一个子空间），对向量个数没有要求。反例：$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$ 与 $\\boldsymbol{\\beta}_1=(1,0,0)^{\\mathsf T},\\boldsymbol{\\beta}_2=(0,1,0)^{\\mathsf T}$ 互相可以线性表示，两组等价，但前者 1 个向量、后者 2 个向量。",
    mis="⚠️易错点：把「等价」与「个数相同」混为一谈。等价只关乎**张成的子空间**是否相同。",
    tags=["重点", "易错"]))

Q_.append(Q(JUDGE, "medium", "4.2",
    "把向量组中的某个向量 $\\boldsymbol{\\beta}$ 替换为 $k\\boldsymbol{\\beta}$（$k\\neq0$），所得向量组与原向量组的线性相关性相同。",
    answer=["A"],
    expl="**答案依据**：§4.2。设原组为 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_{s-1},\\boldsymbol{\\beta}$，它线性相关 $\\iff$ 存在不全为零的 $c_1,\\dots,c_{s-1},c$ 使 $\\sum_{i=1}^{s-1}c_i\\boldsymbol{\\alpha}_i+c\\boldsymbol{\\beta}=\\boldsymbol{0}$；替换后的组线性相关 $\\iff$ 存在不全为零的 $d_1,\\dots,d_{s-1},e$ 使 $\\sum_{i=1}^{s-1}d_i\\boldsymbol{\\alpha}_i+e(k\\boldsymbol{\\beta})=\\boldsymbol{0}$。由于 $k\\neq0$，两组系数之间可互取（$e=c/k$ 或 $c=ek$），且非平凡性保持，故两个条件等价，线性相关性相同。",
    mis="⚠️易错点：以为「换了一个向量」就可能改变相关性。非零倍替换不改变线性相关性（与初等列变换的结论一致）。",
    tags=["高频", "重点"]))

Q_.append(Q(JUDGE, "medium", "4.4",
    "若线性方程组 $A\\boldsymbol{x}=b$ 有解，则它的任意两个解 $\\boldsymbol{x}_1,\\boldsymbol{x}_2$ 之和仍是它的解。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。$A(\\boldsymbol{x}_1+\\boldsymbol{x}_2)=A\\boldsymbol{x}_1+A\\boldsymbol{x}_2=b+b=2b$，而方程组要求等于 $b$；当 $b\\neq\\boldsymbol{0}$ 时 $2b\\neq b$，故和不是解。作为对照，两解之**差**满足 $A(\\boldsymbol{x}_1-\\boldsymbol{x}_2)=b-b=\\boldsymbol{0}$，是齐次方程组的解。",
    mis="⚠️易错点：把非齐次方程组当成齐次的。**作差**回到 $A\\boldsymbol{x}=0$，**作和**变成 $2b$。",
    tags=["重点", "易错", "高频"]))

Q_.append(Q(JUDGE, "hard", "4.5",
    "设 $W$ 是 $R^4$ 的一个三维子空间，$\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$ 是 $R^4$ 中的向量且都属于 $W$，则这四个向量线性相关。",
    answer=["A"],
    expl="**答案依据**：§4.5 维数与 §4.3——子空间 $W$ 的维数为 3，其中线性无关向量的最大个数等于 $\\dim W=3$（极大线性无关组所含的个数）。四个向量放在三维空间里必然线性相关。",
    mis="⚠️易错点：以为「都是非零向量且互不相同」就线性无关。个数超过所在空间的维数是相关的硬指标。",
    tags=["难点", "重点"]))

Q_.append(Q(JUDGE, "hard", "4.3",
    "若矩阵 $A$ 的列向量组线性相关，则 $A$ 的行向量组也线性相关。",
    answer=["B"],
    expl="**答案依据**：该命题**错误**。列向量组线性相关 $\\iff r(A)<n$（$n$ 是列数），行向量组线性相关 $\\iff r(A)<m$（$m$ 是行数），两个条件并不相同。反例：$A=\\begin{pmatrix}1&0&1\\\\0&1&1\\end{pmatrix}$，$r(A)=2$：三个列向量在 $R^2$ 中线性相关，而两个行向量 $(1,0,1)^{\\mathsf T},(0,1,1)^{\\mathsf T}$ 线性无关。",
    mis="⚠️易错点：以为「列相关就整矩阵到处都相关」。相关与否由 $r(A)$ 与**该方向的向量个数**比较决定：列看 $n$、行看 $m$。",
    tags=["难点", "易错"],
    verify=[{"desc": "反例矩阵的秩（为 2，等于行数，故行向量无关）", "code": "M([[1,0,1],[0,1,1]]).rank()", "expected": "2"}]))

# ─────────────────────────────────────────────── 填空 10（基础5 中等3 困难2）
Q_.append(Q(BLANK, "basic", "4.1",
    "设 $\\boldsymbol{\\alpha}=(1,-1,2,0)^{\\mathsf T}$，$\\boldsymbol{\\beta}=(0,3,-1,1)^{\\mathsf T}$，则 $\\boldsymbol{\\alpha}-2\\boldsymbol{\\beta}=$ ______。",
    answer=["(1,-7,4,-2)"],
    accept=["(1,-7,4,-2)", "(1, -7, 4, -2)", "1,-7,4,-2", "(1,-7,4,-2)^T", "(1,-7,4,-2)^{\\mathsf T}"],
    expl="**答案依据**：§4.1 线性组合是逐分量的加减：$2\\boldsymbol{\\beta}=(0,6,-2,2)^{\\mathsf T}$，于是\n$$\\boldsymbol{\\alpha}-2\\boldsymbol{\\beta}=(1,-1,2,0)^{\\mathsf T}-(0,6,-2,2)^{\\mathsf T}=(1,-7,4,-2)^{\\mathsf T}.$$",
    mis="⚠️易错点：第二个分量算成 $-1-(-6)$ 或把 $3\\times2$ 的符号搞反；建议先写出 $2\\boldsymbol{\\beta}$ 再逐分量相减。",
    tags=["基础", "计算"],
    verify=[{"desc": "α-2β 的四个分量", "code": "str(list(M([1,-1,2,0])-2*M([0,3,-1,1])))", "expected": "[1, -7, 4, -2]"}]))

Q_.append(Q(BLANK, "basic", "4.2",
    "当向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性无关时，方程组 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$ 只有 ______ 解。",
    answer=["零解"],
    accept=["零解", "0", "全零", "零解(全零)", "只有零解", "零"],
    expl="**答案依据**：§4.2——线性无关的定义就是「只有全零系数解」，即 $k_1=\\dots=k_s=0$，故该方程组只有零解。",
    mis="⚠️易错点：把「线性无关」与「无解」混为一谈。这里是**有解且唯一**，且这个解只能是零解。",
    tags=["基础", "重点", "必背"]))

Q_.append(Q(BLANK, "basic", "4.3",
    "以向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 为列向量构成的矩阵的秩，就是该向量组的 ______。",
    answer=["秩"],
    accept=["秩", "矩阵的秩", "矩阵秩", "rank"],
    expl="**答案依据**：§4.3 的定理——向量组的秩等于以该向量组为列向量构成的矩阵的秩；等价地，也等于以它为行向量构成的矩阵的秩。",
    mis="⚠️易错点：把答案写成「极大线性无关组的个数」。两者数值相同，但题目问的是与**矩阵的秩**的关系，填「秩」最贴切。",
    tags=["基础", "必背"]))

Q_.append(Q(BLANK, "basic", "4.4",
    "设 $\\boldsymbol{x}_1,\\boldsymbol{x}_2$ 都是线性方程组 $A\\boldsymbol{x}=b$ 的解，则 $\\boldsymbol{x}_1-\\boldsymbol{x}_2$ 一定满足方程 $A\\boldsymbol{x}=$ ______。",
    answer=["0"],
    accept=["0", "零", "零向量", "0(零向量)", "0（零向量）"],
    expl="**答案依据**：§4.4——$A(\\boldsymbol{x}_1-\\boldsymbol{x}_2)=A\\boldsymbol{x}_1-A\\boldsymbol{x}_2=b-b=\\boldsymbol{0}$，故 $\\boldsymbol{x}_1-\\boldsymbol{x}_2$ 是齐次方程组 $A\\boldsymbol{x}=0$ 的解。",
    mis="⚠️易错点：作差时把 $b-b$ 写成 $2b$；或者把 $\\boldsymbol{x}_1-\\boldsymbol{x}_2$ 拿去代入原方程组（它并不满足原方程组）。",
    tags=["基础", "重点", "高频"]))

Q_.append(Q(BLANK, "basic", "4.5",
    "在 $R^3$ 中，集合 $W=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=0\\}$ 是 $R^3$ 的子空间，因为它是某个 ______ 线性方程组的解集。",
    answer=["齐次"],
    accept=["齐次", "齐次的", "齐次线性", "齐次线性方程", "齐次线性方程组"],
    expl="**答案依据**：§4.4 与 §4.5——齐次线性方程组的解集含零向量且对加法与数乘封闭，故是 $R^3$ 的子空间；而非齐次方程组（如 $x+y+z=1$）的解集不含零向量，不是子空间。",
    mis="⚠️易错点：只看到「是一个方程组的解集」就说成子空间。关键区别在**齐次与非齐次**。",
    tags=["基础", "重点", "跨章"]))

Q_.append(Q(BLANK, "medium", "4.1",
    "若两组向量 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 等价，则它们的秩 ______（填「相等」或「不等」）。",
    answer=["相等"],
    accept=["相等", "一样", "相同", "相等。"],
    expl="**答案依据**：§4.1 与 §4.3——等价的两组向量张成同一个子空间，故维数（秩）相同。注意这只是必要条件：秩相等的两组未必等价。",
    mis="⚠️易错点：把「秩相等」反过来当成「等价」的充分条件。秩相等只说明维数相同，位置可能不同。",
    tags=["重点", "易错", "高频"]))

Q_.append(Q(BLANK, "medium", "4.2",
    "向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性相关的充要条件是：存在一组 ______ 的常数 $k_1,\\dots,k_s$，使 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$。",
    answer=["不全为零"],
    accept=["不全为零", "不全为0", "不全为零的", "不全为0的", "不全为零(不全为0)"],
    expl="**答案依据**：§4.2 的定义——「存在**不全为零**的常数 $k_1,\\dots,k_s$」。若允许全零系数，任何向量组都会「线性相关」，定义就失去意义。",
    mis="⚠️易错点：漏掉「不全为零」四个字。这四个字是线性相关定义的核心限定。",
    tags=["重点", "必背", "易错"]))

Q_.append(Q(BLANK, "medium", "4.4",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)<n$，非齐次方程组 $A\\boldsymbol{x}=b$ 有解，则它的解集是零空间 $N(A)$ 的一个 ______。",
    answer=["陪集"],
    accept=["陪集", "一个陪集", "陪集(平移)", "平移", "陪集（平移）"],
    expl="**答案依据**：§4.4——通解 $\\boldsymbol{x}=\\boldsymbol{x}_0+\\sum c_i\\boldsymbol{\\eta}_i$，即解集 $=Z(A)+\\boldsymbol{x}_0$，是零空间的一个**平移**，抽象代数中称为**陪集**。",
    mis="⚠️易错点：写成「子空间」。非齐次解集不含零向量，它只能是一个陪集（平移）。",
    tags=["重点", "易错", "跨章"]))

Q_.append(Q(BLANK, "hard", "4.3",
    "设 $A$ 是 $m\\times n$ 矩阵且 $r(A)=r$。方程组 $A\\boldsymbol{x}=0$ 的解空间的维数与 $A$ 的列空间的维数之和等于 ______。",
    answer=["n"],
    accept=["n", "未知量个数", "n(未知量个数)", "n（未知量个数）"],
    expl="**答案依据**：§4.4 与 §4.3——解空间维数为 $n-r(A)$，列空间维数即 $r(A)$，两者相加 $=n$（$n$ 是未知量的个数）。这就是「秩－零化度定理」。",
    mis="⚠️易错点：把 $n$ 写成 $m$ 或 $n+r$。$m$ 是方程个数，与维数公式无关。",
    tags=["难点", "重点", "高频"],
    verify=[{"desc": "示例：解空间维数 + 列空间维数（4 元 3 阶系数阵）", "code": "len(M([[1,0,1,0],[0,1,1,0],[0,0,1,1]]).nullspace()) + M([[1,0,1,0],[0,1,1,0],[0,0,1,1]]).rank()", "expected": "4"}]))

Q_.append(Q(BLANK, "hard", "4.5",
    "在 $R^4$ 中取四个线性无关的向量 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4$，记 $W_1=L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)$，$W_2=L(\\boldsymbol{\\alpha}_3,\\boldsymbol{\\alpha}_4)$，则 $\\dim(W_1\\cap W_2)=$ ______。",
    answer=["0"],
    accept=["0", "零", "0维", "零维", "0（零）"],
    expl="**答案依据**：若 $\\boldsymbol{v}\\in W_1\\cap W_2$，则 $\\boldsymbol{v}=a\\boldsymbol{\\alpha}_1+b\\boldsymbol{\\alpha}_2=c\\boldsymbol{\\alpha}_3+d\\boldsymbol{\\alpha}_4$，即 $a\\boldsymbol{\\alpha}_1+b\\boldsymbol{\\alpha}_2-c\\boldsymbol{\\alpha}_3-d\\boldsymbol{\\alpha}_4=\\boldsymbol{0}$。四个 $\\boldsymbol{\\alpha}$ 线性无关，故 $a=b=c=d=0$，即 $W_1\\cap W_2=\\{\\boldsymbol{0}\\}$，维数为 $0$。",
    mis="⚠️易错点：以为两个二维子空间的交一定是「一条直线」。交空间的维数由两组向量**合起来**是否线性无关决定。",
    tags=["难点", "重点"],
    verify=[{"desc": "四个 α 作列的矩阵的秩（为 4，即线性无关）", "code": "M([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]).rank()", "expected": "4"}]))

# ─────────────────────────────────────────────── 简答与名词解释 10（基础5 中等3 困难2）
Q_.append(Q(SHORT, "basic", "4.1",
    "说明「向量的线性组合」「线性表示」与「向量组的等价」这三个概念之间的关系，并写出向量组等价的两个方向上的要求。",
    answer_text="**① 线性组合与线性表示（§4.1）**：给定向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 与常数 $k_1,\\dots,k_m$，形如 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_m\\boldsymbol{\\alpha}_m$ 的向量称为这组向量的一个**线性组合**；若这个线性组合恰好等于某个给定向量 $\\boldsymbol{\\beta}$，就称 $\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ **线性表示**。\n\n"
                "**② 与张成空间的关系**：记 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m)=\\{k_1\\boldsymbol{\\alpha}_1+\\cdots+k_m\\boldsymbol{\\alpha}_m\\mid k_i\\in R\\}$，它是这些向量张成的子空间。于是「$\\boldsymbol{\\beta}$ 可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示」与「$\\boldsymbol{\\beta}\\in L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m)$」说的是同一件事。\n\n"
                "**③ 向量组等价（§4.1）**：设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 是两组向量。若 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 中每一个向量都可由 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性表示，**并且** $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 中每一个向量都可由 $\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t$ 线性表示，则称这两个向量组**等价**。\n\n"
                "**④ 三者的关系**：等价 $\\iff$ 两组向量张成同一个子空间，即 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)=L(\\boldsymbol{\\beta}_1,\\dots,\\boldsymbol{\\beta}_t)$；等价 $\\Rightarrow$ 两组的秩相等（§4.3），而秩相等只说明两个子空间的维数相同、位置可能不同，反之未必成立。",
    points=[{"text": "写出线性组合与线性表示的定义，并指出「可线性表示」等价于「落在张成子空间内」", "partial": 2},
            {"text": "写出向量组等价的两个方向上的要求，并说明等价等价于两组张成同一子空间", "partial": 2},
            {"text": "说明等价与秩相等的关系（等价推出秩相等，秩相等未必等价）", "partial": 2}],
    expl="**答案依据**：§4.1 向量组及其线性组合（线性组合、线性表示、向量组等价）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：把等价只写成「一个方向可以表示」——等价要求**两个方向**都成立，这是它与「秩相等」的本质区别。",
    tags=["重点", "必背"]))

Q_.append(Q(SHORT, "basic", "4.2",
    "证明：设向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性无关，则它的任意部分组（例如 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_3$）也线性无关。",
    answer_text="**证明**：设部分组为 $\\boldsymbol{\\alpha}_{i_1},\\dots,\\boldsymbol{\\alpha}_{i_t}$（$t\\le s$）。反设它线性相关，则由 §4.2 的定义，存在不全为零的数 $k_1,\\dots,k_t$，使\n$$k_1\\boldsymbol{\\alpha}_{i_1}+k_2\\boldsymbol{\\alpha}_{i_2}+\\cdots+k_t\\boldsymbol{\\alpha}_{i_t}=\\boldsymbol{0}.$$\n"
                "把这组系数补到原来的 $s$ 个位置上：令 $k_{i_j}=k_j$（$j=1,\\dots,t$），其余系数取 $0$，则得到\n$$k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0},$$\n"
                "且这组系数不全为零（$k_1,\\dots,k_t$ 中至少有一个非零）。这与 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性无关矛盾。故部分组线性无关。$\\blacksquare$\n\n"
                "**要点**：结论的方向是「无关 $\\Rightarrow$ 部分组无关」；反方向的「相关 $\\Rightarrow$ 部分组相关」并不成立（§4.2 中有反例）。",
    points=[{"text": "设出部分组并反设它线性相关，写出不全为零的系数关系", "partial": 2},
            {"text": "把系数补零扩充成原向量组的一组不全为零的系数关系", "partial": 2},
            {"text": "由原组线性无关导出矛盾，并指出结论的方向性", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的定义与基本推论。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性。",
    mis="⚠️易错点：证完后把结论方向说反。「无关 $\\Rightarrow$ 部分组无关」成立，「相关 $\\Rightarrow$ 部分组相关」不成立。",
    tags=["证明", "重点", "高频"]))

Q_.append(Q(SHORT, "basic", "4.3",
    "写出向量组的秩与极大线性无关组的定义，并说明如何用初等行变换求出一个向量组的秩和一个极大线性无关组。",
    answer_text="**① 极大线性无关组（§4.3）**：设 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 是 $R^n$ 中的 $s$ 个向量。若其中一部分 $\\boldsymbol{\\alpha}_{i_1},\\dots,\\boldsymbol{\\alpha}_{i_r}$ **线性无关**，而该向量组中**任何** $r+1$ 个向量都线性相关，则称 $\\boldsymbol{\\alpha}_{i_1},\\dots,\\boldsymbol{\\alpha}_{i_r}$ 是该向量组的一个**极大线性无关组**。\n\n"
                "**② 秩的定义**：向量组的秩 $=$ 其极大线性无关组所含向量的个数，记 $r(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)$。极大线性无关组**不唯一**（可以换底），但**个数唯一**，都等于秩。\n\n"
                "**③ 与矩阵的秩的关系（§4.3）**：向量组的秩 $=$ 以该向量组为列向量构成的矩阵的秩（也等于以它为行向量构成的矩阵的秩）。\n\n"
                "**④ 求法**：以这些向量为列作矩阵 $A$，用初等行变换把 $A$ 化为行阶梯形 $B$（§3.1）。$B$ 的非零行个数就是 $r(A)$，即向量组的秩；而 $B$ 中**有主元**（该列首个非零元素所在的那一列）的那些列，与 $A$ 中对应的列向量构成原向量组的一个极大线性无关组。\n\n"
                "**要点**：取列时必须回到**原矩阵** $A$ 去取对应的列向量，并且只取**有主元**的列；任取前 $r$ 列不一定线性无关。",
    points=[{"text": "写出极大线性无关组的定义（本身线性无关且任何 r+1 个向量都相关）", "partial": 2},
            {"text": "写出秩的定义及它与矩阵秩相等的定理", "partial": 2},
            {"text": "说明用初等行变换求秩与极大无关组的步骤，并强调取有主元的列", "partial": 2}],
    expl="**答案依据**：§4.3 向量组的秩与极大线性无关组；求法配合 §3.1 初等变换。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：行变换后随手取前几列。必须取**有主元**的列，并回到**原矩阵**取对应的列向量。",
    tags=["重点", "方法", "必背"]))

Q_.append(Q(SHORT, "basic", "4.4",
    "说明线性方程组 $A\\boldsymbol{x}=b$ 的解的个数如何由 $r(A)$ 与 $r(A\\mid b)$ 决定，并说明有无穷多解时通解中自由参数的个数。",
    answer_text="**① 三种情形（§4.4，配合 §3.3 的秩判别定理）**：\n"
                "- 若 $r(A)=r(A\\mid b)=n$（$A$ 为 $n$ 阶方阵且可逆）：方程组有**唯一解**；\n"
                "- 若 $r(A)=r(A\\mid b)<n$：方程组有**无穷多解**；\n"
                "- 若 $r(A)<r(A\\mid b)$：方程组**无解**。\n\n"
                "**② 无穷多解时的通解**：此时相容，先求出一个特解 $\\boldsymbol{x}_0$（把常数项换成 0 解齐次方程组，或把增广矩阵化为阶梯形后令自由未知量取 0），再求齐次方程组 $A\\boldsymbol{x}=0$ 的基础解系 $\\boldsymbol{\\eta}_1,\\dots,\\boldsymbol{\\eta}_{n-r}$，则通解为\n$$\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r(A)}\\boldsymbol{\\eta}_{n-r(A)},\\qquad c_i\\in R.$$\n"
                "自由参数（自由未知量）个数为 $n-r(A)$。\n\n"
                "**③ 三种情形的来源**：把增广矩阵化为阶梯形后只会出现三种形态——系数行全为主元（唯一解）、出现零行且对应常数为 0（有无穷多解）、出现 $0=c\\,(c\\neq0)$（无解）。它们本质上是 $r(A)$ 与 $r(A\\mid b)$ 大小关系的直接反映。",
    points=[{"text": "写出三种情形（唯一解、无穷多解、无解）及其与 r(A)、r(A|b) 的大小关系", "partial": 2},
            {"text": "说明无穷多解时如何求特解与基础解系，并写出通解的结构", "partial": 2},
            {"text": "指出自由参数的个数为 n-r(A)，并解释三种情形的来源", "partial": 2}],
    expl="**答案依据**：§4.4 线性方程组的解的结构（通解＝特解＋齐次通解）；判别用 §3.3 的秩判别定理。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：把 $r(A)<r(A\\mid b)$ 与其它情形记混。无解时是增广矩阵的秩**大于**系数矩阵的秩，差值就是矛盾的来源。",
    tags=["重点", "高频", "必背"]))

Q_.append(Q(SHORT, "basic", "4.5",
    "说明如何求向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 张成的子空间 $L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)$ 的一组基与维数，并说明该子空间为什么是 $R^n$ 的子空间。",
    answer_text="**① 为什么是子空间（§4.5）**：$L(\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s)=\\{k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s\\}$。取 $k_1=\\dots=k_s=0$ 得零向量在其中；对任意 $\\boldsymbol{u}=k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s$ 与 $\\boldsymbol{v}=l_1\\boldsymbol{\\alpha}_1+\\cdots+l_s\\boldsymbol{\\alpha}_s$，有\n$$\\boldsymbol{u}+\\boldsymbol{v}=(k_1+l_1)\\boldsymbol{\\alpha}_1+\\cdots+(k_s+l_s)\\boldsymbol{\\alpha}_s,\\qquad c\\boldsymbol{u}=(ck_1)\\boldsymbol{\\alpha}_1+\\cdots+(ck_s)\\boldsymbol{\\alpha}_s,$$\n"
                "二者仍在 $L$ 中，故 $L$ 对加法与数乘封闭，又非空且含零向量，由 §4.5 的判定定理知 $L$ 是 $R^n$ 的子空间。\n\n"
                "**② 求基与维数（§4.3、§4.5）**：以 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 为列作矩阵 $A$，用初等行变换化为行阶梯形：非零行的个数即 $r(A)$，也就是 $\\dim L$；$A$ 中与阶梯形**有主元**的列相对应的那些列向量构成 $L$ 的一组**基**。\n\n"
                "**③ 基与维数的性质**：基不唯一（可以换底），但个数唯一；$\\dim L=r(A)\\le n$。若向量组本身线性无关，则它自身就是 $L$ 的一组基，此时 $\\dim L=s$。",
    points=[{"text": "说明 L 的定义并验证它对加法与数乘封闭、含零向量，故是子空间", "partial": 2},
            {"text": "说明用初等行变换求秩与有主元的列，从而得到 L 的一组基", "partial": 2},
            {"text": "指出基不唯一但维数唯一，且 dim L = r(A) ≤ n", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间；§4.3 向量组的秩与极大线性无关组。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：把「张成空间」与「极大线性无关组」混为一谈。$L$ 由**全部**向量张成，它的基只能从这些向量中挑选。",
    tags=["重点", "真题改编"],
    src="同济《线性代数》第六版 §4.5 向量空间；题型改编自：中科大《线性代数》历年考题（张成子空间的维数与基模型）"))

Q_.append(Q(SHORT, "medium", "4.1",
    "说明向量 $\\boldsymbol{\\beta}$ 由向量组 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ 线性表示时，表示系数的个数与向量组线性相关性之间的关系，并举例说明。",
    answer_text="**① 两种情形（§4.1、§4.2）**：\n"
                "- 若 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_m$ **线性无关**，则 $\\boldsymbol{\\beta}$ 可表示时表示系数**唯一**：若 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_m\\boldsymbol{\\alpha}_m=l_1\\boldsymbol{\\alpha}_1+\\cdots+l_m\\boldsymbol{\\alpha}_m$，则 $(k_i-l_i)$ 是一组不全为零就违反无关性，故 $k_i=l_i$。\n"
                "- 若该向量组**线性相关**，则表示系数**不唯一**：可表示时有无穷多种表示（相关关系给出无穷多组非平凡系数，加到原表示上即可）。\n\n"
                "**② 例子**：取 $\\boldsymbol{\\alpha}_1=(1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(2,0)^{\\mathsf T}$（线性相关），则 $\\boldsymbol{\\beta}=(1,0)^{\\mathsf T}$ 有两种表示：$\\boldsymbol{\\beta}=1\\boldsymbol{\\alpha}_1+0\\boldsymbol{\\alpha}_2=0\\boldsymbol{\\alpha}_1+\\dfrac12\\boldsymbol{\\alpha}_2$。\n"
                "若改取 $\\boldsymbol{\\alpha}_1=(1,0)^{\\mathsf T},\\boldsymbol{\\alpha}_2=(0,1)^{\\mathsf T}$（线性无关），则 $\\boldsymbol{\\beta}=(3,-1)^{\\mathsf T}$ 的表示唯一：$\\boldsymbol{\\beta}=3\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2$。\n\n"
                "**③ 几何解释**：表示式的个数取决于「系数空间」中解的个数——无关时 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_m\\boldsymbol{\\alpha}_m=\\boldsymbol{0}$ 只有零解（解空间是零空间），相关时该方程组有无穷多解。这与 §4.4 中「基础解系含 $n-r(A)$ 个向量 ⇒ 自由参数有 $n-r(A)$ 个」是同一件事。",
    points=[{"text": "说明向量组线性无关时表示系数唯一，并给出证明思路", "partial": 2},
            {"text": "说明向量组线性相关时表示系数不唯一，并举出具体的两组向量与两种表示", "partial": 2},
            {"text": "从解空间（自由参数）的角度解释两种情形的差别", "partial": 2}],
    expl="**答案依据**：§4.1 线性表示；§4.2 线性相关性；与 §4.4 齐次方程组解的结构相互印证。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：以为「表示式唯一」是线性组合本身的性质。它依赖于向量组**线性无关**这个前提。",
    tags=["高频", "易错"]))

Q_.append(Q(SHORT, "medium", "4.2",
    "给出判定一组向量线性相关或线性无关的两种常用方法，并说明每种方法的依据、适用场合以及各自的易错点。",
    answer_text="**方法一：定义法（解系数方程组，§4.2）**：写出方程组 $k_1\\boldsymbol{\\alpha}_1+\\cdots+k_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$，考察它是否有非零解。存在一组不全为零的 $k_i$ 则线性相关；只有零解则线性无关。\n"
                "**依据**：线性相关性的定义本身。**适用**：向量个数少（2～3 个）且元素具体时最直接。**易错点**：算出「有解」就下结论——必须确认解**不全为零**；全零解不说明任何问题。\n\n"
                "**方法二：矩阵法（算秩或行列式，§4.2＋§4.3）**：以这些向量为列作矩阵 $A$。向量组线性无关 $\\iff r(A)=s$（$s$ 是向量个数），线性相关 $\\iff r(A)<s$。当向量个数等于维数（$s=n$，矩阵为方阵）时还可以直接用行列式：$|A|\\neq0$ 则无关，$|A|=0$ 则相关。\n"
                "**依据**：秩是极大线性无关组的大小（§4.3），而 $r(A)=s$ 当且仅当 $A$ 的列向量线性无关。**适用**：向量个数较多时用行变换求秩更省力。**易错点**：把 $r(A)<s$ 中的 $s$ 写成向量所在空间的维数 $n$；或把行变换后「有主元的列个数」与「秩」混为一谈（两者数值相同，但意义不同）。\n\n"
                "**补充方法：极大无关组法**——先求出一个极大线性无关组，再看其余向量是否落在它张成的空间内（落在里面则整个向量组相关）。\n\n"
                "**含参讨论提示**：必须用**充分必要条件**的写法，两头都验证；只举出一个使向量组相关的参数值就收工，是最常见的失分点。",
    points=[{"text": "写出定义法（解系数方程组）的步骤、依据与易错点", "partial": 2},
            {"text": "写出矩阵法（以向量为列作矩阵，看秩或行列式）的步骤、依据与易错点", "partial": 2},
            {"text": "说明两种方法各自的适用场合，并补充含参讨论必须两头验证", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的定义与判定；§4.3 秩；§1.5 行列式与秩的关系。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性。",
    mis="⚠️易错点：把 $r(A)<s$ 中的 $s$ 写成向量所在空间的维数 $n$。$s$ 是**向量个数**，$n$ 是**维数**。",
    tags=["方法", "高频", "必背"]))

Q_.append(Q(SHORT, "medium", "4.4",
    "说明含参线性方程组解的讨论方法：如何按参数取值把方程组分情况讨论，每种情形下解的个数与通解的写法如何确定？",
    answer_text="**① 总思路**：把参数记作 $k$，写出系数矩阵 $A(k)$ 与增广矩阵 $(A(k)\\mid b)$，按 $|A(k)|$ 是否为零把 $k$ 的取值区间分开，然后对每个区间分别计算 $r(A(k))$ 与 $r(A(k)\\mid b)$，用 §4.4 的三种情形判定解的个数。\n\n"
                "**② 讨论步骤**：\n"
                "1. **$|A(k)|\\neq0$ 的情形**（即 $k\\neq k_0$）：$A(k)$ 可逆，方程组至多一个解；再检验相容性，相容时解唯一（此时 $r(A)=n$）。\n"
                "2. **$k=k_0$ 的情形**：此时 $|A(k)|=0$，必须回到增广矩阵比较 $r(A(k))$ 与 $r(A(k)\\mid b)$。二者相等则有无穷多解；$r(A(k)\\mid b)>r(A(k))$ 则无解。\n"
                "3. **写通解**：无穷多解时先求特解 $\\boldsymbol{x}_0$，再求齐次方程组 $A(k_0)\\boldsymbol{x}=0$ 的基础解系 $\\boldsymbol{\\eta}_1,\\dots,\\boldsymbol{\\eta}_{n-r}$，写\n$$\\boldsymbol{x}=\\boldsymbol{x}_0+c_1\\boldsymbol{\\eta}_1+\\cdots+c_{n-r}\\boldsymbol{\\eta}_{n-r},$$"
                "自由参数个数为 $n-r$。\n\n"
                "**③ 典型例子**：$\\begin{cases}x_1+x_2+x_3=1\\\\2x_1+2x_2+kx_3=3\\end{cases}$。第二式减第一式的 2 倍得 $(k-2)x_3=1$：$k\\neq2$ 时 $x_3=\\dfrac1{k-2}$，$x_1+x_2=1-\\dfrac1{k-2}$，有无穷多解（一个自由参数）；$k=2$ 时方程变成 $0=1$，无解。\n\n"
                "**易错点**：只求出 $|A(k)|=0$ 的 $k$ 就不管 $k\\neq k_0$ 的情形；或在 $k=k_0$ 处只算 $|A|$ 就下结论——必须回到**增广矩阵**比较两个秩。",
    points=[{"text": "写出总思路：先看含参行列式把参数区间分开，再对每个区间用秩判别", "partial": 2},
            {"text": "说明 k=k0 处必须比较 r(A) 与 r(A|b) 来区分无解与无穷多解", "partial": 2},
            {"text": "写出无穷多解时通解的构造（特解 + 基础解系），并给出典型例子的计算", "partial": 2}],
    expl="**答案依据**：§4.4 线性方程组的解的结构 + §3.3 秩判别定理。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：只用 $|A(k)|$ 判别就收工。$|A(k)|=0$ 只说明秩小于 $n$，有解还是无解要看 $r(A\\mid b)$。",
    tags=["含参", "高频", "方法"]))

Q_.append(Q(SHORT, "hard", "4.2",
    "证明：设 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$ 线性无关，记 $\\boldsymbol{\\beta}_1=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2+\\boldsymbol{\\alpha}_3$，$\\boldsymbol{\\beta}_2=\\boldsymbol{\\alpha}_1+3\\boldsymbol{\\alpha}_2+5\\boldsymbol{\\alpha}_3$，$\\boldsymbol{\\beta}_3=\\boldsymbol{\\alpha}_1+9\\boldsymbol{\\alpha}_2+25\\boldsymbol{\\alpha}_3$，则 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3$ 线性无关。",
    answer_text="**证明（系数行列式法）**：设\n$$k_1\\boldsymbol{\\beta}_1+k_2\\boldsymbol{\\beta}_2+k_3\\boldsymbol{\\beta}_3=\\boldsymbol{0}.$$\n"
                "把三个 $\\boldsymbol{\\beta}$ 按定义代入，按 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$ 归并同类项：\n$$(k_1+k_2+k_3)\\boldsymbol{\\alpha}_1+(k_1+3k_2+9k_3)\\boldsymbol{\\alpha}_2+(k_1+5k_2+25k_3)\\boldsymbol{\\alpha}_3=\\boldsymbol{0}.$$\n"
                "由于 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2,\\boldsymbol{\\alpha}_3$ 线性无关，三个系数必须全为零，即\n$$\\begin{cases}k_1+k_2+k_3=0\\\\k_1+3k_2+9k_3=0\\\\k_1+5k_2+25k_3=0.\\end{cases}$$\n"
                "该齐次方程组的系数行列式为\n$$C=\\begin{pmatrix}1&1&1\\\\1&3&5\\\\1&9&25\\end{pmatrix},\\qquad |C|=1\\cdot(3\\cdot25-5\\cdot9)-1\\cdot(1\\cdot25-5\\cdot1)+1\\cdot(1\\cdot9-3\\cdot1)=30-20+6=16\\neq0.$$\n"
                "由克拉默法则（或 §4.3 的秩结论）该方程组只有零解 $k_1=k_2=k_3=0$。故 $\\boldsymbol{\\beta}_1,\\boldsymbol{\\beta}_2,\\boldsymbol{\\beta}_3$ 线性无关。$\\blacksquare$\n\n"
                "**说明**：这个系数行列式是**范德蒙德行列式**：形如 $\\begin{pmatrix}1&1&1\\\\1&x_2&x_2^{2}\\\\1&x_3&x_3^{2}\\end{pmatrix}$（此处 $x_2=3,x_3=5$），其值为 $(x_2-1)(x_3-1)(x_3-x_2)=2\\cdot4\\cdot2=16$，与直接展开一致。\n\n"
                "**关键思想**：**线性组合的线性组合仍是线性组合**，所以原向量组线性无关时，新向量组线性无关 $\\iff$ 系数矩阵可逆（行列式非零）。",
    points=[{"text": "设出线性组合为零的方程并按 α 归并同类项，得到关于 k 的齐次方程组", "partial": 2},
            {"text": "写出系数矩阵并算出其行列式为 16≠0，由克拉默法则推出 k1=k2=k3=0", "partial": 2},
            {"text": "得出 β 组线性无关的结论，并指出该行列式是范德蒙德行列式与「线性组合的线性组合」这一关键思想", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的判定（以向量为列的矩阵秩等于向量个数）+ §1.5 行列式按行展开 + §2.4 克拉默法则。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性；题型改编自：中科大《线性代数》历年考题（线性无关的证明模板）。",
    mis="⚠️易错点：归并同类项时把系数写错（例如把 $\\boldsymbol{\\beta}_2$ 的 $\\boldsymbol{\\alpha}_2$ 系数写成 5）。务必逐项对照三个 $\\boldsymbol{\\beta}$ 的定义。",
    tags=["真题改编", "证明", "难点", "高频"],
    src="同济《线性代数》第六版 §4.2 向量组的线性相关性；题型改编自：中科大《线性代数》历年考题（线性无关的证明模板）",
    verify=[{"desc": "系数行列式的值（非零，故 β 组无关）", "code": "M([[1,1,1],[1,3,5],[1,9,25]]).det()", "expected": "16"}]))

Q_.append(Q(SHORT, "hard", "4.5",
    "证明：设 $V$ 是数域 $K$ 上的向量空间，$W$ 是 $V$ 的非空子集，则 $W$ 是 $V$ 的子空间的充分必要条件是对向量的加法与数乘封闭；并说明这一判据为什么不能只用「含零向量」来代替。",
    answer_text="**① 必要性**：设 $W$ 是 $V$ 的子空间。由 §4.5，$W$ 本身是 $K$ 上的向量空间，故对任意 $\\boldsymbol{\\alpha},\\boldsymbol{\\beta}\\in W$ 与任意 $k,l\\in K$ 都有 $k\\boldsymbol{\\alpha}+l\\boldsymbol{\\beta}\\in W$；特别地取 $k=1,l=0$ 与 $k=0,l=1$ 得 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\in W$，取 $k=l=0$ 得 $\\boldsymbol{0}\\in W$。故封闭性必要。\n\n"
                "**② 充分性**：设 $W\\neq\\varnothing$ 且对加法、数乘封闭。任取 $\\boldsymbol{\\alpha}\\in W$，由数乘封闭（标量取 0）得 $\\boldsymbol{0}=0\\boldsymbol{\\alpha}\\in W$；再由数乘封闭（标量取 $-1$）得 $-\\boldsymbol{\\alpha}\\in W$。于是 $W$ 中每个向量都有加法单位元与加法逆元，且运算封闭，因此 $W$ 构成 $K$ 上的向量空间，即 $V$ 的子空间。$\\blacksquare$\n\n"
                "**③ 为什么「含零向量」不足以代替封闭性**：含零向量只是封闭性的一个推论，而非它的全部。反例：在 $R^3$ 中取 $W=\\{\\boldsymbol{0},(1,0,0)^{\\mathsf T}\\}$，它非空且含零向量，但 $(1,0,0)^{\\mathsf T}+(1,0,0)^{\\mathsf T}=(2,0,0)^{\\mathsf T}\\notin W$，对加法不封闭，故不是子空间。另一个反例是 $W=\\{(x,y,z)^{\\mathsf T}\\mid x+y+z=1\\}$，它不含零向量。\n\n"
                "**④ 补充（有限维）**：在有限维向量空间中，若 $W\\subseteq V$ 且 $\\dim W=\\dim V$，则 $W=V$——因为 $W$ 的基也是 $V$ 中的一组线性无关向量，其个数等于 $V$ 的维数，故它必为 $V$ 的基。",
    points=[{"text": "证明必要性：由 W 是向量空间推出对加法与数乘封闭，并推出零向量、负向量在 W 中", "partial": 2},
            {"text": "证明充分性：由封闭性推出零向量与加法逆元在 W 中，从而 W 是向量空间", "partial": 2},
            {"text": "举出「非空且含零向量但对加法不封闭」的反例说明该判据不能被削弱，并补充有限维空间中维数相同则空间相等的说明", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间的定义及判定定理；§4.3 极大线性无关组与维数。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：把「含零向量」当成充分条件。零向量只是封闭性的推论之一，判定必须回到**加法与数乘封闭**两条硬指标。",
    tags=["难点", "证明", "重点"]))

# ─────────────────────────────────────────────── 计算与分析 10（基础5 中等3 困难2）
Q_.append(Q(CALC, "basic", "4.1",
    "设 $\\boldsymbol{\\alpha}_1=(1,2,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,0,1)^{\\mathsf T}$，求向量 $\\boldsymbol{\\beta}=(2,3,3)^{\\mathsf T}$ 由它们线性表示的表示式，并说明该表示式是否唯一。",
    answer_text="**第一步（设出待定系数）**：设 $\\boldsymbol{\\beta}=k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2+k_3\\boldsymbol{\\alpha}_3$，按分量列出方程（§4.1）：\n$$\\begin{cases}k_1+k_3=2\\\\2k_1+k_2=3\\\\k_2+k_3=3.\\end{cases}$$\n"
                "**第二步（解方程组）**：由第一式 $k_3=2-k_1$，由第三式 $k_2=3-k_3=1+k_1$，代入第二式得 $2k_1+1+k_1=3$，即 $3k_1=2$，$k_1=\\dfrac23$；于是 $k_2=1+\\dfrac23=\\dfrac53$，$k_3=2-\\dfrac23=\\dfrac43$。\n\n"
                "**第三步（表示式）**：\n$$\\boxed{\\boldsymbol{\\beta}=\\dfrac23\\boldsymbol{\\alpha}_1+\\dfrac53\\boldsymbol{\\alpha}_2+\\dfrac43\\boldsymbol{\\alpha}_3}.$$\n"
                "**检验**：$\\dfrac23(1,2,0)^{\\mathsf T}+\\dfrac53(0,1,1)^{\\mathsf T}+\\dfrac43(1,0,1)^{\\mathsf T}=(\\dfrac23+\\dfrac43,\\dfrac43+\\dfrac53,\\dfrac53+\\dfrac43)^{\\mathsf T}=(2,3,3)^{\\mathsf T}$ ✓\n\n"
                "**第四步（唯一性）**：以三个向量为列作矩阵\n$$A=\\begin{pmatrix}1&0&1\\\\2&1&0\\\\0&1&1\\end{pmatrix},\\qquad |A|=1\\cdot(1\\cdot1-0\\cdot1)+1\\cdot(2\\cdot1-1\\cdot0)=1+2=3\\neq0,$$\n"
                "故 $A$ 可逆、三个向量线性无关，表示式**唯一**。",
    points=[{"text": "设出待定系数并正确列出三个分量方程", "partial": 2},
            {"text": "解出 k1=2/3、k2=5/3、k3=4/3", "partial": 2},
            {"text": "写出表示式并回代检验", "partial": 2},
            {"text": "用行列式非零说明表示式唯一", "partial": 2}],
    expl="**答案依据**：§4.1 线性表示（列分量方程并解线性方程组）；唯一性由 §4.2 线性无关保证，判定用 §1.5 行列式。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：三个分量方程只解两个就作答。必须三个方程同时成立（本题先由第一、三式定出 $k_3$、$k_2$ 再代入第二式）。",
    tags=["计算", "基础", "高频"],
    verify=[{"desc": "唯一表示系数", "code": "list(M([[1,0,1],[2,1,0],[0,1,1]]).inv()*M([[2],[3],[3]]))", "expected": "[2/3, 5/3, 4/3]"},
            {"desc": "系数矩阵的行列式（非零，故表示唯一）", "code": "M([[1,0,1],[2,1,0],[0,1,1]]).det()", "expected": "3"}]))

Q_.append(Q(CALC, "basic", "4.2",
    "设 $k$ 为常数，$\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(1,1,k)^{\\mathsf T}$。讨论这三个向量线性相关、线性无关的条件；在线性相关时求出一组不全为零的系数。",
    answer_text="**第一步（写成矩阵）**：以三个向量为列作矩阵\n$$A=\\begin{pmatrix}1&0&1\\\\0&1&1\\\\0&0&k\\end{pmatrix}.$$\n"
                "**第二步（算行列式）**：$A$ 是上三角矩阵，$|A|=1\\cdot1\\cdot k=k$。\n\n"
                "**第三步（讨论）**：由 §4.2 与 §4.3，三向量线性无关 $\\iff r(A)=3\\iff|A|\\neq0$，线性相关 $\\iff|A|=0$。因此\n"
                "- $k\\neq0$ 时，$|A|=k\\neq0$，三向量**线性无关**；\n"
                "- $k=0$ 时，$|A|=0$，三向量**线性相关**。\n\n"
                "**第四步（求相关时的系数）**：$k=0$ 时 $\\boldsymbol{\\alpha}_3=(1,1,0)^{\\mathsf T}=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2$，故\n$$1\\cdot\\boldsymbol{\\alpha}_1+1\\cdot\\boldsymbol{\\alpha}_2-1\\cdot\\boldsymbol{\\alpha}_3=\\boldsymbol{0},$$\n"
                "即一组不全为零的系数为 $(k_1,k_2,k_3)=(1,1,-1)$。\n\n"
                "**第五步（验证）**：$(1,0,0)^{\\mathsf T}+(0,1,0)^{\\mathsf T}-(1,1,0)^{\\mathsf T}=(0,0,0)^{\\mathsf T}$ ✓",
    points=[{"text": "写出以三向量为列的矩阵并算出含参行列式 |A|=k", "partial": 2},
            {"text": "用 |A|≠0 无关、|A|=0 相关给出两种情形的结论", "partial": 2},
            {"text": "在 k=0 时写出关系式并给出一组不全为零的系数", "partial": 2},
            {"text": "回代验证并写出最终结论", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的判定（以向量为列的矩阵秩小于向量个数）+ §1.5 行列式按行展开。\n"
          "**考点出处**：同济《线性代数》第六版 §4.2 向量组的线性相关性。",
    mis="⚠️易错点：把「$k=0$ 时相关」只写成一句话就收工——题目还要求给出那组「不全为零」的系数，必须写出来并回代验证。",
    tags=["计算", "含参", "基础", "高频"],
    verify=[{"desc": "含参行列式", "code": "expand(M([[1,0,1],[0,1,1],[0,0,symbols('k')]]).det())", "expected": "k"},
            {"desc": "k=0 时三向量作列的矩阵的秩", "code": "M([[1,0,1],[0,1,1],[0,0,0]]).rank()", "expected": "2"},
            {"desc": "k≠0（取 k=1）时三向量作列的矩阵的秩", "code": "M([[1,0,1],[0,1,1],[0,0,1]]).rank()", "expected": "3"}]))

Q_.append(Q(CALC, "basic", "4.3",
    "求向量组 $\\boldsymbol{\\alpha}_1=(2,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(1,0,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_3=(3,1,1)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_4=(1,1,-1)^{\\mathsf T}$ 的秩，求出一个极大线性无关组，并把其余向量用它线性表示。",
    answer_text="**第一步（作矩阵）**：以四个向量为列作矩阵\n$$A=\\begin{pmatrix}2&1&3&1\\\\1&0&1&1\\\\0&1&1&-1\\end{pmatrix}.$$\n"
                "**第二步（行变换）**：交换第 1、2 行，再作 $R_2\\leftarrow R_2-2R_1$、$R_3\\leftarrow R_3-R_2$：\n$$A\\longrightarrow\\begin{pmatrix}1&0&1&1\\\\2&1&3&1\\\\0&1&1&-1\\end{pmatrix}\\xrightarrow{\\;R_2\\leftarrow R_2-2R_1\\;}\\begin{pmatrix}1&0&1&1\\\\0&1&1&-1\\\\0&1&1&-1\\end{pmatrix}\\xrightarrow{\\;R_3\\leftarrow R_3-R_2\\;}\\begin{pmatrix}1&0&1&1\\\\0&1&1&-1\\\\0&0&0&0\\end{pmatrix}.$$\n"
                "非零行有 2 行，故 $r(A)=2$，向量组的秩为 $\\boxed{2}$。\n\n"
                "**第三步（取有主元的列）**：阶梯形中第 1、2 列有主元，故取 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$。验证它们线性无关：\n$$\\begin{vmatrix}2&1\\\\1&0\\end{vmatrix}=2\\cdot0-1\\cdot1=-1\\neq0.$$\n"
                "**第四步（用极大无关组表示其余向量）**：\n$$\\boldsymbol{\\alpha}_3=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2=(2,1,0)^{\\mathsf T}+(1,0,1)^{\\mathsf T}=(3,1,1)^{\\mathsf T},$$\n$$\\boldsymbol{\\alpha}_4=\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2=(2,1,0)^{\\mathsf T}-(1,0,1)^{\\mathsf T}=(1,1,-1)^{\\mathsf T}.$$\n"
                "**答案**：秩为 $2$，极大线性无关组可取 $\\{\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2\\}$，其余两个向量由它表示如上。",
    points=[{"text": "写出以四向量为列的矩阵并作初等行变换得到阶梯形", "partial": 2},
            {"text": "由非零行数读出秩 r=2", "partial": 2},
            {"text": "指出极大线性无关组为 {α1,α2} 并用二阶子式验证其线性无关", "partial": 2},
            {"text": "把 α3、α4 用该组表示：α3=α1+α2，α4=α1-α2", "partial": 2}],
    expl="**答案依据**：§4.3 向量组的秩 $=$ 矩阵的秩（§3.2）；极大线性无关组由初等行变换后有主元的列给出（§3.1）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：算出秩后不把其余向量表示出来，或把表示式的系数写错。极大线性无关组之外的每个向量都必须能由它表示。",
    tags=["计算", "基础", "高频"],
    verify=[{"desc": "四向量作列的矩阵的秩", "code": "M([[2,1,3,1],[1,0,1,1],[0,1,1,-1]]).rank()", "expected": "2"},
            {"desc": "α1,α2 作列的矩阵的二阶子式（非零，故线性无关）", "code": "M([[2,1],[1,0]]).det()", "expected": "-1"},
            {"desc": "α3=α1+α2 的验证结果", "code": "str(M([2,1,0])+M([1,0,1]))", "expected": "Matrix([[3], [1], [1]])"}]))

Q_.append(Q(CALC, "basic", "4.4",
    "讨论参数 $a$ 的取值，使方程组 $\\begin{cases}x_1+x_2+x_3=1\\\\2x_1+2x_2+a x_3=3\\end{cases}$ 分别有唯一解、无解或无穷多解，并在有解时写出通解。",
    answer_text="**第一步（消元）**：用第二式减去第一式的 2 倍：\n$$(2x_1+2x_2+a x_3)-(2x_1+2x_2+2x_3)=3-2\\quad\\Longrightarrow\\quad (a-2)x_3=1.$$\n"
                "这一步把含参问题化为一元一次方程，$a=2$ 与 $a\\neq2$ 是分界点。\n\n"
                "**第二步（$a\\neq2$）**：$(a-2)x_3=1$ 给出 $x_3=\\dfrac{1}{a-2}$；代回第一式得 $x_1+x_2=1-\\dfrac{1}{a-2}$。此时系数矩阵\n$$A=\\begin{pmatrix}1&1&1\\\\2&2&a\\end{pmatrix}$$\n"
                "的两行不成比例，故 $r(A)=2$；增广矩阵 $\\begin{pmatrix}1&1&1&1\\\\2&2&a&3\\end{pmatrix}$ 的秩也是 2，方程组相容。又 $r(A)=2<n=3$，有 $n-r=1$ 个自由未知量，故有**无穷多解**。\n\n"
                "**通解**：令 $x_2=t$，则 $x_1=1-\\dfrac{1}{a-2}-t$，$x_3=\\dfrac{1}{a-2}$，即\n$$\\boldsymbol{x}=\\begin{pmatrix}1-\\dfrac{1}{a-2}\\\\0\\\\\\dfrac{1}{a-2}\\end{pmatrix}+t\\begin{pmatrix}-1\\\\1\\\\0\\end{pmatrix},\\qquad t\\in R.$$\n\n"
                "**第三步（$a=2$）**：上式变成 $0\\cdot x_3=1$，矛盾。此时 $A=\\begin{pmatrix}1&1&1\\\\2&2&2\\end{pmatrix}$ 的两行成比例，$r(A)=1$，而增广矩阵 $\\begin{pmatrix}1&1&1&1\\\\2&2&2&3\\end{pmatrix}$ 的秩为 2，$r(A\\mid b)=2>1=r(A)$，故方程组**无解**。\n\n"
                "**结论**：$a\\neq2$ 时有无穷多解（一个自由参数），$a=2$ 时无解；任何 $a$ 都没有唯一解（$r(A)\\le2<3$，$A$ 始终不可逆）。",
    points=[{"text": "消元得到 (a-2)x3=1，指出 a=2 与 a≠2 是分界", "partial": 2},
            {"text": "a≠2 时求出 x3 与 x1+x2 的关系，并用两个秩说明相容", "partial": 2},
            {"text": "写出 a≠2 时的通解（特解 + 基础解系形式）", "partial": 2},
            {"text": "a=2 时用 r(A)=1<r(A|b)=2 说明无解，并给出总结论", "partial": 2}],
    expl="**答案依据**：§4.4 非齐次线性方程组解的结构（三种情形与通解）+ §3.3 秩判别定理。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：把 $a\\neq2$ 的情形判成「唯一解」。两个方程、三个未知量，自由未知量有 $n-r=1$ 个，故是**无穷多解**；唯一解要求 $r(A)=n$。",
    tags=["计算", "含参", "基础", "高频"],
    verify=[{"desc": "a=3 时系数矩阵的秩", "code": "M([[1,1,1],[2,2,3]]).rank()", "expected": "2"},
            {"desc": "a=3 时增广矩阵的秩（与 r(A) 相等，故相容）", "code": "M([[1,1,1,1],[2,2,3,3]]).rank()", "expected": "2"},
            {"desc": "a=2 时系数矩阵的秩", "code": "M([[1,1,1],[2,2,2]]).rank()", "expected": "1"},
            {"desc": "a=2 时增广矩阵的秩（大于 r(A)，故无解）", "code": "M([[1,1,1,1],[2,2,2,3]]).rank()", "expected": "2"}]))

Q_.append(Q(CALC, "basic", "4.5",
    "取 $\\boldsymbol{\\alpha}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,1)^{\\mathsf T}$。求向量组 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 张成的子空间 $L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)$ 的一组基与维数，并说明 $L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)$ 是 $R^3$ 的子空间。",
    answer_text="**第一步（判断无关性）**：以两个向量为列作矩阵\n$$A=\\begin{pmatrix}1&0\\\\1&1\\\\0&1\\end{pmatrix},\\qquad |A|=\\begin{vmatrix}1&0\\\\1&1\\end{vmatrix}=1\\neq0,$$\n"
                "故 $\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2$ 线性无关，它们自身就是 $L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)$ 的一组基。\n\n"
                "**第二步（维数）**：基中向量的个数即维数，故\n$$\\dim L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)=2,$$\n"
                "也等于 $r(A)=2$（§4.3）。该子空间还可以写成\n$$L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)=\\{(x,y,z)^{\\mathsf T}\\mid z=y-x\\},$$\n"
                "即三维空间中一个经过原点的平面。\n\n"
                "**第三步（说明是子空间）**：$L(\\boldsymbol{\\alpha}_1,\\boldsymbol{\\alpha}_2)=\\{k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2\\mid k_1,k_2\\in R\\}$。取 $k_1=k_2=0$ 得零向量在其中；设 $\\boldsymbol{u}=k_1\\boldsymbol{\\alpha}_1+k_2\\boldsymbol{\\alpha}_2$、$\\boldsymbol{v}=l_1\\boldsymbol{\\alpha}_1+l_2\\boldsymbol{\\alpha}_2$，则\n$$\\boldsymbol{u}+\\boldsymbol{v}=(k_1+l_1)\\boldsymbol{\\alpha}_1+(k_2+l_2)\\boldsymbol{\\alpha}_2,\\qquad c\\boldsymbol{u}=(ck_1)\\boldsymbol{\\alpha}_1+(ck_2)\\boldsymbol{\\alpha}_2,$$\n"
                "仍属于 $L$，故 $L$ 对加法与数乘封闭；又 $L$ 非空且含零向量，由 §4.5 的判定定理知 $L$ 是 $R^3$ 的子空间。",
    points=[{"text": "写出矩阵并算出二阶子式非零，得两向量线性无关", "partial": 2},
            {"text": "指出 α1、α2 自身即为 L 的一组基，维数为 2", "partial": 2},
            {"text": "写出 L 的线性组合定义并验证其对加法与数乘封闭", "partial": 2},
            {"text": "用判定定理得出 L 是 R^3 的子空间的结论", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间的判定定理；§4.3 向量组的秩与极大线性无关组。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：把「张成的子空间」当成「这些向量本身」。只有当向量组线性无关时，它自身才是一组基。",
    tags=["计算", "基础", "真题改编"],
    src="同济《线性代数》第六版 §4.5 向量空间；题型改编自：中科大《线性代数》历年考题（张成子空间的维数与基模型）",
    verify=[{"desc": "两向量作列的矩阵的秩（为 2）", "code": "M([[1,0],[1,1],[0,1]]).rank()", "expected": "2"},
            {"desc": "二阶子式（非零，故两向量无关）", "code": "M([[1,0],[1,1]]).det()", "expected": "1"}]))

Q_.append(Q(CALC, "medium", "4.1",
    "设向量组 $\\boldsymbol{\\alpha}_1=(1,0,0)^{\\mathsf T}$，$\\boldsymbol{\\alpha}_2=(0,1,0)^{\\mathsf T}$ 与向量组 $\\boldsymbol{\\beta}_1=(1,1,0)^{\\mathsf T}$，$\\boldsymbol{\\beta}_2=(1,-1,0)^{\\mathsf T}$。判断这两组向量是否等价，并写出两个方向的线性表示式。",
    answer_text="**第一步（写出两个方向的表示式）**：\n"
                "方向一（$\\boldsymbol{\\beta}$ 组由 $\\boldsymbol{\\alpha}$ 组表示）：\n$$\\boldsymbol{\\beta}_1=\\boldsymbol{\\alpha}_1+\\boldsymbol{\\alpha}_2,\\qquad \\boldsymbol{\\beta}_2=\\boldsymbol{\\alpha}_1-\\boldsymbol{\\alpha}_2.$$\n"
                "方向二（$\\boldsymbol{\\alpha}$ 组由 $\\boldsymbol{\\beta}$ 组表示）：\n$$\\boldsymbol{\\alpha}_1=\\dfrac{1}{2}(\\boldsymbol{\\beta}_1+\\boldsymbol{\\beta}_2),\\qquad \\boldsymbol{\\alpha}_2=\\dfrac{1}{2}(\\boldsymbol{\\beta}_1-\\boldsymbol{\\beta}_2).$$\n"
                "**第二步（结论）**：两个方向的表示都成立，按 §4.1 的定义，两组向量**等价**。\n\n"
                "**第三步（几何说明）**：两组向量都张成同一个平面 $L=\\{(x,y,0)^{\\mathsf T}\\mid x,y\\in R\\}$，等价正是「张成同一子空间」的另一种说法。两组的秩都等于 2（$\\begin{vmatrix}1&1\\\\1&-1\\end{vmatrix}=-2\\neq0$，$\\begin{vmatrix}1&0\\\\0&1\\end{vmatrix}=1\\neq0$）。注意：**秩相等只是等价的必要条件**，这里能断定等价，是因为两个方向的表示式都能给出。",
    points=[{"text": "写出 β 组由 α 组表示的两个表示式", "partial": 2},
            {"text": "写出 α 组由 β 组表示的两个表示式（用 1/2 的组合）", "partial": 2},
            {"text": "依据 §4.1 的定义得出两组等价的结论", "partial": 2},
            {"text": "用张成同一子空间与秩相等作几何说明，指出秩相等只是必要条件", "partial": 2}],
    expl="**答案依据**：§4.1 向量组等价（互相可以线性表示）；§4.3 秩与张成空间。\n"
          "**考点出处**：同济《线性代数》第六版 §4.1 向量组及其线性组合。",
    mis="⚠️易错点：只验证一个方向就宣布等价。等价要求**两个方向**都能线性表示。",
    tags=["计算", "高频", "易错"],
    verify=[{"desc": "α1=（β1+β2）/2 的验证结果", "code": "str((M([1,1,0])+M([1,-1,0]))/2)", "expected": "Matrix([[1], [0], [0]])"},
            {"desc": "α2=（β1-β2）/2 的验证结果", "code": "str((M([1,1,0])-M([1,-1,0]))/2)", "expected": "Matrix([[0], [1], [0]])"}]))

Q_.append(Q(CALC, "medium", "4.4",
    "求线性方程组 $\\begin{cases}x_1+x_2=3\\\\x_1-x_2=1\\end{cases}$ 与 $\\begin{cases}x_1+2x_2=4\\\\2x_1-x_2=3\\end{cases}$ 的公共解，并说明公共解与「联立求解」的关系。",
    answer_text="**第一步（联立成一个方程组）**：公共解必须同时满足两个方程组的四个方程，即\n$$\\begin{cases}x_1+x_2=3\\\\x_1-x_2=1\\\\x_1+2x_2=4\\\\2x_1-x_2=3.\\end{cases}$$\n"
                "**第二步（消元）**：用第一式减第二式得 $2x_2=2$，即 $x_2=1$；代回第二式得 $x_1=2$。再代回第三、四式检验：$2+2\\times1=4$ ✓，$2\\times2-1=3$ ✓。\n\n"
                "**第三步（结论）**：公共解为\n$$\\boxed{(x_1,x_2)=(2,1)}.$$\n"
                "（也可以把四个方程的系数与常数项放在一起，用一次初等行变换化阶梯形：$\\begin{pmatrix}1&1&3\\\\1&-1&1\\\\1&2&4\\\\2&-1&3\\end{pmatrix}$ 化简后读出 $x_1=2,\\ x_2=1$，结果相同。）\n\n"
                "**第四步（关系说明）**：两个方程组的公共解集恰好是「把两组方程联立后所得方程组」的解集——这就是公共解与联立求解的关系。推广地，若两个方程组同解，则把它们的方程合并后联立求解得到的解集就同时是两者的解集；判别同解可借助秩的必要条件：两方程组同解必有 $r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$（仅必要，反之不成立）。",
    points=[{"text": "把两个方程组的四个方程联立，写出公共解应满足的方程组", "partial": 2},
            {"text": "消元解出 x1=2、x2=1 并回代检验四个方程", "partial": 2},
            {"text": "给出公共解的结论", "partial": 2},
            {"text": "说明公共解与联立求解的关系，并指出同解的秩的必要条件", "partial": 2}],
    expl="**答案依据**：§4.4 线性方程组的解的结构（解集即方程组的解集）；公共解的求法配合 §3.1 初等行变换与 §3.3 秩判别。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构。",
    mis="⚠️易错点：只解出一个方程组就当作公共解。公共解必须**同时**满足两个方程组的所有方程，答案要回代检验。",
    tags=["计算", "高频", "真题改编"],
    src="同济《线性代数》第六版 §4.4 线性方程组的解的结构；题型改编自：中科大《线性代数》历年考题（两方程组公共解模型）",
    verify=[{"desc": "(2,1) 代入第一个方程组", "code": "str(list(M([[1,1],[1,-1]])*M([[2],[1]])))", "expected": "[3, 1]"},
            {"desc": "(2,1) 代入第二个方程组", "code": "str(list(M([[1,2],[2,-1]])*M([[2],[1]])))", "expected": "[4, 3]"}]))

Q_.append(Q(CALC, "medium", "4.3",
    "设 $A$ 是以 $s$ 个向量 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$（取自 $R^n$）为列构成的矩阵。证明下列三个命题等价：(1) 向量组线性无关；(2) $r(A)=s$；(3) 方程组 $A\\boldsymbol{x}=\\boldsymbol{0}$ 只有零解。",
    answer_text="**证明**：\n\n"
                "**(2)$\\Rightarrow$(1)**：$r(A)=s$ 表示存在 $s$ 个线性无关的列向量。若 $\\boldsymbol{\\alpha}_1,\\dots,\\boldsymbol{\\alpha}_s$ 线性相关，则存在不全为零的 $k_1,\\dots,k_s$ 使 $A\\boldsymbol{k}=\\boldsymbol{0}$（$\\boldsymbol{k}=(k_1,\\dots,k_s)^{T}$），即 $A$ 的列向量被压在维数小于 $s$ 的子空间中，$r(A)<s$，与 $r(A)=s$ 矛盾。故向量组线性无关。\n\n"
                "**(1)$\\Rightarrow$(3)**：若 $A\\boldsymbol{x}=\\boldsymbol{0}$ 有非零解 $\\boldsymbol{x}=(x_1,\\dots,x_s)^{T}$，则 $x_1\\boldsymbol{\\alpha}_1+\\cdots+x_s\\boldsymbol{\\alpha}_s=\\boldsymbol{0}$ 且系数不全为零，这与 (1) 矛盾。故只有零解。\n\n"
                "**(3)$\\Rightarrow$(2)**：若 (3) 成立而 $r(A)<s$，则 $A$ 的列向量组线性相关，由 (1) 的逆否命题知存在不全为零的 $k$ 使 $A\\boldsymbol{k}=\\boldsymbol{0}$，即 $A\\boldsymbol{x}=\\boldsymbol{0}$ 有非零解，与 (3) 矛盾。故 $r(A)=s$。三个命题等价。$\\blacksquare$\n\n"
                "**说明**：三个命题是同一件事的三个侧面——列空间的维数（秩）等于列数 $s$，等价于列向量张成的空间是「满」的（没有非平凡的零组合）。这一结论也把 §4.3 的秩与 §4.4 的解空间维数连了起来：解空间维数 $=n-r(A)$，当 $r(A)=s$ 时零空间退化为 $\\{\\boldsymbol{0}\\}$。",
    points=[{"text": "证明 (2)⇒(1)：用 r(A)=s 与列向量相关的秩小于 s 矛盾", "partial": 2},
            {"text": "证明 (1)⇒(3)：用非零解直接给出非平凡系数关系", "partial": 2},
            {"text": "证明 (3)⇒(2)：用逆否命题把零空间的非零解与 r(A)<s 对应起来", "partial": 2},
            {"text": "说明三个命题的统一含义（秩等于列数、列空间满、零空间为零）", "partial": 2}],
    expl="**答案依据**：§4.2 线性相关性的判定；§4.3 秩与极大线性无关组；§4.4 齐次方程组解的结构（解空间维数 $n-r(A)$）。\n"
          "**考点出处**：同济《线性代数》第六版 §4.3 向量组的秩。",
    mis="⚠️易错点：把「零空间只有零解」与「零空间维数为 0」当成两件事——它们说的是同一件事，但表述的对象不同，别把对象写错。",
    tags=["证明", "高频", "重点"],
    verify=[{"desc": "示例：方阵满秩（秩等于列数，故列向量无关）", "code": "M([[1,2],[3,4]]).rank()", "expected": "2"},
            {"desc": "示例：满秩方阵的齐次方程组只有零解（零空间为空）", "code": "len(M([[1,2],[3,4]]).nullspace())", "expected": "0"}]))

Q_.append(Q(CALC, "hard", "4.4",
    "设线性方程组 $A\\boldsymbol{x}=b$ 与 $C\\boldsymbol{x}=d$ 同解。证明：必有 $r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$；并举例说明这两个等式成立还不足以保证两个方程组同解。",
    answer_text="**第一步（由同解得相容）**：两个方程组同解，自然都有解，故由 §3.3 的秩判别定理\n$$r(A)=r(A\\mid b),\\qquad r(C)=r(C\\mid d).$$\n"
                "**第二步（由同解得解空间维数相同）**：设 $A$ 为 $m\\times n$ 矩阵。同解意味着两个方程组的解集相同，记为 $S$。非齐次方程组 $A\\boldsymbol{x}=b$ 的解集是零空间 $N(A)=\\{\\boldsymbol{x}\\mid A\\boldsymbol{x}=0\\}$ 的一个平移，故\n$$\\dim S=\\dim N(A)=n-r(A).$$\n"
                "同理 $\\dim S=n-r(C)$。由 $\\dim S$ 的唯一性得 $n-r(A)=n-r(C)$，即 $r(A)=r(C)$。\n\n"
                "**第三步（合并）**：把第一步与第二步合起来即得 $r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$。$\\blacksquare$\n\n"
                "**第四步（反例：条件不充分）**：取方程组 $\\mathrm{I}: x_1=0$ 与 $\\mathrm{II}: x_2=0$（都在 $R^2$ 中）。\n"
                "- 系数矩阵 $A=\\begin{pmatrix}1&0\\end{pmatrix}$，$C=\\begin{pmatrix}0&1\\end{pmatrix}$，故 $r(A)=r(C)=1$；\n"
                "- 增广矩阵 $\\begin{pmatrix}1&0&0\\end{pmatrix}$ 与 $\\begin{pmatrix}0&1&0\\end{pmatrix}$ 的秩也是 1，即 $r(A\\mid b)=r(C\\mid d)=1$；\n"
                "- 但 $\\mathrm{I}$ 的解集是 $\\{(0,t)^{T}\\mid t\\in R\\}$，$\\mathrm{II}$ 的解集是 $\\{(t,0)^{T}\\mid t\\in R\\}$，二者不同：$(0,1)^{T}$ 满足 $\\mathrm{I}$ 而不满足 $\\mathrm{II}$（代入 $\\mathrm{II}$ 得 $1\\neq0$）。\n\n"
                "**结论**：$r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$ 是同解的**必要**条件，判定同解还需更强的条件（等价地：把两组方程联立后所得方程组的解集与二者的解集相同）。",
    points=[{"text": "由同解说明两个方程组都相容，得 r(A)=r(A|b)、r(C)=r(C|d)", "partial": 2},
            {"text": "由同解说明解集相同，用维数 n-r(A)=n-r(C) 得 r(A)=r(C)", "partial": 2},
            {"text": "合并得到 r(A)=r(C) 且 r(A|b)=r(C|d) 的必要条件结论", "partial": 2},
            {"text": "给出 x1=0 与 x2=0 的反例，说明两个等式不足以保证同解", "partial": 2}],
    expl="**答案依据**：§4.4 线性方程组的解的结构（解集＝零空间的平移，维数 $n-r(A)$）+ §3.3 秩判别定理。\n"
          "**考点出处**：同济《线性代数》第六版 §4.4 线性方程组的解的结构；题型改编自：中科大《线性代数》历年考题（同解判据模型）。",
    mis="⚠️易错点：把必要条件当成充分条件。$r(A)=r(C)$ 且 $r(A\\mid b)=r(C\\mid d)$ 只说明两方程组「秩相同」，判别同解还要看解集是否重合。",
    tags=["真题改编", "证明", "难点", "高频"],
    src="同济《线性代数》第六版 §4.4 线性方程组的解的结构；题型改编自：中科大《线性代数》历年考题（同解判据模型）",
    verify=[{"desc": "反例中第一个系数矩阵的秩", "code": "M([[1,0]]).rank()", "expected": "1"},
            {"desc": "反例中第二个系数矩阵的秩", "code": "M([[0,1]]).rank()", "expected": "1"},
            {"desc": "(0,1) 不满足第二个方程组 x2=0", "code": "str(list(M([[0,1]])*M([[0],[1]])))", "expected": "[1]"}]))

Q_.append(Q(CALC, "hard", "4.5",
    "在 $R^3$ 中，设 $a$ 为常数。判断下列集合是否为 $R^3$ 的子空间，并说明理由：(1) $W_1=\\{(x,y,z)^{\\mathsf T}\\mid x+a y-z=0\\}$；(2) $W_2=\\{(x,y,z)^{\\mathsf T}\\mid x+a y-z=1\\}$；(3) $W_3=\\{(x,y,z)^{\\mathsf T}\\mid x^{2}+y^{2}+z^{2}=1\\}$。",
    answer_text="**判定依据（§4.5）**：设 $W$ 是 $V$ 的非空子集，则 $W$ 是 $V$ 的子空间 $\\iff W$ 非空且对向量的加法与数乘封闭（等价地：含零向量且封闭）。\n\n"
                "**(1) $W_1$ 是子空间（对任意 $a$ 都成立）**：$W_1$ 非空，且零向量满足 $0+a\\cdot0-0=0$。设 $\\boldsymbol{\\alpha}=(x_1,y_1,z_1)^{T},\\boldsymbol{\\beta}=(x_2,y_2,z_2)^{T}\\in W_1$，则 $x_i+a y_i-z_i=0$（$i=1,2$）。于是\n$$(\\boldsymbol{\\alpha}+\\boldsymbol{\\beta})\\text{ 满足 } (x_1+x_2)+a(y_1+y_2)-(z_1+z_2)=(x_1+a y_1-z_1)+(x_2+a y_2-z_2)=0,$$\n"
                "而 $c\\boldsymbol{\\alpha}$ 满足 $cx_1+ca y_1-cz_1=c(x_1+a y_1-z_1)=0$。故 $W_1$ 对加法与数乘封闭，是子空间。\n"
                "（几何上：$x+ay-z=0$ 是过原点的平面；它正是**齐次**线性方程的解集，与 §4.4 呼应。）\n\n"
                "**(2) $W_2$ 不是子空间（对任意 $a$ 都成立）**：零向量的分量为 0，代入 $x+a y-z=1$ 得 $0\\neq1$，故 $\\boldsymbol{0}\\notin W_2$。子空间必含零向量，因此 $W_2$ 不是子空间。（它是非齐次方程 $x+ay-z=1$ 的解集，是一个不经过原点的平面。）\n\n"
                "**(3) $W_3$ 不是子空间**：零向量满足 $0+0+0=0\\neq1$，故 $\\boldsymbol{0}\\notin W_3$，已经可以否定。它对加法也不封闭：取 $\\boldsymbol{\\alpha}=(1,0,0)^{T}$ 与 $\\boldsymbol{\\beta}=(0,1,0)^{T}$，二者都满足分量平方和为 1，属于 $W_3$；但 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}=(1,1,0)^{T}$ 的分量平方和为 $1+1=2\\neq1$，故 $\\boldsymbol{\\alpha}+\\boldsymbol{\\beta}\\notin W_3$。（$W_3$ 是单位球面，由**非线性**条件给出，一般不是子空间。）",
    points=[{"text": "写出子空间判定定理作为统一依据", "partial": 2},
            {"text": "判定 W1 是子空间并证明其对加法与数乘封闭", "partial": 2},
            {"text": "判定 W2 不是子空间（不含零向量），并指出与 (1) 的区别在齐次与非齐次", "partial": 2},
            {"text": "判定 W3 不是子空间（不含零向量且对加法不封闭），说明非线性条件给出的一般情形", "partial": 2}],
    expl="**答案依据**：§4.5 向量空间与子空间的判定定理；与 §4.4「齐次解集是子空间、非齐次解集不是子空间」相互印证。\n"
          "**考点出处**：同济《线性代数》第六版 §4.5 向量空间。",
    mis="⚠️易错点：以为「只差一个常数」的 $W_1$ 与 $W_2$ 地位相同。齐次方程的解集含原点是子空间，非齐次的不含原点。",
    tags=["计算", "难点", "重点", "含参"],
    verify=[{"desc": "W1 中向量 (1,0,1) 满足 x+2y-z=0（取 a=2）", "code": "M([1,0,1])[0]+2*M([1,0,1])[1]-M([1,0,1])[2]", "expected": "0"},
            {"desc": "零向量不满足 W2 的条件 x+2y-z=1", "code": "M([0,0,0])[0]+2*M([0,0,0])[1]-M([0,0,0])[2]", "expected": "0"},
            {"desc": "W3 中 (1,0,0)+(0,1,0)=(1,1,0) 的分量平方和为 2，不等于 1", "code": "str(M([[1,1,0]]).dot(M([[1],[1],[0]])))", "expected": "2"}]))

Q = Q_
