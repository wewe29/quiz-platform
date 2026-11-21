'use strict';
/* 子站**运行期行为**门禁（2026-11-22 新增）。
 *
 * 用法：node tools/platform/test_app_behavior.js <app.js 路径>
 *
 * 【这个门禁在防什么】
 * 前六轮实答验的都是内容与渲染，**交互功能一次都没被点过** ——
 * 导出/导入、错题本、答题卡、统计面板、主题切换、组卷练习、分享，
 * 在门禁眼里根本不存在：内容门禁只看题库，字节门禁只看「线上 == HEAD 成品」，
 * **用户点下去会发生什么，从来没人管**。于是抓到三个真缺陷：
 *
 *   ① 跨学科进度文件被**静默合并**（只校验 kind/version/state.v/checksum，
 *      从不校验文件里明写着的 subject/bankId）；
 *   ② 错题本 badge 说谎（计数用未过滤的 Object.keys(state.wrongBook).length，
 *      题库里不存在的题号也计数 ⇒「共 2 题」而列表只有 1 题）；
 *   ③ 「用时」把关页面的时间也算进去（lastTick 存在 localStorage 里，
 *      页面一关就是几小时的空档 ⇒ 实际练了 5 分钟，线上显示 191:43:32）。
 *
 * 【为什么必须驱动真实代码】
 * 这三个都是**运行期行为**，不是源码里的一句话。grep 源码等于「拿参数重放自己」：
 * 把变量名一改就骗过去了。所以这里装载**真实的 app.js**，用**真的按钮**触发，
 * 断言**真的 localStorage 与页面文本**。
 *
 * 反向测试（造错必须报错）在 tools/platform/test_check_app_behavior.py。
 */
const fs = require('fs');
const path = require('path');
const H = require('./jsdom_lite.js');

const appFile = process.argv[2];
if (!appFile) {
  console.error('用法：node test_app_behavior.js <app.js 路径>');
  process.exit(2);
}
if (!fs.existsSync(appFile)) {
  console.error('[FAIL] 找不到被测文件：' + appFile);
  process.exit(2);
}
const src = fs.readFileSync(appFile, 'utf8');
const storeFile = path.join(path.dirname(appFile), 'core', 'store.js');

// 两种变体：平台子站（要 window.SUBJECT/LABank/LAStore）与单文件版（自带题库逻辑）
const isPlatform = /window\.LABank/.test(src);
const singleKey = /var KEY = '([^']+)'/.exec(src);
// 导出/导入进度是平台子站才有的功能（单文件版没有「导出进度/导入进度」入口）——
// 没有该功能的变体不跑这组用例，但必须**显式跳过**，不许静默当成通过。
const hasDataModal = /EXPORT_KIND/.test(src);

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
const STORAGE_KEY = isPlatform ? SUBJECT.storageKey : (singleKey ? singleKey[1] : null);

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
    storeFile: storeFile, appFile: appFile, initialState: initialState,
    storageKey: STORAGE_KEY,
    selfContained: !isPlatform,
    bank: { id: 'test-bank', questions: H.defaultQuestions() }
  });
}

function applyButton(ctx) {
  return ctx.modal.__roleButtons.filter((b) => b.getAttribute('data-role') === 'data-apply')[0];
}

function toastText(ctx) {
  return ctx.doc.getElementById('toast').textContent || '';
}

