'use strict';
/* jsdom_lite —— 够用的 DOM/Storage 垫片，让 Node 能**真的跑起来**学科子站的 app.js。
 *
 * 【为什么不用 jsdom、也不用手写静态检查】
 * 2026-11-22 浏览器实答抓到两个真缺陷：
 *   ① 跨学科进度文件被**静默合并**（只校验 kind/version/state.v/checksum，
 *      从不校验文件里明写着的 subject/bankId）；
 *   ② 错题本计数用 Object.keys(state.wrongBook).length，题库里不存在的
 *      题号也计数 ⇒ 页面显示「共 2 题」而列表只有 1 题。
 * 这两条都是**行为**，不是字符串。若门禁只 grep 源码里有没有某句话，
 * 那就是「拿参数重放自己」的自洽式校验——改个变量名就能骗过去。
 * 所以门禁必须驱动**真实的 app.js**：真装载、真点按钮、真读 localStorage。
 *
 * 垫片只实现 app.js 真正用到的那部分 DOM（查表 + 事件 + innerHTML 字符串），
 * 不追求规范完整性——它只是让被测代码跑到断言点。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

/* ---------- localStorage ---------- */
function MemoryStorage() {
  this._m = new Map();
}
MemoryStorage.prototype.getItem = function (k) {
  return this._m.has(String(k)) ? this._m.get(String(k)) : null;
};
MemoryStorage.prototype.setItem = function (k, v) { this._m.set(String(k), String(v)); };
MemoryStorage.prototype.removeItem = function (k) { this._m.delete(String(k)); };
MemoryStorage.prototype.key = function (i) { const a = Array.from(this._m.keys()); return i < a.length ? a[i] : null; };
MemoryStorage.prototype.clear = function () { this._m.clear(); };
Object.defineProperty(MemoryStorage.prototype, 'length', { get: function () { return this._m.size; } });

/* ---------- 元素 ---------- */
function makeClassList() {
  const set = new Set();
  return {
    add: function () { Array.prototype.forEach.call(arguments, (x) => set.add(x)); },
    remove: function () { Array.prototype.forEach.call(arguments, (x) => set.delete(x)); },
    toggle: function (x, force) {
      if (force === undefined) { if (set.has(x)) { set.delete(x); } else { set.add(x); } }
      else if (force) { set.add(x); } else { set.delete(x); }
    },
    contains: function (x) { return set.has(x); },
    _set: set
  };
}

class El {
  constructor(tag) {
    this.tagName = String(tag || 'div').toUpperCase();
    this.id = '';
    this.style = { setProperty: function () {}, removeProperty: function () {}, getPropertyValue: function () { return ''; } };
    this.dataset = {};
    this.classList = makeClassList();
    this.className = '';
    this.innerHTML = '';
    this.textContent = '';
    this.value = '';
    this.checked = false;
    this.hidden = false;
    this.disabled = false;
    this.type = '';
    this.href = '';
    this.download = '';
    this.attrs = {};
    this.children = [];
    this.__listeners = {};
    this.__dataRole = null;
    this.__roleButtons = null;
  }
  addEventListener(type, fn) {
    (this.__listeners[type] = this.__listeners[type] || []).push(fn);
  }
  removeEventListener(type, fn) {
    const a = this.__listeners[type];
    if (!a) return;
    const i = a.indexOf(fn);
    if (i >= 0) a.splice(i, 1);
  }
  /** 派发事件；返回是否真的有监听器被调用（用于断言「按钮确实接上了线」）。 */
  dispatch(type, ev) {
    const a = (this.__listeners[type] || []).slice();
    const e = Object.assign({ type: type, target: this, preventDefault: function () {}, stopPropagation: function () {} }, ev || {});
    a.forEach((fn) => fn.call(this, e));
    return a.length > 0;
  }
  click() { return this.dispatch('click'); }
  change() { return this.dispatch('change', { target: this }); }
  input() { return this.dispatch('input', { target: this }); }
  focus() {}
  blur() {}
  select() {}
  remove() {}
  setAttribute(n, v) {
    this.attrs[n] = String(v);
    if (n === 'id') this.id = String(v);
    if (n === 'data-role') this.__dataRole = String(v);
  }
  getAttribute(n) {
    if (n === 'data-role' && this.__dataRole !== null) return this.__dataRole;
    return this.attrs[n] === undefined ? null : this.attrs[n];
  }
  hasAttribute(n) { return this.getAttribute(n) !== null; }
  appendChild(c) { this.children.push(c); return c; }
  insertBefore(c) { this.children.unshift(c); return c; }
  cloneNode() { return new El(this.tagName); }
  getBoundingClientRect() { return { top: 0, left: 0, width: 0, height: 0, bottom: 0, right: 0 }; }
  scrollIntoView() {}
  contains() { return false; }
  closest() { return null; }
  querySelector() { return null; }
  querySelectorAll(sel) {
    // 唯一需要「真的有东西」的容器是导出/导入弹窗：四个 [data-role] 按钮。
    if (sel === '[data-role]' && this.__roleButtons) return this.__roleButtons.slice();
    return [];
  }
}

