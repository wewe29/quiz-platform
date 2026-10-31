/* tools/render_coverage.js — 渲染层内容覆盖门禁
 *
 * 为什么需要它：数据层的审计（答案键 ↔ 解析自洽、解析非空、采分点结构）
 * 全绿，**不代表渲染时内容没被丢掉**。真实踩过：
 *   splitExplanation 把「答案依据」单独摘出来后，buildExplain 把它挂在
 *   「其它段落」上渲染 —— 而整篇解析只有「答案依据 + 逐项错因」时
 *   其它段落为空，依据就被整段丢弃（856 题里 103 题中招）。
 *   数据层面看，解析字段一直存在、一直非空，所以所有数据门禁都是绿的。
 *
 * 本脚本加载**真实的 assets/js/ui/render.js**，对全库逐题跑一遍
 * splitExplanation + explainBlocks，检查：
 *   1) 解析里有「答案依据」→ 渲染块里必须能找回这段依据；
 *   2) 解析里的每一行「其它段落」→ 必须出现在渲染块里；
 *   3) 解析里的每个逐项错因字母 → 必须出现在渲染块里。
 *
 * 用法：
 *   node tools/render_coverage.js <questions.json>
 *   type questions.json | node tools/render_coverage.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const JS_DIR = path.join(__dirname, 'assets', 'js');

/* ---- 加载真实的前端渲染模块 ---- */
global.window = global;
global.QX = undefined;
for (const f of ['ui/dom.js', 'ui/render.js']) {
  const p = path.join(JS_DIR, f);
  vm.runInThisContext(fs.readFileSync(p, 'utf8'), { filename: p });
}
const QX = global.QX;
QX.render.init({ dom: QX.dom });

/* ---- 取题库 ---- */
function readQuestions() {
  const arg = process.argv[2];
  let raw;
  if (arg && arg !== '-') {
    raw = fs.readFileSync(arg, 'utf8');
  } else {
    raw = fs.readFileSync(0, 'utf8');
  }
  const data = JSON.parse(raw);
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.questions)) return data.questions;
  throw new Error('输入不是题目数组');
}

const questions = readQuestions();
const errs = [];
let checked = 0;
let basisKept = 0;
let explicitBasis = 0;

for (const q of questions) {
  checked += 1;
  const expl = q.explanation || '';
  if (/^\s*\*\*答案依据\*\*/.test(expl)) explicitBasis += 1;
  const parts = QX.render.splitExplanation(expl);
  const blocks = QX.render.explainBlocks(expl);

  const proseBlk = blocks.find((b) => b.kind === 'prose');
  const reasonsBlk = blocks.find((b) => b.kind === 'reasons');

  // 1) 依据段必须能找回
  if (parts.basis) {
    if (!proseBlk || !proseBlk.basis) {
      errs.push(q.id + '：解析含「答案依据」但渲染块里丢失（' + parts.basis.length + ' 字）');
    } else if (proseBlk.basis !== parts.basis) {
      errs.push(q.id + '：渲染出的依据与解析里的依据不一致');
    } else {
      basisKept += 1;
    }
  }

  // 2) 其它段落逐行都要在
  const renderedProse = proseBlk ? proseBlk.items.join('\n') : '';
  for (const s of parts.rest) {
    if (!s.trim()) continue;
    if (renderedProse.indexOf(s) < 0) {
      errs.push(q.id + '：段落未出现在渲染块里 → ' + s.slice(0, 40));
    }
  }

  // 3) 逐项错因字母都要在
  const renderedLetters = reasonsBlk ? reasonsBlk.items.map((r) => r.letter) : [];
  for (const r of parts.reasons) {
    if (renderedLetters.indexOf(r.letter) < 0) {
      errs.push(q.id + '：错因 ' + r.letter + ' 未出现在渲染块里');
    }
  }

  // 4) 客观题必须有答案字母可渲染
  if (['single', 'multi', 'judge'].indexOf(q.type) >= 0) {
    if (!q.answer || !q.answer.length) {
      errs.push(q.id + '：客观题没有答案字母');
    }
  }
}

console.log('[render] 逐题检查 ' + checked + ' 道，保留依据 ' + basisKept +
  ' 道（其中显式「答案依据」段 ' + explicitBasis + ' 道，其余为首段回退）');
if (errs.length) {
  console.log('[render] 发现 ' + errs.length + ' 个渲染层内容丢失：');
  for (const e of errs.slice(0, 20)) console.log('  [FAIL] ' + e);
  if (errs.length > 20) console.log('  ... 其余 ' + (errs.length - 20) + ' 条省略');
  process.exit(1);
}
console.log('[render] 渲染层内容覆盖检查通过');
