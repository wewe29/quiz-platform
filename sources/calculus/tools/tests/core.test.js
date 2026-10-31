/* tests/core.test.js — core/ 层单测（node --test） */
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const H = require('./harness.js');

/* ---------------- judge ---------------- */

test('judge.fullScore 按题型给分', () => {
  const { judge } = H.loadCore();
  assert.strictEqual(judge.fullScore({ type: 'single' }), 2);
  assert.strictEqual(judge.fullScore({ type: 'multi' }), 3);
  assert.strictEqual(judge.fullScore({ type: 'judge' }), 2);
  assert.strictEqual(judge.fullScore({ type: 'blank' }), 2);
  assert.strictEqual(judge.fullScore({ type: 'term' }), 4);
  assert.strictEqual(judge.fullScore({ type: 'short' }), 6);
  assert.strictEqual(judge.fullScore({ type: 'calc' }), 8);
});

test('judge.multiVerdict：全对/少选/错选/未选 四种判定', () => {
  const { judge } = H.loadCore();
  const ans = ['A', 'C'];
  assert.strictEqual(judge.multiVerdict(['A', 'C'], ans), 'correct');
  assert.strictEqual(judge.multiVerdict(['C', 'A'], ans), 'correct');  // 顺序无关
  assert.strictEqual(judge.multiVerdict(['A'], ans), 'partial');      // 少选
  assert.strictEqual(judge.multiVerdict(['A', 'B'], ans), 'wrong');   // 错选
  assert.strictEqual(judge.multiVerdict([], ans), 'blank');
});

test('judge.blankMatch 支持数值等价（3/2 ≡ 1.5）', () => {
  const { judge } = H.loadCore();
  const q = { type: 'blank', answer: ['3/2'], accept: null };
  assert.strictEqual(judge.blankMatch('3/2', q), true);
  assert.strictEqual(judge.blankMatch('1.5', q), true);
  assert.strictEqual(judge.blankMatch(' 1.5 ', q), true);
  assert.strictEqual(judge.blankMatch('2/3', q), false);
  assert.strictEqual(judge.blankMatch('', q), false);
});

test('judge.blankMatch 接受 accept 列表', () => {
  const { judge } = H.loadCore();
  const q = { type: 'blank', answer: ['x'], accept: ['X', 'variable'] };
  assert.strictEqual(judge.blankMatch('variable', q), true);
  assert.strictEqual(judge.blankMatch('y', q), false);
});

test('judge.norm 归一化全角与空白', () => {
  const { judge } = H.loadCore();
  assert.strictEqual(judge.norm('  ＡＢ　 '), 'ab');
  assert.strictEqual(judge.norm('x＝1'), 'x=1');
  assert.strictEqual(judge.norm('1，2'), '1,2');
});

test('judge.judgeObjective 客观题判分', () => {
  const { judge } = H.loadCore();
  const s = { type: 'single', answer: ['C'] };
  assert.deepStrictEqual(judge.judgeObjective(s, ['C']), { correct: true, earned: 2, full: 2 });
  assert.deepStrictEqual(judge.judgeObjective(s, ['A']), { correct: false, earned: 0, full: 2 });
  const m = { type: 'multi', answer: ['A', 'C'] };
  assert.strictEqual(judge.judgeObjective(m, ['A', 'C']).earned, 3);
  assert.strictEqual(judge.judgeObjective(m, ['A']).earned, 0);     // 少选 0 分
  assert.strictEqual(judge.judgeObjective(m, ['A', 'B']).earned, 0); // 错选 0 分
});

/* ---------------- store ---------------- */

test('store.load 返回空状态；save/load 往返一致', () => {
  const { store } = H.loadCore();
  const st = store.load('test-bank');
  assert.strictEqual(st.bank, 'test-bank');
  assert.strictEqual(st.v, 2);
  store.set((s) => { s.settings.theme = 'dark'; s.favorites['x-1'] = { at: 1 }; });
  store.flush();
  const st2 = store.load('test-bank');
  assert.strictEqual(st2.settings.theme, 'dark');
  assert.ok(st2.favorites['x-1']);
});