/* ---------- document ---------- */
function makeDocument() {
  const registry = new Map();
  const doc = {
    readyState: 'complete',
    title: '',
    body: new El('body'),
    documentElement: new El('html'),
    createElement: (tag) => new El(tag),
    createTextNode: (t) => {
      const n = new El('#text');
      n.nodeType = 3;
      n.nodeValue = String(t);
      n.textContent = String(t);
      return n;
    },
    addEventListener: function () {},
    removeEventListener: function () {},
    execCommand: function () { return true; },
    getElementById(id) {
      if (!registry.has(id)) {
        const e = new El('div');
        e.id = id;
        registry.set(id, e);
      }
      return registry.get(id);
    },
    querySelector(sel) {
      if (typeof sel === 'string' && sel.charAt(0) === '#') return doc.getElementById(sel.slice(1));
      return new El('div');
    },
    querySelectorAll() { return []; }
  };
  doc.__registry = registry;
  return doc;
}

/* ---------- 沙箱 ---------- */
/**
 * 建一个能跑 app.js 的全局环境。
 * @param {object} opts.subject  window.SUBJECT（学科配置）
 * @param {object} opts.meta     manifest 内容
 * @param {Array}  opts.questions 题库
 * @param {object} opts.initialState 预置到 localStorage 的旧进度（用于模拟历史遗留）
 */
