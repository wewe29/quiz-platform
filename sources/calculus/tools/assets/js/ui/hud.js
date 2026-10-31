/* ui/hud.js — 顶部指标条（进度 / 用时 / 得分 / 得分率 / 客观正确率）+ 进度条 */
(function (ns) {
  'use strict';

  var dom = null;
  var els = {};

  function init(deps) {
    dom = deps.dom;
    els = {
      progress: document.getElementById('m-progress'),
      time: document.getElementById('m-time'),
      score: document.getElementById('m-score'),
      rate: document.getElementById('m-rate'),
      acc: document.getElementById('m-acc'),
      bar: document.getElementById('progress-bar'),
      fill: document.getElementById('progress-fill')
    };
  }

  function setText(node, v) { if (node) node.textContent = v; }

  /** metrics: {answered,total,elapsed,earned,full,rate,acc} */
  function update(metrics) {
    var m = metrics || {};
    setText(els.progress, (m.answered || 0) + ' / ' + (m.total || 0));
    setText(els.time, dom.fmtTime(m.elapsed || 0));
    setText(els.score, (m.earned || 0) + ' / ' + (m.full || 0));
    setText(els.rate, m.rate === null || m.rate === undefined ? '—' : (m.rate + '%'));
    setText(els.acc, m.acc === null || m.acc === undefined ? '—' : (m.acc + '%'));
    var p = m.total ? Math.round(((m.answered || 0) / m.total) * 1000) / 10 : 0;
    if (els.fill) els.fill.style.width = p + '%';
    if (els.bar) els.bar.setAttribute('aria-valuenow', String(p));
  }

  function updateTime(ms) {
    setText(els.time, dom.fmtTime(ms || 0));
  }

  ns.hud = { init: init, update: update, updateTime: updateTime };
})(window.QX = window.QX || {});
