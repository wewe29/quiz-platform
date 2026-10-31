/* tools/research/katex_probe.js — 给一组候选公式问 KaTeX 本尊：哪些真的渲染不了？
 *
 * 用法：node katex_probe.js <input.json>
 *   input.json: { "formulas": ["...", ...] }
 * 输出：逐条 OK / FAIL，最后给出失败条数。
 */
'use strict';

const fs = require('fs');
const path = require('path');

const KATEX_DIR = 'D:\\workspace\\5-docs\\exam\\数据库\\node_modules\\katex\\dist';
const katex = require(path.join(KATEX_DIR, 'katex.min.js'));

const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const list = data.formulas || [];
let bad = 0;
list.forEach(function (tex, i) {
  try {
    katex.renderToString(tex, {
      throwOnError: true, displayMode: false, strict: 'ignore', trust: false, macros: {}
    });
    console.log('OK   #' + i + '  ' + tex.slice(0, 100).replace(/\n/g, ' '));
  } catch (e) {
    bad++;
    console.log('FAIL #' + i + '  ' + String(e.message).slice(0, 160));
    console.log('         ' + tex.slice(0, 160).replace(/\n/g, ' '));
  }
});
console.log('---- 共 ' + list.length + ' 条，失败 ' + bad + ' 条');
