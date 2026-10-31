/* tests/ui.test.js — ui/ 层纯函数单测（node --test）
   只测不依赖 DOM 的部分：解析拆解、文本转义、时间格式化。 */
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const H = require('./harness.js');

function setup() {
  const QX = H.loadCoreAndUi();
  QX.render.init({ dom: QX.dom });
  return QX;
}

test('render.splitExplanation 拆出「答案依据」与逐项错因', () => {
  const { render } = setup();
  const expl = [
    '**答案依据**：定义域由两个约束联立，故 C 正确。',
    'A 错：只保留了 $|x|\\le 1$ 这一段。',
    'B 错：漏掉了挖去 $x=2$。',
    'D 错：漏掉了根号对 $|x|\\ge 1$ 的约束。'
  ].join('\n');
  const p = render.splitExplanation(expl);
  assert.ok(p.basis.indexOf('两个约束联立') >= 0, '答案依据应被抽出');
  assert.strictEqual(p.reasons.length, 4, 'A/B/D 错因 + 依据里点名的 C 正确项');
  assert.deepStrictEqual(p.reasons.map((r) => r.letter), ['A', 'B', 'C', 'D']);
  assert.ok(p.reasons.filter((r) => r.ok === false).length === 3, '「X 错」应判为错项');
  assert.strictEqual(p.reasons.filter((r) => r.ok === true)[0].letter, 'C');
});

test('render.splitExplanation 识别「X 正确 / X 成立」为对项', () => {
  const { render } = setup();
  const p = render.splitExplanation('**答案依据**：A 成立。\nB 错：漏条件。');
  assert.strictEqual(p.reasons.length, 2);
  assert.strictEqual(p.reasons[0].ok, true);
  assert.strictEqual(p.reasons[1].ok, false);
});

test('render.splitExplanation 无「答案依据」段时回退取首段', () => {
  const { render } = setup();
  const p = render.splitExplanation('先化简再求导。\nA 错：求导顺序不对。');
  assert.ok(p.basis.indexOf('先化简') >= 0);
  assert.strictEqual(p.reasons.length, 1);
});

test('render.splitExplanation 空解析不报错', () => {
  const { render } = setup();
  const p = render.splitExplanation('');
  assert.strictEqual(p.basis, '');
  assert.strictEqual(p.reasons.length, 0);
});

test('render.mdLite 转义 HTML 并保留粗体', () => {
  const { render } = setup();
  const html = render.mdLite('**答案依据**：$x<1$ & "y"');
  assert.ok(html.indexOf('<strong>答案依据</strong>') >= 0);
  assert.ok(html.indexOf('&lt;') >= 0, '裸 < 必须转义');
  assert.ok(html.indexOf('&amp;') >= 0);
  assert.ok(html.indexOf('&quot;') >= 0);
});

test('render.mdLite 不把用户内容当成标签注入', () => {
  const { render } = setup();
  const html = render.mdLite('<img src=x onerror=alert(1)>');
  assert.ok(html.indexOf('<img') < 0, '不得保留裸标签');
  assert.ok(html.indexOf('&lt;img') >= 0);
});

test('dom.esc 转义 5 个危险字符', () => {
  const { dom } = setup();
  assert.strictEqual(dom.esc('<>&"\''), '&lt;&gt;&amp;&quot;&#39;');
});

test('dom.fmtTime 分钟与小时格式', () => {
  const { dom } = setup();
  assert.strictEqual(dom.fmtTime(0), '00:00');
  assert.strictEqual(dom.fmtTime(65000), '01:05');
  assert.strictEqual(dom.fmtTime(3725000), '1:02:05');
});

test('dom.pct 防除零', () => {
  const { dom } = setup();
  assert.strictEqual(dom.pct(1, 0), 0);
  assert.strictEqual(dom.pct(1, 3), 33.3);
});

test('keys.isTyping 识别输入框与文本域', () => {
  const { keys } = setup();
  assert.strictEqual(keys.isTyping({ target: { tagName: 'INPUT' } }), true);
  assert.strictEqual(keys.isTyping({ target: { tagName: 'TEXTAREA' } }), true);
  assert.strictEqual(keys.isTyping({ target: { tagName: 'SELECT' } }), true);
  assert.strictEqual(keys.isTyping({ target: { tagName: 'DIV', isContentEditable: true } }), true);
  assert.strictEqual(keys.isTyping({ target: { tagName: 'DIV' } }), false);
});

/* ---------------- keys.resolve（键位映射）---------------- */

