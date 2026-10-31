/* tools/check_keyboard_contract.js — 键盘快捷键契约门禁
 *
 * 真实踩过（2026-10-31，线上复验时发现，发布后浏览器实测）：
 *   多选题上选好答案后按 Enter（快捷键面板写明的「提交答案」）**提交不了**，
 *   而点「提交答案（Enter）」按钮完全正常 —— 纯键盘路径坏、鼠标路径好。
 *
 * 根因（两个处理器抢同一个键）：
 *   ① 选项元素自己绑了 keydown：Enter/Space → view.onPick(L)；
 *   ② 全局 keys.js 又把 Enter 映射成 'submit'（Space → 'next'）。
 *   事件冒泡顺序是「先选项、后 document」：
 *      ① Enter 先打到选项 → onPick('A')；
 *      ② 多选题的 onPick 是 toggle（再点一次＝取消）→ 刚选的 A 被自己取消；
 *      ③ 事件继续冒泡到 document → 提交时缓冲区已空 → 弹「还没作答，先选一个选项」。
 *   单选题不受影响（onPick 是赋值不是 toggle），所以只有多选题坏 —— 很难被自测发现。
 *
 * 这道门禁用**真实的 render.js + 真实的 keys.js** 跑一遍真实路径：
 *   ① 渲染一道题，找出每个选项元素；
 *   ② 断言选项元素上**没有** keydown 监听器（否则它会抢 Enter）；
 *   ③ 从选项元素上派发 Enter：全局必须收到 'submit'，且**已选字母不得被取消**；
 *   ④ 从选项元素上派发空格：全局必须收到 'next'，且已选字母不得被取消；
 *   ⑤ 点选项仍然要触发 onPick（防止「为了不抢键把选择功能一起删了」）。
 *
 * 用法：node tools/check_keyboard_contract.js   （无 stdin 参数，自带题库桩）
 */
'use strict';

const path = require('path');
const H = require(path.join(__dirname, 'tests', 'harness.js'));

/* ---------------- 最小 DOM 桩 ----------------
   只实现 render.js 真正用到的那几个动作；目的不是模拟浏览器，
   而是让「真实 render.js」能在这条门禁里跑出真实的选项元素与监听器。 */

const docListeners = {};

function makeNode(tag) {
  return {
    tagName: String(tag).toUpperCase(),
    className: '',
    textContent: '',
    innerHTML: '',
    attributes: {},
    children: [],
    listeners: {},
    style: {},
    appendChild(c) { this.children.push(c); return c; },
    removeChild(c) {
      const i = this.children.indexOf(c);
      if (i >= 0) this.children.splice(i, 1);
      return c;
    },
    get firstChild() { return this.children.length ? this.children[0] : null; },
    setAttribute(k, v) { this.attributes[k] = v; },
    getAttribute(k) { return this.attributes[k]; },
    addEventListener(t, fn) { (this.listeners[t] = this.listeners[t] || []).push(fn); },
    removeEventListener(t, fn) {
      const arr = this.listeners[t] || [];
      const i = arr.indexOf(fn);
      if (i >= 0) arr.splice(i, 1);
    }
  };
}

const fakeDocument = {
  addEventListener(t, fn) { (docListeners[t] = docListeners[t] || []).push(fn); },
  removeEventListener(t, fn) {
    const arr = docListeners[t] || [];
    const i = arr.indexOf(fn);
    if (i >= 0) arr.splice(i, 1);
  },
  createElement(tag) { return makeNode(tag); },
  createTextNode(t) { return { textContent: t }; },
  getElementById() { return null; },
  querySelector() { return null; },
  querySelectorAll() { return []; }
};

const fakeDom = {
  el(tag, attrs, children) {
    const node = makeNode(tag);
    if (attrs) {
      Object.keys(attrs).forEach((k) => {
        const v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'class' || k === 'className') node.className = v;
        else if (k === 'text') node.textContent = v;
        else if (k === 'html') node.innerHTML = v;
        else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') {
          node.addEventListener(k.slice(2).toLowerCase(), v);
        } else if (v === true) node.setAttribute(k, '');
        else node.setAttribute(k, v);
      });
    }
    (children || []).forEach((c) => {
      if (c === null || c === undefined || c === false) return;
      node.appendChild(typeof c === 'string' ? { textContent: c } : c);
    });
    return node;
  },
  clear(node) { while (node && node.children.length) node.removeChild(node.children[0]); },
  esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  },
  renderMath() { /* 公式渲染与本门禁无关 */ }
};

/* ---------------- 在假 DOM 里派发一次按键（模拟冒泡） ---------------- */
function fireKey(node, key) {
  let stopped = false;
  const ev = {
    key,
    target: node,
    ctrlKey: false, metaKey: false, altKey: false, shiftKey: false,
    preventDefault() {},
    stopPropagation() { stopped = true; }
  };
  (node.listeners['keydown'] || []).forEach((fn) => fn(ev));
  if (!stopped) {
    (docListeners['keydown'] || []).forEach((fn) => fn(ev));
  }
  return ev;
}

