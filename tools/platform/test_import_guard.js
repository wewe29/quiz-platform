'use strict';
/* 导入守卫 + 错题本计数的**行为**门禁（2026-11-22）。
 *
 * 用法：node tools/platform/test_import_guard.js <app.js 路径>
 *
 * 【为什么必须是行为测试】
 * 浏览器实答抓到的两个缺陷都发生在**运行期**：
 *   ① 跨学科进度文件被静默合并（只校验 kind/version/state.v/checksum，
 *      从不校验文件里明写着的 subject/bankId）——2026-11-22 实测：导入
 *      一份 dataviz 的进度到 ml 子站，页面只提示「导入完成」，什么都没报；
 *   ② 错题本 badge 用 Object.keys(state.wrongBook).length，题库里不存在的
 *      题号也计数——实测「共 2 题」而列表只有 1 题。
 * grep 源码找某句话是「拿参数重放自己」：改个变量名就骗过去了。
 * 所以这里装载**真实的 app.js**，用**真的按钮**触发，断言**真的状态**。
 *
 * 反向测试（造错必须报错）在 tools/platform/test_check_import_guard.py。
 */
const fs = require('fs');
const path = require('path');
const H = require('./jsdom_lite.js');

const appFile = process.argv[2];
if (!appFile) {
  console.error('用法：node test_import_guard.js <app.js 路径>');
  process.exit(2);
}
if (!fs.existsSync(appFile)) {
  console.error('[FAIL] 找不到被测文件：' + appFile);
  process.exit(2);
}
const storeFile = path.join(path.dirname(appFile), 'core', 'store.js');

const SUBJECT = {
  id: 'ml',
  name: '机器学习',
  dataDir: 'data/',
  storageKey: 'quiz-ml-v2',
  legacyKeys: [],
  portalUrl: '../../',
  katex: 'assets/vendor/katex/'
};
const BANK_ID = 'ml-course-v1';

let failures = [];
let passes = 0;

function check(name, cond, detail) {
  if (cond) {
    passes++;
    console.log('  PASS  ' + name);
  } else {
    failures.push(name + (detail ? '：' + detail : ''));
    console.log('  FAIL  ' + name + (detail ? '：' + detail : ''));
  }
}

function boot(initialState) {
  const meta = H.defaultMeta({
    id: SUBJECT.id, name: SUBJECT.name, textbook: '测试教材',
    bankId: BANK_ID, chapters: 2, chapterLabels: { '1': '第1章', '2': '第2章' }
  });
  return H.createSandbox({
    subject: SUBJECT, meta: meta, questions: H.defaultQuestions(),
    storeFile: storeFile, appFile: appFile, initialState: initialState
  });
}

function applyButton(ctx) {
  return ctx.modal.__roleButtons.filter((b) => b.getAttribute('data-role') === 'data-apply')[0];
}

function toastText(ctx) {
  return ctx.doc.getElementById('toast').textContent || '';
}

function readState(ctx) {
  const raw = ctx.store.getItem(SUBJECT.storageKey);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
}

/* ---------- 用例 1：导出的文件必须带来源标识 ---------- */
function caseExportCarriesIdentity() {
  const ctx = boot();
  return H.settle().then(() => {
    ctx.doc.getElementById('btn-export').click();
    const raw = ctx.doc.getElementById('data-text').value;
    check('导出弹窗给出了内容', !!raw && raw.length > 0);
    let p = null;
    try { p = JSON.parse(raw); } catch (e) { /* 下面断言会报 */ }
    check('导出的内容是合法 JSON', !!p);
    if (!p) return;
    check('导出文件带 subject 标识（跨学科拒绝的依据）', p.subject === SUBJECT.id,
      '实际 ' + JSON.stringify(p.subject));
    check('导出文件带 bankId 标识（题库版本拒绝的依据）', p.bankId === BANK_ID,
      '实际 ' + JSON.stringify(p.bankId));
  });
}

