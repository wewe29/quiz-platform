/* ui/card.js — 答题卡（题号网格）
   显示每题状态：未答 / 已答对 / 已答错 / 当前；收藏题加下边荧光条。 */
(function (ns) {
  'use strict';

  var dom = null, session = null, store = null;
  var box = null;
  var onJump = null;
  var lastSig = '';

  function init(deps) {
    dom = deps.dom;
    session = deps.session;
    store = deps.store;
    box = document.getElementById('card-grid');
    onJump = deps.onJump;
  }

  function cellState(qid, idx, curIdx) {
    if (idx === curIdx) return 'now';
    var a = session.raw.answers[qid];
    if (!a) return '';
    if (a.selfGraded) return a.correct === true ? 'done' : 'wrong';
    return a.correct === true ? 'done' : 'wrong';
  }

  /** 增量刷新：题数不变时只改 class，避免整块重建 */
  function update() {
    if (!box) return;
    var s = session.raw;
    var order = s.order || [];
    var cur = session.currentIndex();
    var favs = store.get().favorites || {};
    var sig = order.length + '|' + cur + '|' + Object.keys(favs).length;
    if (sig !== lastSig && box.children.length !== order.length) {
      rebuild();
      lastSig = sig;
      return;
    }
    var cells = box.children;
    for (var i = 0; i < cells.length && i < order.length; i++) {
      var qid = order[i];
      var cell = cells[i];
      var st = cellState(qid, i, cur);
      cell.className = 'card-cell' + (st ? ' ' + st : '') + (favs[qid] ? ' fav' : '');
      cell.textContent = String(i + 1);
      cell.setAttribute('aria-current', i === cur ? 'true' : 'false');
    }
    lastSig = sig;
  }

  function rebuild() {
    if (!box) return;
    dom.clear(box);
    var order = session.raw.order || [];
    var cur = session.currentIndex();
    var favs = store.get().favorites || {};
    order.forEach(function (qid, i) {
      var st = cellState(qid, i, cur);
      var b = dom.el('button', {
        type: 'button',
        class: 'card-cell' + (st ? ' ' + st : '') + (favs[qid] ? ' fav' : ''),
        title: '第 ' + (i + 1) + ' 题',
        'aria-current': i === cur ? 'true' : 'false',
        text: String(i + 1)
      });
      b.addEventListener('click', function () { onJump(i); });
      box.appendChild(b);
    });
  }

  function setBadge(n) {
    var el = document.getElementById('card-count');
    if (el) el.textContent = n + ' 题';
  }

  ns.card = { init: init, update: update, rebuild: rebuild, setBadge: setBadge };
})(window.QX = window.QX || {});