test('store 存储不可用时降级为内存态，不抛异常', () => {
  const { store } = H.loadCore();
  store.load('b');
  global.localStorage.fail = true;
  const ok = store.save();
  assert.strictEqual(ok, false);
  assert.strictEqual(store.isStorageOk(), false);
  global.localStorage.fail = false;
});

test('store 版本不匹配时保留旧串，不覆盖用户历史', () => {
  const { store } = H.loadCore();
  global.localStorage.setItem('hx_quiz_v2', JSON.stringify({ v: 1, favorites: { 'q-1': { at: 5 } } }));
  const st = store.load('b');
  assert.strictEqual(st.v, 2);
  assert.ok(global.localStorage.getItem('hx_quiz_v2-legacy-1'));
});

test('store.saveMerged 合并多标签页的错题本与收藏', () => {
  const { store } = H.loadCore();
  const st = store.load('b');
  store.flush();
  // 模拟另一个标签页写入更新的状态
  const other = JSON.parse(global.localStorage.getItem('hx_quiz_v2'));
  other.updatedAt = st.updatedAt + 1000;
  other.wrongBook = { 'q-9': { wrongCount: 3, resolved: false, lastWrongAt: 9, firstWrongAt: 1 } };
  other.favorites = { 'q-8': { at: 3 } };
  global.localStorage.setItem('hx_quiz_v2', JSON.stringify(other));
  store.saveMerged();
  const after = store.get();
  assert.ok(after.wrongBook['q-9']);
  assert.strictEqual(after.wrongBook['q-9'].wrongCount, 3);
  assert.ok(after.favorites['q-8']);
});

/* ---------------- schema ---------------- */

test('schema.validate 拦截缺字段 / 非法答案 / 缺解析', () => {
  const { schema } = H.loadCore();
  const good = H.mkQ();
  assert.strictEqual(schema.validate(good, ['1.1']).ok, true);
  assert.strictEqual(schema.validate(H.mkQ({ stem: '' }), ['1.1']).ok, false);
  assert.strictEqual(schema.validate(H.mkQ({ answer: ['E'] }), ['1.1']).ok, false);
  assert.strictEqual(schema.validate(H.mkQ({ explanation: '' }), ['1.1']).ok, false);
  assert.strictEqual(schema.validate(H.mkQ({ type: 'multi', answer: ['A'] }), ['1.1']).ok, false);
  assert.strictEqual(schema.validate(H.mkQ({ knowledgePoint: '9.9' }), ['1.1']).ok, false);
});

test('schema.validate 对真题强制来源链接与改编标记', () => {
  const { schema } = H.loadCore();
  const orig = H.mkQ({
    source: { text: '2024 考研数学一 第 12 题', kind: 'exam-original', year: 2024, region: '全国', paper: '数学一', number: 12, url: '' }
  });
  assert.strictEqual(schema.validate(orig, ['1.1']).ok, false, '缺 url 应不通过');
  orig.source.url = 'https://example.com/a';
  orig.provenance = { level: 'original', url: 'https://example.com/a', note: '', verifiedAt: null };
  assert.strictEqual(schema.validate(orig, ['1.1']).ok, true);

  const ad = H.mkQ({
    source: { text: '2024 考研数学一 第 12 题（改编）', kind: 'exam-adapted', year: 2024, region: '全国', paper: '数学一', number: 12, url: null },
    provenance: { level: 'adapted', url: null, note: '改编自第 12 题', verifiedAt: null },
    tags: []
  });
  assert.strictEqual(schema.validate(ad, ['1.1']).ok, false, '改编题缺「真题改编」标记应不通过');
  ad.tags = ['真题改编'];
  assert.strictEqual(schema.validate(ad, ['1.1']).ok, true);
});

test('schema.normalize 补默认字段', () => {
  const { schema } = H.loadCore();
  const n = schema.normalize({ id: 'x', type: 'single' });
  assert.deepStrictEqual(n.knowledgePoints, []);
  assert.deepStrictEqual(n.options, []);
  assert.deepStrictEqual(n.answer, []);
  assert.deepStrictEqual(n.tags, []);
});

/* ---------------- session ---------------- */

