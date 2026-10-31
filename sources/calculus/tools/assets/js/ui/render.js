/* ui/render.js — 单题聚焦渲染（一次只渲染一道题 + 答题卡题号）
   性能口径：680 题下若整块 innerHTML 重建，每次交互都是 O(n)。
   这里改为「只重建当前题的卡片 DOM」，题序、答题卡、统计都是增量更新。

   解析文本体例（题库统一）：
     **答案依据**：…
     **考点出处**：…
     A 错：…
   渲染时拆成「答案依据 / 逐项错因 / 其它段落」三块。 */
(function (ns) {
  'use strict';

  var dom = null;
  var TYPE_LABEL = {
    single: '单选题', multi: '多选题', judge: '判断题', blank: '填空题',
    term: '名词解释', short: '简答题', calc: '计算与分析题'
  };
  var DIFF_LABEL = { basic: '基础', medium: '中等', hard: '困难' };
  var LETTERS = 'ABCDE';

  function init(deps) { dom = deps.dom; }

  /* ---------------- 解析文本拆解 ---------------- */
  var SEC_RE = /^\*\*(.+?)\*\*\s*[：:]\s*(.*)$/;
  var REASON_RE = /^([A-E])\s*(错|不对|不成立|对|正确|成立)\s*[：:、]?\s*(.*)$/;

  /** 解析区的渲染顺序：逐项错因 → 答案依据与解析。
      依据段**独立成块**，不再依赖「其它段落」是否为空 ——
      整篇解析只有「答案依据 + 逐项错因」时（856 题中 103 题属此类），
      依据曾因为挂在其它段落上而被整段丢弃。 */
  function explainBlocks(expl) {
    var parts = splitExplanation(expl);
    var blocks = [];
    if (parts.reasons.length) {
      blocks.push({ kind: 'reasons', items: parts.reasons });
    }
    var prose = parts.rest.filter(function (s) { return s.trim(); });
    if (prose.length || parts.basis) {
      blocks.push({ kind: 'prose', items: prose, basis: parts.basis });
    }
    return blocks;
  }

  function splitExplanation(expl) {
    var out = { basis: '', reasons: [], rest: [] };
    var lines = String(expl || '').split('\n');
    var cur = 'rest';
    lines.forEach(function (ln) {
      if (!ln.trim()) return;
      var m = ln.match(SEC_RE);
      if (m) {
        var key = m[1];
        if (/答案依据/.test(key)) { cur = 'basis'; out.basis = m[2]; return; }
        if (/辨析|错因|易错/.test(key)) { cur = 'rest'; out.rest.push(ln); return; }
        cur = 'rest';
        out.rest.push(ln);
        return;
      }
      var r = ln.match(REASON_RE);
      if (r) {
        // 「X 错 / 不对 / 不成立」= 错项；「X 对 / 正确 / 成立」= 对项
        var isWrong = /错|不对|不成立/.test(r[2]);
        out.reasons.push({ letter: r[1], ok: !isWrong, text: r[3] || ln });
        return;
      }
      out.rest.push(ln);
    });
    if (!out.basis) {
      // 没有显式「答案依据」段：把第一段非错因内容当作依据，
      // 并把它从「其它段落」里摘掉 —— 否则同一段会被渲染两遍
      //（一遍当依据、一遍当普通段落）。
      var idx = -1;
      for (var k = 0; k < out.rest.length; k++) {
        if (!REASON_RE.test(out.rest[k])) { idx = k; break; }
      }
      if (idx >= 0) {
        out.basis = out.rest[idx].replace(SEC_RE, '').trim();
        out.rest.splice(idx, 1);
      }
    }
    // 「答案依据」里常有「故 C 正确」这类对项断言，单独抽出来，
    // 否则逐项错因只列错项、漏掉正确项，学生看不到完整对照。
    var basisReasons = scanBasis(out.basis);
    basisReasons.forEach(function (br) {
      var dup = out.reasons.some(function (r) { return r.letter === br.letter; });
      if (!dup) out.reasons.push(br);
    });
    out.reasons.sort(function (a, b) { return a.letter < b.letter ? -1 : (a.letter > b.letter ? 1 : 0); });
    return out;
  }

  /** 从「答案依据」里抽出「X 正确 / X 成立」式的对项断言 */
  function scanBasis(basis) {
    var out = [];
    var text = String(basis || '');
    if (!text) return out;
    var sentences = text.split(/[。；;]/);
    var re = /([A-E])\s*(?:选项)?\s*(正确|成立)/g;
    var m;
    while ((m = re.exec(text)) !== null) {
      var L = m[1];
      var snippet = '';
      for (var i = 0; i < sentences.length; i++) {
        if (sentences[i].indexOf(L) >= 0 && /(正确|成立)/.test(sentences[i])) {
          snippet = sentences[i].trim();
          break;
        }
      }
      out.push({ letter: L, ok: true, text: snippet || (L + ' 正确') });
    }
    return out;
  }

  function mdLite(text) {
    // 只处理两种：**粗体** 与换行；其余按文本转义后交给 KaTeX。
    return dom.esc(text)
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }

  /* ---------------- 头部徽标 ---------------- */
  function buildHead(q, view) {
    var head = dom.el('div', { class: 'q-head' });
    head.appendChild(dom.el('span', {
      class: 'q-no',
      text: '第 ' + (view.index + 1) + ' / ' + view.total + ' 题'
    }));
    head.appendChild(dom.el('span', { class: 'badge badge-type', text: TYPE_LABEL[q.type] || q.type }));
    head.appendChild(dom.el('span', {
      class: 'badge badge-diff-' + q.difficulty,
      text: DIFF_LABEL[q.difficulty] || q.difficulty
    }));
    head.appendChild(dom.el('span', { class: 'badge badge-kp', text: q.knowledgePoint }));

    var kpExtra = (q.knowledgePoints || []).filter(function (k) { return k && k !== q.knowledgePoint; });
    if (kpExtra.length) {
      head.appendChild(dom.el('span', { class: 'badge badge-kp', text: '＋' + kpExtra.join('、') }));
    }

    var src = q.source || {};
    if (src.kind === 'exam-original') {
      head.appendChild(dom.el('span', { class: 'badge badge-fluoro', text: '真题原题' }));
    } else if (src.kind === 'exam-adapted') {
      head.appendChild(dom.el('span', { class: 'badge badge-fluoro', text: '真题改编' }));
    } else if (src.kind === 'extension') {
      head.appendChild(dom.el('span', { class: 'badge badge-fluoro', text: '引申' }));
    }
    if (src.year) {
      head.appendChild(dom.el('span', {
        class: 'badge badge-src',
        text: [src.year, src.region, src.paper, src.number ? '第' + src.number + '题' : '']
          .filter(Boolean).join(' · ')
      }));
    }

    var spacer = dom.el('span', { class: 'spacer', style: { flex: '1' } });
    head.appendChild(spacer);

    var favBtn = dom.el('button', {
      type: 'button', class: 'btn btn-sm' + (view.fav ? ' btn-primary' : ' btn-ghost'),
      title: '收藏（F）', 'aria-pressed': view.fav ? 'true' : 'false',
      text: view.fav ? '★ 已收藏' : '☆ 收藏'
    });
    favBtn.addEventListener('click', function () { view.onToggleFav(); });
    head.appendChild(favBtn);
    return head;
  }

  /* ---------------- 作答区 ---------------- */
  function buildOptions(q, view) {
    var wrap = dom.el('div', { class: 'q-options' });
    var picked = view.picked || [];
    var locked = !!view.record;

    (q.options || []).forEach(function (text, i) {
      var L = LETTERS[i];
      var isPicked = picked.indexOf(L) >= 0;
      var cls = 'option';
      if (locked) {
        cls += ' locked';
        if ((q.answer || []).indexOf(L) >= 0) cls += ' is-correct';
        else if (isPicked) cls += ' is-wrong';
      } else if (isPicked) {
        cls += ' picked';
      }
      var opt = dom.el('div', {
        class: cls, role: 'radio', tabindex: locked ? '-1' : '0',
        'aria-checked': isPicked ? 'true' : 'false', 'data-letter': L
      });
      opt.appendChild(dom.el('span', { class: 'option-letter', text: L }));
      opt.appendChild(dom.el('span', { class: 'option-text', html: dom.esc(text) }));
      if (!locked) {
        opt.addEventListener('click', function () { view.onPick(L); });
        // ⚠ 选项元素上**不能**再挂 keydown 处理器（2026-10-31 线上复验时实测到）。
        // 选项自己处理 Enter，会和全局快捷键「Enter = 提交答案」抢同一个键：
        //   ① Enter 先落到选项 → onPick(L)；
        //   ② 多选题的 onPick 是 toggle（再点一次＝取消），于是刚选好的答案被自己抹掉；
        //   ③ 事件继续冒泡到全局 → 提交时缓冲区已空 → 弹「还没作答，先选一个选项」。
        // 现象：多选题上按 Enter（快捷键面板里写明的「提交答案」）根本提交不了，
        // 而点「提交答案（Enter）」按钮又完全正常 —— 纯键盘路径是坏的，鼠标路径是好的。
        // 现在选项的键盘选择统一交给全局的 A–D / 1–4；
        // Enter 归「提交答案」、空格归「下一题」，与快捷键面板的约定一致。
        // 回归门禁：tools/check_keyboard_contract.js（造错必须报错）。
      }
      wrap.appendChild(opt);
    });
    return wrap;
  }

  function buildBlank(q, view) {
    var wrap = dom.el('div', { class: 'q-options' });
    var input = dom.el('input', {
      type: 'text', class: 'blank-input', id: 'blank-input',
      placeholder: '输入答案，支持 3/2 或 1.5 等等价写法',
      value: (view.picked && view.picked[0]) || '',
      autocomplete: 'off', spellcheck: 'false'
    });
    input.addEventListener('input', function () { view.onPick(input.value); });
    if (view.record) { input.setAttribute('disabled', 'disabled'); }
    wrap.appendChild(input);
    return wrap;
  }

  /* ---------------- 采分点自评 ---------------- */
  function buildPoints(q, view) {
    var ul = dom.el('ul', { class: 'points' });
    var hits = (view.record && view.record.pointsHit) || null;
    (q.points || []).forEach(function (p, i) {
      var hit = hits ? hits[i] : null;
      var li = dom.el('li', { class: 'point' + (hit === true ? ' hit-true' : hit === false ? ' hit-false' : '') });
      li.appendChild(dom.el('span', { class: 'point-main', html: dom.esc(p.text) }));
      var btns = dom.el('span', { class: 'point-btns' });
      var bHit = dom.el('button', {
        type: 'button', class: 'point-btn hit', 'data-hit': 'true', 'data-i': String(i),
        text: '得到', 'aria-pressed': hit === true ? 'true' : 'false'
      });
      var bMiss = dom.el('button', {
        type: 'button', class: 'point-btn hit', 'data-hit': 'false', 'data-i': String(i),
        text: '未得到', 'aria-pressed': hit === false ? 'true' : 'false'
      });
      if (hit === true) bHit.classList.add('on');
      if (hit === false) bMiss.classList.add('on');
      bHit.addEventListener('click', function () { view.onSelfGrade(i, true); });
      bMiss.addEventListener('click', function () { view.onSelfGrade(i, false); });
      btns.appendChild(bHit);
      btns.appendChild(bMiss);
      li.appendChild(btns);
      ul.appendChild(li);
    });
    return ul;
  }

  /* ---------------- 判定条 ---------------- */
  function buildVerdict(q, view) {
    var r = view.record;
    var bar = dom.el('div', { class: 'verdict' });
    var text, cls;
    if (r.selfGraded) {
      var full = r.full, earned = r.earned;
      cls = earned >= full ? 'verdict-ok' : (earned > 0 ? 'verdict-warn' : 'verdict-bad');
      text = earned >= full ? '采分点全部得到' : (earned > 0 ? '部分采分点未得到' : '采分点均未得到');
    } else if (r.correct === true) {
      cls = 'verdict-ok'; text = '答对了';
    } else if (r.correct === false) {
      var picked = view.picked || [];
      var isMulti = q.type === 'multi';
      var partial = isMulti && picked.length > 0 &&
        picked.every(function (L) { return (q.answer || []).indexOf(L) >= 0; });
      cls = partial ? 'verdict-warn' : 'verdict-bad';
      text = partial ? '少选（不得分）' : '答错了';
    } else {
      cls = 'verdict-warn'; text = '已作答';
    }
    bar.className = 'verdict ' + cls;
    bar.appendChild(dom.el('span', { text: text }));
    bar.appendChild(dom.el('span', { class: 'verdict-score', text: r.earned + ' / ' + r.full + ' 分' }));
    return bar;
  }

  /* ---------------- 解析区 ---------------- */
  function buildExplain(q, view) {
    var box = dom.el('div', { class: 'explain' });

    if (q.type === 'single' || q.type === 'multi' || q.type === 'judge') {
      var ansLetters = (q.answer || []).join('、');
      box.appendChild(dom.el('h4', { text: '正确答案' }));
      box.appendChild(dom.el('div', { class: 'answer-text', html: mdLite('**' + ansLetters + '**') }));
    } else if (q.answerText) {
      box.appendChild(dom.el('h4', { text: '参考答案' }));
      box.appendChild(dom.el('div', { class: 'answer-text', html: mdLite(q.answerText) }));
    }

    var blocks = explainBlocks(q.explanation);
    blocks.forEach(function (blk) {
      if (blk.kind === 'reasons') {
        box.appendChild(dom.el('h4', { text: '逐项错因' }));
        var rs = dom.el('div', { class: 'reasons' });
        blk.items.forEach(function (rr) {
          var row = dom.el('div', { class: 'reason ' + (rr.ok ? 'ok' : 'bad') });
          row.appendChild(dom.el('span', { class: 'reason-letter', text: rr.letter }));
          row.appendChild(dom.el('span', { html: mdLite(rr.text) }));
          rs.appendChild(row);
        });
        box.appendChild(rs);
      } else if (blk.kind === 'prose') {
        box.appendChild(dom.el('h4', { text: '答案依据与解析' }));
        var prose = dom.el('div', { class: 'prose' });
        blk.items.forEach(function (s) { prose.appendChild(dom.el('p', { html: mdLite(s) })); });
        if (blk.basis) prose.appendChild(dom.el('p', { html: mdLite('**答案依据**：' + blk.basis) }));
        box.appendChild(prose);
      }
    });

    if (q.misconception) {
      box.appendChild(dom.el('h4', { text: '易错点' }));
      box.appendChild(dom.el('div', { class: 'prose', html: mdLite(q.misconception) }));
    }
    if (q.extension) {
      box.appendChild(dom.el('h4', { text: '引申' }));
      box.appendChild(dom.el('div', { class: 'prose', html: mdLite(q.extension) }));
    }

    if ((q.type === 'term' || q.type === 'short' || q.type === 'calc') && (q.points || []).length) {
      box.appendChild(dom.el('h4', { text: '采分点自评' }));
      box.appendChild(buildPoints(q, view));
    }

    // 来源与溯源
    var src = q.source || {};
    var prov = q.provenance || {};
    var meta = dom.el('div', { class: 'provenance' });
    var bits = [];
    bits.push('<b>出处</b>：' + dom.esc(src.text || ''));
    if (src.year) {
      bits.push('<b>来源</b>：' + dom.esc([src.year, src.region, src.paper,
        src.number ? '第 ' + src.number + ' 题' : ''].filter(Boolean).join(' · ')));
    }
    if (prov.level) {
      bits.push('<b>溯源等级</b>：' + dom.esc(prov.level === 'original' ? '原题' : '改编'));
    }
    if (prov.note) bits.push('<b>改编说明</b>：' + dom.esc(prov.note));
    if (prov.verifiedAt) bits.push('<b>核验时间</b>：' + dom.esc(prov.verifiedAt));
    var url = prov.url || src.url;
    if (url) {
      bits.push('<b>原始链接</b>：<a href="' + dom.esc(url) + '" target="_blank" rel="noopener noreferrer">' +
        dom.esc(url) + '</a>');
    }
    meta.innerHTML = bits.join('<br>');
    box.appendChild(meta);

    return box;
  }

  /* ---------------- 操作栏 ---------------- */
  function buildActions(q, view) {
    var bar = dom.el('div', { class: 'q-actions' });
    var isSubjective = (q.type === 'term' || q.type === 'short' || q.type === 'calc');

    if (!view.record) {
      if (isSubjective) {
        bar.appendChild(dom.el('span', {
          class: 'muted', style: { fontSize: 'var(--fs-xs)' },
          text: '主观题由你按采分点自评 —— 提交后展开参考答案与采分点。'
        }));
      } else {
        var sub = dom.el('button', { type: 'button', class: 'btn btn-primary', text: '提交答案（Enter）' });
        sub.addEventListener('click', function () { view.onSubmit(); });
        bar.appendChild(sub);
        var picked = view.picked || [];
        bar.appendChild(dom.el('span', {
          class: 'muted', style: { fontSize: 'var(--fs-xs)' },
          text: picked.length ? ('已选 ' + picked.join('、')) : '未作答'
        }));
      }
    } else {
      var redo = dom.el('button', { type: 'button', class: 'btn', text: '重做本题' });
      redo.addEventListener('click', function () { view.onRedo(); });
      bar.appendChild(redo);
      var wb = dom.el('button', { type: 'button', class: 'btn btn-ghost', text: '加入错题本（W）' });
      wb.addEventListener('click', function () { view.onToggleWrong(); });
      bar.appendChild(wb);
    }

    bar.appendChild(dom.el('span', { class: 'spacer' }));

    var prev = dom.el('button', { type: 'button', class: 'btn btn-ghost', text: '← 上一题' });
    prev.addEventListener('click', function () { view.onNav(-1); });
    bar.appendChild(prev);
    var next = dom.el('button', { type: 'button', class: 'btn', text: '下一题 →' });
    next.addEventListener('click', function () { view.onNav(1); });
    bar.appendChild(next);
    return bar;
  }

  /* ---------------- 主渲染 ---------------- */
  function render(container, q, view) {
    dom.clear(container);
    if (!q) {
      container.appendChild(dom.el('div', { class: 'empty' }, [
        dom.el('div', { class: 'empty-icon', text: '∅' }),
        dom.el('h3', { text: '当前筛选没有匹配的题目' }),
        dom.el('p', { text: '试着放宽筛选条件，或到「错题本」里挑几道练。' })
      ]));
      return;
    }

    var card = dom.el('article', { class: 'q-card', id: 'q-card' });
    card.appendChild(buildHead(q, view));

    var stem = dom.el('div', { class: 'q-stem', html: mdLite(q.stem) });
    card.appendChild(stem);

    if (q.type === 'blank') card.appendChild(buildBlank(q, view));
    else if (q.options && q.options.length) card.appendChild(buildOptions(q, view));
    else if (!view.record) {
      card.appendChild(dom.el('div', { class: 'q-options' }, [
        dom.el('button', {
          type: 'button', class: 'btn btn-primary', text: '提交并查看解析',
          onclick: function () { view.onSubmit(); }
        })
      ]));
    }

    if (view.record) {
      var fb = dom.el('div', { class: 'feedback' });
      fb.appendChild(buildVerdict(q, view));
      fb.appendChild(buildExplain(q, view));
      card.appendChild(fb);
    }

    card.appendChild(buildActions(q, view));
    container.appendChild(card);
    dom.renderMath(card);

    if (!view.record && q.type === 'blank') {
      var inp = document.getElementById('blank-input');
      if (inp) inp.focus();
    }
  }

  ns.render = {
    init: init, render: render, splitExplanation: splitExplanation,
    explainBlocks: explainBlocks, mdLite: mdLite,
    TYPE_LABEL: TYPE_LABEL, DIFF_LABEL: DIFF_LABEL
  };
})(window.QX = window.QX || {});