/* ---------- 用例 2/3/4：来源不符一律拒绝，且一个字都不许写进去 ---------- */
function caseReject(kind, mutate) {
  const ctx = boot();
  return H.settle().then(() => {
    const payload = H.makePayload({
      subject: SUBJECT.id, bankId: BANK_ID,
      sessions: { 'sess-foreign': { id: 'sess-foreign', updatedAt: 9e15, answers: {} } },
      wrongBook: { 'q-foreign-001': { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' } }
    });
    mutate(payload);
    ctx.doc.getElementById('data-text').value = JSON.stringify(payload);

    const before = ctx.store.getItem(SUBJECT.storageKey);
    const wired = applyButton(ctx).dispatch('click');
    check('导入按钮确实接上了监听器（' + kind + '）', wired);
    const after = ctx.store.getItem(SUBJECT.storageKey);
    check('来源不符的进度文件被拒绝：状态一个字都没写（' + kind + '）', before === after,
      '写入前=' + String(before).slice(0, 80) + ' 写入后=' + String(after).slice(0, 80));
    check('来源不符的进度文件被拒绝：给出错误提示（' + kind + '）',
      /拒绝导入/.test(toastText(ctx)), '实际提示：' + toastText(ctx));
    const st = readState(ctx);
    const sessions = st ? Object.keys(st.sessions || {}) : [];
    const wrong = st ? Object.keys(st.wrongBook || {}) : [];
    check('来源不符的进度文件被拒绝：外来会话没进来（' + kind + '）',
      sessions.indexOf('sess-foreign') < 0, '实际会话：' + sessions.join(','));
    check('来源不符的进度文件被拒绝：外来题号没进错题本（' + kind + '）',
      wrong.indexOf('q-foreign-001') < 0, '实际错题：' + wrong.join(','));
  });
}

/* ---------- 用例 5：同源文件必须能导入（不能把功能改死） ---------- */
function caseAcceptSameSubject() {
  const ctx = boot();
  return H.settle().then(() => {
    const payload = H.makePayload({
      subject: SUBJECT.id, bankId: BANK_ID,
      sessions: { 'sess-ok': { id: 'sess-ok', updatedAt: 9e15, answers: {} } },
      wrongBook: { q1: { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 2, resolved: false, note: '' } }
    });
    ctx.doc.getElementById('data-text').value = JSON.stringify(payload);
    applyButton(ctx).dispatch('click');
    const st = readState(ctx);
    check('同学科同题库的文件能导入（会话并入）',
      !!st && Object.keys(st.sessions || {}).indexOf('sess-ok') >= 0,
      '实际会话：' + (st ? Object.keys(st.sessions || {}).join(',') : '(无状态)'));
    check('同学科同题库的文件能导入（错题并入）',
      !!st && Object.keys(st.wrongBook || {}).indexOf('q1') >= 0,
      '实际错题：' + (st ? Object.keys(st.wrongBook || {}).join(',') : '(无状态)'));
    check('导入成功给出成功提示', /导入完成/.test(toastText(ctx)), '实际提示：' + toastText(ctx));
  });
}

/* ---------- 用例 6：同源文件里的失效题号不进错题本 ---------- */
function caseSkipUnknownQid() {
  const ctx = boot();
  return H.settle().then(() => {
    const payload = H.makePayload({
      subject: SUBJECT.id, bankId: BANK_ID,
      sessions: {},
      wrongBook: {
        q1: { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' },
        'q-not-in-bank': { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' }
      }
    });
    ctx.doc.getElementById('data-text').value = JSON.stringify(payload);
    applyButton(ctx).dispatch('click');
    const st = readState(ctx);
    const wrong = st ? Object.keys(st.wrongBook || {}) : [];
    check('导入同源文件：真实题号进来了', wrong.indexOf('q1') >= 0, '实际错题：' + wrong.join(','));
    check('导入同源文件：题库里没有的题号被忽略', wrong.indexOf('q-not-in-bank') < 0,
      '实际错题：' + wrong.join(','));
    check('导入同源文件：提示里说明了忽略了几条', /忽略\s*1\s*条/.test(toastText(ctx)),
      '实际提示：' + toastText(ctx));
  });
}

/* ---------- 用例 7：错题本 badge 不得说谎（历史遗留的失效题号） ---------- */
function caseWrongBookCountHonest() {
  const initial = {
    v: 1, bank: BANK_ID, updatedAt: 0,
    sessions: {},
    wrongBook: {
      q1: { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' },
      'q-ghost-001': { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' }
    },
    stats: {},
    settings: {}
  };
  const ctx = boot(initial);
  return H.settle().then(() => {
    ctx.doc.getElementById('panel-wrong').hidden = true;
    ctx.doc.getElementById('btn-wrong').click();
    const badge = ctx.doc.getElementById('wrong-count').textContent || '';
    const list = ctx.doc.getElementById('wrong-list').innerHTML || '';
    const n = (list.match(/class="wrong-item/g) || []).length;
    check('错题本 badge 只算题库里真实存在的题号', badge === '共 1 题', '实际：' + badge);
    check('错题本 badge 数字与列表条数一致', badge === '共 ' + n + ' 题',
      'badge=' + badge + '，列表条数=' + n);
    check('错题本列表确实渲染出了那 1 题', n === 1, '列表条数=' + n);
  });
}

/* ---------- 用例 8：导出里的错题计数也不该说谎 ---------- */
function caseExportCountHonest() {
  const initial = {
    v: 1, bank: BANK_ID, updatedAt: 0,
    sessions: {},
    wrongBook: {
      q1: { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' },
      'q-ghost-001': { firstWrongAt: 1, lastWrongAt: 2, wrongCount: 1, resolved: false, note: '' }
    },
    stats: {},
    settings: {}
  };
  const ctx = boot(initial);
  return H.settle().then(() => {
    ctx.doc.getElementById('btn-export').click();
    let p = null;
    try { p = JSON.parse(ctx.doc.getElementById('data-text').value); } catch (e) { /* 下面断言会报 */ }
    check('导出内容是合法 JSON', !!p);
    if (!p) return;
    check('导出里的错题计数不含失效题号', p.stats && p.stats.wrongBook === 1,
      '实际：' + JSON.stringify(p.stats));
  });
}

/* ---------- 主流程 ---------- */
const cases = [
  ['导出的文件必须带来源标识', caseExportCarriesIdentity],
  ['跨学科文件必须被拒绝', () => caseReject('跨学科', (p) => { p.subject = 'dataviz'; })],
  ['题库版本不符的文件必须被拒绝', () => caseReject('题库版本', (p) => { p.bankId = 'dataviz-v1'; })],
  ['缺来源标识的文件必须被拒绝', () => caseReject('缺标识', (p) => { delete p.subject; delete p.bankId; })],
  ['同学科同题库的文件必须能导入', caseAcceptSameSubject],
  ['同源文件里的失效题号不得进错题本', caseSkipUnknownQid],
  ['错题本 badge 不得说谎', caseWrongBookCountHonest],
  ['导出里的错题计数不得说谎', caseExportCountHonest]
];

(async function main() {
  console.log('[import-guard] 被测文件：' + appFile);
  for (const [name, fn] of cases) {
    console.log('· ' + name);
    try {
      await fn();
    } catch (e) {
      failures.push(name + '：用例抛异常 ' + (e && e.message ? e.message : e));
      console.log('  FAIL  ' + name + '：用例抛异常 ' + (e && e.stack ? e.stack : e));
    }
  }
  console.log('');
  if (failures.length) {
    console.log('[FAIL] ' + failures.length + ' 项断言不通过（共 ' + (passes + failures.length) + ' 项）：');
    failures.forEach((f) => console.log('  - ' + f));
    process.exit(1);
  }
  console.log('[OK ] ' + passes + ' 项断言全部通过（真实 app.js 行为）');
  process.exit(0);
})();