function setupSession(questions, opts) {
  const QX = H.loadCore();
  const o = opts || {};
  QX.store.load('b');
  QX.session.init({
    store: QX.store, bus: QX.bus, judge: QX.judge,
    catalog: o.catalog || {
      chapters: [], secKeys: ['1.1'],
      typeGroups: [{ key: 'single', label: '单选', rank: 0 }, { key: 'multi', label: '多选', rank: 1 }],
      diffs: [{ key: 'basic', label: '基础', rank: 0 }, { key: 'hard', label: '困难', rank: 2 }],
      kinds: ['textbook', 'exam-original']
    }
  });
  QX.stats.init({ store: QX.store, session: QX.session });
  QX.session.setQuestions(questions);
  QX.session.ensureSession();
  QX.session.refreshOrder();
  return QX;
}

test('session.passes 按类型 / 难度 / 章节 / 知识点 / 出处类型筛选', () => {
  const q1 = H.mkQ({ id: 'a', type: 'single', difficulty: 'basic', chapter: 1, knowledgePoint: '1.1' });
  const q2 = H.mkQ({ id: 'b', type: 'multi', typeGroup: 'multi', difficulty: 'hard', chapter: 2, knowledgePoint: '1.1',
    source: { text: 'x', kind: 'exam-original', year: 2024, region: '全国', paper: '数学一', number: 1, url: 'u' } });
  const { session } = setupSession([q1, q2]);
  const f = session.blankFilter(false);
  assert.strictEqual(session.passes(q1, f), true);
  f.types = ['multi'];
  assert.strictEqual(session.passes(q1, f), false);
  assert.strictEqual(session.passes(q2, f), true);
  f.types = []; f.diffs = ['hard'];
  assert.strictEqual(session.passes(q1, f), false);
  f.diffs = []; f.chapters = ['1'];
  assert.strictEqual(session.passes(q1, f), true, '选第 1 章必须能选出第 1 章的题');
  assert.strictEqual(session.passes(q2, f), false);
  f.chapters = []; f.kinds = ['exam-original'];
  assert.strictEqual(session.passes(q1, f), false);
  assert.strictEqual(session.passes(q2, f), true);
  f.kinds = []; f.knowledgePoints = ['1.1'];
  assert.strictEqual(session.passes(q1, f), true);
});

test('session.passes 章节筛选：chip 的字符串 key 必须能选出对应章节的题', () => {
  // 回归：真实踩过（用户实机发现「函数与极限(154)」点下去命中 0 题）——
  // chip 存的是字符串 "1"，题目里 chapter 是数字 1，
  // passes 用 indexOf(q.chapter) 比 → 任何章节都命中 0 题，界面却写着 154。
  // 老用例只断言了「排除别章」（有 bug / 无 bug 都通过），从没断言「选中本章」，
  // 所以这个洞从单测里漏了过去 —— 这里把正例补上。
  const q1 = H.mkQ({ id: 'a', chapter: 1 });
  const q2 = H.mkQ({ id: 'b', chapter: 2 });
  const { session } = setupSession([q1, q2]);
  const f = session.blankFilter(false);
  f.chapters = ['1'];                 // 界面上 chip 产出的 key 就是字符串
  assert.strictEqual(session.passes(q1, f), true, '选第 1 章必须能选出第 1 章的题');
  assert.strictEqual(session.passes(q2, f), false);
  f.chapters = ['2'];
  assert.strictEqual(session.passes(q2, f), true);
  assert.strictEqual(session.passes(q1, f), false);
  f.chapters = ['1', '2'];
  assert.strictEqual(session.passes(q1, f), true);
  assert.strictEqual(session.passes(q2, f), true);
  f.chapters = [1];                   // 旧存档里可能是数字，也必须能匹配
  assert.strictEqual(session.passes(q1, f), true, '数字 key 也要能匹配');
});

test('session.passes 支持只看错题 / 收藏 / 关键词', () => {
  const q1 = H.mkQ({ id: 'a' });
  const { session, store } = setupSession([q1]);
  const f = session.blankFilter(false);
  f.onlyWrong = true;
  assert.strictEqual(session.passes(q1, f), false);
  store.get().wrongBook['a'] = { wrongCount: 1, resolved: false, lastWrongAt: 1, firstWrongAt: 1 };
  assert.strictEqual(session.passes(q1, f), true);
  f.onlyWrong = false; f.onlyFavorite = true;
  assert.strictEqual(session.passes(q1, f), false);
  store.get().favorites['a'] = { at: 1 };
  assert.strictEqual(session.passes(q1, f), true);
  f.onlyFavorite = false; f.kw = '题干';
  assert.strictEqual(session.passes(q1, f), true);
  f.kw = '不存在的词';
  assert.strictEqual(session.passes(q1, f), false);
});

