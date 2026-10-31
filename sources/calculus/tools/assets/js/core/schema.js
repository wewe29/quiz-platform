/* core/schema.js — 运行时数据契约（无 DOM 依赖）
   与 Python 侧 tools/qa_bank/schema.py 的规则对齐，但只保留**运行期必须拦**
   的关键项：目的是「坏题被隔离，其余题照常可用」，而不是整站崩掉。

   与构建期门禁的分工：
     构建期（validate_bank.py）  —— 穷尽校验，不通过就别想出包
     运行期（本文件）            —— 轻量校验，坏题进 quarantine 并提示 */
(function (ns) {
  'use strict';

  var TYPES = ['single', 'multi', 'judge', 'blank', 'term', 'short', 'calc'];
  var DIFFS = ['basic', 'medium', 'hard'];
  var KINDS = ['textbook', 'exam-original', 'exam-adapted', 'extension'];
  var OBJECTIVE = ['single', 'multi', 'judge'];
  var SUBJECTIVE = ['term', 'short', 'calc'];
  var ADAPTED_TAG = '真题改编';

  function isStr(x) { return typeof x === 'string' && x.length > 0; }

  /**
   * 校验一道题。返回 { ok: bool, errors: [string] }。
   * 只报 error 级问题（warn 级留给构建期）。
   */
  function validate(q, secKeys) {
    var errs = [];
    if (!q || typeof q !== 'object') return { ok: false, errors: ['题目不是对象'] };
    if (!isStr(q.id)) errs.push('缺 id');
    if (TYPES.indexOf(q.type) < 0) errs.push('type 非法: ' + q.type);
    if (DIFFS.indexOf(q.difficulty) < 0) errs.push('difficulty 非法: ' + q.difficulty);
    if (typeof q.chapter !== 'number' || q.chapter < 1 || q.chapter > 12) {
      errs.push('chapter 非法: ' + q.chapter);
    }
    if (!isStr(q.stem)) errs.push('缺题干');
    if (!q.source || !isStr(q.source.text)) errs.push('缺出处');
    if (q.source && KINDS.indexOf(q.source.kind) < 0) {
      errs.push('source.kind 非法: ' + q.source.kind);
    }
    if (secKeys && secKeys.length && secKeys.indexOf(q.knowledgePoint) < 0) {
      errs.push('知识点未登记: ' + q.knowledgePoint);
    }
    if (OBJECTIVE.indexOf(q.type) >= 0) {
      var opts = q.options || [];
      if (!opts.length) {
        errs.push('客观题缺选项');
      } else {
        var letters = 'ABCDE'.slice(0, opts.length);
        (q.answer || []).forEach(function (a) {
          if (letters.indexOf(a) < 0) errs.push('答案 ' + a + ' 不在选项内');
        });
      }
      if ((q.type === 'single' || q.type === 'judge') && (q.answer || []).length !== 1) {
        errs.push(q.type + ' 答案数 != 1');
      }
      if (q.type === 'multi' && (q.answer || []).length < 2) {
        errs.push('多选答案数 < 2');
      }
    }
    if (SUBJECTIVE.indexOf(q.type) >= 0) {
      if (!isStr(q.answerText)) errs.push('主观题缺参考答案');
      if (!q.points || !q.points.length) errs.push('主观题缺采分点');
    }
    if (!isStr(q.explanation)) errs.push('缺解析');
    if (q.source && q.source.kind === 'exam-original') {
      if (!isStr(q.source.url)) errs.push('原题缺来源链接');
      if (!q.provenance || q.provenance.level !== 'original') {
        errs.push('原题的 provenance.level 必须是 original');
      }
    }
    if (q.source && q.source.kind === 'exam-adapted') {
      if ((q.tags || []).indexOf(ADAPTED_TAG) < 0) errs.push('改编题缺「' + ADAPTED_TAG + '」标记');
      if (!q.provenance || !isStr(q.provenance.note)) errs.push('改编题缺改编依据');
    }
    return { ok: errs.length === 0, errors: errs };
  }

  /** 归一化：补运行期需要的默认字段 */
  function normalize(q) {
    var n = {};
    Object.keys(q || {}).forEach(function (k) { n[k] = q[k]; });
    if (!n.knowledgePoints) {
      n.knowledgePoints = n.knowledgePoint ? [n.knowledgePoint] : [];
    }
    if (!n.provenance) n.provenance = { level: null, url: null, note: '' };
    if (!n.source) n.source = { text: '', kind: 'textbook' };
    if (!n.options) n.options = [];
    if (!n.answer) n.answer = [];
    if (!n.tags) n.tags = [];
    if (!n.verify) n.verify = [];
    return n;
  }

  ns.schema = {
    TYPES: TYPES, DIFFS: DIFFS, KINDS: KINDS,
    OBJECTIVE: OBJECTIVE, SUBJECTIVE: SUBJECTIVE,
    validate: validate, normalize: normalize
  };
})(window.QX = window.QX || {});
