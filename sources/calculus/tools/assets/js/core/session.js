/* core/session.js — 会话状态机（无 DOM 依赖）
   一个会话 = 一次连续作答：筛选条件 + 题序 + 游标 + 逐题作答记录。
   支持跳题、末题循环、刷新恢复、计时冻结。 */
(function (ns) {
  'use strict';

  var store = null, bus = null, judge = null;
  var catalog = { chapters: [], secKeys: [], typeGroups: [], diffs: [] };
  var questions = [];          // 已载入的全部题目
  var qById = {};
  var session = null;
  var timerHandle = null;

  function now() { return Date.now(); }

  function blankFilter(onlyWrong) {
    return {
      types: [], diffs: [], chapters: [], knowledgePoints: [], kinds: [],
      onlyWrong: !!onlyWrong, onlyFavorite: false, kw: ''
    };
  }

  function newSessionId() {
    return 's' + now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  function init(deps) {
    store = deps.store;
    bus = deps.bus;
    judge = deps.judge;
    if (deps.catalog) catalog = deps.catalog;
  }

  function setQuestions(list) {
    questions = list || [];
    qById = {};
    questions.forEach(function (q) { qById[q.id] = q; });
  }

  function allQuestions() { return questions; }
  function questionById(id) { return qById[id] || null; }

  /* ---------------- 会话生命周期 ---------------- */

  function ensureSession() {
    var s = latestActive();
    if (!s) {
      s = {
        id: newSessionId(), startedAt: now(), updatedAt: now(), endedAt: null,
        elapsedMs: 0, lastTick: null, hidden: false,
        filter: blankFilter(false),
        order: [], cursor: 0, status: 'active', answers: {}
      };
      store.get().sessions[s.id] = s;
    }
    if (!s.answers) s.answers = {};
    if (!s.filter) s.filter = blankFilter(false);
    // 兼容旧记录：早期版本把 pointsHit 初始化成全 false（= 已判「未得到」）
    Object.keys(s.answers).forEach(function (k) {
      var a = s.answers[k];
      if (!a || !a.selfGraded || !a.pointsHit || !a.pointsHit.length) return;
      var allFalse = a.pointsHit.every(function (h) { return h === false; });
      if (allFalse && !a.earned) a.pointsHit = a.pointsHit.map(function () { return null; });
    });
    session = s;
    return s;
  }

  function latestActive() {
    var st = store.get();
    var best = null;
    Object.keys(st.sessions || {}).forEach(function (sid) {
      var s = st.sessions[sid];
      if (!s || s.status !== 'active') return;
      if (!best || (s.updatedAt || 0) > (best.updatedAt || 0)) best = s;
    });
    return best;
  }

  function endSession() {
    if (!session) return;
    session.status = 'finished';
    session.endedAt = now();
    store.saveMerged();
    bus.emit('session:ended', session);
  }

  function resetSession(keepWrong) {
    if (session) {
      session.status = 'finished';
      session.endedAt = now();
    }
    session = {
      id: newSessionId(), startedAt: now(), updatedAt: now(), endedAt: null,
      elapsedMs: 0, lastTick: null, hidden: false,
      filter: blankFilter(!!keepWrong),
      order: [], cursor: 0, status: 'active', answers: {}
    };
    store.get().sessions[session.id] = session;
    store.saveMerged();
    return session;
  }

  /* ---------------- 筛选与排序 ---------------- */

  function passes(q, f) {
    if (!q) return false;
    if (f.types && f.types.length && f.types.indexOf(q.typeGroup) < 0) return false;
    if (f.diffs && f.diffs.length && f.diffs.indexOf(q.difficulty) < 0) return false;
    // 章节：chip 存的是**字符串**（String(c.n)），题目里 chapter 是**数字**。
    // 直接 indexOf 会出现 ["1"].indexOf(1) === -1 → 一点章节就命中 0 题。
    // （bank.js 里按章取题用的是 String(q.chapter) === key，两处必须一致。）
    if (f.chapters && f.chapters.length) {
      var ch = String(q.chapter);
      var hitCh = f.chapters.some(function (c) { return String(c) === ch; });
      if (!hitCh) return false;
    }
    if (f.kinds && f.kinds.length) {
      var kind = (q.source && q.source.kind) || 'textbook';
      if (f.kinds.indexOf(kind) < 0) return false;
    }
    if (f.knowledgePoints && f.knowledgePoints.length) {
      var kps = q.knowledgePoints || [q.knowledgePoint];
      var hit = kps.some(function (k) { return f.knowledgePoints.indexOf(k) >= 0; });
      if (!hit) return false;
    }
    var st = store.get();
    // 「只看错题本」= 还没订正的错题；已订正的不再占用练习队列
    if (f.onlyWrong) {
      var wb = st.wrongBook[q.id];
      if (!wb || wb.resolved) return false;
    }
    if (f.onlyFavorite && !st.favorites[q.id]) return false;
    if (f.kw) {
      var k = f.kw.toLowerCase();
      var hay = (q.stem + ' ' + (q.explanation || '') + ' ' + (q.knowledgePoint || '') +
                 ' ' + ((q.source && q.source.text) || '') + ' ' +
                 (q.tags || []).join(' ')).toLowerCase();
      if (hay.indexOf(k) < 0) return false;
    }
    return true;
  }

  function typeRank(key) {
    var i = 0;
    catalog.typeGroups.forEach(function (t) { if (t.key === key) i = t.rank; });
    return i;
  }

  function diffRank(key) {
    var i = 0;
    catalog.diffs.forEach(function (d) { if (d.key === key) i = d.rank; });
    return i;
  }

  function computeOrder() {
    var f = session.filter;
    var list = questions.filter(function (q) { return passes(q, f); });
    var mode = (store.get().settings.order) || 'difficulty_desc';
    list.sort(function (a, b) {
      if (mode === 'difficulty_asc') {
        var d1 = diffRank(a.difficulty) - diffRank(b.difficulty);
        if (d1 !== 0) return d1;
      } else if (mode === 'difficulty_desc') {
        var d2 = diffRank(b.difficulty) - diffRank(a.difficulty);
        if (d2 !== 0) return d2;
      } else if (mode === 'chapter') {
        if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      } else if (mode === 'type') {
        var t1 = typeRank(a.typeGroup) - typeRank(b.typeGroup);
        if (t1 !== 0) return t1;
        if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      }
      if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      var g1 = typeRank(a.typeGroup) - typeRank(b.typeGroup);
      if (g1 !== 0) return g1;
      return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
    });
    if (store.get().settings.shuffle) {
      for (var i = list.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = list[i]; list[i] = list[j]; list[j] = tmp;
      }
    }
    return list.map(function (q) { return q.id; });
  }

  /** 题序是否已与当前题库脱节（题库更新 / 筛选变化后需要重算） */
  function orderIsStale() {
    if (!session || !session.order.length) return true;
    var known = 0;
    for (var i = 0; i < session.order.length; i++) {
      if (qById[session.order[i]]) known++;
    }
    return known !== session.order.length;
  }

  function refreshOrder() {
    if (!session) return [];
    var prev = session.order[session.cursor];
    session.order = computeOrder();
    if (session.order.length) {
      var at = session.order.indexOf(prev);
      session.cursor = at >= 0 ? at : Math.min(session.cursor, session.order.length - 1);
    } else {
      session.cursor = 0;
    }
    session.updatedAt = now();
    store.saveMerged();
    return session.order;
  }

  /* ---------------- 游标 ---------------- */

  function clampCursor() {
    if (!session) return;
    if (!session.order.length) { session.cursor = 0; return; }
    if (session.cursor < 0) session.cursor = 0;
    if (session.cursor > session.order.length - 1) session.cursor = session.order.length - 1;
  }

  function gotoIdx(i) {
    if (!session || !session.order.length) return;
    if (i < 0 || i > session.order.length - 1) return;
    session.cursor = i;
    session.updatedAt = now();
    store.saveMerged();
    bus.emit('question:changed', current());
  }

  function current() {
    if (!session || !session.order.length) return null;
    clampCursor();
    return qById[session.order[session.cursor]] || null;
  }

  function currentIndex() { return session ? session.cursor : 0; }
  function next() { gotoIdx(session.cursor + 1); }
  function prev() { gotoIdx(session.cursor - 1); }

  /** 末题之后跳到第一道未作答的题；全答完则回到第一题 */
  function nextUnanswered() {
    if (!session || !session.order.length) return;
    for (var k = 1; k <= session.order.length; k++) {
      var i = (session.cursor + k) % session.order.length;
      if (!session.answers[session.order[i]]) { gotoIdx(i); return; }
    }
    gotoIdx(0);
  }

  function firstUnanswered() {
    if (!session || !session.order.length) return;
    for (var i = 0; i < session.order.length; i++) {
      if (!session.answers[session.order[i]]) { gotoIdx(i); return; }
    }
  }

  /* ---------------- 作答 ---------------- */

  function recordAnswer(q, rec) {
    var prev = session.answers[q.id];
    var attempts = (prev ? (prev.attempts || 1) : 0) + 1;
    session.answers[q.id] = {
      type: q.type, value: rec.value, submittedAt: now(),
      correct: rec.correct, earned: rec.earned, full: rec.full,
      selfGraded: !!rec.selfGraded, pointsHit: rec.pointsHit || null, attempts: attempts
    };
    var st = store.get();
    if (rec.earned < rec.full) {
      var wb = st.wrongBook[q.id];
      if (!wb) {
        wb = st.wrongBook[q.id] = {
          firstWrongAt: now(), lastWrongAt: now(), wrongCount: 1, resolved: false, note: ''
        };
      } else {
        wb.wrongCount = (wb.wrongCount || 0) + 1;
        wb.lastWrongAt = now();
        wb.resolved = false;
      }
      if (!wb.note) {
        var kp = q.knowledgePoint || '';
        wb.note = kp + '（第' + q.chapter + '章）';
      }
    } else if (st.wrongBook[q.id]) {
      st.wrongBook[q.id].resolved = true;
      st.wrongBook[q.id].lastWrongAt = now();
    }
    session.updatedAt = now();
    store.saveMerged();
    bus.emit('answer:graded', { question: q, answer: session.answers[q.id] });
  }

  /** 主观题：展开参考答案与采分点，但**不做自评**（不判错、不进错题本） */
  function revealSubjective(q) {
    if (!session) return null;
    var prev = session.answers[q.id];
    var full = judge.fullScore(q);
    var hits = (q.points || []).map(function () { return null; });
    session.answers[q.id] = {
      type: q.type, value: [], submittedAt: now(),
      correct: false, earned: 0, full: full,
      selfGraded: true, pointsHit: hits,
      attempts: prev ? (prev.attempts || 1) : 1
    };
    session.updatedAt = now();
    store.saveMerged();
    bus.emit('answer:graded', { question: q, answer: session.answers[q.id] });
    return session.answers[q.id];
  }

  function redo(qid) {
    if (!session || !session.answers[qid]) return;
    delete session.answers[qid];
    session.updatedAt = now();
    store.saveMerged();
    bus.emit('answer:changed', qid);
  }

  function setSelfGrade(qid, pointsHit) {
    var a = session.answers[qid];
    if (!a) return;
    var q = qById[qid];
    var full = judge.fullScore(q);
    var earned = 0;
    (q.points || []).forEach(function (p, i) { if (pointsHit[i]) earned += (p.partial || 2); });
    var prevAttempts = a.attempts;
    a.pointsHit = pointsHit;
    a.earned = earned;
    a.correct = earned >= full;
    a.attempts = prevAttempts;
    var st = store.get();
    var anyDecided = pointsHit.some(function (h) { return h === true || h === false; });
    if (!anyDecided) {
      // 尚未自评，不动错题本
    } else if (earned < full) {
      var wb = st.wrongBook[qid];
      if (!wb) wb = st.wrongBook[qid] = { firstWrongAt: now(), lastWrongAt: now(), wrongCount: 1, resolved: false, note: '' };
      else { wb.lastWrongAt = now(); wb.resolved = false; }
    } else if (st.wrongBook[qid]) {
      st.wrongBook[qid].resolved = true;
      st.wrongBook[qid].lastWrongAt = now();
    }
    session.updatedAt = now();
    store.saveMerged();
    bus.emit('answer:graded', { question: q, answer: a });
  }

  /* ---------------- 计时 ---------------- */

  function tick() {
    if (!session || session.status !== 'active') return;
    var t = now();
    if (session.lastTick && !session.hidden) session.elapsedMs += (t - session.lastTick);
    session.lastTick = t;
    bus.emit('time:tick', session.elapsedMs);
  }

  function startTimer() {
    stopTimer();
    timerHandle = setInterval(tick, 1000);
  }

  function stopTimer() {
    if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }
  }

  function setHidden(hidden) {
    if (!session) return;
    session.hidden = hidden;
    session.lastTick = now();
    if (hidden) store.saveMerged();
  }

  function elapsed() { return session ? (session.elapsedMs || 0) : 0; }

  ns.session = {
    init: init,
    setQuestions: setQuestions,
    allQuestions: allQuestions,
    questionById: questionById,
    ensureSession: ensureSession,
    resetSession: resetSession,
    endSession: endSession,
    latestActive: latestActive,
    passes: passes,
    computeOrder: computeOrder,
    orderIsStale: orderIsStale,
    refreshOrder: refreshOrder,
    gotoIdx: gotoIdx,
    current: current,
    currentIndex: currentIndex,
    next: next,
    prev: prev,
    nextUnanswered: nextUnanswered,
    firstUnanswered: firstUnanswered,
    recordAnswer: recordAnswer,
    revealSubjective: revealSubjective,
    redo: redo,
    setSelfGrade: setSelfGrade,
    tick: tick,
    startTimer: startTimer,
    stopTimer: stopTimer,
    setHidden: setHidden,
    elapsed: elapsed,
    blankFilter: blankFilter,
    get raw() { return session; }
  };
})(window.QX = window.QX || {});