test('session.computeOrder 按难度降序（默认）', () => {
  const q1 = H.mkQ({ id: 'easy', difficulty: 'basic', chapter: 1 });
  const q2 = H.mkQ({ id: 'hard', difficulty: 'hard', chapter: 1 });
  const q3 = H.mkQ({ id: 'mid', difficulty: 'medium', chapter: 2 });
  const { session } = setupSession([q1, q2, q3]);
  const order = session.computeOrder();
  assert.deepStrictEqual(order.slice(0, 3).sort(), ['easy', 'hard', 'mid']);
  assert.strictEqual(order[0], 'hard', '默认 difficulty_desc，困难应在前');
});

test('session.orderIsStale 在题库换题后为真', () => {
  const q1 = H.mkQ({ id: 'a' });
  const { session } = setupSession([q1]);
  assert.strictEqual(session.orderIsStale(), false);
  session.setQuestions([H.mkQ({ id: 'b' })]);
  assert.strictEqual(session.orderIsStale(), true);
});

test('session.nextUnanswered 末题后循环到第一道未作答', () => {
  const qs = [H.mkQ({ id: 'a' }), H.mkQ({ id: 'b' }), H.mkQ({ id: 'c' })];
  const { session } = setupSession(qs);
  session.recordAnswer(qs[0], { value: ['B'], correct: true, earned: 2, full: 2 });
  session.recordAnswer(qs[1], { value: ['B'], correct: true, earned: 2, full: 2 });
  session.gotoIdx(2);
  session.nextUnanswered();
  assert.strictEqual(session.current().id, 'c');
  session.recordAnswer(qs[2], { value: ['B'], correct: true, earned: 2, full: 2 });
  session.gotoIdx(2);
  session.nextUnanswered();
  assert.strictEqual(session.current().id, 'a', '全答完后回到第一题');
});

test('session.recordAnswer 答错进错题本，答对后标记 resolved', () => {
  const q = H.mkQ({ id: 'a' });
  const { session, store } = setupSession([q]);
  session.recordAnswer(q, { value: ['A'], correct: false, earned: 0, full: 2 });
  assert.ok(store.get().wrongBook['a']);
  assert.strictEqual(store.get().wrongBook['a'].resolved, false);
  session.recordAnswer(q, { value: ['B'], correct: true, earned: 2, full: 2 });
  assert.strictEqual(store.get().wrongBook['a'].resolved, true);
  assert.strictEqual(store.get().wrongBook['a'].wrongCount, 1, '答对不应增加错误次数');
});

test('session.revealSubjective 展开解析但不判错、不进错题本', () => {
  const q = H.mkQ({ id: 's', type: 'calc', answerText: '答案', points: [{ text: 'p1', partial: 2 }, { text: 'p2', partial: 2 }] });
  const { session, store } = setupSession([q]);
  session.revealSubjective(q);
  const rec = session.raw.answers['s'];
  assert.ok(rec);
  assert.strictEqual(rec.earned, 0);
  assert.deepStrictEqual(rec.pointsHit, [null, null]);
  assert.strictEqual(store.get().wrongBook['s'], undefined, '未自评时不得进错题本');
});

test('session.setSelfGrade 按采分点计分并更新错题本', () => {
  const q = H.mkQ({ id: 's', type: 'calc', answerText: '答案', points: [{ text: 'p1', partial: 2 }, { text: 'p2', partial: 2 }] });
  const { session, store } = setupSession([q]);
  session.revealSubjective(q);
  session.setSelfGrade('s', [true, false]);
  const rec = session.raw.answers['s'];
  assert.strictEqual(rec.earned, 2);
  assert.strictEqual(rec.correct, false);
  assert.ok(store.get().wrongBook['s'], '自评有失分应进错题本');
  session.setSelfGrade('s', [true, true]);
  assert.strictEqual(session.raw.answers['s'].earned, 4);
  assert.strictEqual(session.raw.answers['s'].correct, true);
  assert.strictEqual(store.get().wrongBook['s'].resolved, true);
});

