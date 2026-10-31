/* tools/research/katex_check.js — KaTeX 合法性复核
 *
 * 读入 JSON 数组 [{ id, formulas: ["...", ...] }]，用本地 KaTeX 逐条渲染，
 * 任何渲染失败都算错误。Typst→LaTeX 转写可能留下非法记号，这道门禁专门挡它。
 *
 * 用法：node katex_check.js <input.json> [output.json]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const KATEX_DIR = 'D:\\workspace\\5-docs\\exam\\数据库\\node_modules\\katex\\dist';
let katex;
try {
  katex = require(path.join(KATEX_DIR, 'katex.min.js'));
} catch (e) {
  console.error('无法加载 KaTeX：' + e.message);
  process.exit(2);
}

const input = process.argv[2];
if (!input) {
  console.error('用法：node katex_check.js <input.json> [output.json]');
  process.exit(2);
}

const data = JSON.parse(fs.readFileSync(input, 'utf8'));
const bad = [];
let total = 0;

for (const item of data) {
  for (let i = 0; i < item.formulas.length; i++) {
    const tex = item.formulas[i];
    total++;
    try {
      katex.renderToString(tex, {
        throwOnError: true,
        displayMode: false,
        strict: 'ignore',
        trust: false,
        macros: {}
      });
    } catch (e) {
      bad.push({ id: item.id, index: i, tex: tex.slice(0, 200), error: String(e.message).slice(0, 220) });
    }
  }
}

const out = process.argv[3];
if (out) {
  fs.writeFileSync(out, JSON.stringify({ total, badCount: bad.length, bad }, null, 1), 'utf8');
}
console.log('公式总数 ' + total + '，渲染失败 ' + bad.length);
for (const b of bad.slice(0, 25)) {
  console.log('  [FAIL] ' + b.id + ' #' + b.index + '  ' + b.error);
  console.log('         ' + b.tex);
}
process.exit(bad.length ? 1 : 0);
