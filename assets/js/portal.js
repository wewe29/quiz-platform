/* 复习刷题平台 — 门户逻辑
   数据源：subjects/registry.json（构建流水线生成，门户不手写学科信息）。
   进度读取：各学科子站的 localStorage 命名空间（同源，键 quiz-<id>-v2）。 */
(function () {
  'use strict';

  var THEME_KEY = 'quiz-platform-theme';
  var THEMES = [
    { key: 'auto', label: '主题：跟随系统' },
    { key: 'light', label: '主题：浅色' },
    { key: 'dark', label: '主题：深色' }
  ];

  function applyTheme() {
    var pref = 'auto';
    try { pref = localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) {}
    var dark = pref === 'dark' ||
      (pref === 'auto' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    var btn = document.getElementById('portal-theme');
    if (btn) {
      var t = null;
      THEMES.forEach(function (x) { if (x.key === pref) t = x; });
      btn.textContent = t ? t.label : '主题';
    }
  }
  function cycleTheme() {
    var pref = 'auto';
    try { pref = localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) {}
    var i = 0;
    THEMES.forEach(function (x, k) { if (x.key === pref) i = k; });
    try { localStorage.setItem(THEME_KEY, THEMES[(i + 1) % THEMES.length].key); } catch (e) {}
    applyTheme();
  }

  /** 读取一个学科的本地进度。返回 {answered, total, wrongPending, acc} 或 null。 */
  function readSubjectProgress(subjectId, total) {
    var raw = null;
    try { raw = localStorage.getItem('quiz-' + subjectId + '-v2'); } catch (e) { return null; }
    if (!raw) return null;
    var st;
    try { st = JSON.parse(raw); } catch (e) { return null; }
    if (!st || typeof st !== 'object') return null;
    var answered = {};
    var objA = 0, objC = 0;
    Object.keys(st.sessions || {}).forEach(function (sid) {
      var ans = (st.sessions[sid] || {}).answers || {};
      Object.keys(ans).forEach(function (qid) {
        answered[qid] = true;
        var a = ans[qid] || {};
        if (!a.selfGraded) { objA++; if (a.correct === true) objC++; }
      });
    });
    var wrongPending = 0;
    Object.keys(st.wrongBook || {}).forEach(function (qid) {
      if (!(st.wrongBook[qid] || {}).resolved) wrongPending++;
    });
    return {
      answered: Object.keys(answered).length,
      total: total,
      objA: objA, objC: objC,
      wrongPending: wrongPending
    };
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function pct(n, d) { return d > 0 ? Math.round(n / d * 100) : 0; }

  function renderCard(s) {
    var prog = readSubjectProgress(s.id, s.total);
    var answered = prog ? prog.answered : 0;
    var wrong = prog ? prog.wrongPending : 0;
    var acc = prog && prog.objA > 0 ? Math.round(prog.objC / prog.objA * 100) + '%' : '—';
    var h = '';
    h += '<a class="scard" href="' + esc(s.url) + '">';
    h += '<div class="sc-name">' + esc(s.name) + '</div>';
    h += '<div class="sc-textbook">' + esc(s.textbook) + '</div>';
    h += '<div class="sc-meta">';
    h += '<span class="sc-tag">' + s.total + ' 题</span>';
    h += '<span class="sc-tag">' + s.chapters + ' 章</span>';
    if (s.realExamTagged > 0) h += '<span class="sc-tag hot">真题改编 ' + s.realExamTagged + '</span>';
    h += '</div>';
    h += '<div class="sc-progress"><i style="width:' + pct(answered, s.total) + '%"></i></div>';
    h += '<div class="sc-row"><span>已答 ' + answered + ' / ' + s.total + '</span><span>待订正 ' + wrong + ' · 正确率 ' + acc + '</span></div>';
    h += '<div class="sc-cta">进入刷题 →</div>';
    h += '</a>';
    return h;
  }

  function boot() {
    applyTheme();
    var btn = document.getElementById('portal-theme');
    if (btn) btn.addEventListener('click', cycleTheme);
    if (window.matchMedia) {
      try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
          var pref = 'auto';
          try { pref = localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) {}
          if (pref === 'auto') applyTheme();
        });
      } catch (e) {}
    }

    fetch('subjects/registry.json').then(function (r) {
      if (!r.ok) throw new Error('registry HTTP ' + r.status);
      return r.json();
    }).then(function (reg) {
      var list = reg.subjects || [];
      var box = document.getElementById('cards');
      if (!list.length) {
        box.innerHTML = '<div class="empty">暂无学科。</div>';
        return;
      }
      var h = '';
      var aggAnswered = 0, aggTotal = 0, aggWrong = 0, aggObjA = 0, aggObjC = 0;
      list.forEach(function (s) {
        h += renderCard(s);
        var prog = readSubjectProgress(s.id, s.total);
        if (prog) {
          aggAnswered += prog.answered; aggTotal += s.total;
          aggWrong += prog.wrongPending; aggObjA += prog.objA; aggObjC += prog.objC;
        }
      });
      box.innerHTML = h;
      var agg = document.getElementById('aggregate');
      agg.hidden = false;
      document.getElementById('agg-answered').textContent = aggAnswered;
      document.getElementById('agg-acc').textContent =
        aggObjA > 0 ? Math.round(aggObjC / aggObjA * 100) + '%' : '—';
      document.getElementById('agg-wrong').textContent = aggWrong;
    }).catch(function (e) {
      document.getElementById('cards').innerHTML =
        '<div class="empty">学科列表加载失败（' + esc(e.message) + '）。请刷新重试。</div>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