test('session.redo 清掉作答记录', () => {
  const q = H.mkQ({ id: 'a' });
  const { session } = setupSession([q]);
  session.recordAnswer(q, { value: ['B'], correct: true, earned: 2, full: 2 });
  assert.ok(session.raw.answers['a']);
  session.redo('a');
  assert.strictEqual(session.raw.answers['a'], undefined);
});

/* ---------------- stats ---------------- */

test('stats.recompute 按题型 / 难度 / 章节 / 知识点四维统计', () => {
  const q1 = H.mkQ({ id: 'a', type: 'single', typeGroup: 'single', difficulty: 'basic', chapter: 1, knowledgePoint: '1.1' });
  const q2 = H.mkQ({ id: 'b', type: 'single', typeGroup: 'single', difficulty: 'hard', chapter: 2, knowledgePoint: '1.1' });
  const { session, stats, store } = setupSession([q1, q2]);
  session.recordAnswer(q1, { value: ['B'], correct: true, earned: 2, full: 2 });
  session.recordAnswer(q2, { value: ['A'], correct: false, earned: 0, full: 2 });
  const st = stats.recompute();
  assert.strictEqual(st.totalAnswered, 2);
  assert.strictEqual(st.totalCorrect, 1);
  assert.strictEqual(st.byType.single.answered, 2);
  assert.strictEqual(st.byDifficulty.basic.answered, 1);
  assert.strictEqual(st.byChapter['1'].answered, 1);
  assert.strictEqual(st.byKnowledgePoint['1.1'].answered, 2);
  assert.strictEqual(st.objectiveAnswered, 2);
  assert.strictEqual(st.objectiveCorrect, 1);
  assert.strictEqual(store.get().stats.totalAnswered, 2);
});

test('stats.sessionMetrics 返回本次会话指标', () => {
  const q1 = H.mkQ({ id: 'a' });
  const q2 = H.mkQ({ id: 'b' });
  const { session, stats } = setupSession([q1, q2]);
  session.recordAnswer(q1, { value: ['B'], correct: true, earned: 2, full: 2 });
  const m = stats.sessionMetrics();
  assert.strictEqual(m.answered, 1);
  assert.strictEqual(m.total, 2);
  assert.strictEqual(m.earned, 2);
  assert.strictEqual(m.rate, 100, '得分率按已作答题计');
  assert.strictEqual(m.acc, 100);
});

/* ---------------- bus ---------------- */

test('bus 一个监听器抛错不影响其它监听器', () => {
  const { bus } = H.loadCore();
  let reached = false;
  bus.on('x', () => { throw new Error('boom'); });
  bus.on('x', () => { reached = true; });
  bus.emit('x', null);
  assert.strictEqual(reached, true);
});

test('bus.off 能退订', () => {
  const { bus } = H.loadCore();
  let n = 0;
  const off = bus.on('y', () => { n++; });
  bus.emit('y', null);
  off();
  bus.emit('y', null);
  assert.strictEqual(n, 1);
});

/* ---------------- picked（选择缓冲状态机）---------------- */
test('picked.sync 同一题重渲染**保留**已选项（回归：曾被重渲染抹掉）', () => {
  const { picked } = H.loadCore();
  const st = { qid: null, picked: [] };
  const q = H.mkQ({ id: 't-001' });
  picked.sync(st, q, {});
  st.picked = ['B'];                 // 用户点了 B
  picked.sync(st, q, {});            // 选完立刻重渲染
  assert.deepStrictEqual(st.picked, ['B'], '同题重渲染不能清空已选项');
});

test('picked.sync 切题时重置缓冲', () => {
  const { picked } = H.loadCore();
  const st = { qid: null, picked: [] };
  const q1 = H.mkQ({ id: 't-001' });
  const q2 = H.mkQ({ id: 't-002' });
  picked.sync(st, q1, {});
  st.picked = ['B'];
  picked.sync(st, q2, {});
  assert.deepStrictEqual(st.picked, [], '切到别的题必须清空');
});

test('picked.sync 切题时从作答记录回填已选项', () => {
  const { picked } = H.loadCore();
  const st = { qid: null, picked: [] };
  const q = H.mkQ({ id: 't-001' });
  const answers = { 't-001': { value: ['C'], correct: true, earned: 2, full: 2 } };
  picked.sync(st, q, answers);
  assert.deepStrictEqual(st.picked, ['C']);
});