test('keys.resolve 裸 A–D / 1–4 选选项', () => {
  const { keys } = setup();
  assert.strictEqual(keys.resolve({ key: 'a' }), 'pick:a');
  assert.strictEqual(keys.resolve({ key: 'b' }), 'pick:b');
  assert.strictEqual(keys.resolve({ key: 'c' }), 'pick:c');
  assert.strictEqual(keys.resolve({ key: 'd' }), 'pick:d');
  assert.strictEqual(keys.resolve({ key: '1' }), 'pick:a');
  assert.strictEqual(keys.resolve({ key: '4' }), 'pick:d');
});

test('keys.resolve Shift+B/C/D 打开面板（与选项字母不冲突）', () => {
  // 回归：原方案里裸 B/C/D 既想选选项又想做面板动作，
  // 结果三个面板快捷键**永远打不开**（'abcd' 判断在前，全被当成选项）。
  const { keys } = setup();
  assert.strictEqual(keys.resolve({ key: 'B', shiftKey: true }), 'wrongbook');
  assert.strictEqual(keys.resolve({ key: 'C', shiftKey: true }), 'card');
  assert.strictEqual(keys.resolve({ key: 'D', shiftKey: true }), 'theme');
  // 裸字母仍然是选项
  assert.strictEqual(keys.resolve({ key: 'b' }), 'pick:b');
  assert.strictEqual(keys.resolve({ key: 'c' }), 'pick:c');
  assert.strictEqual(keys.resolve({ key: 'd' }), 'pick:d');
});

test('keys.resolve 其余快捷键', () => {
  const { keys } = setup();
  assert.strictEqual(keys.resolve({ key: 'ArrowLeft' }), 'prev');
  assert.strictEqual(keys.resolve({ key: 'ArrowRight' }), 'next');
  assert.strictEqual(keys.resolve({ key: 'k' }), 'prev');
  assert.strictEqual(keys.resolve({ key: 'j' }), 'next');
  assert.strictEqual(keys.resolve({ key: ' ' }), 'next');
  assert.strictEqual(keys.resolve({ key: 'Enter' }), 'submit');
  assert.strictEqual(keys.resolve({ key: 'Escape' }), 'escape');
  assert.strictEqual(keys.resolve({ key: '?' }), 'help');
  assert.strictEqual(keys.resolve({ key: '/' , shiftKey: true }), 'help');
  assert.strictEqual(keys.resolve({ key: 'f' }), 'fav');
  assert.strictEqual(keys.resolve({ key: 'w' }), 'wrong');
  assert.strictEqual(keys.resolve({ key: 's' }), 'stats');
  assert.strictEqual(keys.resolve({ key: 'x' }), null);
  assert.strictEqual(keys.resolve({ key: 'Shift' }), null);
});

/* ---------------- render.explainBlocks（渲染层内容覆盖）---------------- */

test('render.explainBlocks：整篇解析只有「依据 + 错因」时依据仍要渲染出来', () => {
  const { render } = setup();
  // 这正是 856 题里 103 题的形态：没有「其它段落」，依据曾被整段丢弃
  const expl = [
    '**答案依据**：定义域由两个约束联立，故 C 正确。',
    'A 错：只保留了 $|x|\\le 1$ 这一段。',
    'B 错：漏掉了挖去 $x=2$。'
  ].join('\n');
  const blocks = render.explainBlocks(expl);
  const prose = blocks.find((b) => b.kind === 'prose');
  assert.ok(prose, '必须存在「答案依据与解析」渲染块');
  assert.ok(prose.basis && prose.basis.indexOf('两个约束联立') >= 0, '依据不能丢');
  const reasons = blocks.find((b) => b.kind === 'reasons');
  assert.ok(reasons && reasons.items.length === 3, '错因要照常渲染');
});

test('render.explainBlocks：依据 + 其它段落 + 错因 混排时三段都在', () => {
  const { render } = setup();
  const expl = [
    '**答案依据**：代入得 $f(x)=x^2$。',
    '先化简再求导。',
    'A 错：求导顺序不对。'
  ].join('\n');
  const blocks = render.explainBlocks(expl);
  const prose = blocks.find((b) => b.kind === 'prose');
  assert.ok(prose.basis.indexOf('x^2') >= 0, '依据在');
  assert.ok(prose.items.join('\n').indexOf('先化简') >= 0, '其它段落在');
  assert.ok(blocks.find((b) => b.kind === 'reasons').items.length === 1);
});

test('render.explainBlocks：没有显式依据段时回退取首段，且首段不重复渲染', () => {
  const { render } = setup();
  const blocks = render.explainBlocks('先化简再求导。\nA 错：求导顺序不对。');
  const prose = blocks.find((b) => b.kind === 'prose');
  assert.ok(prose, '有其它段落时仍应有 prose 块');
  assert.strictEqual(prose.basis, '先化简再求导。', '首段回退为依据');
  assert.strictEqual(prose.items.length, 0, '首段已被摘为依据，不应再渲染一遍');
});