function createSandbox(opts) {
  const doc = makeDocument();
  const store = new MemoryStorage();
  const sandbox = {
    document: doc,
    location: { href: opts.href || 'https://example.test/subjects/x/', hash: '' },
    history: { replaceState: function () {}, pushState: function () {} },
    navigator: {},
    localStorage: store,
    console: console,
    setTimeout: setTimeout,
    clearTimeout: clearTimeout,
    setInterval: function () {
      const t = setInterval.apply(null, arguments);
      if (t && t.unref) t.unref();      // 别让计时器吊住 Node 进程
      return t;
    },
    clearInterval: clearInterval,
    URL: URL,
    URLSearchParams: URLSearchParams,
    matchMedia: function () { return { matches: false, addEventListener: function () {} }; },
    scrollTo: function () {},
    print: function () {},
    addEventListener: function () {},
    removeEventListener: function () {},
    getComputedStyle: function () { return { getPropertyValue: function () { return ''; } }; },
    __errors: []
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;

  if (opts.initialState) {
    store.setItem(opts.subject.storageKey, JSON.stringify(opts.initialState));
  }

  // 弹窗里的四个 [data-role] 按钮（app.js 用 $$('[data-role]', $('#data-modal')) 接线）
  const modal = doc.getElementById('data-modal');
  const roles = ['data-copy', 'data-download', 'data-apply', 'data-close'];
  modal.__roleButtons = roles.map((r) => {
    const b = new El('button');
    b.setAttribute('data-role', r);
    return b;
  });

  const ctx = vm.createContext(sandbox);
  const load = (file) => {
    const code = fs.readFileSync(file, 'utf8');
    vm.runInContext(code, ctx, { filename: file });
  };

  // 学科配置（真实页面由 subject.js 提供；这里直接给等价物）
  sandbox.SUBJECT = opts.subject;
  // 题库装载（真实页面由 core/bank.js 走 fetch；这里给同形状的内存实现）
  sandbox.LABank = {
    load: function () {
      return Promise.resolve({ meta: opts.meta, questions: opts.questions });
    }
  };
  const storeFile = opts.storeFile;
  if (storeFile && fs.existsSync(storeFile)) load(storeFile);
  load(opts.appFile);

  return { sandbox: sandbox, doc: doc, store: store, modal: modal };
}

/** 等 app.js 的 boot()（LABank.load 是 Promise）跑完。 */
function settle(times) {
  let p = Promise.resolve();
  for (let i = 0; i < (times || 4); i++) {
    p = p.then(() => new Promise((r) => setImmediate(r)));
  }
  return p;
}

/** djb2 —— 与 app.js 里的实现同口径（进度文件格式的一部分）。 */
function djb2(str) {
  let h = 5381;
  for (let i = 0; i < str.length; i++) h = ((h << 5) + h + str.charCodeAt(i)) >>> 0;
  return h.toString(16);
}

/** 造一份格式合法的进度文件（checksum 按 app.js 的口径算）。 */
function makePayload(opts) {
  const st = { v: 1, sessions: opts.sessions || {}, wrongBook: opts.wrongBook || {} };
  const body = JSON.stringify(st);
  const p = {
    kind: 'quiz-platform-progress',
    version: 1,
    state: st,
    checksum: djb2(body)
  };
  if (opts.subject !== undefined) p.subject = opts.subject;
  if (opts.bankId !== undefined) p.bankId = opts.bankId;
  return p;
}

module.exports = {
  MemoryStorage: MemoryStorage,
  El: El,
  createSandbox: createSandbox,
  settle: settle,
  djb2: djb2,
  makePayload: makePayload,
  defaultQuestions: function () {
    return [
      { id: 'q1', type: 'single', typeGroup: 'single', difficulty: 'basic', chapter: 1,
        knowledgePoint: 'kp1', source: { text: '测试来源', kind: 'textbook' }, stem: '题目一',
        options: ['甲', '乙', '丙', '丁'], answer: ['A'], explanation: '解析一' },
      { id: 'q2', type: 'single', typeGroup: 'single', difficulty: 'medium', chapter: 1,
        knowledgePoint: 'kp1', source: { text: '测试来源', kind: 'textbook' }, stem: '题目二',
        options: ['甲', '乙', '丙', '丁'], answer: ['B'], explanation: '解析二' },
      { id: 'q3', type: 'single', typeGroup: 'single', difficulty: 'hard', chapter: 2,
        knowledgePoint: 'kp2', source: { text: '测试来源', kind: 'textbook' }, stem: '题目三',
        options: ['甲', '乙', '丙', '丁'], answer: ['C'], explanation: '解析三' }
    ];
  },
  defaultMeta: function (subject) {
    return {
      schema: 'quiz-platform-subject-v1',
      subject: subject,
      sections: {},
      caliber: { total: 3, byType: { single: 3 }, byDifficulty: { basic: 1, medium: 1, hard: 1 },
        byChapter: { '1': 2, '2': 1 }, limits: { singleMin: 0, singleMax: 9999, multiRange: 9999 } },
      summary: { sub: '测试副标题', desc: '测试描述', aboutHtml: '', footerHtml: '', realExamTagged: 0 },
      shards: []
    };
  }
};
