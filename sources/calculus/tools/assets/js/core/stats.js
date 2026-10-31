/* core/stats.js — 统计（无 DOM 依赖）
   四个维度：题型 / 难度 / 章节 / 知识点。全部从「所有会话的作答记录」重算，
   不做增量累加——增量在多标签页下会重复计数。 */
(function (ns) {
  'use strict';

  var store = null, session = null;

  function init(deps) {
    store = deps.store;
    session = deps.session;
  }

  function blank() {
    return { answered: 0, earned: 0, full: 0, correct: 0 };
  }

  function bump(map, key) {
    if (!map[key]) map[key] = blank();
    return map[key];
  }

  function recompute() {
    var st = store.get();
    var out = {
      byType: {}, byDifficulty: {}, byChapter: {}, byKnowledgePoint: {},
      answerPosition: { A: 0, B: 0, C: 0, D: 0 },
      multiLetter: { A: 0, B: 0, C: 0, D: 0 },
      totalAnswered: 0, totalCorrect: 0, totalEarned: 0, totalFull: 0,
      objectiveAnswered: 0, objectiveCorrect: 0
    };
    Object.keys(st.sessions || {}).forEach(function (sid) {
      var s = st.sessions[sid];
      var ans = (s && s.answers) || {};
      Object.keys(ans).forEach(function (qid) {
        var a = ans[qid];
        var q = session.questionById(qid);
        if (!q) return;
        var g = q.typeGroup;
        var t = bump(out.byType, g);
        t.answered++; t.earned += a.earned; t.full += a.full;
        if (a.correct === true) t.correct++;
        var d = bump(out.byDifficulty, q.difficulty);
        d.answered++; d.earned += a.earned; d.full += a.full;
        if (a.correct === true) d.correct++;
        var c = bump(out.byChapter, String(q.chapter));
        c.answered++; c.earned += a.earned; c.full += a.full;
        if (a.correct === true) c.correct++;
        (q.knowledgePoints || [q.knowledgePoint]).forEach(function (k) {
          if (!k) return;
          var kk = bump(out.byKnowledgePoint, k);
          kk.answered++; kk.earned += a.earned; kk.full += a.full;
          if (a.correct === true) kk.correct++;
        });
        out.totalAnswered++;
        out.totalEarned += a.earned;
        out.totalFull += a.full;
        if (a.correct === true) out.totalCorrect++;
        if (!a.selfGraded) {
          out.objectiveAnswered++;
          if (a.correct === true) out.objectiveCorrect++;
        }
        if (q.type === 'single' || q.type === 'judge') {
          var L = (a.value || [])[0];
          if (L && out.answerPosition[L] != null) out.answerPosition[L]++;
        }
        if (q.type === 'multi') {
          (a.value || []).forEach(function (L) {
            if (L && out.multiLetter[L] != null) out.multiLetter[L]++;
          });
        }
      });
    });
    st.stats = out;
    store.saveMerged();
    return out;
  }

  /** 得分率（按分值）；无分值时返回 null */
  function rate(earned, full) {
    if (!full) return null;
    return Math.round((earned / full) * 1000) / 10;
  }

  /** 客观题正确率 */
  function accuracy() {
    var st = store.get().stats;
    if (!st.objectiveAnswered) return null;
    return Math.round((st.objectiveCorrect / st.objectiveAnswered) * 1000) / 10;
  }

  /** 本次会话的即时指标 */
  function sessionMetrics() {
    var s = session.raw;
    if (!s) return { answered: 0, total: 0, earned: 0, full: 0, rate: null, acc: null };
    var answered = 0, earned = 0, full = 0, objA = 0, objC = 0;
    Object.keys(s.answers || {}).forEach(function (qid) {
      var a = s.answers[qid];
      answered++; earned += a.earned; full += a.full;
      if (!a.selfGraded) { objA++; if (a.correct === true) objC++; }
    });
    return {
      answered: answered,
      total: (s.order || []).length,
      earned: earned,
      full: full,
      rate: rate(earned, full),
      acc: objA ? Math.round((objC / objA) * 1000) / 10 : null
    };
  }

  ns.stats = {
    init: init,
    recompute: recompute,
    rate: rate,
    accuracy: accuracy,
    sessionMetrics: sessionMetrics
  };
})(window.QX = window.QX || {});
