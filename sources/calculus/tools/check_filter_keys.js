/* tools/check_filter_keys.js — 筛选键契约门禁
 *
 * 真实踩过（2026-10-28，用户实机发现）：
 *   章节 chip 上写着「函数与极限(154)」，点下去却显示「当前筛选命中 0 题」。
 *   根因：chip 的 key 是 String(c.n) = "1"（字符串），而题目里 chapter 是数字 1，
 *   session.passes 用 f.chapters.indexOf(q.chapter) 比 → ["1"].indexOf(1) === -1
 *   → 任何章节筛选都命中 0 题；而 chip 括号里的数字来自 tally（按 String 归一），所以是 154。
 *   也就是说：**计数的 key 空间和筛选的 key 空间不是同一个**，界面自相矛盾却不报错。
 *
 * 这道门禁逐个 chip 做两件事（用**真实的** session.passes 与 filters.chipKeys）：
 *   ① 选这个 chip 能不能选出题（必须 > 0）；
 *   ② 选出来的题数是否等于 chip 括号上写的数（必须完全相等）。
 * 任何一条不满足 ⇒ 失败。因为 key 由 UI 与门禁共用（filters.chipList/chipKeys），
 * 两边不会各自漂移。
 *
 * 用法：node tools/check_filter_keys.js < payload.json
 *   stdin = { "questions": [...], "catalog": {...} }
 */
'use strict';

const fs = require('fs');
const path = require('path');

const H = require(path.join(__dirname, 'tests', 'harness.js'));

function readStdin() {
  try {
    return fs.readFileSync(0, 'utf8');
  } catch (e) {
    return '';
  }
}

function main() {
  // 既支持 stdin，也支持 `node check_filter_keys.js <payload.json>`
  const arg = process.argv[2];
  let raw = '';
  if (arg) {
    raw = fs.readFileSync(arg, 'utf8');
  } else {
    raw = readStdin();
  }
  if (!raw || !raw.trim()) {
    console.error('[filter-keys] 没有收到 payload（stdin 应为 {questions, catalog} 的 JSON）');
    return 1;
  }
  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (e) {
    console.error('[filter-keys] payload 不是合法 JSON：' + e.message);
    return 1;
  }
  const questions = payload.questions || [];
  const catalog = payload.catalog || {};
  if (!questions.length) {
    console.error('[filter-keys] 题库为空');
    return 1;
  }

  const QX = H.loadCoreAndUi();
  QX.store.load('filter-keys-gate');
  QX.session.init({ store: QX.store, bus: QX.bus, judge: QX.judge, catalog: catalog });
  QX.session.setQuestions(questions);
  QX.filters.setCatalog(catalog);
  QX.filters.tally(questions);

  const DIMS = [
    { dim: 'types', field: 'types', counts: 'type' },
    { dim: 'diffs', field: 'diffs', counts: 'diff' },
    { dim: 'chapters', field: 'chapters', counts: 'chapter' },
    { dim: 'kinds', field: 'kinds', counts: 'kind' },
    { dim: 'knowledgePoints', field: 'knowledgePoints', counts: 'kp' }
  ];

  const problems = [];
  const empties = [];
  let checked = 0;

  for (const d of DIMS) {
    const keys = QX.filters.chipKeys(d.dim);
    if (!keys.length) {
      problems.push('维度 ' + d.dim + ' 没有任何 chip key');
      continue;
    }
    const visible = QX.filters.visibleChipList(d.dim).map((x) => x.key);
    for (const key of keys) {
      const f = {
        types: [], diffs: [], chapters: [], knowledgePoints: [], kinds: [],
        onlyWrong: false, onlyFavorite: false, kw: ''
      };
      f[d.field] = [key];
      let hit = 0;
      for (const q of questions) {
        if (QX.session.passes(q, f)) hit++;
      }
      const label = QX.filters.countOf(d.dim, key);
      checked++;

      // 不变式①：界面上的计数 == 实际能选出的题数
      if (hit !== label) {
        problems.push('维度 ' + d.dim + ' 的 chip "' + key + '" 界面上写 ' + label +
                      ' 题，实际选中 ' + hit + ' 题');
      }
      // 不变式②：0 题的项不得出现在界面上（点下去必然是空白页）
      if (label === 0) {
        empties.push(d.dim + ':' + key);
        if (visible.indexOf(key) >= 0) {
          problems.push('维度 ' + d.dim + ' 的 chip "' + key + '" 一题也没有，却仍然显示在界面上');
        }
      } else if (visible.indexOf(key) < 0) {
        problems.push('维度 ' + d.dim + ' 的 chip "' + key + '" 有 ' + label +
                      ' 题，却没有出现在界面上');
      }
    }
  }

  if (empties.length) {
    console.log('[filter-keys] 注：catalog 中有 ' + empties.length +
                ' 个项目在本库没有题目（已从界面隐藏）：' + empties.join(', '));
  }

  if (problems.length) {
    console.log('[filter-keys] 筛选键契约检查失败：');
    for (const p of problems.slice(0, 20)) console.log('  [FAIL] ' + p);
    if (problems.length > 20) console.log('  ... 共 ' + problems.length + ' 条');
    return 1;
  }
  console.log('[filter-keys] 筛选键契约检查通过：' + checked +
              ' 个 chip 全部「标注题数 == 实际选中题数」，且没有 0 题的死入口');
  return 0;
}

process.exit(main());
