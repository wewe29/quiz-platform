/* app.js — v2 装配层
   职责：启动流程、状态编排、事件接线。
   业务逻辑全在 core/，渲染全在 ui/，本文件只做「把它们接起来」。

   数据源两种：
     多文件站：fetch('data/index.json') + fetch('data/chNN.json')
     单文件包：window.__BANK__ 内联，走内存分支 */
(function (ns) {
  'use strict';

  var store = null, bus = null, judge = null, session = null, stats = null, bank = null;
  var dom = null, render = null, hud = null, filters = null, card = null, drawer = null, keys = null, theme = null;

  var state = {
    picked: [],
    focusLetter: null,
    ready: false,
    error: null,
    qid: null            // 当前渲染的题 id —— 用来判断这次渲染是不是「切题」
  };

  /* ---------------- 启动 ---------------- */
  function boot() {
    dom = ns.dom; render = ns.render; hud = ns.hud; filters = ns.filters;
    card = ns.card; drawer = ns.drawer; keys = ns.keys; theme = ns.theme;
    store = ns.store; bus = ns.bus; judge = ns.judge; session = ns.session;
    stats = ns.stats; bank = ns.bank;

    /* 单文件包：window.__BANK__ 里已内联全部题库，必须交给 bank。
       否则 hasInline() 恒为 false → 误走 fetch('data/index.json') →
       单文件包必然 404 → 页面只剩「题库载入失败」。
       （多文件站不定义 window.__BANK__，这段自然不生效。） */
    if (window.__BANK__) bank.setInline(window.__BANK__);

    dom.init && dom.init();
    render.init({ dom: dom });
    hud.init({ dom: dom });
    card.init({ dom: dom, session: session, store: store, onJump: function (i) { session.gotoIdx(i); afterChange(); } });
    drawer.init({
      dom: dom, session: session, store: store, stats: stats,
      hooks: {
        onPracticeWrong: function () { practiceOnly('wrong'); },
        onPracticeFav: function () { practiceOnly('fav'); },
        onJumpTo: function (qid) { jumpToQuestion(qid); },
        onDataChanged: function () { refreshAll(); }
      }
    });
    filters.init({
      dom: dom, session: session, store: store, catalog: bank.getCatalog(),
      onChange: function () { onFilterChanged(); }
    });
    keys.init({
      prev: function () { nav(-1); },
      next: function () { nav(1); },
      submit: function () { handleSubmit(); },
      escape: function () { drawer.close(); },
      fav: function () { toggleFav(); },
      wrong: function () { toggleWrong(); },
      theme: function () { cycleTheme(); },
      stats: function () { drawer.toggle('stats'); },
      wrongbook: function () { drawer.toggle('wrong'); },
      card: function () { toggleCardPanel(); },
      help: function () { drawer.toggle('keys'); },
      'pick:a': function () { pickByLetter('A'); },
      'pick:b': function () { pickByLetter('B'); },
      'pick:c': function () { pickByLetter('C'); },
      'pick:d': function () { pickByLetter('D'); }
    });
    keys.bind();

    store.load(currentBankId());
    theme.init({ store: store });
    theme.apply();
    theme.bindSystem();

    if (!store.isStorageOk()) {
      var warn = document.getElementById('storage-warn');
      if (warn) warn.removeAttribute('hidden');
    }

    load().then(function () {
      state.ready = true;
      wireHud();
      renderCurrent();
      refreshAll();
    }).catch(function (e) {
      showError(e);
    });

    // 页面隐藏/关闭前落盘，避免丢失最后一次作答
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) session.setHidden(true);
      else session.setHidden(false);
      store.flush();
    });
    window.addEventListener('pagehide', function () { store.flush(); });
    window.addEventListener('beforeunload', function () { store.flush(); });
  }

  function currentBankId() {
    if (window.__BANK__ && window.__BANK__.id) return window.__BANK__.id;
    var idx = bank.getIndex();
    if (idx && idx.bank && idx.bank.id) return idx.bank.id;
    return 'advanced-math-tj7-v2';
  }

  function load() {
    state.error = null;
    // loadIndex() 自己分两种模式：内联包直接读 window.__BANK__，多文件站才 fetch。
    // 早前这里写成 `bank.hasInline() ? Promise.resolve() : bank.loadIndex()`，
    // 于是内联模式跳过了 loadIndex() —— 而 catalog 正是在 loadIndex() 里合并的，
    // 结果单文件包的筛选维度全是空壳（chip 一片不渲染）。统一交给 loadIndex()。
    var p = bank.loadIndex();
    return p.then(function () {
      var cat = bank.getCatalog();
      ns.catalog = { kpLabel: (cat && cat.kpLabel) || {} };
      // index 此刻才加载完，catalog 才有真数据 —— 必须同步给 filters，
      // 否则五组筛选 chip 会因为拿到空壳 catalog 而全都不渲染。
      filters.setCatalog(cat);
      session.init({ store: store, bus: bus, judge: judge, catalog: cat });
      stats.init({ store: store, session: session });
      return bank.loadAll();
    }).then(function (questions) {
      if (!questions || !questions.length) {
        throw new Error('题库为空：没有载入任何题目');
      }
      session.setQuestions(questions);
      var s = session.ensureSession();
      if (session.orderIsStale() || !s.order.length) session.refreshOrder();
      filters.tally(questions);
      filters.build();
      renderFooter(bank.getIndex() && bank.getIndex().summary);
      session.startTimer();
      bus.on('time:tick', function (ms) { hud.updateTime(ms); });
      return questions;
    });
  }

  /* ---------------- 页脚与标题 ---------------- */
  function renderFooter(summary) {
    var foot = document.getElementById('foot');
    if (!foot || !summary) return;
    dom.clear(foot);
    var t = summary.typeLabel || {};
    var k = summary.kindLabel || {};
    function names(counter, labelmap) {
      return Object.keys(counter || {}).sort(function (a, b) {
        return (counter[b] || 0) - (counter[a] || 0);
      }).map(function (key) {
        return (labelmap[key] || key) + ' ' + counter[key];
      }).join(' · ');
    }
    foot.appendChild(dom.el('p', { html:
      '题库共 <b>' + (summary.total || 0) + '</b> 题。' +
      '题型：' + dom.esc(names(summary.byTypeGroup, t)) + '。' +
      '难度：' + dom.esc(names(summary.byDifficulty, { basic: '基础', medium: '中等', hard: '困难' })) + '。' +
      '出处：' + dom.esc(names(summary.byKind, k)) + '。'
    }));
    foot.appendChild(dom.el('p', {
      text: '内容基准：同济大学数学系《高等数学》第七版（上、下册，高等教育出版社）；真题部分标注年份、卷别、题号与来源链接。'
    }));
    foot.appendChild(dom.el('p', {
      text: '判分口径：客观题自动判分（多选全对满分、少选与错选 0 分）；简答与计算题由你按采分点自评。'
    }));

    var sub = document.getElementById('hud-sub');
    if (sub) {
      sub.textContent = (summary.total || 0) + ' 题 · 按章节与知识点筛选 · 支持键盘快捷键';
    }
  }

  /* ---------------- 错误与空态 ---------------- */
  function showError(e) {
    state.error = e;
    var host = document.getElementById('quiz');
    if (!host) return;
    dom.clear(host);
    var box = dom.el('div', { class: 'q-card' });
    box.appendChild(dom.el('div', { class: 'banner err', text: '题库载入失败：' + (e && e.message ? e.message : e) }));
    var actions = dom.el('div', { class: 'q-actions' });
    var retry = dom.el('button', { type: 'button', class: 'btn btn-primary', text: '重试' });
    retry.addEventListener('click', function () {
      bank.reset();
      load().then(function () { renderCurrent(); refreshAll(); }).catch(showError);
    });
    actions.appendChild(retry);
    box.appendChild(actions);
    host.appendChild(box);
  }

  /* ---------------- 渲染 ---------------- */
  function currentQ() { return session.current(); }

  function buildView() {
    var q = currentQ();
    var s = session.raw;
    var rec = q ? s.answers[q.id] : null;
    return {
      index: session.currentIndex(),
      total: (s.order || []).length,
      picked: state.picked,
      record: rec,
      fav: q ? !!(store.get().favorites || {})[q.id] : false,
      onPick: handlePick,
      onSubmit: handleSubmit,
      onSelfGrade: handleSelfGrade,
      onToggleFav: toggleFav,
      onToggleWrong: toggleWrong,
      onRedo: handleRedo,
      onNav: nav
    };
  }

  function renderCurrent() {
    var host = document.getElementById('quiz');
    if (!host) return;
    var q = currentQ();
    // 选择缓冲的对齐规则在 core/picked.js：**只有切题才重置**，
    // 同题重渲染（选完选项、收藏、改主题）必须保留已选项。
    ns.picked.sync(state, q, session.raw.answers);
    render.render(host, q, buildView());
    if (state.focusLetter) {
      var sel = host.querySelector('[data-letter="' + state.focusLetter + '"]');
      if (sel) { sel.focus(); }
      state.focusLetter = null;
    }
    hud.update(stats.sessionMetrics());
    card.update();
  }

  function refreshAll() {
    hud.update(stats.sessionMetrics());
    card.rebuild();
    card.update();
    filters.setCount((session.raw.order || []).length);
    card.setBadge((session.raw.order || []).length);
  }

  /* ---------------- 交互 ---------------- */
  function handlePick(v) {
    var q = currentQ();
    if (!q || session.raw.answers[q.id]) return;
    if (q.type === 'blank') {
      state.picked = [v];
      return;                       // 不重渲染，否则输入框失焦
    }
    if (q.type === 'multi') {
      var i = state.picked.indexOf(v);
      if (i >= 0) state.picked.splice(i, 1); else state.picked.push(v);
    } else {
      state.picked = [v];
    }
    state.focusLetter = v;
    renderCurrent();
  }

  function pickByLetter(L) {
    var q = currentQ();
    if (!q || !q.options || !q.options.length) return;
    var idx = 'ABCDE'.indexOf(L);
    if (idx < 0 || idx >= q.options.length) return;
    handlePick(L);
  }

  function handleSubmit() {
    var q = currentQ();
    if (!q) return;
    if (session.raw.answers[q.id]) return;
    var subjective = (q.type === 'term' || q.type === 'short' || q.type === 'calc');
    if (subjective) {
      session.revealSubjective(q);
    } else {
      if (!state.picked || !state.picked.length) {
        dom.toast('还没作答，先选一个选项');
        return;
      }
      var res = judge.judgeObjective(q, state.picked);
      session.recordAnswer(q, {
        value: state.picked.slice(),
        correct: res.correct, earned: res.earned, full: res.full
      });
    }
    renderCurrent();
    refreshAll();
  }

  function handleSelfGrade(i, hit) {
    var q = currentQ();
    if (!q) return;
    var rec = session.raw.answers[q.id];
    if (!rec) return;
    var hits = (rec.pointsHit || []).slice();
    while (hits.length < (q.points || []).length) hits.push(null);
    hits[i] = hit;
    session.setSelfGrade(q.id, hits);
    renderCurrent();
    refreshAll();
  }

  function handleRedo() {
    var q = currentQ();
    if (!q) return;
    session.redo(q.id);
    ns.picked.clear(state);
    renderCurrent();
    refreshAll();
  }

  function toggleFav() {
    var q = currentQ();
    if (!q) return;
    var id = q.id;
    store.set(function (st) {
      if (!st.favorites) st.favorites = {};
      if (st.favorites[id]) delete st.favorites[id];
      else st.favorites[id] = { at: Date.now() };
    });
    dom.toast(store.get().favorites[id] ? '已收藏' : '已取消收藏');
    renderCurrent();
    card.update();
  }

  function toggleWrong() {
    var q = currentQ();
    if (!q) return;
    var id = q.id;
    var existed = !!(store.get().wrongBook || {})[id];
    var resolved = existed && store.get().wrongBook[id].resolved;
    store.set(function (st) {
      if (!st.wrongBook) st.wrongBook = {};
      if (existed && !resolved) delete st.wrongBook[id];
      else {
        st.wrongBook[id] = {
          firstWrongAt: Date.now(), lastWrongAt: Date.now(),
          wrongCount: (st.wrongBook[id] && st.wrongBook[id].wrongCount) || 1,
          resolved: false, note: q.knowledgePoint + '（第' + q.chapter + '章）'
        };
      }
    });
    dom.toast(store.get().wrongBook[id] ? '已加入错题本' : '已移出错题本');
    renderCurrent();
    card.update();
  }

  function nav(dir) {
    if (dir < 0) session.prev();
    else session.nextUnanswered();
    afterChange();
  }

  function afterChange() {
    renderCurrent();
    refreshAll();
  }

  function onFilterChanged() {
    session.refreshOrder();
    afterChange();
  }

  function practiceOnly(mode) {
    var f = session.raw.filter;
    f.onlyWrong = (mode === 'wrong');
    f.onlyFavorite = (mode === 'fav');
    session.refreshOrder();
    drawer.close();
    filters.build();
    afterChange();
  }

  function jumpToQuestion(qid) {
    var order = session.raw.order || [];
    var i = order.indexOf(qid);
    if (i < 0) {
      // 该题不在当前筛选结果里：放宽筛选后再跳
      var f = session.raw.filter;
      f.onlyWrong = false; f.onlyFavorite = false;
      session.refreshOrder();
      order = session.raw.order || [];
      i = order.indexOf(qid);
      filters.build();
    }
    if (i >= 0) session.gotoIdx(i);
    drawer.close();
    afterChange();
  }

  function cycleTheme() {
    var mode = theme.cycleTheme();
    dom.toast('主题：' + ({ auto: '跟随系统', light: '浅色', dark: '深色' })[mode]);
  }

  function toggleCardPanel() {
    var panel = document.getElementById('card-panel');
    if (!panel) return;
    panel.classList.toggle('open');
  }

  function wireHud() {
    var b = document.getElementById('btn-finish');
    if (b) b.addEventListener('click', function () {
      session.endSession();
      session.resetSession(false);
      session.refreshOrder();
      filters.build();
      afterChange();
      stats.recompute();          // 结算时固化累计统计
      dom.toast('本次作答已结算');
    });
    var r = document.getElementById('btn-reset');
    if (r) r.addEventListener('click', function () {
      if (!window.confirm('重新开始会清空本次作答记录，确定？')) return;
      session.resetSession(false);
      session.refreshOrder();
      filters.build();
      afterChange();
    });
    var s = document.getElementById('btn-stats');
    if (s) s.addEventListener('click', function () { drawer.toggle('stats'); });
    var w = document.getElementById('btn-wrong');
    if (w) w.addEventListener('click', function () { drawer.toggle('wrong'); });
    var f = document.getElementById('btn-fav');
    if (f) f.addEventListener('click', function () { drawer.toggle('fav'); });
    var c = document.getElementById('btn-card');
    if (c) c.addEventListener('click', toggleCardPanel);
    var k = document.getElementById('btn-keys');
    if (k) k.addEventListener('click', function () { drawer.toggle('keys'); });
    var t = document.getElementById('btn-theme');
    if (t) t.addEventListener('click', cycleTheme);
  }

  ns.app = { boot: boot, state: state };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})(window.QX = window.QX || {});
