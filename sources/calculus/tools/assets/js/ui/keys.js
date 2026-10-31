/* ui/keys.js — 键盘快捷键
   定案：←/K 上一题、→/J/Space 下一题、A–D 与 1–4 选项、Enter 提交、
        F 收藏、W 加入/移出错题本、S 统计、Shift+B 错题本、Shift+C 答题卡、
        Shift+D 深色、? 帮助、Esc 关抽屉。输入框 / 文本域 / 可编辑元素内不触发。

   为什么面板动作要加 Shift：
       A–D 是**印在题面上的选项字母**，肌肉记忆优先级最高，不能被面板抢走；
       而 B/C/D 同时被原方案用作「错题本 / 答题卡 / 深色」——
       两者直接撞车，结果是这三个快捷键**永远打不开**
       （keys.js 里 'abcd' 判断在前，裸 B/C/D 都被当成选项吃掉了）。
       于是：裸 B/C/D = 选项；Shift+B/C/D = 面板动作。 */
(function (ns) {
  'use strict';

  var handlers = {};
  var bound = false;

  function init(map) { handlers = map || {}; }

  function isTyping(e) {
    var t = e.target;
    if (!t) return false;
    var tag = (t.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
    if (t.isContentEditable) return true;
    return false;
  }

  function emit(name, e) {
    var fn = handlers[name];
    if (typeof fn === 'function') { fn(e); return true; }
    return false;
  }

  var PICK_BY_DIGIT = { '1': 'a', '2': 'b', '3': 'c', '4': 'd' };

  /**
   * 把一次按键解析成一个动作名；不处理时返回 null。
   * 抽成纯函数是为了能单测「哪个键触发哪个动作」。
   */
  function resolve(e) {
    if (!e) return null;
    var k = e.key;
    switch (k) {
      case 'ArrowLeft': return 'prev';
      case 'ArrowRight': return 'next';
      case ' ': case 'Spacebar': return 'next';
      case 'Enter': return 'submit';
      case 'Escape': return 'escape';
      default: break;
    }
    if (k === '?' || (k === '/' && e.shiftKey)) return 'help';
    if (typeof k !== 'string' || k.length !== 1) return null;
    var lower = k.toLowerCase();

    // Shift + B/C/D：面板动作
    if (e.shiftKey) {
      if (lower === 'b') return 'wrongbook';
      if (lower === 'c') return 'card';
      if (lower === 'd') return 'theme';
      return null;
    }
    // 裸 A–D / 1–4：选择选项
    if ('abcd'.indexOf(lower) >= 0) return 'pick:' + lower;
    if (/^[1-4]$/.test(k)) return 'pick:' + PICK_BY_DIGIT[k];

    switch (lower) {
      case 'k': return 'prev';
      case 'j': return 'next';
      case 'f': return 'fav';
      case 'w': return 'wrong';
      case 's': return 'stats';
      default: return null;
    }
  }

  function onKeyDown(e) {
    if (isTyping(e)) {
      // 文本域里只放行 Esc（关抽屉）
      if (e.key === 'Escape') emit('escape', e);
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;

    var name = resolve(e);
    if (name && emit(name, e)) e.preventDefault();
  }

  function bind() {
    if (bound) return;
    document.addEventListener('keydown', onKeyDown);
    bound = true;
  }

  function unbind() {
    if (!bound) return;
    document.removeEventListener('keydown', onKeyDown);
    bound = false;
  }

  ns.keys = {
    init: init, bind: bind, unbind: unbind, isTyping: isTyping, resolve: resolve
  };
})(window.QX = window.QX || {});