test('picked.sync 填空题回填填空值，主观题不回填选项', () => {
  const { picked } = H.loadCore();
  const st = { qid: null, picked: [] };
  const blank = H.mkQ({ id: 't-blank', type: 'blank', answerText: '1/2' });
  const calc = H.mkQ({ id: 't-calc', type: 'calc' });
  const answers = {
    't-blank': { value: ['1/2'], correct: true, earned: 2, full: 2 },
    't-calc': { value: ['x'], selfGraded: true, earned: 2, full: 2 }
  };
  picked.sync(st, blank, answers);
  assert.deepStrictEqual(st.picked, ['1/2']);
  picked.sync(st, calc, answers);
  assert.deepStrictEqual(st.picked, [], '主观题不缓存选项');
});

test('picked.clear 清空已选项但保留当前题归属（重做本题）', () => {
  const { picked } = H.loadCore();
  const st = { qid: null, picked: [] };
  const q = H.mkQ({ id: 't-001' });
  picked.sync(st, q, {});
  st.picked = ['B'];
  picked.clear(st);
  assert.deepStrictEqual(st.picked, []);
  picked.sync(st, q, {});
  assert.deepStrictEqual(st.picked, [], '重做后不应从记录回填');
});

/* ---------------- bank（题库载入）---------------- */

test('bank.setCatalog 就地更新：提前持有引用的模块也能拿到新数据', () => {
  // 回归：filters 在 init() 时就拿到了 catalog 的引用（那时 index 还没加载完），
  // 若 setCatalog 整体换对象，filters 会永远握着空壳 → 五组筛选 chip 全不渲染。
  const { bank } = H.loadCore();
  const held = bank.getCatalog();
  assert.strictEqual(held.typeGroups.length, 0, '初始是空壳');
  bank.setCatalog({ chapters: [{ n: 1 }], typeGroups: [{ key: 'single', label: '单选' }], diffs: [] });
  assert.strictEqual(bank.getCatalog(), held, '必须保持同一对象引用');
  assert.strictEqual(held.typeGroups.length, 1, '提前持有的引用要能看到新数据');
});

test('bank 内联模式：setInline 后全程不碰 fetch（单文件包的命门）', async () => {
  // 回归：单文件包（离线双击即用）里 window.__BANK__ 已内联全部题库，
  // 但若不把它交给 bank，hasInline() 恒为 false → 误走 fetch('data/index.json')
  // → 离线时必然 404 → 页面只剩「题库载入失败」。这个测试锁住"内联模式零网络请求"。
  const { bank } = H.loadCore();
  let fetched = 0;
  const realFetch = global.fetch;
  global.fetch = function () { fetched++; return Promise.reject(new Error('单文件包不允许发起网络请求')); };

  try {
    assert.strictEqual(bank.hasInline(), false, '未 setInline 前不是内联模式');

    const q = H.mkQ({ id: 'inline-1', chapter: 3 });
    bank.setInline({
      id: 'inline-bank',
      title: '内联题库',
      questions: [q],
      catalog: { chapters: [{ n: 3, title: '第三章' }], typeGroups: [], diffs: [], knowledgePoints: [] },
      index: { bank: { id: 'inline-bank', title: '内联题库' }, total: 1, chapters: [{ n: 3 }], summary: {} }
    });

    assert.strictEqual(bank.hasInline(), true, 'setInline 后必须是内联模式');
    assert.strictEqual(bank.getCatalog().chapters.length, 1, '内联 catalog 必须被采纳');

    const idx = await bank.loadIndex();
    assert.strictEqual(idx.total, 1, 'loadIndex 在内联模式下直接返回内置索引');
    assert.strictEqual(bank.getCatalog().chapters.length, 1, 'loadIndex 后 catalog 仍在');
    const qs = await bank.loadAll();
    assert.strictEqual(qs.length, 1, 'loadAll 在内联模式下直接返回内联题目');
    assert.strictEqual(qs[0].id, 'inline-1');
    assert.strictEqual(fetched, 0, '内联模式绝不允许发起任何 fetch');
  } finally {
    global.fetch = realFetch;
  }
});
