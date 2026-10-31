/* ui/dom.js — DOM 小工具 + 公式渲染 + Toast（依赖 KaTeX auto-render 已在全局就绪） */
(function (ns) {
  'use strict';

  var uid = 0;

  /** 创建元素：el('div', {class:'x', text:'hi'}, [child]) */
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'class' || k === 'className') { node.className = v; }
        else if (k === 'text') { node.textContent = v; }
        else if (k === 'html') { node.innerHTML = v; }
        else if (k === 'style' && typeof v === 'object') {
          Object.keys(v).forEach(function (p) { node.style[p] = v[p]; });
        }
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') {
          node.addEventListener(k.slice(2).toLowerCase(), v);
        }
        else if (v === true) { node.setAttribute(k, ''); }
        else { node.setAttribute(k, v); }
      });
    }
    (children || []).forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return node;
  }

  function clear(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
    return node;
  }

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /** 事件委托：on(root, 'click', '.opt', handler) */
  function on(root, evt, sel, fn) {
    root.addEventListener(evt, function (e) {
      var t = e.target;
      while (t && t !== root) {
        if (t.nodeType === 1 && t.matches && t.matches(sel)) {
          fn.call(t, e, t);
          return;
        }
        t = t.parentNode;
      }
    });
  }

  /* ---------------- 公式渲染 ---------------- */
  var DELIMS = [
    { left: '$$', right: '$$', display: true },
    { left: '\\[', right: '\\]', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false }
  ];

  /** 渲染节点内的 $...$ 公式；KaTeX 未就绪时原样保留（不报错、不静默吞掉） */
  function renderMath(root) {
    if (!root) return false;
    var fn = window.renderMathInElement;
    if (typeof fn !== 'function') return false;
    try {
      fn(root, {
        delimiters: DELIMS,
        throwOnError: false,
        errorColor: '#B3261E',
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option']
      });
      return true;
    } catch (e) {
      if (window.console && console.warn) console.warn('[math] 渲染失败：', e);
      return false;
    }
  }

  function mathReady() { return typeof window.renderMathInElement === 'function'; }

  /* ---------------- Toast ---------------- */
  var toastTimer = null;

  function toast(msg, ms) {
    var old = document.querySelector('.toast');
    if (old) old.parentNode.removeChild(old);
    var t = el('div', { class: 'toast', text: msg, role: 'status' });
    document.body.appendChild(t);
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      if (t.parentNode) t.parentNode.removeChild(t);
    }, ms || 1900);
    return t;
  }

  /* ---------------- 杂项 ---------------- */
  function fmtTime(ms) {
    var s = Math.max(0, Math.floor(ms / 1000));
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    function p(n) { return n < 10 ? '0' + n : '' + n; }
    return (h > 0 ? h + ':' + p(m) : p(m)) + ':' + p(ss);
  }

  function pct(a, b) { return b ? Math.round((a / b) * 1000) / 10 : 0; }

  function nextId(prefix) { uid += 1; return (prefix || 'u') + uid; }

  ns.dom = {
    el: el, clear: clear, $: $, $$: $$, esc: esc, on: on,
    renderMath: renderMath, mathReady: mathReady,
    toast: toast, fmtTime: fmtTime, pct: pct, nextId: nextId
  };
})(window.QX = window.QX || {});