/* 找到题卡里 data-letter === L 的选项元素 */
function findOption(node, letter) {
  if (!node) return null;
  if (node.attributes && node.attributes['data-letter'] === letter) return node;
  for (const c of (node.children || [])) {
    const hit = findOption(c, letter);
    if (hit) return hit;
  }
  return null;
}

function main() {
  global.document = fakeDocument;

  const QX = H.loadCoreAndUi();
  QX.render.init({ dom: fakeDom });

  const submits = [];
  const nexts = [];
  QX.keys.init({
    submit: () => submits.push(true),
    next: () => nexts.push(true),
    pick: () => {}
  });
  QX.keys.bind();

  const problems = [];

  // 契约①：Enter 归全局提交、空格归全局翻题（这两条不能被改坏）
  if (QX.keys.resolve({ key: 'Enter' }) !== 'submit') {
    problems.push('全局键位表里 Enter 不再是 submit');
  }
  if (QX.keys.resolve({ key: ' ' }) !== 'next') {
    problems.push('全局键位表里空格不再是 next');
  }

  const CASES = [
    { type: 'multi', label: '多选题' },
    { type: 'single', label: '单选题' },
    { type: 'judge', label: '判断题' }
  ];

  for (const c of CASES) {
    // 多选题的 onPick 是 toggle；单选/判断是赋值。这里按 app.js 的真实语义模拟。
    let picked = ['A'];
    const view = {
      picked: picked,
      record: null,
      fav: false,
      index: 0,
      total: 1,
      onPick: (L) => {
        if (c.type === 'multi') {
          const i = picked.indexOf(L);
          if (i >= 0) picked.splice(i, 1); else picked.push(L);
        } else {
          picked = [L];
        }
        view.picked = picked;
      },
      onSubmit: () => {},
      onRedo: () => {},
      onNav: () => {},
      onToggleFav: () => {},
      onToggleWrong: () => {},
      onSelfGrade: () => {}
    };

    const q = H.mkQ({ id: 'kb-' + c.type, type: c.type, typeGroup: c.type, answer: ['A'] });
    const container = fakeDom.el('div', {});
    QX.render.render(container, q, view);

    const optA = findOption(container, 'A');
    if (!optA) {
      problems.push(c.label + '：渲染结果里找不到 data-letter="A" 的选项元素');
      continue;
    }

    // 契约②：选项元素上不得挂 keydown 监听器（它会抢 Enter）
    if ((optA.listeners['keydown'] || []).length) {
      problems.push(c.label + '：选项元素上挂了 keydown 监听器 —— 它会抢走 Enter（全局的「提交答案」键）；' +
        '多选题上还会因 onPick 是 toggle 而把刚选的答案取消掉');
    }

    // 契约③：Enter 从选项上冒泡到全局 ⇒ 触发提交，且不得改变已选
    submits.length = 0;
    fireKey(optA, 'Enter');
    if (!submits.length) {
      problems.push(c.label + '：在选项上按 Enter 没有触发全局提交');
    }
    if (picked.indexOf('A') < 0) {
      problems.push(c.label + '：在选项上按 Enter 把已选字母取消了（多选题的 onPick 是 toggle）');
    }

    // 契约④：空格从选项上冒泡到全局 ⇒ 触发翻题，且不得改变已选
    nexts.length = 0;
    fireKey(optA, ' ');
    if (!nexts.length) {
      problems.push(c.label + '：在选项上按空格没有触发全局翻题');
    }
    if (picked.indexOf('A') < 0) {
      problems.push(c.label + '：在选项上按空格把已选字母取消了');
    }

    // 契约⑤：点选项仍然要能选（别为了不抢键把选择功能删了）
    let pickedByClick = null;
    const view2 = Object.assign({}, view, {
      picked: [],
      onPick: (L) => { pickedByClick = L; }
    });
    const container2 = fakeDom.el('div', {});
    QX.render.render(container2, q, view2);
    const optA2 = findOption(container2, 'A');
    if (!optA2) {
      problems.push(c.label + '：第二次渲染找不到选项元素');
      continue;
    }
    (optA2.listeners['click'] || []).forEach((fn) => fn({}));
    if (pickedByClick !== 'A') {
      problems.push(c.label + '：点击选项没有触发 onPick —— 选择功能被弄坏了');
    }
  }

  if (problems.length) {
    console.log('[keyboard] 键盘快捷键契约检查失败：');
    for (const p of problems) console.log('  [FAIL] ' + p);
    return 1;
  }
  console.log('[keyboard] 键盘快捷键契约检查通过：' + CASES.length +
    ' 种题型上 Enter=提交 / 空格=翻题 均不被选项抢占，且已选答案不会被取消');
  return 0;
}

process.exit(main());
