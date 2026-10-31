/* tests/harness.js — 在 Node 里加载浏览器端的 core/ ui/ 模块
   core/ 与 ui/ 是 IIFE，挂到 window.QX 上。Node 里把 window 指向 global 即可复用。 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const JS_DIR = path.join(__dirname, '..', 'assets', 'js');
const CORE = ['bus.js', 'store.js', 'judge.js', 'schema.js', 'bank.js', 'session.js', 'stats.js', 'picked.js'];
const UI = ['dom.js', 'theme.js', 'render.js', 'hud.js', 'filters.js', 'card.js', 'drawer.js', 'keys.js'];
const CORE_DIR = ['core'];
const UI_DIR = ['ui'];

class MemoryStorage {
  constructor() { this.m = new Map(); this.fail = false; }
  getItem(k) { if (this.fail) throw new Error('storage unavailable'); return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { if (this.fail) throw new Error('storage unavailable'); this.m.set(k, String(v)); }
  removeItem(k) { this.m.delete(k); }
  clear() { this.m.clear(); }
}

function load(pairs) {
  global.window = global;
  global.QX = undefined;
  global.localStorage = new MemoryStorage();
  for (const p of pairs) {
    const file = path.join(JS_DIR, p);
    vm.runInThisContext(fs.readFileSync(file, 'utf8'), { filename: file });
  }
  return global.QX;
}

function loadCore() {
  return load(CORE.map((f) => path.join('core', f)));
}
function loadCoreAndUi() {
  return load(CORE.map((f) => path.join('core', f)).concat(UI.map((f) => path.join('ui', f))));
}

/** 一道最小可用的题目 */
function mkQ(over) {
  const q = Object.assign({
    id: 't-001',
    type: 'single',
    typeGroup: 'single',
    difficulty: 'basic',
    chapter: 1,
    knowledgePoint: '1.1',
    knowledgePoints: ['1.1'],
    source: { text: '同济《高等数学》第七版 §1.1', kind: 'textbook', year: null, region: null, paper: null, number: null, url: null },
    provenance: { level: null, url: null, verifiedAt: null, note: '' },
    stem: '题干 $x$',
    options: ['A 项', 'B 项', 'C 项', 'D 项'],
    answer: ['B'],
    accept: null,
    answerText: null,
    points: null,
    explanation: '**答案依据**：B。',
    misconception: null,
    extension: null,
    tags: [],
    verify: []
  }, over || {});
  return q;
}

module.exports = { loadCore, loadCoreAndUi, mkQ, MemoryStorage, CORE, UI };
