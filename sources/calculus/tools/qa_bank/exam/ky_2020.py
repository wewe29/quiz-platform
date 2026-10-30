# -*- coding: utf-8 -*-
"""2020 年全国硕士研究生招生考试数学（一）真题（高等数学范围）。

来源：GitHub 仓库 TsekaLuk/Kaoyan-Math1-Papers
题干文件：papers/…；答案解析：solutions/2020年解析/…

入库口径：题干 / 选项 / 答案 / 解析取自源卷面文件；
          只收属于同济《高等数学》范围的题，线代与概率统计整题丢弃。
"""
from ..common import Q

Q = [
    Q('calc', "medium", "1.3",
      stem="设函数 $f(x)$ 在区间 $(-1, 1)$ 内有定义，且 $\\lim_{x \\to 0} f(x) = 0$ ，则（ ）.",
      answer_text="方法一\n\n若 $f(x)$ 在 $x = 0$ 处可导，则 $f(x)$ 在 $x = 0$ 处连续，由 $\\lim_{x\\to 0}f(x) = 0$ 得 $f(0) = 0$\n\n因为 $\\lim_{x\\to 0}\\frac{f(x) - f(0)}{x - 0} = \\lim_{x\\to 0}\\frac{f(x)}{x}$ 存在，所以 $f(x)$ 为 $x$ 的同阶或高阶无穷小，故\n\n$\\lim_{x \\to 0} \\frac{f(x)}{\\sqrt{|x|}} = 0$ ，应选（C）.\n\n方法二\n\n取 $f(x) = |x|$ ，显然 $\\lim_{x\\to 0}\\frac{f(x)}{\\sqrt{|x|}} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不可导，（A）不对；\n\n取 $f(x) = \\begin{cases} 2, & x = 0, \\\\ x^2, & x \\neq 0, \\end{cases}$ 显然 $f(x)$ 在 $(-1,1)$ 内有定义且 $\\lim_{x \\to 0} f(x) = 0$ ，显然 $\\lim_{x \\to 0} \\frac{f(x)}{x^2} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不连续，从而 $f(x)$ 在 $x = 0$ 处不可导，(B) 不对；\n\n取 $f(x) = 2x$ ，显然 $f(x)$ 在 $x = 0$ 处可导，但 $\\lim_{x\\to 0}\\frac{f(x)}{x^2}$ 不存在，（D）不对，应选(C).",
      points=[{'text': "方法一", 'partial': 2}, {'text': "若 $f(x)$ 在 $x = 0$ 处可导，则 $f(x)$ 在 $x = 0$ 处连续，由 $\\lim_{x\\to 0}f(x) = 0$ 得 $f(0) = 0$", 'partial': 2}, {'text': "因为 $\\lim_{x\\to 0}\\frac{f(x) - f(0)}{x - 0} = \\lim_{x\\to 0}\\frac{f(x)}{x}$ 存在，所以 $f(x)$ 为 $x$ 的同阶或高阶无穷小，故", 'partial': 2}, {'text': "$\\lim_{x \\to 0} \\frac{f(x)}{\\sqrt{|x|}} = 0$ ，应选（C）.", 'partial': 2}, {'text': "方法二", 'partial': 2}, {'text': "取 $f(x) = |x|$ ，显然 $\\lim_{x\\to 0}\\frac{f(x)}{\\sqrt{|x|}} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不可导，（A）不对；；取 $f(x) = \\begin{cases} 2, & x = 0, \\\\ x^2, & x \\neq 0, \\end{cases}$ 显然 $f(x)$ 在 $(-1,1)$ 内有定义且 $\\lim_{x \\to 0} f(x) = 0$ ，显然 $\\lim_{x \\to 0} \\frac{f(x)}{x^2} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不连续，从而 $f(x)$ 在 $x = 0$ 处不可导，(B) 不对；；取 $f(x) = 2x$ ，显然 $f(x)$ 在 $x = 0$ 处可导，但 $\\lim_{x\\to 0}\\frac{f(x)}{x^2}$ 不存在，（D）不对，应选(C).", 'partial': 2}],
      expl="**答案依据**：C\n方法一\n\n若 $f(x)$ 在 $x = 0$ 处可导，则 $f(x)$ 在 $x = 0$ 处连续，由 $\\lim_{x\\to 0}f(x) = 0$ 得 $f(0) = 0$\n\n因为 $\\lim_{x\\to 0}\\frac{f(x) - f(0)}{x - 0} = \\lim_{x\\to 0}\\frac{f(x)}{x}$ 存在，所以 $f(x)$ 为 $x$ 的同阶或高阶无穷小，故\n\n$\\lim_{x \\to 0} \\frac{f(x)}{\\sqrt{|x|}} = 0$ ，应选（C）.\n\n方法二\n\n取 $f(x) = |x|$ ，显然 $\\lim_{x\\to 0}\\frac{f(x)}{\\sqrt{|x|}} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不可导，（A）不对；\n\n取 $f(x) = \\begin{cases} 2, & x = 0, \\\\ x^2, & x \\neq 0, \\end{cases}$ 显然 $f(x)$ 在 $(-1,1)$ 内有定义且 $\\lim_{x \\to 0} f(x) = 0$ ，显然 $\\lim_{x \\to 0} \\frac{f(x)}{x^2} = 0$ ，但 $f(x)$ 在 $x = 0$ 处不连续，从而 $f(x)$ 在 $x = 0$ 处不可导，(B) 不对；\n\n取 $f(x) = 2x$ ，显然 $f(x)$ 在 $x = 0$ 处可导，但 $\\lim_{x\\to 0}\\frac{f(x)}{x^2}$ 不存在，（D）不对，应选(C).",
      src="2020 年考研数学（一）第 2 题",
      kind='exam-original',
      src_year=2020,
      src_region='全国',
      src_paper="2020 年考研数学（一）",
      src_number="2",
      src_url="https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
      prov={'level': 'original', 'url': "https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
            'verifiedAt': '2026-10-28',
            'note': '题干、选项、答案与解析取自源卷面 Markdown 文件；答案解析文件：https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/solutions/2020年解析/2020年解析.md'},
      qid="ky-2020-2-428ad6",
      tags=['考研真题'],
    ),
    Q('calc', "hard", "12.4",
      stem="设数列 $\\{a_{n}\\}$ 满足： $a_1 = 1,(n + 1)a_{n + 1} = \\left(n + \\frac{1}{2}\\right)a_n$ ，证明：当 $|x| < 1$ 时，幂级数 $\\sum_{n = 1}^{\\infty}a_{n}x^{n}$ 收敛，并求其和函数.",
      answer_text="由 $(n + 1)a_{n + 1} = \\left(n + \\frac{1}{2}\\right)a_n$ 得 $\\frac{a_{n + 1}}{a_n} = \\frac{n + \\frac{1}{2}}{n + 1},$\n从而 $\\lim_{n\\to \\infty}\\frac{a_{n + 1}}{a_n} = 1$ ，即幂级数 $\\sum_{n = 1}^{\\infty}a_{n}x^{n}$ 的收敛半径为 $R = 1$\n\n故当 $|x| < 1$ 时，幂级数 $\\sum_{n=1}^{\\infty} a_n x^n$ 收敛.\n\n令 $S(x) = \\sum_{n=1}^{\\infty} a_n x^n$ ，则\n\n$$\n\\begin{array}{l} S ^ {\\prime} (x) = 1 + \\sum_ {n = 1} ^ {\\infty} (n + 1) a _ {n + 1} x ^ {n} = 1 + \\sum_ {n = 1} ^ {\\infty} \\left(n + \\frac {1}{2}\\right) a _ {n} x ^ {n} \\\\ = 1 + x \\sum_ {n = 1} ^ {\\infty} n a _ {n} x ^ {n - 1} + \\frac {1}{2} \\sum_ {n = 1} ^ {\\infty} a _ {n} x ^ {n} = 1 + x S ^ {\\prime} (x) + \\frac {1}{2} S (x), \\\\ \\end{array}\n$$\n\n即 $S^{\\prime}(x) - \\frac{1}{2(1 - x)} S(x) = \\frac{1}{1 - x}$ ，解得\n\n$$\nS (x) = (- 2 \\sqrt {1 - x} + C) \\frac {1}{\\sqrt {1 - x}} = \\frac {C}{\\sqrt {1 - x}} - 2,\n$$\n\n由 $S(0) = 0$ 得 $C = 2$ ，故 $S(x) = \\frac{2}{\\sqrt{1 - x}} - 2.$",
      points=[{'text': "由 $(n + 1)a_{n + 1} = \\left(n + \\frac{1}{2}\\right)a_n$ 得 $\\frac{a_{n + 1}}{a_n} = \\frac{n + \\frac{1}{2}}{n + 1},$\n从而 $\\lim_{n\\to \\infty}\\frac{a_{n + 1}}{a_n} = 1$ ，即幂级数 $\\sum_{n = 1}^{\\infty}a_{n}x^{n}$ 的收敛半径为 $R = 1$", 'partial': 2}, {'text': "故当 $|x| < 1$ 时，幂级数 $\\sum_{n=1}^{\\infty} a_n x^n$ 收敛.", 'partial': 2}, {'text': "令 $S(x) = \\sum_{n=1}^{\\infty} a_n x^n$ ，则", 'partial': 2}, {'text': "$$\n\\begin{array}{l} S ^ {\\prime} (x) = 1 + \\sum_ {n = 1} ^ {\\infty} (n + 1) a _ {n + 1} x ^ {n} = 1 + \\sum_ {n = 1} ^ {\\infty} \\left(n + \\frac {1}{2}\\right) a _ {n} x ^ {n} \\\\ = 1 + x \\sum_ {n = 1} ^ {\\infty} n a _ {n} x ^ {n - 1} + \\frac {1}{2} \\sum_ {n = 1} ^ {\\infty} a _ {n} x ^ {n} = 1 + x S ^ {\\prime} (x) + \\frac {1}{2} S (x), \\\\ \\end{array}\n$$", 'partial': 2}, {'text': "即 $S^{\\prime}(x) - \\frac{1}{2(1 - x)} S(x) = \\frac{1}{1 - x}$ ，解得", 'partial': 2}, {'text': "$$\nS (x) = (- 2 \\sqrt {1 - x} + C) \\frac {1}{\\sqrt {1 - x}} = \\frac {C}{\\sqrt {1 - x}} - 2,\n$$；由 $S(0) = 0$ 得 $C = 2$ ，故 $S(x) = \\frac{2}{\\sqrt{1 - x}} - 2.$", 'partial': 2}],
      expl="**答案依据**：见解析\n由 $(n + 1)a_{n + 1} = \\left(n + \\frac{1}{2}\\right)a_n$ 得 $\\frac{a_{n + 1}}{a_n} = \\frac{n + \\frac{1}{2}}{n + 1},$\n从而 $\\lim_{n\\to \\infty}\\frac{a_{n + 1}}{a_n} = 1$ ，即幂级数 $\\sum_{n = 1}^{\\infty}a_{n}x^{n}$ 的收敛半径为 $R = 1$\n\n故当 $|x| < 1$ 时，幂级数 $\\sum_{n=1}^{\\infty} a_n x^n$ 收敛.\n\n令 $S(x) = \\sum_{n=1}^{\\infty} a_n x^n$ ，则\n\n$$\n\\begin{array}{l} S ^ {\\prime} (x) = 1 + \\sum_ {n = 1} ^ {\\infty} (n + 1) a _ {n + 1} x ^ {n} = 1 + \\sum_ {n = 1} ^ {\\infty} \\left(n + \\frac {1}{2}\\right) a _ {n} x ^ {n} \\\\ = 1 + x \\sum_ {n = 1} ^ {\\infty} n a _ {n} x ^ {n - 1} + \\frac {1}{2} \\sum_ {n = 1} ^ {\\infty} a _ {n} x ^ {n} = 1 + x S ^ {\\prime} (x) + \\frac {1}{2} S (x), \\\\ \\end{array}\n$$\n\n即 $S^{\\prime}(x) - \\frac{1}{2(1 - x)} S(x) = \\frac{1}{1 - x}$ ，解得\n\n$$\nS (x) = (- 2 \\sqrt {1 - x} + C) \\frac {1}{\\sqrt {1 - x}} = \\frac {C}{\\sqrt {1 - x}} - 2,\n$$\n\n由 $S(0) = 0$ 得 $C = 2$ ，故 $S(x) = \\frac{2}{\\sqrt{1 - x}} - 2.$",
      src="2020 年考研数学（一）第 17 题",
      kind='exam-original',
      src_year=2020,
      src_region='全国',
      src_paper="2020 年考研数学（一）",
      src_number="17",
      src_url="https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
      prov={'level': 'original', 'url': "https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
            'verifiedAt': '2026-10-28',
            'note': '题干、选项、答案与解析取自源卷面 Markdown 文件；答案解析文件：https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/solutions/2020年解析/2020年解析.md'},
      qid="ky-2020-17-8b84b5",
      tags=['考研真题'],
    ),
    Q('calc', "hard", "1.8",
      stem="设 $\\Sigma$ 为曲面 $z = \\sqrt{x^2 + y^2}$ （ $1 \\leqslant x^2 + y^2 \\leqslant 4$ ）的下侧， $f(x)$ 是连续函数，计算\n$$\nI = \\iint_ {\\Sigma} [ x f (x y) + 2 x - y ] d y d z + [ y f (x y) + 2 y + x ] d z d x + [ z f (x y) + z ] d x d y.\n$$",
      answer_text="因为 $\\Sigma$ 的法向量为 $(x, y, -z)$ ，所以\n$$\n\\begin{array}{l} I = \\iint_ {\\Sigma} \\frac {1}{\\sqrt {2 (x ^ {2} + y ^ {2})}} \\left[ \\left(x ^ {2} + y ^ {2} - z ^ {2}\\right) f (x y) + 2 x ^ {2} + 2 y ^ {2} - z ^ {2} \\right] d S \\\\ = \\frac {\\sqrt {2}}{2} \\iint_ {\\Sigma} \\sqrt {x ^ {2} + y ^ {2}} d S. \\\\ \\end{array}\n$$\n\n记 $D = \\{(x,y)\\mid 1\\leqslant x^2 +y^2\\leqslant 4\\}$ ，又\n\n$$\n\\sqrt {\\left(\\frac {\\partial z}{\\partial x}\\right) ^ {2} + \\left(\\frac {\\partial z}{\\partial y}\\right) ^ {2} + 1} = \\sqrt {\\left(\\frac {x}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + \\left(\\frac {y}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + 1} = \\sqrt {2}.\n$$\n\n故\n\n$$\n\\begin{array}{l} I = \\iint_ {D} \\sqrt {x ^ {2} + y ^ {2}} d x d y \\\\ = \\int_ {0} ^ {2 \\pi} \\mathrm {d} \\theta \\int_ {1} ^ {2} r ^ {2} \\mathrm {d} r \\\\ = \\frac {1 4}{3} \\pi . \\\\ \\end{array}\n$$",
      points=[{'text': "因为 $\\Sigma$ 的法向量为 $(x, y, -z)$ ，所以\n$$\n\\begin{array}{l} I = \\iint_ {\\Sigma} \\frac {1}{\\sqrt {2 (x ^ {2} + y ^ {2})}} \\left[ \\left(x ^ {2} + y ^ {2} - z ^ {2}\\right) f (x y) + 2 x ^ {2} + 2 y ^ {2} - z ^ {2} \\right] d S \\\\ = \\frac {\\sqrt {2}}{2} \\iint_ {\\Sigma} \\sqrt {x ^ {2} + y ^ {2}} d S. \\\\ \\end{array}\n$$", 'partial': 2}, {'text': "记 $D = \\{(x,y)\\mid 1\\leqslant x^2 +y^2\\leqslant 4\\}$ ，又", 'partial': 2}, {'text': "$$\n\\sqrt {\\left(\\frac {\\partial z}{\\partial x}\\right) ^ {2} + \\left(\\frac {\\partial z}{\\partial y}\\right) ^ {2} + 1} = \\sqrt {\\left(\\frac {x}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + \\left(\\frac {y}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + 1} = \\sqrt {2}.\n$$", 'partial': 2}, {'text': "故", 'partial': 2}, {'text': "$$\n\\begin{array}{l} I = \\iint_ {D} \\sqrt {x ^ {2} + y ^ {2}} d x d y \\\\ = \\int_ {0} ^ {2 \\pi} \\mathrm {d} \\theta \\int_ {1} ^ {2} r ^ {2} \\mathrm {d} r \\\\ = \\frac {1 4}{3} \\pi . \\\\ \\end{array}\n$$", 'partial': 2}],
      expl="**答案依据**：见解析\n因为 $\\Sigma$ 的法向量为 $(x, y, -z)$ ，所以\n$$\n\\begin{array}{l} I = \\iint_ {\\Sigma} \\frac {1}{\\sqrt {2 (x ^ {2} + y ^ {2})}} \\left[ \\left(x ^ {2} + y ^ {2} - z ^ {2}\\right) f (x y) + 2 x ^ {2} + 2 y ^ {2} - z ^ {2} \\right] d S \\\\ = \\frac {\\sqrt {2}}{2} \\iint_ {\\Sigma} \\sqrt {x ^ {2} + y ^ {2}} d S. \\\\ \\end{array}\n$$\n\n记 $D = \\{(x,y)\\mid 1\\leqslant x^2 +y^2\\leqslant 4\\}$ ，又\n\n$$\n\\sqrt {\\left(\\frac {\\partial z}{\\partial x}\\right) ^ {2} + \\left(\\frac {\\partial z}{\\partial y}\\right) ^ {2} + 1} = \\sqrt {\\left(\\frac {x}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + \\left(\\frac {y}{\\sqrt {x ^ {2} + y ^ {2}}}\\right) ^ {2} + 1} = \\sqrt {2}.\n$$\n\n故\n\n$$\n\\begin{array}{l} I = \\iint_ {D} \\sqrt {x ^ {2} + y ^ {2}} d x d y \\\\ = \\int_ {0} ^ {2 \\pi} \\mathrm {d} \\theta \\int_ {1} ^ {2} r ^ {2} \\mathrm {d} r \\\\ = \\frac {1 4}{3} \\pi . \\\\ \\end{array}\n$$",
      src="2020 年考研数学（一）第 18 题",
      kind='exam-original',
      src_year=2020,
      src_region='全国',
      src_paper="2020 年考研数学（一）",
      src_number="18",
      src_url="https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
      prov={'level': 'original', 'url': "https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/papers/2020年考研数学(一)真题.md",
            'verifiedAt': '2026-10-28',
            'note': '题干、选项、答案与解析取自源卷面 Markdown 文件；答案解析文件：https://github.com/TsekaLuk/Kaoyan-Math1-Papers/blob/main/solutions/2020年解析/2020年解析.md'},
      qid="ky-2020-18-b9d2bc",
      tags=['考研真题'],
    ),
]
