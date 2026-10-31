/* ui/drawer.js — 右侧抽屉：统计面板 / 错题本 / 收藏 / 快捷键帮助
   抽屉内容全部由 store + session 现算，不额外落盘。 */
(function (ns) {
  'use strict';

  var dom = null, session = null, store = null, stats = null;
  var drawer = null, backdrop = null, body = null, titleEl = null;
  var current = null;
  var hooks = {};

  function init(deps) {
    dom = deps.dom;
    session = deps.session;
    store = deps.store;
    stats = deps.stats;
    hooks = deps.hooks || {};
    drawer = document.getElementById('drawer');
    backdrop = document.getElementById('drawer-backdrop');
    body = document.getElementById('drawer-body');
    titleEl = document.getElementById('drawer-title');
    if (backdrop) backdrop.addEventListener('click', close);
    var closeBtn = document.getElementById('drawer-close');
    if (closeBtn) closeBtn.addEventListener('click', close);
  }

  function isOpen() { return !!drawer && !drawer.hasAttribute('hidden'); }

  function close() {
    if (!drawer) return;
    drawer.setAttribute('hidden', '');
    if (backdrop) backdrop.setAttribute('hidden', '');
    current = null;
  }

  function open(kind) {
    if (!drawer) return;
    current = kind;
    if (backdrop) backdrop.removeAttribute('hidden');
    drawer.removeAttribute('hidden');
    dom.clear(body);
    if (kind === 'stats') renderStats();
    else if (kind === 'wrong') renderWrong();
    else if (kind === 'fav') renderFav();
    else if (kind === 'keys') renderKeys();
  }

  function toggle(kind) {
    if (isOpen() && current === kind) close(); else open(kind);
  }

  /* ---------------- 统计 ---------------- */
  function tile(k, v, sub) {
    var t = dom.el('div', { class: 'stat-tile' });
    t.appendChild(dom.el('div', { class: 'k', text: k }));
    var vv = dom.el('div', { class: 'v' });
    vv.appendChild(document.createTextNode(String(v)));
    if (sub) vv.appendChild(dom.el('small', { text: ' ' + sub }));
    t.appendChild(vv);
    return t;
  }

  function barRows(map, labelFn, sortFn) {
    var wrap = dom.el('div');
    var keys = Object.keys(map || {});
    if (sortFn) keys.sort(sortFn);
    if (!keys.length) {
      wrap.appendChild(dom.el('p', { class: 'muted', text: '暂无数据' }));
      return wrap;
    }
    keys.forEach(function (k) {
      var d = map[k];
      var rate = d.full ? (d.earned / d.full) * 100 : 0;
      var row = dom.el('div', { class: 'bar-row' });
      row.appendChild(dom.el('span', { class: 'bar-label', text: labelFn ? labelFn(k) : k, title: labelFn ? labelFn(k) : k }));
      var track = dom.el('span', { class: 'bar-track' });
      var fill = dom.el('span', { class: 'bar-fill' + (rate >= 80 ? ' ok' : rate < 60 ? ' bad' : '') });
      fill.style.width = Math.max(0, Math.min(100, rate)) + '%';
      track.appendChild(fill);
      row.appendChild(track);
      row.appendChild(dom.el('span', { class: 'bar-val', text: d.answered + '题 ' + Math.round(rate * 10) / 10 + '%' }));
      wrap.appendChild(row);
    });
    return wrap;
  }

  function section(title, node) {
    var s = dom.el('section', { style: { marginTop: 'var(--sp-6)' } });
    s.appendChild(dom.el('h3', { text: title, style: { fontSize: 'var(--fs-md)', marginBottom: 'var(--sp-3)' } }));
    s.appendChild(node);
    return s;
  }

  function renderStats() {
    titleEl.textContent = '统计面板';
    // 打开统计时**重算一次**。recompute() 之前在整个项目里从未被调用过，
    // 于是 store.stats 永远停在初始空壳 —— 统计面板整块显示 0 / 「暂无数据」，
    // 而「本次作答」却是准的（它走的是 sessionMetrics，不读缓存）。
    var st = stats.recompute() || store.get().stats || {};
    var m = stats.sessionMetrics();
    var grid = dom.el('div', { class: 'stat-grid' });
    grid.appendChild(tile('已答题数', st.totalAnswered || 0));
    grid.appendChild(tile('客观正确率', st.objectiveAnswered ? Math.round((st.objectiveCorrect / st.objectiveAnswered) * 1000) / 10 : '—', st.objectiveAnswered ? '%' : ''));
    grid.appendChild(tile('总得分', st.totalEarned || 0, '/ ' + (st.totalFull || 0)));
    grid.appendChild(tile('本次作答', m.answered, '/ ' + m.total));
    grid.appendChild(tile('本次得分率', m.rate === null ? '—' : m.rate, m.rate === null ? '' : '%'));
    grid.appendChild(tile('错题本', Object.keys(store.get().wrongBook || {}).filter(function (k) {
      return !(store.get().wrongBook[k] || {}).resolved;
    }).length, '题'));
    body.appendChild(grid);

    var typeLabel = {
      single: '单选', multi: '多选', judge: '判断', blank: '填空',
      short: '简答与名词解释', calc: '计算与分析题'
    };
    body.appendChild(section('按题型', barRows(st.byType, function (k) { return typeLabel[k] || k; })));

    var diffLabel = { basic: '基础', medium: '中等', hard: '困难' };
    body.appendChild(section('按难度', barRows(st.byDifficulty, function (k) { return diffLabel[k] || k; })));

    body.appendChild(section('按章节', barRows(st.byChapter, function (k) { return '第 ' + k + ' 章'; },
      function (a, b) { return Number(a) - Number(b); })));

    var kpLabels = ns.catalog && ns.catalog.kpLabel ? ns.catalog.kpLabel : {};
    body.appendChild(section('按知识点（正确率最低的 15 个）', barRows(st.byKnowledgePoint, function (k) {
      return k + ' ' + (kpLabels[k] || '');
    }, function (a, b) {
      var ra = (st.byKnowledgePoint[a].earned / (st.byKnowledgePoint[a].full || 1));
      var rb = (st.byKnowledgePoint[b].earned / (st.byKnowledgePoint[b].full || 1));
      return ra - rb;
    })));

    // 答案位置分布（题库实测）
    var pos = st.answerPosition || {};
    var total = Object.keys(pos).reduce(function (a, k) { return a + (pos[k] || 0); }, 0);
    var dist = dom.el('div');
    dist.appendChild(dom.el('p', { class: 'muted', text: '共 ' + total + ' 道单选/判断题的作答分布（这是你的实际作答，不是声称的题库分布）。' }));
    var bars = dom.el('div', { class: 'dist-bars' });
    ['A', 'B', 'C', 'D'].forEach(function (L, i) {
      var n = pos[L] || 0;
      var sp = dom.el('span', { class: 'db-' + 'abcd'[i], title: L + '：' + n + ' 题', text: n ? String(n) : '' });
      if (total) sp.style.flex = '1';
      bars.appendChild(sp);
    });
    dist.appendChild(bars);
    body.appendChild(section('答案位置分布', dist));
  }

  /* ---------------- 错题本 / 收藏 ---------------- */
  function renderWrong() {
    titleEl.textContent = '错题本';
    var wb = store.get().wrongBook || {};
    var allIds = Object.keys(wb);
    // 未订正的排前面；**已订正的也保留在列表里**并标注「已订正」——
    // 订正过的题要看得见，才知道哪些已经补上、哪些还没补。
    allIds.sort(function (a, b) {
      var ra = wb[a].resolved ? 1 : 0, rb = wb[b].resolved ? 1 : 0;
      if (ra !== rb) return ra - rb;
      return (wb[b].lastWrongAt || 0) - (wb[a].lastWrongAt || 0);
    });
    var unresolved = allIds.filter(function (id) { return !wb[id].resolved; }).length;
    var qs = allIds.map(function (id) { return session.questionById(id); }).filter(Boolean);
    body.appendChild(dom.el('p', {
      class: 'muted',
      text: '未订正 ' + unresolved + ' 道 · 已订正 ' + (allIds.length - unresolved) +
        ' 道（累计记录 ' + allIds.length + ' 道）'
    }));

    var foot = document.getElementById('drawer-foot');
    if (foot) {
      dom.clear(foot);
      var practice = dom.el('button', { type: 'button', class: 'btn btn-primary', text: '只练这些题' });
      practice.addEventListener('click', function () { if (hooks.onPracticeWrong) hooks.onPracticeWrong(); });
      foot.appendChild(practice);
      var clr = dom.el('button', { type: 'button', class: 'btn btn-ghost', text: '清空错题本' });
      clr.addEventListener('click', function () {
        if (!window.confirm('确定清空错题本？此操作不可撤销。')) return;
        store.set(function (st) { st.wrongBook = {}; });
        renderWrong();
        if (hooks.onDataChanged) hooks.onDataChanged();
      });
      foot.appendChild(clr);
    }

    if (!qs.length) {
      body.appendChild(dom.el('div', { class: 'empty' }, [
        dom.el('div', { class: 'empty-icon', text: '✓' }),
        dom.el('h3', { text: '错题本是空的' }),
        dom.el('p', { text: '做错的题会自动收进来，方便集中复盘。' })
      ]));
      return;
    }
    qs.forEach(function (q) {
      var item = dom.el('div', { class: 'wrong-item' });
      var head = dom.el('div', { class: 'wi-head' });
      head.appendChild(dom.el('span', { class: 'badge badge-kp', text: q.knowledgePoint }));
      head.appendChild(dom.el('span', { class: 'badge badge-diff-' + q.difficulty, text: q.difficulty }));
      if (q.source && q.source.kind && q.source.kind !== 'textbook') {
        head.appendChild(dom.el('span', { class: 'badge badge-fluoro', text: '真题' }));
      }
      if (wb[q.id].resolved) {
        head.appendChild(dom.el('span', { class: 'badge badge-done', text: '已订正' }));
      }
      item.appendChild(head);
      item.appendChild(dom.el('div', { class: 'wi-stem', text: String(q.stem).slice(0, 90) }));
      var meta = dom.el('div', { class: 'wi-meta' });
      meta.textContent = (wb[q.id].resolved ? '已订正 · ' : '') +
        '错 ' + (wb[q.id].wrongCount || 1) + ' 次 · ' + (q.source && q.source.text || '');
      item.appendChild(meta);
      item.addEventListener('click', function () {
        if (hooks.onJumpTo) hooks.onJumpTo(q.id);
      });
      body.appendChild(item);
    });
  }

  function renderFav() {
    titleEl.textContent = '我的收藏';
    var favs = store.get().favorites || {};
    var qs = Object.keys(favs).map(function (id) { return session.questionById(id); }).filter(Boolean);
    body.appendChild(dom.el('p', { class: 'muted', text: '共收藏 ' + qs.length + ' 题。' }));
    var foot = document.getElementById('drawer-foot');
    if (foot) {
      dom.clear(foot);
      var practice = dom.el('button', { type: 'button', class: 'btn btn-primary', text: '只练收藏题' });
      practice.addEventListener('click', function () { if (hooks.onPracticeFav) hooks.onPracticeFav(); });
      foot.appendChild(practice);
    }
    if (!qs.length) {
      body.appendChild(dom.el('div', { class: 'empty' }, [
        dom.el('div', { class: 'empty-icon', text: '☆' }),
        dom.el('h3', { text: '还没有收藏' }),
        dom.el('p', { text: '按 F 收藏当前题，收藏题会带荧光标记。' })
      ]));
      return;
    }
    qs.forEach(function (q) {
      var item = dom.el('div', { class: 'wrong-item' });
      item.appendChild(dom.el('div', { class: 'wi-head' }, [
        dom.el('span', { class: 'badge badge-kp', text: q.knowledgePoint })
      ]));
      item.appendChild(dom.el('div', { class: 'wi-stem', text: String(q.stem).slice(0, 90) }));
      item.addEventListener('click', function () { if (hooks.onJumpTo) hooks.onJumpTo(q.id); });
      body.appendChild(item);
    });
  }

  /* ---------------- 快捷键 ---------------- */
  var KEYMAP = [
    ['← / K', '上一题'],
    ['→ / J / Space', '下一题'],
    ['A–D / 1–4', '选择选项（客观题）'],
    ['Enter', '提交答案'],
    ['F', '收藏 / 取消收藏'],
    ['W', '加入 / 移出错题本'],
    ['S', '打开统计面板'],
    ['Shift+B', '打开错题本'],
    ['Shift+C', '打开答题卡'],
    ['Shift+D', '切换深色模式'],
    ['?', '显示本帮助'],
    ['Esc', '关闭抽屉']
  ];

  function renderKeys() {
    titleEl.textContent = '键盘快捷键';
    var grid = dom.el('div', { class: 'keys-grid' });
    KEYMAP.forEach(function (row) {
      var r = dom.el('div', { class: 'keys-row' });
      r.appendChild(dom.el('span', { class: 'k' }, [dom.el('kbd', { text: row[0] })]));
      r.appendChild(dom.el('span', { text: row[1] }));
      grid.appendChild(r);
    });
    body.appendChild(grid);
    body.appendChild(dom.el('p', {
      class: 'muted', style: { marginTop: 'var(--sp-5)' },
      text: '输入框与文本域内不触发快捷键。'
    }));
    var foot = document.getElementById('drawer-foot');
    if (foot) {
      dom.clear(foot);
      var b = dom.el('button', { type: 'button', class: 'btn', text: '知道了' });
      b.addEventListener('click', close);
      foot.appendChild(b);
    }
  }

  ns.drawer = { init: init, open: open, close: close, toggle: toggle, isOpen: isOpen };
})(window.QX = window.QX || {});
