/* core/judge.js — 判分（无 DOM 依赖）
   逻辑自 app.js v1 原样迁出：多选「全对满分 / 少选 0 分 / 错选 0 分」；
   填空题做文本归一化 + 数值等价（3/2 ≡ 1.5）。 */
(function (ns) {
  'use strict';

  function fullScore(q) {
    // 主观题以采分点之和为准：Q() 里 points 的 partial 默认 2，
    // 采分点个数与题型对应（term 2 / short 3 / calc 4），
    // 用固定表会把「满分」说错——自评得分与满分必须同一口径。
    if (q && (q.type === 'term' || q.type === 'short' || q.type === 'calc')) {
      if (q.points && q.points.length) {
        var sum = 0;
        for (var i = 0; i < q.points.length; i++) {
          sum += (q.points[i] && q.points[i].partial !== undefined) ? q.points[i].partial : 2;
        }
        return sum;
      }
    }
    if (q.type === 'single') return 2;
    if (q.type === 'multi') return 3;
    if (q.type === 'judge') return 2;
    if (q.type === 'blank') return 2;
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

  /** 文本归一化：用于填空题判分 */
  function norm(s) {
    if (s == null) return '';
    var t = String(s);
    t = t.replace(/[　\s]+/g, '');
    // 全角字母/数字/标点 → 半角。中文输入法下打「ＡＢ」「１，２」很常见，
    // 不折叠就会被判错，而学生并没有写错。
    t = t.replace(/[\uFF01-\uFF5E]/g, function (ch) {
      return String.fromCharCode(ch.charCodeAt(0) - 0xFEE0);
    });
    t = t.replace(/\u3000/g, '');
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

  function numOf(s) {
    if (!/^-?\d+(\.\d+)?$/.test(s)) return null;
    return parseFloat(s);
  }

  function blankMatch(input, q) {
    var v = norm(input);
    if (!v) return false;
    var accepts = (q.accept || q.answer || []).map(norm);
    for (var i = 0; i < accepts.length; i++) {
      if (accepts[i] === v) return true;
    }
    // 数值等价：3/2 与 1.5、1/2 与 0.5、2 与 2.0
    // 注意比较对象也可能是分数（"3/2" vs "1.5"），所以两边都要能求值。
    var nv = evalNum(v);
    if (nv !== null && nv !== undefined) {
      for (var j = 0; j < accepts.length; j++) {
        var na = evalNum(accepts[j]);
        if (na !== null && na !== undefined && Math.abs(na - nv) < 1e-9) return true;
      }
    }
    return false;
  }

  /** 数值型答案（如 "1/2"）求值，用于展示参考答案 */
  function evalNum(s) {
    var m = /^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/.exec(norm(s));
    if (m) return parseFloat(m[1]) / parseFloat(m[2]);
    return numOf(norm(s));
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

  ns.judge = {
    fullScore: fullScore,
    multiVerdict: multiVerdict,
    judgeObjective: judgeObjective,
    blankMatch: blankMatch,
    norm: norm,
    numOf: numOf,
    evalNum: evalNum
  };
})(window.QX = window.QX || {});
