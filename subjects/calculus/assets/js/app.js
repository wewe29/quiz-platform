/* 大学《线性代数》题库刷题 — 应用逻辑（复习刷题平台子站版）
   数据来源：core/bank.js 异步装载 data/manifest.json + 分片（契约 quiz-platform-subject-v1）。
   状态存 localStorage（键见 subject.js 的 storageKey；从单文件版 la_quiz_v1 自动迁移）。
   与单文件版的差异只有三处：数据异步装载、存储命名空间、文案由 manifest 注入；
   判分/渲染/窗口化/答题卡/快捷键逻辑与单文件版保持同一份实现语义。

   渲染策略（题库扩到 500 题后必须窗口化）：
     单题聚焦模式 —— 一屏一题，KaTeX 只渲染当前题，任何设备都流畅（默认）；
     列表分页模式 —— 每页 PER_PAGE 题，翻页浏览。
   两种模式共用同一条 order（会话顺序）与 cursor（当前题下标），切换互丢进度。 */
(function () {
  'use strict';

  var SUBJECT = window.SUBJECT;
  if (!SUBJECT || !window.LABank || !window.LAStore) {
    document.getElementById('quiz').innerHTML =
      '<div class="empty">子站脚本加载不完整，请刷新重试。</div>';
    return;
  }

  var BANK = null;          // initApp 时注入：{ id, limits }
  var QUESTIONS = [];
  var META = null;          // manifest.json 原文（导出/诊断用）
  // 答案位置的判定阈值由构建脚本按 target.py 口径写进 manifest.json，
  // 页面不再写死数字——题库扩容后阈值自动跟着变，不会出现「口径打架」。
  var LIMITS = { singleMin: 0, singleMax: 9999, multiRange: 9999 };
  var KEY = SUBJECT.storageKey;
  var LEGACY_KEYS = SUBJECT.legacyKeys || [];
  var BANK_ID = '';

  /* ---------- 常量表 ---------- */
  var TYPE_GROUPS = [
    { key: 'single', label: '单选', full: 2 },
    { key: 'multi', label: '多选', full: 3 },
    { key: 'judge', label: '判断', full: 2 },
    { key: 'blank', label: '填空', full: 2 },
    { key: 'short', label: '简答与名词解释', full: null },
    { key: 'calc', label: '计算与分析题', full: 8 }
  ];
  var TYPE_GROUP_LABEL = {};
  TYPE_GROUPS.forEach(function (t) { TYPE_GROUP_LABEL[t.key] = t.label; });

  var DIFFS = [
    { key: 'basic', label: '基础' },
    { key: 'medium', label: '中等' },
    { key: 'hard', label: '困难' }
  ];
  var DIFF_LABEL = {};
  var DIFF_RANK = { basic: 0, medium: 1, hard: 2 };
  DIFFS.forEach(function (d, i) { DIFF_LABEL[d.key] = d.label; DIFF_LABEL[d.key + '_rank'] = i; });

  /* 章节表在 initApp 时由 manifest.subject.chapterLabels 生成（单一事实源在题库构建侧） */
  var CHAPTERS = [];
  var CHAPTER_LABEL = {};

  var LETTERS = ['A', 'B', 'C', 'D', 'E'];

  /** 列表分页模式的每页题数。500 题一页全渲染会让 KaTeX 卡死数秒，必须分页。 */
  var PER_PAGE = 20;
  var THEMES = [
    { key: 'auto', label: '主题：跟随系统' },
    { key: 'light', label: '主题：浅色' },
    { key: 'dark', label: '主题：深色' }
  ];

  /* ---------- DOM ---------- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var hud = $('#hud'), quizEl = $('#quiz');
  var storageOk = true;

  /* ---------- 工具 ---------- */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /** 轻量 Markdown：**加粗** 与 `行内代码`。
   *  只在数学片段之外替换——否则 $a**2$、$x^{**}$ 里的 ** 会被误当成加粗标记。
   *  拆分后偶数下标是文本、奇数下标是数学片段。 */
  function mdLite(s) {
    if (s == null || s === '') return '';
    var parts = String(s).split(/(\$\$[\s\S]*?\$\$|\$[^$]*\$)/);
    for (var i = 0; i < parts.length; i++) {
      if (i % 2 === 1) continue;
      parts[i] = parts[i]
        .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`\n]+)`/g, '<code>$1</code>');
    }
    return parts.join('');
  }
  function now() { return Date.now(); }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function fmtClock(ms) {
    var t = Math.max(0, Math.floor(ms / 1000));
    var h = Math.floor(t / 3600), m = Math.floor((t % 3600) / 60), s = t % 60;
    return (h > 0 ? h + ':' + pad2(m) : pad2(m)) + ':' + pad2(s);
  }
  function fmtDate(ts) {
    var d = new Date(ts);
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate()) + ' ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes());
  }

  /** 文本归一化：用于填空题判分 */
  function norm(s) {
    if (s == null) return '';
    var t = String(s);
    t = t.replace(/[\u3000\s]+/g, '');
    t = t.replace(/[，、；;]/g, ',');
    t = t.replace(/[（(]/g, '(').replace(/[）)]/g, ')');
    t = t.replace(/[。．]/g, '.');
    t = t.replace(/[×✕]/g, '*').replace(/[÷]/g, '/');
    t = t.replace(/[－—–]/g, '-');
    t = t.replace(/[＝]/g, '=');
    t = t.replace(/[＄$]/g, '');
    t = t.replace(/\\\\/g, '');
    t = t.replace(/\\left|\\right/g, '');
    t = t.replace(/\\[,;!]/g, '');
    t = t.replace(/[{}]/g, '');
    t = t.replace(/[·⋅•]/g, '*');
    t = t.replace(/[，]/g, ',');
    t = t.replace(/^\.+|\.+$/g, '');
    return t.toLowerCase();
  }
  function blankMatch(input, q) {
    var v = norm(input);
    if (!v) return false;
    var accepts = (q.accept || q.answer || []).map(norm);
    for (var i = 0; i < accepts.length; i++) {
      if (accepts[i] === v) return true;
    }
    // 允许数值等价：3/2 与 1.5、1/2 与 0.5
    var nv = numOf(v);
    if (nv !== null) {
      for (var j = 0; j < accepts.length; j++) {
        var na = numOf(accepts[j]);
        if (na !== null && Math.abs(na - nv) < 1e-9) return true;
      }
    }
    return false;
  }
  function numOf(s) {
    if (!/^-?\d+(\.\d+)?$/.test(s)) return null;
    return parseFloat(s);
  }
  /** 数值型答案（如 "1/2"）求值，用于展示参考答案 */
  function evalNum(s) {
    var m = /^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/.exec(norm(s));
    if (m) return parseFloat(m[1]) / parseFloat(m[2]);
    var n = numOf(norm(s));
    return n;
  }

  /* ---------- 状态 ---------- */
  var state = null;
  var session = null;

  function blankState() {
    return {
      v: 1, bank: BANK_ID, updatedAt: 0,
      sessions: {}, wrongBook: {},
      stats: { byType: {}, byDifficulty: {}, byChapter: {}, answerPosition: { A: 0, B: 0, C: 0, D: 0 }, multiLetter: { A: 0, B: 0, C: 0, D: 0 }, totalAnswered: 0, totalCorrect: 0, totalEarned: 0, totalFull: 0 },
      settings: { order: 'difficulty_desc', shuffle: false, mode: 'single', theme: 'auto' }
    };
  }

  function readRaw(key) {
    try { return window.localStorage.getItem(key); } catch (e) { storageOk = false; return null; }
  }
  function writeRaw(key, val) {
    try { window.localStorage.setItem(key, val); return true; } catch (e) { storageOk = false; return false; }
  }

  function load() {
    var boot = LAStore.bootstrap({ storageKey: KEY, legacyKeys: LEGACY_KEYS });
    var data = boot.state;
    if (!data) {
      state = blankState();
      return;
    }
    if (boot.migratedFrom) {
      console.info('[store] 已从 ' + boot.migratedFrom + ' 迁移进度到 ' + KEY +
        '（旧键保留未动）');
    }
    var b = blankState();
    state = {
      v: 1, bank: BANK_ID, updatedAt: data.updatedAt || 0,
      sessions: data.sessions || {}, wrongBook: data.wrongBook || {},
      stats: Object.assign(b.stats, data.stats || {}),
      settings: Object.assign(b.settings, data.settings || {})
    };
    state.stats.answerPosition = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.answerPosition || {});
    state.stats.multiLetter = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.multiLetter || {});
  }

  function save() {
    state.updatedAt = now();
    var ok = writeRaw(KEY, JSON.stringify(state));
    if (!ok) showStorageWarn();
  }

  /** 多标签页保护：写入前合并外部更新的 wrongBook / sessions */
  function saveMerged() {
    var raw = readRaw(KEY);
    if (raw) {
      try {
        var other = JSON.parse(raw);
        if (other && other.v === 1 && other.updatedAt > state.updatedAt) {
          Object.keys(other.wrongBook || {}).forEach(function (k) {
            var o = other.wrongBook[k], m = state.wrongBook[k];
            if (!m) { state.wrongBook[k] = o; }
            else {
              m.wrongCount = Math.max(m.wrongCount || 0, o.wrongCount || 0);
              m.firstWrongAt = Math.min(m.firstWrongAt || Infinity, o.firstWrongAt || Infinity);
              m.lastWrongAt = Math.max(m.lastWrongAt || 0, o.lastWrongAt || 0);
              if (o.resolved) m.resolved = true;
              if (!m.note && o.note) m.note = o.note;
            }
          });
          Object.keys(other.sessions || {}).forEach(function (k) {
            if (!state.sessions[k]) state.sessions[k] = other.sessions[k];
            else {
              var a = state.sessions[k], c = other.sessions[k];
              var at = a.updatedAt || 0, ct = c.updatedAt || 0;
              if (ct > at) state.sessions[k] = c;
            }
          });
        }
      } catch (e) {}
    }
    save();
  }

  function showStorageWarn() {
    storageOk = false;
    var w = $('#storage-warn');
    if (w) w.hidden = false;
  }

  /* ---------- 主题 ---------- */
  /** 实际生效的主题由 JS 解析（auto → 跟随系统）后写到 <html data-theme>，
   *  CSS 只写一份 [data-theme="dark"] 覆盖块，避免媒体查询与选择器无法合并的重复。 */
  function applyTheme() {
    var pref = (state && state.settings.theme) || 'auto';
    var dark = pref === 'dark' ||
      (pref === 'auto' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    var btn = $('#btn-theme');
    if (btn) {
      var t = null;
      THEMES.forEach(function (x) { if (x.key === pref) t = x; });
      btn.textContent = t ? t.label : '主题';
    }
  }
  function cycleTheme() {
    var cur = (state.settings.theme || 'auto');
    var i = 0;
    THEMES.forEach(function (x, k) { if (x.key === cur) i = k; });
    state.settings.theme = THEMES[(i + 1) % THEMES.length].key;
    applyTheme();
    saveMerged();
  }

  /* ---------- Session ---------- */
  function newSessionId() {
    var d = new Date();
    return 's-' + d.getFullYear() + pad2(d.getMonth() + 1) + pad2(d.getDate()) + '-' +
      pad2(d.getHours()) + pad2(d.getMinutes()) + pad2(d.getSeconds()) + '-' + Math.floor(Math.random() * 1000);
  }
  function latestActive() {
    var ids = Object.keys(state.sessions).filter(function (k) { return state.sessions[k].status === 'active'; });
    if (!ids.length) return null;
    ids.sort(function (a, b) { return (state.sessions[b].startedAt || 0) - (state.sessions[a].startedAt || 0); });
    return state.sessions[ids[0]];
  }
  function ensureSession() {
    var s = latestActive();
    if (!s) {
      s = {
        id: newSessionId(), startedAt: now(), updatedAt: now(), endedAt: null,
        elapsedMs: 0, lastTick: null, hidden: false,
        filter: { types: [], diffs: [], chapters: [], onlyWrong: false, kw: '' },
        order: [], cursor: 0, status: 'active', answers: {}
      };
      state.sessions[s.id] = s;
    }
    if (!s.answers) s.answers = {};
    if (!s.filter) s.filter = { types: [], diffs: [], chapters: [], onlyWrong: false, kw: '' };
    // 兼容旧记录：早期版本把 pointsHit 初始化成全 false（= 已判「未得到」），
    // 这里迁移成 null（尚未自评），否则老记录一打开就显示「未得到任何采分点」。
    Object.keys(s.answers).forEach(function (k) {
      var a = s.answers[k];
      if (!a || !a.selfGraded || !a.pointsHit || !a.pointsHit.length) return;
      var allFalse = a.pointsHit.every(function (h) { return h === false; });
      if (allFalse && !a.earned) a.pointsHit = a.pointsHit.map(function () { return null; });
    });
    session = s;
    return s;
  }
  function endSession() {
    if (!session) return;
    session.status = 'finished';
    session.endedAt = now();
    saveMerged();
  }
  function newSession(keepWrong) {
    if (session) { session.status = 'finished'; session.endedAt = now(); }
    session = {
      id: newSessionId(), startedAt: now(), updatedAt: now(), endedAt: null,
      elapsedMs: 0, lastTick: null, hidden: false,
      filter: keepWrong ? { types: [], diffs: [], chapters: [], onlyWrong: true, kw: '' }
                        : { types: [], diffs: [], chapters: [], onlyWrong: false, kw: '' },
      order: [], cursor: 0, status: 'active', answers: {}
    };
    state.sessions[session.id] = session;
    saveMerged();
  }

  /* ---------- 计时 ---------- */
  var timerHandle = null;
  function tick() {
    if (!session || session.status !== 'active') return;
    var t = now();
    if (session.lastTick && !session.hidden) session.elapsedMs += (t - session.lastTick);
    session.lastTick = t;
    updateHudTime();
  }
  function startTimer() {
    if (timerHandle) clearInterval(timerHandle);
    timerHandle = setInterval(tick, 1000);
  }
  document.addEventListener('visibilitychange', function () {
    if (!session) return;
    if (document.hidden) {
      session.hidden = true;
      session.lastTick = now();
      saveMerged();
    } else {
      session.hidden = false;
      session.lastTick = now();
    }
  });
  window.addEventListener('beforeunload', function () {
    if (session && session.status === 'active') { tick(); saveMerged(); }
  });

  /* ---------- 筛选与排序 ---------- */
  function passes(q, f) {
    if (f.types && f.types.length && f.types.indexOf(q.typeGroup) < 0) return false;
    if (f.diffs && f.diffs.length && f.diffs.indexOf(q.difficulty) < 0) return false;
    if (f.chapters && f.chapters.length && f.chapters.indexOf(q.chapter) < 0) return false;
    if (f.onlyWrong && !state.wrongBook[q.id]) return false;
    if (f.kw) {
      var k = f.kw.toLowerCase();
      var hay = (q.stem + ' ' + (q.explanation || '') + ' ' + (q.knowledgePoint || '') + ' ' + (q.source && q.source.text || '')).toLowerCase();
      if (hay.indexOf(k) < 0) return false;
    }
    return true;
  }
  function computeOrder() {
    var f = session.filter;
    var list = QUESTIONS.filter(function (q) { return passes(q, f); });
    var mode = state.settings.order || 'difficulty_desc';
    list.sort(function (a, b) {
      if (mode === 'difficulty_asc') {
        var d = DIFF_RANK[a.difficulty] - DIFF_RANK[b.difficulty];
        if (d !== 0) return d;
      } else if (mode === 'difficulty_desc') {
        var d2 = DIFF_RANK[b.difficulty] - DIFF_RANK[a.difficulty];
        if (d2 !== 0) return d2;
      } else if (mode === 'chapter') {
        if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      } else if (mode === 'type') {
        var ta = TYPE_GROUPS.findIndex(function (t) { return t.key === a.typeGroup; });
        var tb = TYPE_GROUPS.findIndex(function (t) { return t.key === b.typeGroup; });
        if (ta !== tb) return ta - tb;
        if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      }
      if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      var ga = TYPE_GROUPS.findIndex(function (t) { return t.key === a.typeGroup; });
      var gb = TYPE_GROUPS.findIndex(function (t) { return t.key === b.typeGroup; });
      if (ga !== gb) return ga - gb;
      return a.idx - b.idx;
    });
    if (state.settings.shuffle) {
      for (var i = list.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = list[i]; list[i] = list[j]; list[j] = tmp;
      }
    }
    return list.map(function (q) { return q.id; });
  }

  /* ---------- 判分 ---------- */
  function fullScore(q) {
    if (q.type === 'single') return 2;
    if (q.type === 'multi') return 3;
    if (q.type === 'judge') return 2;
    if (q.type === 'blank') return 2;
    // 主观题：满分 = 采分点分值之和。采分点数随学科/题目变化
    // （线代固定 term2/short3/calc4 点×2 分 → 4/6/8；高数 calc 有 1–6 点不等），
    // 固定满分会让少采分点的题永远到不了满分、错题本被污染。
    var pts = q.points || [];
    if (pts.length) {
      var s = 0;
      for (var i = 0; i < pts.length; i++) s += (pts[i] && pts[i].partial) || 2;
      return s;
    }
    if (q.type === 'term') return 4;
    if (q.type === 'short') return 6;
    if (q.type === 'calc') return 8;
    return 0;
  }
  function multiVerdict(picked, answer) {
    var ans = answer.slice().sort().join(',');
    var pk = picked.slice().sort().join(',');
    if (pk === ans) return 'correct';
    if (picked.length === 0) return 'blank';
    var hasWrong = picked.some(function (p) { return answer.indexOf(p) < 0; });
    if (hasWrong) return 'wrong';       // 错选：含任一非答案项
    return 'partial';                    // 少选：真子集且无错项 → 0 分
  }
  function judgeObjective(q, picked) {
    var earned = 0, correct = null;
    if (q.type === 'single') {
      correct = (picked.length === 1 && picked[0] === q.answer[0]);
      earned = correct ? 2 : 0;
    } else if (q.type === 'multi') {
      var v = multiVerdict(picked, q.answer);
      correct = (v === 'correct');
      earned = correct ? 3 : 0;
      if (v === 'partial' || v === 'wrong') correct = false;
    } else if (q.type === 'judge') {
      correct = (picked.length === 1 && picked[0] === q.answer[0]);
      earned = correct ? 2 : 0;
    } else if (q.type === 'blank') {
      var ok = blankMatch(picked[0] || '', q);
      correct = ok;
      earned = ok ? 2 : 0;
    }
    return { correct: correct, earned: earned, full: fullScore(q) };
  }

  function recordAnswer(q, rec) {
    var prev = session.answers[q.id];
    var attempts = (prev ? (prev.attempts || 1) : 0) + 1;
    session.answers[q.id] = {
      type: q.type, value: rec.value, submittedAt: now(),
      correct: rec.correct, earned: rec.earned, full: rec.full,
      selfGraded: !!rec.selfGraded, pointsHit: rec.pointsHit || null, attempts: attempts
    };
    // 错题本：得分率 < 100% 入册
    if (rec.earned < rec.full) {
      var wb = state.wrongBook[q.id];
      if (!wb) {
        wb = state.wrongBook[q.id] = { firstWrongAt: now(), lastWrongAt: now(), wrongCount: 1, resolved: false, note: '' };
      } else {
        wb.wrongCount = (wb.wrongCount || 0) + 1;
        wb.lastWrongAt = now();
        wb.resolved = false;
      }
      if (!wb.note) wb.note = (q.knowledgePoint || '') + '（' + CHAPTER_LABEL[q.chapter] + '）';
    } else if (state.wrongBook[q.id]) {
      state.wrongBook[q.id].resolved = true;
      state.wrongBook[q.id].lastWrongAt = now();
    }
    session.updatedAt = now();
    saveMerged();
  }

  /* ---------- 统计 ---------- */
  function recomputeStats() {
    var st = state.stats;
    st.byType = {}; st.byDifficulty = {}; st.byChapter = {};
    st.totalAnswered = 0; st.totalCorrect = 0; st.totalEarned = 0; st.totalFull = 0;
    var objAnswered = 0, objCorrect = 0;
    Object.keys(state.sessions).forEach(function (sid) {
      var s = state.sessions[sid];
      var ans = s.answers || {};
      Object.keys(ans).forEach(function (qid) {
        var a = ans[qid];
        var q = qById[qid];
        if (!q) return;
        var g = q.typeGroup;
        st.byType[g] = st.byType[g] || { answered: 0, earned: 0, full: 0 };
        st.byType[g].answered++; st.byType[g].earned += a.earned; st.byType[g].full += a.full;
        var dd = q.difficulty;
        st.byDifficulty[dd] = st.byDifficulty[dd] || { answered: 0, earned: 0, full: 0 };
        st.byDifficulty[dd].answered++; st.byDifficulty[dd].earned += a.earned; st.byDifficulty[dd].full += a.full;
        st.byChapter[q.chapter] = st.byChapter[q.chapter] || { answered: 0, earned: 0, full: 0 };
        st.byChapter[q.chapter].answered++; st.byChapter[q.chapter].earned += a.earned; st.byChapter[q.chapter].full += a.full;
        st.totalAnswered++; st.totalEarned += a.earned; st.totalFull += a.full;
        if (a.correct === true) st.totalCorrect++;
        if (!a.selfGraded) { objAnswered++; if (a.correct === true) objCorrect++; }
      });
    });
    st.objectiveAnswered = objAnswered;
    st.objectiveCorrect = objCorrect;
  }

  /** 答案位置统计：基于题库本体，实测而非声称 */
  function answerPositionStats() {
    var single = { A: 0, B: 0, C: 0, D: 0 };
    var multi = { A: 0, B: 0, C: 0, D: 0 };
    QUESTIONS.forEach(function (q) {
      if (q.type === 'single' && q.answer[0]) single[q.answer[0]] = (single[q.answer[0]] || 0) + 1;
      if (q.type === 'multi') q.answer.forEach(function (L) { multi[L] = (multi[L] || 0) + 1; });
    });
    return { single: single, multi: multi };
  }

  /* ---------- 渲染：筛选器 ---------- */
  function renderFilters() {
    var f = session.filter;
    function chipRow(container, items, selected, key) {
      container.innerHTML = '';
      items.forEach(function (it) {
        var lab = document.createElement('label');
        lab.className = 'chip' + (selected.indexOf(it.key) >= 0 ? ' is-on' : '');
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = selected.indexOf(it.key) >= 0;
        cb.addEventListener('change', function () {
          var arr = f[key].slice();
          var i = arr.indexOf(it.key);
          if (cb.checked && i < 0) arr.push(it.key);
          if (!cb.checked && i >= 0) arr.splice(i, 1);
          f[key] = arr;
          refreshOrder();
          render();
        });
        lab.appendChild(cb);
        lab.appendChild(document.createTextNode(it.label));
        var c = document.createElement('span');
        c.className = 'cnt';
        c.textContent = it.count != null ? it.count : '';
        lab.appendChild(c);
        container.appendChild(lab);
      });
    }
    var cntType = {}, cntDiff = {}, cntCh = {};
    QUESTIONS.forEach(function (q) {
      cntType[q.typeGroup] = (cntType[q.typeGroup] || 0) + 1;
      cntDiff[q.difficulty] = (cntDiff[q.difficulty] || 0) + 1;
      cntCh[q.chapter] = (cntCh[q.chapter] || 0) + 1;
    });
    chipRow($('#f-types'), TYPE_GROUPS.map(function (t) { return { key: t.key, label: t.label, count: cntType[t.key] || 0 }; }), f.types, 'types');
    chipRow($('#f-diffs'), DIFFS.map(function (d) { return { key: d.key, label: d.label, count: cntDiff[d.key] || 0 }; }), f.diffs, 'diffs');
    // 章节短标签：非教材章（如 ML 的「综合测试卷」）由 manifest.subject.chapterShortLabels 提供
    var chapterShort = (META && META.subject && META.subject.chapterShortLabels) || {};
    chipRow($('#f-chapters'), CHAPTERS.map(function (c) {
      return { key: c.n, label: chapterShort[c.n] || ('第' + c.n + '章'), count: cntCh[c.n] || 0 };
    }), f.chapters, 'chapters');

    $('#f-order').value = state.settings.order;
    $('#f-mode').value = state.settings.mode || 'single';
    $('#f-shuffle').checked = !!state.settings.shuffle;
    $('#f-wrongonly').checked = !!f.onlyWrong;
    if ($('#f-kw').value !== (f.kw || '')) $('#f-kw').value = f.kw || '';
  }

  function refreshOrder() {
    session.order = computeOrder();
    if (session.cursor >= session.order.length) session.cursor = Math.max(0, session.order.length - 1);
    session.updatedAt = now();
    writeHash();   // 筛选状态同步到 URL（可分享/刷新还原）
  }

  /** 恢复的会话顺序可能来自**旧题库**（题库扩容/换版后旧记录仍在）。
   *  顺序里出现当前题库没有的题 id，或题数与当前筛选结果对不上，都算失效，
   *  必须重建——否则进度条会显示成旧题库的题数（如 1 / 36 而实际题库更多）。 */
  function orderIsStale() {
    var o = session.order || [];
    for (var i = 0; i < o.length; i++) if (!qById[o[i]]) return true;
    return o.length !== computeOrder().length;
  }

  /* ---------- 渲染：题目 ---------- */
  /* qById 在 initApp 里随异步题库注入时重建（模块加载时题库还没到） */
  var qById = {};

  function typeLabel(q) {
    if (q.type === 'term') return '名词解释';
    if (q.type === 'short') return '简答';
    if (q.type === 'calc') return '计算与分析';
    return TYPE_GROUP_LABEL[q.typeGroup];
  }

  /** 当前视窗应渲染的题 id 列表（窗口化：绝不一次渲染全部 500 题）。
   *  单题模式渲染 cursor 指向的 1 题；列表模式渲染 cursor 所在的整页。 */
  function visibleIds() {
    var ids = session.order;
    if (!ids.length) return [];
    if (state.settings.mode === 'single') {
      var cur = ids[Math.min(session.cursor, ids.length - 1)];
      return cur ? [cur] : [];
    }
    var page = Math.min(Math.floor(session.cursor / PER_PAGE), Math.ceil(ids.length / PER_PAGE) - 1);
    return ids.slice(page * PER_PAGE, (page + 1) * PER_PAGE);
  }

  function render() {
    var ids = visibleIds();
    var list = ids.map(function (id) { return qById[id]; }).filter(Boolean);
    var html = '';
    if (!list.length) {
      html = '<div class="empty">当前筛选条件下没有题目。请调整左侧筛选，或点「重新开始」。</div>';
    } else {
      html += pagerHtml();
      list.forEach(function (q, i) {
        html += cardHtml(q, session.order.indexOf(q.id));
      });
      html += pagerHtml();
    }
    quizEl.innerHTML = html;
    bindCards();
    bindPager();
    updateHud();
    if (!$('#panel-sheet').hidden) renderSheet();
    renderMathAll();
  }

  /** 翻页条：单题模式 = 上一题/下一题；列表模式 = 页码导航。
   *  题卡自带的前后题按钮保留（移动端翻页条不便），两者并存。 */
  function pagerHtml() {
    var n = session.order.length;
    if (!n) return '';
    var h = '<nav class="pager" aria-label="翻页导航">';
    if (state.settings.mode === 'single') {
      h += '<button type="button" class="btn btn-sm" data-role="pg-prev"' + (session.cursor <= 0 ? ' disabled' : '') + '>← 上一题</button>';
      h += '<span class="pager-info">' + (session.cursor + 1) + ' / ' + n + '</span>';
      h += '<button type="button" class="btn btn-sm" data-role="pg-next"' + (session.cursor >= n - 1 ? ' disabled' : '') + '>下一题 →</button>';
      h += '<button type="button" class="btn btn-sm btn-ghost" data-role="pg-unanswered">跳到未作答</button>';
    } else {
      var pages = Math.ceil(n / PER_PAGE);
      var page = Math.min(Math.floor(session.cursor / PER_PAGE), pages - 1);
      h += '<button type="button" class="btn btn-sm" data-role="pg-prev"' + (page <= 0 ? ' disabled' : '') + '>← 上一页</button>';
      for (var p = 0; p < pages; p++) {
        h += '<button type="button" class="btn btn-sm pg-num' + (p === page ? ' is-cur' : '') +
          '" data-role="pg-page" data-page="' + p + '">' + (p + 1) + '</button>';
      }
      h += '<button type="button" class="btn btn-sm" data-role="pg-next"' + (page >= pages - 1 ? ' disabled' : '') + '>下一页 →</button>';
      h += '<span class="pager-info">第 ' + (page + 1) + ' / ' + pages + ' 页</span>';
    }
    h += '</nav>';
    return h;
  }

  function bindPager() {
    $$('[data-role^="pg-"]', quizEl).forEach(function (btn) {
      var role = btn.getAttribute('data-role');
      if (role === 'sg') return;
      btn.addEventListener('click', function () {
        if (role === 'pg-prev') {
          gotoIdx(session.cursor - 1);
        } else if (role === 'pg-next') {
          gotoIdx(session.cursor + 1);
        } else if (role === 'pg-page') {
          var p = parseInt(btn.getAttribute('data-page'), 10);
          gotoIdx(p * PER_PAGE);
        } else if (role === 'pg-unanswered') {
          gotoUnanswered(session.cursor);
        }
      });
    });
  }

  function cardHtml(q, idx) {
    var a = session.answers[q.id];
    var stateCls = '';
    if (a) {
      if (a.selfGraded) stateCls = a.earned >= a.full ? ' is-answered' : (a.earned > 0 ? ' is-partial' : ' is-wrong');
      else stateCls = a.correct ? ' is-answered' : ' is-wrong';
    }
    var isExt = q.source && q.source.kind === 'extension';
    var h = '';
    h += '<article class="qcard' + stateCls + '" id="card-' + q.id + '" data-qid="' + q.id + '">';
    h += '<div class="q-head">';
    h += '<span class="q-no">第 ' + (idx + 1) + ' / ' + session.order.length + ' 题</span>';
    h += '<span class="q-tag t-type">' + esc(typeLabel(q)) + '</span>';
    h += '<span class="q-tag t-diff-' + q.difficulty + '">' + DIFF_LABEL[q.difficulty] + '</span>';
    h += '<span class="q-tag">' + esc(CHAPTER_LABEL[q.chapter]) + '</span>';
    if (isExt) h += '<span class="q-tag t-ext">选学·引申</span>';
    h += '<span class="q-kp">知识点 ' + esc(q.knowledgePoint || '—') + '</span>';
    h += '</div>';
    h += '<div class="q-stem">' + mdLite(q.stem) + '</div>';

    var opts = q.options;
    if ((!opts || !opts.length) && q.type === 'judge') opts = ['正确', '错误'];
    if (opts && opts.length) {
      h += '<div class="opts' + (a ? ' is-locked' : '') + '" data-role="opts">';
      opts.forEach(function (o, oi) {
        var L = LETTERS[oi];
        var cls = '';
        if (a && q.type !== 'short' && q.type !== 'calc' && q.type !== 'term') {
          var isAns = q.answer.indexOf(L) >= 0;
          var isPicked = (a.value || []).indexOf(L) >= 0;
          if (isAns) cls = ' is-correct';
          else if (isPicked) cls = ' is-wrong';
        }
        var inputType = q.type === 'multi' ? 'checkbox' : 'radio';
        var checked = a ? ((a.value || []).indexOf(L) >= 0 ? ' checked' : '') : '';
        h += '<label class="opt' + cls + '">';
        h += '<input type="' + inputType + '" name="opt-' + q.id + '" value="' + L + '"' + checked + (a ? ' disabled' : '') + '>';
        h += '<span class="opt-letter">' + L + '</span><span class="opt-text">' + mdLite(o) + '</span>';
        h += '</label>';
      });
      h += '</div>';
    }

    if (q.type === 'blank') {
      var v = a ? (a.value || [''])[0] : '';
      var cls2 = a ? (a.correct ? ' is-correct' : ' is-wrong') : '';
      h += '<div class="fill-in"><input type="text" data-role="blank" value="' + esc(v) + '" placeholder="在此填写答案"' + (a ? ' disabled' : '') + ' class="' + cls2 + '"></div>';
    }

    h += '<div class="q-actions">';
    if (!a) {
      if (q.type === 'multi') {
        h += '<button type="button" class="btn btn-primary" data-role="submit-multi">确认作答</button>';
      } else if (q.type === 'blank') {
        h += '<button type="button" class="btn btn-primary" data-role="submit-blank">提交</button>';
      } else if (q.type === 'short' || q.type === 'calc' || q.type === 'term') {
        h += '<button type="button" class="btn btn-primary" data-role="submit-open">提交并看解析</button>';
      } else {
        h += '<button type="button" class="btn btn-primary" data-role="submit-auto">点选选项即自动提交</button>';
      }
    } else {
      h += '<button type="button" class="btn" data-role="redo">重新作答</button>';
    }
    h += '<button type="button" class="btn btn-ghost" data-role="prev">上一题</button>';
    h += '<button type="button" class="btn btn-ghost" data-role="next">下一题</button>';
    h += '<button type="button" class="btn btn-ghost" data-role="next-unanswered">跳到下一道未作答</button>';
    h += '</div>';

    if (a) h += explanationHtml(q, a);
    h += '</article>';
    return h;
  }

  function explanationHtml(q, a) {
    var h = '';
    var verdictCls, verdictText;
    if (a.selfGraded) {
      var decided = (a.pointsHit || []).some(function (h) { return h === true || h === false; });
      if (!decided) { verdictCls = 'mid'; verdictText = '— 请在下方勾选采分点进行自评'; }
      else if (a.earned >= a.full) { verdictCls = 'ok'; verdictText = '✔ 自评：全部采分点得到（满分 ' + a.full + ' 分）'; }
      else if (a.earned > 0) { verdictCls = 'mid'; verdictText = '◐ 自评：部分采分点未得到（' + a.earned + ' / ' + a.full + ' 分）'; }
      else { verdictCls = 'bad'; verdictText = '✘ 自评：未得到任何采分点（0 / ' + a.full + ' 分）'; }
    } else if (a.correct === true) { verdictCls = 'ok'; verdictText = '✔ 回答正确（' + a.earned + ' / ' + a.full + ' 分）'; }
    else if (a.correct === false) { verdictCls = 'bad'; verdictText = '✘ 回答错误（0 / ' + a.full + ' 分）'; }
    else { verdictCls = 'mid'; verdictText = '— 已作答'; }

    h += '<div class="answer-box ' + verdictCls + '">';
    h += '<div class="verdict ' + verdictCls + '">' + verdictText + '</div>';

    if (q.type === 'multi') {
      var picked = a.value || [];
      var ans = q.answer;
      if (!a.correct && picked.length && !picked.some(function (p) { return ans.indexOf(p) < 0; })) {
        h += '<p class="mis">⚠️ <b>少选</b>：所选项均为正确选项的子集，按规则计 <b>0 分</b>。</p>';
      } else if (!a.correct && picked.some(function (p) { return ans.indexOf(p) < 0; })) {
        h += '<p class="mis">⚠️ <b>错选</b>：含非正确选项，按规则计 <b>0 分</b>。</p>';
      }
    }
    if (q.type === 'blank' && !a.correct) {
      h += '<p class="mis">⚠️ 本空正确答案：<b>' + esc((q.answer || []).join(' 或 ')) + '</b></p>';
    }

    if (q.type === 'term' || q.type === 'short' || q.type === 'calc') {
      h += '<div class="ref-answer"><b>参考答案：</b>' + mdLite(q.answerText || '') + '</div>';
      if (q.points && q.points.length) {
        h += '<div class="selfgrade"><div class="selfgrade-h">采分点自评（每点 ' + (q.points[0].partial || 2) + ' 分）</div><div class="sg-list">';
        q.points.forEach(function (p, pi) {
          var hit = (a.pointsHit || [])[pi];
          var cls = hit === true ? ' hit' : (hit === false ? ' miss' : '');
          var mark = hit === true ? '✔' : (hit === false ? '✘' : '○');
          // 采分点必须始终可勾选：pointsHit 用 null 表示「尚未自评」。
          // 早前用 false 初始化会被渲染成 disabled，自评功能整个点不动。
          h += '<div class="sg-item' + cls + '"><label><input type="checkbox" data-role="sg" data-pi="' + pi + '"' +
            (hit === true ? ' checked' : '') + '><span class="sg-mark">' + mark + '</span>' +
            '<span>' + esc(p.text) + '</span></label></div>';
        });
        h += '</div><div class="sg-score">本题得分：<b>' + a.earned + '</b> / ' + a.full + ' 分（勾选「得到」即计入；取消勾选记为未得到）</div></div>';
      }
    }

    h += '<div class="expl">' + mdLite(q.explanation || '') + '</div>';
    if (q.misconception) {
      // 题库里的易错点文本本身常已带「⚠️易错点：」前缀，避免重复显示两遍
      var misLabel = /^\s*⚠/.test(q.misconception) ? '' : '⚠️ <b>易错点：</b>';
      h += '<div class="mis">' + misLabel + mdLite(q.misconception) + '</div>';
    }
    if (q.source && q.source.text) {
      h += '<div class="src">📖 <b>考点出处：</b><code>' + esc(q.source.text) + '</code>' +
        (q.source.kind === 'extension' ? '（引申内容）' : '') + '</div>';
    }
    if (q.extension) h += '<div class="ext"><b>引申</b>：' + mdLite(q.extension) + '</div>';
    if (q.tags && q.tags.length) {
      h += '<div class="tags">';
      q.tags.forEach(function (t) { h += '<span class="tag">' + esc(t) + '</span>'; });
      h += '</div>';
    }
    h += '</div>';
    return h;
  }

  /* ---------- 事件绑定 ---------- */
  function bindCards() {
    $$('.qcard', quizEl).forEach(function (card) {
      var qid = card.getAttribute('data-qid');
      var q = qById[qid];
      var a = session.answers[qid];

      // 选项（单选/判断自动提交，多选需确认）
      $$('input[type="radio"],input[type="checkbox"]', card).forEach(function (input) {
        if (input.getAttribute('data-role') === 'sg') return;
        input.addEventListener('change', function () {
          if (a) return;
          if (q.type === 'multi') {
            // 多选：仅更新选中态，等待「确认作答」
            $$('.opt', card).forEach(function (o) {
              o.classList.remove('is-correct', 'is-wrong');
            });
            return;
          }
          var picked = [input.value];
          var rec = judgeObjective(q, picked);
          recordAnswer(q, { value: picked, correct: rec.correct, earned: rec.earned, full: rec.full });
          render();
          scrollToCard(qid);
        });
      });

      // 填空：Enter 提交
      var bi = $('[data-role="blank"]', card);
      if (bi && !a) {
        bi.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); submitBlank(q, card); } });
      }

      // 按钮
      $$('[data-role]', card).forEach(function (btn) {
        var role = btn.getAttribute('data-role');
        if (role === 'sg') return;
        btn.addEventListener('click', function () {
          if (role === 'submit-multi') {
            var picked = $$('input[type="checkbox"]', card).filter(function (x) { return x.checked; }).map(function (x) { return x.value; });
            var rec = judgeObjective(q, picked);
            recordAnswer(q, { value: picked, correct: rec.correct, earned: rec.earned, full: rec.full });
            render(); scrollToCard(qid);
          } else if (role === 'submit-blank') {
            submitBlank(q, card);
          } else if (role === 'submit-open') {
            var pts = (q.points || []).map(function () { return null; });   // null = 尚未自评
            recordAnswer(q, { value: null, correct: null, earned: 0, full: fullScore(q), selfGraded: true, pointsHit: pts });
            render(); scrollToCard(qid);
          } else if (role === 'redo') {
            redo(qid);
          } else if (role === 'prev') {
            gotoIdx(idxOf(qid) - 1);
          } else if (role === 'next') {
            gotoIdx(idxOf(qid) + 1);
          } else if (role === 'next-unanswered') {
            gotoUnanswered(idxOf(qid));
          }
        });
      });

      // 采分点自评
      $$('input[data-role="sg"]', card).forEach(function (cb) {
        cb.addEventListener('change', function () {
          var pi = parseInt(cb.getAttribute('data-pi'), 10);
          var hits = (session.answers[qid].pointsHit || []).slice();
          hits[pi] = cb.checked;
          var earned = 0;
          (q.points || []).forEach(function (p, i) { if (hits[i]) earned += (p.partial || 2); });
          var prevAttempts = session.answers[qid].attempts;
          session.answers[qid].pointsHit = hits;
          session.answers[qid].earned = earned;
          session.answers[qid].correct = earned >= fullScore(q);
          session.answers[qid].attempts = prevAttempts;
          // 得分率 < 100% 入错题本；全对则标记已订正
          // 一个采分点都还没自评时先不入错题本——刚提交就被判错不公道
          var anyDecided = hits.some(function (h) { return h === true || h === false; });
          if (!anyDecided) {
            // 尚未自评，不动错题本
          } else if (earned < fullScore(q)) {
            var wb = state.wrongBook[qid];
            if (!wb) wb = state.wrongBook[qid] = { firstWrongAt: now(), lastWrongAt: now(), wrongCount: 1, resolved: false, note: (q.knowledgePoint || '') + '（' + CHAPTER_LABEL[q.chapter] + '）' };
            else { wb.lastWrongAt = now(); wb.resolved = false; }
          } else if (state.wrongBook[qid]) {
            state.wrongBook[qid].resolved = true;
            state.wrongBook[qid].lastWrongAt = now();
          }
          session.updatedAt = now();
          saveMerged();
          render(); scrollToCard(qid);
        });
      });
    });
  }

  function submitBlank(q, card) {
    var bi = $('[data-role="blank"]', card);
    var val = bi ? bi.value : '';
    var rec = judgeObjective(q, [val]);
    recordAnswer(q, { value: [val], correct: rec.correct, earned: rec.earned, full: rec.full });
    render(); scrollToCard(q.id);
  }

  function redo(qid) {
    if (!session.answers[qid]) return;
    delete session.answers[qid];
    session.updatedAt = now();
    saveMerged();
    render(); scrollToCard(qid);
  }

  function idxOf(qid) { return session.order.indexOf(qid); }
  /** 跳到 order 的第 i 题。窗口化渲染下目标题卡可能还没生成，
   *  所以这里必须先 render() 再滚动——与旧版「全量渲染、只滚动」不同。 */
  function gotoIdx(i) {
    if (i < 0 || i >= session.order.length) return;
    session.cursor = i;
    saveMerged();
    render();
    scrollToCard(session.order[i]);
  }
  function gotoUnanswered(from) {
    for (var k = 1; k <= session.order.length; k++) {
      var i = (from + k) % session.order.length;
      if (!session.answers[session.order[i]]) { gotoIdx(i); return; }
    }
  }
  function scrollToCard(qid) {
    var el = document.getElementById('card-' + qid);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /** 把粘性 HUD 的实际高度写进 CSS 变量。
   *  .qcard 用 scroll-margin-top 避让它——否则 scrollIntoView 会把题卡顶边
   *  顶到视口顶端，正好藏到粘性页头底下，下方题卡的选项点不动。 */
  function syncHudOffset() {
    var h = hud && hud.getBoundingClientRect ? Math.round(hud.getBoundingClientRect().height) : 0;
    document.documentElement.style.setProperty('--hud-h', (h || 132) + 'px');
  }

  /* ---------- HUD ---------- */
  function updateHudTime() {
    var el = $('#m-time');
    if (el && session) el.textContent = fmtClock(session.elapsedMs);
  }
  function updateHud() {
    var total = session.order.length;
    var answered = session.order.filter(function (id) { return !!session.answers[id]; }).length;
    var earned = 0, full = 0, objA = 0, objC = 0;
    session.order.forEach(function (id) {
      var a = session.answers[id];
      if (!a) return;
      earned += a.earned; full += a.full;
      if (!a.selfGraded) { objA++; if (a.correct === true) objC++; }
    });
    $('#m-progress').textContent = answered + ' / ' + total;
    $('#m-score').textContent = earned + ' / ' + full;
    $('#m-rate').textContent = full > 0 ? (Math.round(earned / full * 1000) / 10) + '%' : '—';
    $('#m-acc').textContent = objA > 0 ? (Math.round(objC / objA * 1000) / 10) + '%' : '—';
    var pct = total > 0 ? (answered / total * 100) : 0;
    $('#progress-fill').style.width = pct + '%';
    var pb = $('#progress-bar');
    pb.setAttribute('aria-valuenow', Math.round(pct));
    pb.setAttribute('aria-valuemax', total);
    updateHudTime();
    $('#f-count').textContent = '当前筛选：' + total + ' 题（题库共 ' + QUESTIONS.length + ' 题）';
  }

  /* ---------- 统计面板 ---------- */
  function renderStats() {
    recomputeStats();
    var st = state.stats;
    var html = '';
    function box(title, rows) {
      html += '<div class="stat-box"><h4>' + title + '</h4>';
      rows.forEach(function (r) {
        var max = Math.max.apply(null, rows.map(function (x) { return x.v; })) || 1;
        html += '<div class="bar-row"><span class="bar-name">' + esc(r.k) + '</span>' +
          '<span class="bar"><i style="width:' + Math.round(r.v / max * 100) + '%"></i></span>' +
          '<span class="bar-n">' + r.v + '</span></div>';
      });
      html += '</div>';
    }
    box('按题型（已答题数）', TYPE_GROUPS.map(function (t) { return { k: t.label, v: (st.byType[t.key] || {}).answered || 0 }; }));
    box('按难度（已答题数）', DIFFS.map(function (d) { return { k: d.label, v: (st.byDifficulty[d.key] || {}).answered || 0 }; }));
    box('按章节（已答题数）', CHAPTERS.map(function (c) { return { k: '第' + c.n + '章', v: (st.byChapter[c.n] || {}).answered || 0 }; }));
    html += '<div class="stat-box"><h4>总计（跨全部会话累计）</h4>' +
      '<div class="bar-row"><span class="bar-name">已答题数</span><span class="bar-n">' + st.totalAnswered + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">累计得分</span><span class="bar-n">' + st.totalEarned + ' / ' + st.totalFull + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">得分率口径</span><span class="bar-n">' + (st.totalFull ? (Math.round(st.totalEarned / st.totalFull * 1000) / 10) + '%' : '—') + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">客观正确率</span><span class="bar-n">' + (st.objectiveAnswered ? (Math.round(st.objectiveCorrect / st.objectiveAnswered * 1000) / 10) + '%' : '—') + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">客观题数口径</span><span class="bar-n">' + st.objectiveCorrect + ' / ' + st.objectiveAnswered + '</span></div>' +
      '</div>';
    $('#stat-grid').innerHTML = html;

    // 答案位置统计
    var pos = answerPositionStats();
    var nSingle = QUESTIONS.filter(function (q) { return q.type === 'single'; }).length;
    var ph = '<table class="simple"><thead><tr><th>题型</th>' +
      '<th class="num">A</th><th class="num">B</th><th class="num">C</th><th class="num">D</th><th class="num">合计</th><th>判定</th></tr></thead><tbody>';
    ph += '<tr><td>单选（' + nSingle + ' 题）</td>' +
      ['A', 'B', 'C', 'D'].map(function (L) { return '<td class="num">' + pos.single[L] + '</td>'; }).join('') +
      '<td class="num">' + (pos.single.A + pos.single.B + pos.single.C + pos.single.D) + '</td><td>每档 ∈ [' +
      LIMITS.singleMin + ',' + LIMITS.singleMax + ']</td></tr>';
    ph += '<tr><td>多选答案字母出现次数</td>' +
      ['A', 'B', 'C', 'D'].map(function (L) { return '<td class="num">' + pos.multi[L] + '</td>'; }).join('') +
      '<td class="num">' + (pos.multi.A + pos.multi.B + pos.multi.C + pos.multi.D) + '</td><td>四档极差 ≤ ' +
      LIMITS.multiRange + '</td></tr>';
    ph += '</tbody></table>';
    $('#pos-stat').innerHTML = ph;

    // 分值口径
    var th = '<table class="simple"><thead><tr><th>题型</th><th class="num">题数</th><th class="num">分值小计</th><th class="num">占比</th></tr></thead><tbody>';
    var totalFull = 0, perType = {};
    QUESTIONS.forEach(function (q) {
      perType[q.typeGroup] = (perType[q.typeGroup] || 0) + fullScore(q);
      totalFull += fullScore(q);
    });
    TYPE_GROUPS.forEach(function (t) {
      var cnt = QUESTIONS.filter(function (q) { return q.typeGroup === t.key; }).length;
      var v = perType[t.key] || 0;
      th += '<tr><td>' + t.label + '</td><td class="num">' + cnt + '</td><td class="num">' + v + '</td><td class="num">' +
        (totalFull ? (Math.round(v / totalFull * 1000) / 10) : 0) + '%</td></tr>';
    });
    th += '<tr><td><b>合计</b></td><td class="num"><b>' + QUESTIONS.length + '</b></td><td class="num"><b>' + totalFull + '</b></td><td class="num">100%</td></tr></tbody></table>';
    $('#score-table').innerHTML = th;
  }

  /* ---------- 错题本 ---------- */
  function renderWrong() {
    var ids = Object.keys(state.wrongBook);
    $('#wrong-count').textContent = ids.length ? '共 ' + ids.length + ' 题' : '';
    if (!ids.length) {
      $('#wrong-list').innerHTML = '<div class="empty">错题本为空。得分率低于 100% 的题会自动收入此处。</div>';
      return;
    }
    ids.sort(function (a, b) { return (state.wrongBook[b].lastWrongAt || 0) - (state.wrongBook[a].lastWrongAt || 0); });
    // 待订正知识点聚合 Top5：按未订正错题的知识点计数
    var kpCount = {}, pending = 0;
    ids.forEach(function (id) {
      var q = qById[id];
      if (!q) return;
      if (!state.wrongBook[id].resolved) {
        pending++;
        var k = q.knowledgePoint || '—';
        kpCount[k] = (kpCount[k] || 0) + 1;
      }
    });
    var h = '';
    if (pending) {
      var top = Object.keys(kpCount).sort(function (a, b) { return kpCount[b] - kpCount[a]; }).slice(0, 5);
      var max = kpCount[top[0]] || 1;
      h += '<div class="wrong-agg"><div class="selfgrade-h">待订正 ' + pending +
        ' 题 · 知识点 Top ' + top.length + '（点击题号跳原题订正）</div>';
      top.forEach(function (k) {
        h += '<div class="bar-row"><span class="bar-name">' + esc(k) + '</span>' +
          '<span class="bar"><i style="width:' + Math.round(kpCount[k] / max * 100) + '%"></i></span>' +
          '<span class="bar-n">' + kpCount[k] + ' 题</span></div>';
      });
      h += '</div>';
    }
    ids.forEach(function (id) {
      var q = qById[id];
      if (!q) return;
      var w = state.wrongBook[id];
      h += '<div class="wrong-item' + (w.resolved ? ' resolved' : '') + '">';
      h += '<div class="wi-head"><span class="q-tag t-type">' + esc(typeLabel(q)) + '</span>' +
        '<span class="q-tag t-diff-' + q.difficulty + '">' + DIFF_LABEL[q.difficulty] + '</span>' +
        '<span class="q-tag">' + esc(CHAPTER_LABEL[q.chapter]) + '</span>' +
        (w.resolved ? '<span class="q-tag t-diff-basic">已订正</span>' : '<span class="q-tag t-diff-hard">待订正</span>') +
        '<span class="muted">错 ' + (w.wrongCount || 1) + ' 次 · ' + fmtDate(w.lastWrongAt) + '</span></div>';
      h += '<div class="wi-stem">' + mdLite(q.stem) + '</div>';
      if (w.note) h += '<div class="muted" style="margin-top:4px">' + esc(w.note) + '</div>';
      h += '</div>';
    });
    $('#wrong-list').innerHTML = h;
    // 错题本里的题干含公式，插入 DOM 后要再走一次 KaTeX，否则显示原始 $…$
    renderMathAll();
  }

  /* ---------- 答题卡 ---------- */
  /** 答题卡状态：correct 是 true/false 的题直接标对错；
   *  自评未完成（correct=null）标为「已作答·未判定」。 */
  function sheetStatus(qid) {
    var a = session.answers[qid];
    if (!a) return 'none';
    if (a.correct === true) return 'ok';
    if (a.correct === false) return 'bad';
    return 'mid';
  }

  function renderSheet() {
    var grid = $('#sheet-grid'), legend = $('#sheet-legend');
    if (!grid) return;
    var n = session.order.length;
    var cnt = { none: 0, mid: 0, ok: 0, bad: 0 };
    var h = '';
    session.order.forEach(function (qid, i) {
      var st = sheetStatus(qid);
      cnt[st]++;
      h += '<button type="button" class="sheet-cell st-' + st + (i === session.cursor ? ' is-cur' : '') +
        '" data-idx="' + i + '" title="' + esc(CHAPTER_LABEL[qById[qid].chapter]) + '" aria-label="第 ' + (i + 1) + ' 题">' + (i + 1) + '</button>';
    });
    grid.innerHTML = h;
    var total = session.order.length;
    legend.innerHTML =
      '<span class="lg-item"><i class="lg-dot st-none"></i>未作答 ' + cnt.none + '</span>' +
      '<span class="lg-item"><i class="lg-dot st-mid"></i>已答·未判定 ' + cnt.mid + '</span>' +
      '<span class="lg-item"><i class="lg-dot st-ok"></i>正确 ' + cnt.ok + '</span>' +
      '<span class="lg-item"><i class="lg-dot st-bad"></i>错误 ' + cnt.bad + '</span>' +
      '<span class="lg-item muted">当前筛选 ' + total + ' 题 · 点击题号跳题</span>';
    $$('.sheet-cell', grid).forEach(function (cell) {
      cell.addEventListener('click', function () {
        gotoIdx(parseInt(cell.getAttribute('data-idx'), 10));
        $('#panel-sheet').hidden = true;
      });
    });
  }

  /* ---------- 结算 ---------- */
  function renderResult() {
    var total = session.order.length;
    var answered = 0, earned = 0, full = 0, objA = 0, objC = 0;
    session.order.forEach(function (id) {
      var a = session.answers[id]; if (!a) return;
      answered++; earned += a.earned; full += a.full;
      if (!a.selfGraded) { objA++; if (a.correct === true) objC++; }
    });
    var wrongIds = Object.keys(state.wrongBook);
    var h = '';
    h += '<div class="stat-grid">';
    h += '<div class="stat-box"><h4>本次结算</h4>' +
      '<div class="bar-row"><span class="bar-name">完成题数</span><span class="bar-n">' + answered + ' / ' + total + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">总得分</span><span class="bar-n">' + earned + ' / ' + full + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">得分率口径</span><span class="bar-n">' + (full ? (Math.round(earned / full * 1000) / 10) + '%' : '—') + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">客观正确率</span><span class="bar-n">' + (objA ? (Math.round(objC / objA * 1000) / 10) + '%' : '—') + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">用时</span><span class="bar-n">' + fmtClock(session.elapsedMs) + '</span></div>' +
      '<div class="bar-row"><span class="bar-name">错题本累计</span><span class="bar-n">' + wrongIds.length + ' 题</span></div>' +
      '</div>';
    h += '</div>';
    var box = $('#result-box');
    if (!box) {
      box = document.createElement('div');
      box.id = 'result-box';
      var p = $('#panel-stats');
      p.insertBefore(box, p.firstChild);
    }
    box.innerHTML = h;
  }

  /* ---------- KaTeX ---------- */
  function renderMathAll() {
    if (typeof renderMathInElement !== 'function') return;
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        throwOnError: false,
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
      });
    } catch (e) { /* 渲染失败不中断页面 */ }
  }

  /* ---------- 键盘快捷键（仅单题聚焦模式） ---------- */
  /** ←/→ 切题；A–D（或 1–4）选择当前题的选项（多选为切换勾选）；Enter 确认。
   *  焦点在输入框/下拉框时不拦截——否则填空、关键词搜索会打不出字母。 */
  function currentQuestion() {
    var id = session.order[session.cursor];
    return id ? qById[id] : null;
  }
  function handleKeys(e) {
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return;
    if (state.settings.mode !== 'single') {
      if (e.key === 'ArrowLeft') { gotoIdx(session.cursor - 1); }
      else if (e.key === 'ArrowRight') { gotoIdx(session.cursor + 1); }
      return;
    }
    if (e.key === 'ArrowLeft') { e.preventDefault(); gotoIdx(session.cursor - 1); return; }
    if (e.key === 'ArrowRight') { e.preventDefault(); gotoIdx(session.cursor + 1); return; }
    var q = currentQuestion();
    if (!q || session.answers[q.id]) return;
    var keyToLetter = { a: 'A', b: 'B', c: 'C', d: 'D', '1': 'A', '2': 'B', '3': 'C', '4': 'D' };
    if (keyToLetter[e.key.toLowerCase()] && (q.type === 'single' || q.type === 'multi' || q.type === 'judge')) {
      var L = keyToLetter[e.key.toLowerCase()];
      var opts = q.options || (q.type === 'judge' ? ['正确', '错误'] : []);
      if (opts && opts.length >= (LETTERS.indexOf(L) + 1)) {
        var input = document.querySelector('input[name="opt-' + q.id + '"][value="' + L + '"]');
        if (input && !input.disabled) {
          input.checked = q.type === 'multi' ? !input.checked : true;
          input.dispatchEvent(new Event('change', { bubbles: true }));
          e.preventDefault();
        }
      }
      return;
    }
    if (e.key === 'Enter' && q.type === 'multi') {
      var btn = document.querySelector('#card-' + q.id + ' [data-role="submit-multi"]');
      if (btn) { btn.click(); e.preventDefault(); }
    }
  }

  /* ---------- 数据自主权：导出 / 导入（D17） ---------- */
  var EXPORT_KIND = 'quiz-platform-progress';
  var EXPORT_VERSION = 1;

  function djb2(str) {
    var h = 5381;
    for (var i = 0; i < str.length; i++) h = ((h << 5) + h + str.charCodeAt(i)) >>> 0;
    return h.toString(16);
  }

  function buildExportPayload() {
    var stateJson = JSON.stringify({ v: state.v, sessions: state.sessions, wrongBook: state.wrongBook });
    return {
      kind: EXPORT_KIND,
      version: EXPORT_VERSION,
      subject: SUBJECT.id,
      bankId: BANK_ID,
      exportedAt: new Date().toISOString(),
      stats: { answered: Object.keys(session ? session.answers : {}).length, wrongBook: Object.keys(state.wrongBook).length },
      checksum: djb2(stateJson),
      state: JSON.parse(stateJson)
    };
  }

  /** 导入合并：会话按 id 取较新者；错题本按键合并（错次取大、订正状态取或）；
   *  settings/stat 保留本地（stats 由会话重算）。返回 {merged, sessionsAdded}。 */
  function applyImportPayload(payload) {
    if (!payload || payload.kind !== EXPORT_KIND || payload.version !== EXPORT_VERSION) {
      throw new Error('不是本平台的进度文件（kind/version 不符）');
    }
    if (!payload.state || payload.state.v !== 1) throw new Error('进度状态结构不符');
    var body = JSON.stringify({ v: payload.state.v, sessions: payload.state.sessions, wrongBook: payload.state.wrongBook });
    if (payload.checksum && djb2(body) !== payload.checksum) throw new Error('校验和不符，文件可能已损坏');
    var added = 0;
    Object.keys(payload.state.sessions || {}).forEach(function (sid) {
      var incoming = payload.state.sessions[sid];
      var local = state.sessions[sid];
      if (!local) { state.sessions[sid] = incoming; added++; }
      else if ((incoming.updatedAt || 0) > (local.updatedAt || 0)) state.sessions[sid] = incoming;
    });
    Object.keys(payload.state.wrongBook || {}).forEach(function (qid) {
      var o = payload.state.wrongBook[qid], m = state.wrongBook[qid];
      if (!m) { state.wrongBook[qid] = o; return; }
      m.wrongCount = Math.max(m.wrongCount || 0, o.wrongCount || 0);
      m.resolved = !!(m.resolved || o.resolved);
      m.lastWrongAt = Math.max(m.lastWrongAt || 0, o.lastWrongAt || 0);
      if (!m.firstWrongAt) m.firstWrongAt = o.firstWrongAt;
    });
    saveMerged();
    return { sessionsAdded: added };
  }

  function showToast(msg, cls) {
    var t = $('#toast');
    if (!t) return;
    t.textContent = msg;
    t.className = 'toast show' + (cls ? ' ' + cls : '');
    clearTimeout(showToast._h);
    showToast._h = setTimeout(function () { t.className = 'toast'; }, 3200);
  }

  function openDataModal(mode) {
    var modal = $('#data-modal');
    var text = $('#data-text');
    var hint = $('#data-hint');
    if (!modal) return;
    $('#data-modal-title').textContent = mode === 'import' ? '导入进度（粘贴 JSON）' : '导出进度';
    if (mode === 'import') {
      text.value = '';
      hint.textContent = '粘贴此前导出的进度 JSON 后点「从文本导入」。合并规则：会话与错题本双向保留，设置以本机为准。';
    } else {
      text.value = JSON.stringify(buildExportPayload(), null, 1);
      hint.textContent = '复制整段 JSON 带走（或点「下载 .json」）；换设备时在目标子站点「导入进度」粘贴。';
    }
    modal.hidden = false;
    text.focus();
  }

  function downloadExport() {
    try {
      var payload = JSON.stringify(buildExportPayload(), null, 1);
      var blob = new Blob([payload], { type: 'application/json' });
      var a = document.createElement('a');
      var d = new Date();
      a.download = 'quiz-' + SUBJECT.id + '-progress-' +
        d.getFullYear() + pad2(d.getMonth() + 1) + pad2(d.getDate()) + '.json';
      a.href = URL.createObjectURL(blob);
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
      showToast('已开始下载进度文件');
    } catch (e) {
      showToast('下载失败，请用「复制」带走', 'bad');
    }
  }

  function importFromText() {
    var text = $('#data-text').value.trim();
    if (!text) { showToast('请先粘贴进度 JSON', 'bad'); return; }
    try {
      var payload = JSON.parse(text);
      var r = applyImportPayload(payload);
      $('#data-modal').hidden = true;
      refreshOrder(); renderFilters(); render();
      showToast('导入完成：并入 ' + r.sessionsAdded + ' 个新会话（含错题本合并）', 'ok');
    } catch (e) {
      showToast('导入失败：' + (e && e.message || e), 'bad');
    }
  }

  /* ---------- hash 路由（筛选状态可分享） ---------- */
  function filterToHash() {
    var f = session.filter;
    var p = new URLSearchParams();
    if (f.chapters && f.chapters.length) p.set('ch', f.chapters.join(','));
    if (f.types && f.types.length) p.set('type', f.types.join(','));
    if (f.diffs && f.diffs.length) p.set('diff', f.diffs.join(','));
    if (f.onlyWrong) p.set('wrong', '1');
    if (f.kw) p.set('kw', f.kw);
    var qs = p.toString();
    return '#/s/' + SUBJECT.id + (qs ? '?' + qs : '');
  }

  function applyHashToFilter() {
    var h = location.hash || '';
    if (h.indexOf('#/s/' + SUBJECT.id) !== 0) return false;
    var f = session.filter;
    var q = {};
    h.slice(('#/s/' + SUBJECT.id).length).replace(/^\?/, '').split('&').forEach(function (kv) {
      if (!kv) return;
      var i = kv.indexOf('=');
      q[kv.slice(0, i)] = decodeURIComponent(kv.slice(i + 1));
    });
    f.chapters = q.ch ? q.ch.split(',').map(function (x) { return parseInt(x, 10); }).filter(function (x) { return !isNaN(x); }) : [];
    f.types = q.type ? q.type.split(',') : [];
    f.diffs = q.diff ? q.diff.split(',') : [];
    f.onlyWrong = q.wrong === '1';
    f.kw = q.kw || '';
    return true;
  }

  function writeHash() {
    var h = filterToHash();
    if (location.hash !== h) {
      try { history.replaceState(null, '', h); } catch (e) { location.hash = h; }
    }
  }

  /* ---------- 初始化 ---------- */
  function init() {
    load();
    ensureSession();
    // URL hash 携带的筛选状态（分享链接/刷新还原）优先于本地会话的旧筛选
    if (applyHashToFilter()) refreshOrder();
    if (!session.order.length || orderIsStale()) refreshOrder();
    renderFilters();
    render();
    startTimer();

    $('#f-order').addEventListener('change', function (e) {
      state.settings.order = e.target.value; refreshOrder(); render(); saveMerged();
    });
    $('#f-mode').addEventListener('change', function (e) {
      state.settings.mode = e.target.value === 'list' ? 'list' : 'single';
      if (session.cursor >= session.order.length) session.cursor = Math.max(0, session.order.length - 1);
      render(); saveMerged();
    });
    $('#f-shuffle').addEventListener('change', function (e) {
      state.settings.shuffle = e.target.checked; refreshOrder(); render(); saveMerged();
    });
    $('#f-wrongonly').addEventListener('change', function (e) {
      session.filter.onlyWrong = e.target.checked; refreshOrder(); render(); saveMerged();
    });
    var kwTimer = null;
    $('#f-kw').addEventListener('input', function (e) {
      var v = e.target.value;
      clearTimeout(kwTimer);
      kwTimer = setTimeout(function () {
        session.filter.kw = v; refreshOrder(); render(); saveMerged();
      }, 220);
    });

    $('#btn-finish').addEventListener('click', function () {
      endSession();
      renderResult();
      $('#panel-stats').hidden = false;
      renderStats();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    $('#btn-reset').addEventListener('click', function () {
      newSession(false);
      // 必须重建题目顺序：新会话的 order 是空数组，不刷新就会停在「0 题」空页。
      refreshOrder();
      renderFilters(); render(); saveMerged();
    });
    $('#btn-stats').addEventListener('click', function () {
      var p = $('#panel-stats');
      p.hidden = !p.hidden;
      if (!p.hidden) { renderResult(); renderStats(); }
    });
    $('#btn-sheet').addEventListener('click', function () {
      var p = $('#panel-sheet');
      p.hidden = !p.hidden;
      if (!p.hidden) { renderSheet(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
    });
    $('#btn-theme').addEventListener('click', cycleTheme);
    if (window.matchMedia) {
      // 跟随系统模式下，系统切换深浅色时页面实时跟着变
      try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
          if ((state.settings.theme || 'auto') === 'auto') applyTheme();
        });
      } catch (e) { /* 旧浏览器不支持 addEventListener 形式，忽略 */ }
    }
    document.addEventListener('keydown', handleKeys);
    $('#btn-wrong').addEventListener('click', function () {
      var p = $('#panel-wrong');
      p.hidden = !p.hidden;
      if (!p.hidden) renderWrong();
    });
    $('#btn-wrong-practice').addEventListener('click', function () {
      session.filter.onlyWrong = true;
      refreshOrder(); render(); renderFilters();
      $('#panel-wrong').hidden = true;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    $('#btn-wrong-clear').addEventListener('click', function () {
      state.wrongBook = {};
      saveMerged(); renderWrong();
    });
    $('#btn-wrong-print').addEventListener('click', function () {
      document.body.classList.add('print-wrong');
      var done = function () {
        document.body.classList.remove('print-wrong');
        window.removeEventListener('afterprint', done);
      };
      window.addEventListener('afterprint', done);
      window.print();
      setTimeout(done, 2000);  // afterprint 不触发时的兜底
    });
    $('#btn-share').addEventListener('click', function () {
      var url = location.href;
      var done = function () { showToast('链接已复制，粘贴给同学即可还原同一筛选视图', 'ok'); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done, function () { fallbackCopy(url); done(); });
      } else { fallbackCopy(url); done(); }
    });
    $('#btn-export').addEventListener('click', function () { openDataModal('export'); });
    $('#btn-import').addEventListener('click', function () { openDataModal('import'); });
    $$('[data-role]', $('#data-modal')).forEach(function (btn) {
      var role = btn.getAttribute('data-role');
      if (role === 'data-copy') btn.addEventListener('click', function () {
        var v = $('#data-text').value;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(v).then(function () { showToast('已复制', 'ok'); },
            function () { fallbackCopy(v); showToast('已复制', 'ok'); });
        } else { fallbackCopy(v); showToast('已复制', 'ok'); }
      });
      else if (role === 'data-download') btn.addEventListener('click', downloadExport);
      else if (role === 'data-apply') btn.addEventListener('click', importFromText);
      else if (role === 'data-close') btn.addEventListener('click', function () { $('#data-modal').hidden = true; });
    });
    window.addEventListener('hashchange', function () {
      // 外部触发的 hash 变化（粘贴分享链接/前进后退）→ 反向应用为筛选
      if (location.hash === filterToHash()) return;   // 自己写入的，忽略
      if (applyHashToFilter()) { refreshOrder(); renderFilters(); render(); saveMerged(); }
    });

    if (!storageOk) showStorageWarn();
    applyTheme();
    syncHudOffset();
    window.addEventListener('resize', syncHudOffset);
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    ta.remove();
  }

  /** manifest 注入：文案/章节/阈值全部来自构建产物，页面不写死任何题量数字。 */
  function fillStaticTexts(meta) {
    var s = meta.summary || {};
    document.title = '大学《' + meta.subject.name + '》题库刷题 · 复习刷题平台';
    $('#hud-sub').textContent = s.sub || '';
    var about = $('#about-block');
    if (about) about.innerHTML = s.aboutHtml || '';
    var foot = $('#foot-dynamic');
    if (foot) foot.innerHTML = s.footerHtml || '';
  }

  function initApp(meta, questions) {
    META = meta;
    BANK = { id: meta.subject.bankId, limits: (meta.caliber && meta.caliber.limits) || LIMITS };
    BANK_ID = meta.subject.bankId;
    LIMITS = BANK.limits;
    QUESTIONS = questions;
    var labels = (meta.subject.chapterLabels || {});
    CHAPTERS = Object.keys(labels).map(function (n) {
      return { n: parseInt(n, 10), label: labels[n] };
    }).sort(function (a, b) { return a.n - b.n; });
    CHAPTER_LABEL = {};
    CHAPTERS.forEach(function (c) { CHAPTER_LABEL[c.n] = c.label; });
    qById = {};
    QUESTIONS.forEach(function (q) { qById[q.id] = q; });

    fillStaticTexts(meta);
    init();
  }

  /* ---------- 启动：异步装载题库 ---------- */
  function boot() {
    LABank.load(SUBJECT).then(function (b) {
      initApp(b.meta, b.questions);
    }).catch(function (e) {
      console.error('[boot] 题库装载失败', e);
      var box = $('#quiz');
      if (box) box.innerHTML =
        '<div class="empty">题库装载失败（' + esc(e && e.message || e) + '）。' +
        '请刷新重试；若持续失败，可使用单文件离线版：' +
        '<a href="https://wewe29.github.io/linear-algebra-quiz/">linear-algebra-quiz</a></div>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