function readState(ctx) {
  const raw = ctx.store.getItem(STORAGE_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
}

/** "191:43:32" → 秒；"01:05" → 秒 */
function clockSeconds(t) {
  const parts = String(t || '').split(':').map(Number);
  if (!parts.length || parts.some((v) => !isFinite(v))) return NaN;
  return parts.reduce((acc, v, i) => acc + v * Math.pow(60, parts.length - 1 - i), 0);
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

    const before = ctx.store.getItem(STORAGE_KEY);
    const wired = applyButton(ctx).dispatch('click');
    check('导入按钮确实接上了监听器（' + kind + '）', wired);
    const after = ctx.store.getItem(STORAGE_KEY);
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

/* ---------- 用例 9：关掉页面的那段时间不许算进「用时」 ---------- */
function caseTimerIgnoresClosedTabGap() {
  const GAP = 8 * 24 * 3600 * 1000;      // 页面关了 8 天
  const initial = {
    v: 1, bank: BANK_ID, updatedAt: Date.now(),
    sessions: {
      's-gap': {
        id: 's-gap', startedAt: Date.now() - GAP, updatedAt: Date.now(),
        elapsedMs: 60000, lastTick: Date.now() - GAP, hidden: false,
        endedAt: null, filter: { types: [], diffs: [], chapters: [], onlyWrong: false, kw: '' },
        order: [], cursor: 0, status: 'active', answers: {}
      }
    },
    wrongBook: {}, stats: {}, settings: {}
  };
  const ctx = boot(initial);
  return H.settle()
    .then(() => new Promise((r) => setTimeout(r, 1600)))   // 等计时器跑一拍
    .then(() => {
      const m = ctx.doc.getElementById('m-time').textContent || '';
      const sec = clockSeconds(m);
      check('关掉页面的 8 天没有被算进「用时」', isFinite(sec) && sec <= 600,
        'HUD「用时」= ' + m + '（' + sec + ' 秒）');
      check('「用时」没有归零（种子里的 1 分钟还在）', isFinite(sec) && sec >= 60,
        'HUD「用时」= ' + m);
    });
}

/* ---------- 用例 10：重新打开页面时 hidden 标记必须按当前可见性重置 ---------- */
function caseTimerResetsHiddenFlag() {
  const initial = {
    v: 1, bank: BANK_ID, updatedAt: Date.now(),
    sessions: {
      's-hidden': {
        id: 's-hidden', startedAt: Date.now() - 60000, updatedAt: Date.now(),
        elapsedMs: 0, lastTick: Date.now() - 5000, hidden: true,
        endedAt: null, filter: { types: [], diffs: [], chapters: [], onlyWrong: false, kw: '' },
        order: [], cursor: 0, status: 'active', answers: {}
      }
    },
    wrongBook: {}, stats: {}, settings: {}
  };
  const ctx = boot(initial);
  return H.settle()
    .then(() => new Promise((r) => setTimeout(r, 1600)))
    .then(() => {
      const m = ctx.doc.getElementById('m-time').textContent || '';
      const sec = clockSeconds(m);
      check('上次关闭时标签在后台，重新打开后计时要恢复', isFinite(sec) && sec >= 1,
        'HUD「用时」= ' + m + '（' + sec + ' 秒）');
    });
}

/* ---------- 主流程 ---------- */
const DATA_CASES = [
  ['导出的文件必须带来源标识', caseExportCarriesIdentity],
  ['跨学科文件必须被拒绝', () => caseReject('跨学科', (p) => { p.subject = 'dataviz'; })],
  ['题库版本不符的文件必须被拒绝', () => caseReject('题库版本', (p) => { p.bankId = 'dataviz-v1'; })],
  ['缺来源标识的文件必须被拒绝', () => caseReject('缺标识', (p) => { delete p.subject; delete p.bankId; })],
  ['同学科同题库的文件必须能导入', caseAcceptSameSubject],
  ['同源文件里的失效题号不得进错题本', caseSkipUnknownQid],
  ['导出里的错题计数不得说谎', caseExportCountHonest]
];
const COMMON_CASES = [
  ['错题本 badge 不得说谎', caseWrongBookCountHonest],
  ['关掉页面的时间不得算进「用时」', caseTimerIgnoresClosedTabGap],
  ['重新打开页面时 hidden 标记必须重置', caseTimerResetsHiddenFlag]
];

(async function main() {
  console.log('[app-behavior] 被测文件：' + appFile +
    '（变体：' + (isPlatform ? '平台子站' : '单文件版') +
    '，存储键：' + STORAGE_KEY +
    '，导出/导入：' + (hasDataModal ? '有' : '无（该变体没有这个功能）') + '）');
  if (!hasDataModal) {
    DATA_CASES.forEach((c) => console.log('· [跳过] ' + c[0] + ' —— 该变体没有导出/导入进度功能'));
  }
  const cases = (hasDataModal ? DATA_CASES : []).concat(COMMON_CASES);
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
