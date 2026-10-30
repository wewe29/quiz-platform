// KaTeX 渲染探针：用本机 dist 版 KaTeX 渲染公式，检查 HTML 输出里是否真的有 ≠
// 用途：区分「公式在浏览器里渲染坏了」与「文本提取工具的假象」
const path = require('path');
const katexDir = 'D:\\workspace\\5-docs\\exam\\数据库\\node_modules\\katex\\dist';
const katex = require(path.join(katexDir, 'katex.min.js'));

const cases = [
  ['$|A|\\neq0\\iff A$', 'q-001 解析首个公式'],
  ['$B\\neq0$', 'q-001 选项 C'],
  ['$|A|=\\prod\\lambda_i$', 'q-001 解析 D'],
  ['$\\begin{vmatrix}1&1\\\\1&1\\end{vmatrix}=0$', 'q-001 反例矩阵'],
];

let bad = 0;
for (const [raw, label] of cases) {
  // 页面里由 KaTeX auto-render 负责剥离 $…$ 定界符，renderToString 只吃裸 TeX
  const tex = raw.replace(/^\$+|\$+$/g, '');
  const html = katex.renderToString(tex, { throwOnError: false, displayMode: false });
  const hasNe = html.includes('\u2260');            // ≠
  const hasBackslashNe = html.includes('\\neq');      // 未被解析的裸命令
  const err = html.includes('katex-error');
  console.log('--- ' + label);
  console.log('  tex      : ' + tex);
  console.log('  含 ≠ 字符 : ' + hasNe);
  console.log('  残留 \\neq: ' + hasBackslashNe);
  console.log('  katex-error: ' + err);
  if (!hasNe || hasBackslashNe || err) {
    bad++;
    console.log('  HTML 片段: ' + html.replace(/\s+/g, ' ').slice(0, 400));
  }
}
console.log('\n结论：' + (bad === 0 ? '全部正常渲染，≠ 存在于 KaTeX HTML 输出中' : bad + ' 条异常'));
process.exit(bad === 0 ? 0 : 1);
