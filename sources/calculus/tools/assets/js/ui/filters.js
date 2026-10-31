/* ui/filters.js — 左侧筛选面板
   维度：题型 / 难度 / 章节 / 知识点 / 出处类型 / 练习设置。
   筛选条件写在 session.filter 里，改动即触发题序重算。 */
(function (ns) {
  'use strict';

  var dom = null, session = null, store = null;
  var catalog = null;
  var counts = { type: {}, diff: {}, chapter: {}, kp: {}, kind: {} };
  var nodes = {};
  var onChange = null;

  function init(deps) {
    dom = deps.dom;
    session = deps.session;
    store = deps.store;
    onChange = deps.onChange;
    catalog = deps.catalog || { chapters: [], typeGroups: [], diffs: [], knowledgePoints: [] };
    nodes = {
      types: document.getElementById('f-types'),
      diffs: document.getElementById('f-diffs'),
      chapters: document.getElementById('f-chapters'),
      kp: document.getElementById('f-kp'),
      kinds: document.getElementById('f-kinds'),
      order: document.getElementById('f-order'),
      shuffle: document.getElementById('f-shuffle'),
      wrongonly: document.getElementById('f-wrongonly'),
      favonly: document.getElementById('f-favonly'),
      kw: document.getElementById('f-kw'),
      count: document.getElementById('f-count')
    };
    bindControls();
    collapseOnNarrow();
  }

  /** 窄屏判定：与 app.css 的 `@media (max-width: 860px)` 断点保持一致。 */
  function isNarrow() {
    if (window.matchMedia) return window.matchMedia('(max-width: 860px)').matches;
    return window.innerWidth <= 860;
  }

  /** 手机上默认折叠筛选块：首屏必须是题目，不是筛选面板。
      只在启动时做一次，不跟用户之后的手动展开/收起打架。 */
  function collapseOnNarrow() {
    if (!isNarrow()) return;
    var blocks = document.querySelectorAll('#filters details.filter-block');
    for (var i = 0; i < blocks.length; i++) blocks[i].removeAttribute('open');
  }

  /** 更新 catalog（index 加载完成后才有真数据）。 */
  function setCatalog(c) {
    if (c) catalog = c;
    return catalog;
  }

  /**
   * 静态控件（排序 / 随机乱序 / 只看错题 / 只看收藏 / 关键词）的监听**只绑一次**。
   * 以前这些监听绑在 build() 里，而 build() 会被调用多次（启动、切换练习模式、
   * 重新开始…）→ 监听重复叠加，改一次排序会触发多次 onChange。
   */
  function bindControls() {
    if (nodes.order) {
      nodes.order.addEventListener('change', function () {
        store.set(function (st) { st.settings.order = nodes.order.value; });
        onChange();
      });
    }
    if (nodes.shuffle) {
      nodes.shuffle.addEventListener('change', function () {
        store.set(function (st) { st.settings.shuffle = nodes.shuffle.checked; });
        onChange();
      });
    }
    if (nodes.wrongonly) {
      nodes.wrongonly.addEventListener('change', function () {
        session.raw.filter.onlyWrong = nodes.wrongonly.checked;
        onChange();
      });
    }
    if (nodes.favonly) {
      nodes.favonly.addEventListener('change', function () {
        session.raw.filter.onlyFavorite = nodes.favonly.checked;
        onChange();
      });
    }
    if (nodes.kw) {
      nodes.kw.addEventListener('input', function () {
        session.raw.filter.kw = nodes.kw.value;
        onChange();
      });
    }
  }

  /** 统计各维度题量，供 chip 上显示括号数字 */
  function tally(questions) {
    counts = { type: {}, diff: {}, chapter: {}, kp: {}, kind: {} };
    (questions || []).forEach(function (q) {
      counts.type[q.typeGroup] = (counts.type[q.typeGroup] || 0) + 1;
      counts.diff[q.difficulty] = (counts.diff[q.difficulty] || 0) + 1;
      counts.chapter[String(q.chapter)] = (counts.chapter[String(q.chapter)] || 0) + 1;
      counts.kind[(q.source && q.source.kind) || 'textbook'] = (counts.kind[(q.source && q.source.kind) || 'textbook'] || 0) + 1;
      (q.knowledgePoints || [q.knowledgePoint]).forEach(function (k) {
        if (k) counts.kp[k] = (counts.kp[k] || 0) + 1;
      });
    });
  }

  function chip(label, count, active, onToggle) {
    var b = dom.el('button', {
      type: 'button', class: 'chip', 'aria-pressed': active ? 'true' : 'false',
      title: label
    });
    b.appendChild(document.createTextNode(label));
    if (count !== undefined) {
      b.appendChild(dom.el('small', { text: '(' + count + ')' }));
    }
    b.addEventListener('click', function () {
      onToggle();
      syncChips();
      onChange();
    });
    return b;
  }

  function toggleIn(arr, v) {
    var i = arr.indexOf(v);
    if (i >= 0) arr.splice(i, 1); else arr.push(v);
  }

  function buildChips(container, list, key, countMap) {
    if (!container) return;
    dom.clear(container);
    var filter = session.raw.filter;
    list.forEach(function (item) {
      var c = countMap ? (countMap[item.key] || 0) : undefined;
      container.appendChild(chip(item.label, c, filter[key].indexOf(item.key) >= 0, function () {
        toggleIn(filter[key], item.key);
      }));
    });
  }

  function buildKpSelect() {
    if (!nodes.kp) return;
    dom.clear(nodes.kp);
    var filter = session.raw.filter;
    var sel = dom.el('select', { id: 'f-kp-select' });
    sel.appendChild(dom.el('option', { value: '', text: '全部知识点' }));
    var byChapter = {};
    visibleChipList('knowledgePoints').forEach(function (kp) {
      if (!byChapter[kp.chapter]) byChapter[kp.chapter] = [];
      byChapter[kp.chapter].push(kp);
    });
    Object.keys(byChapter).sort(function (a, b) { return Number(a) - Number(b); }).forEach(function (ch) {
      var og = dom.el('optgroup', { label: '第 ' + ch + ' 章' });
      byChapter[ch].forEach(function (kp) {
        var o = dom.el('option', {
          value: kp.key,
          text: kp.key + ' ' + kp.label + '（' + countOf('knowledgePoints', kp.key) + '）'
        });
        og.appendChild(o);
      });
      sel.appendChild(og);
    });
    sel.value = filter.knowledgePoints.length === 1 ? filter.knowledgePoints[0] : '';
    sel.addEventListener('change', function () {
      filter.knowledgePoints = sel.value ? [sel.value] : [];
      onChange();
    });
    nodes.kp.appendChild(sel);
  }

  var KIND_LABEL = {
    textbook: '教材命题', 'exam-original': '真题原题', 'exam-adapted': '真题改编', extension: '引申'
  };

  /**
   * 某个维度在 catalog 里的全部 chip 项 [{key, label}]（不含「界面是否展示」的判断）。
   */
  function chipList(dim) {
    if (dim === 'types') {
      return (catalog.typeGroups || []).map(function (t) { return { key: t.key, label: t.label }; });
    }
    if (dim === 'diffs') {
      return (catalog.diffs || []).map(function (d) { return { key: d.key, label: d.label }; });
    }
    if (dim === 'chapters') {
      return (catalog.chapters || []).map(function (c) {
        return { key: String(c.n), label: c.title || c.label };
      });
    }
    if (dim === 'kinds') {
      return (catalog.kinds || []).map(function (k) {
        return { key: k, label: KIND_LABEL[k] || k };
      });
    }
    if (dim === 'knowledgePoints') {
      return (catalog.knowledgePoints || []).map(function (k) {
        return { key: k.key, label: k.label, chapter: k.chapter };
      });
    }
    return [];
  }

  /** 某个维度所有 chip 的 key（门禁用，含 0 题的项）。 */
  function chipKeys(dim) {
    return chipList(dim).map(function (x) { return x.key; });
  }

  /** 某个维度的题量（chip 括号上写的那个数）。 */
  function countOf(dim, key) {
    var m = {
      types: counts.type, diffs: counts.diff, chapters: counts.chapter,
      kinds: counts.kind, knowledgePoints: counts.kp
    }[dim];
    return m ? (m[key] || 0) : 0;
  }

  /**
   * 界面上真正展示的 chip 项：**只保留有题的**。
   * 一个写着「真题改编(0)」的 chip 点下去必然是空白页——那是死路，不该给用户。
   */
  function visibleChipList(dim) {
    return chipList(dim).filter(function (x) { return countOf(dim, x.key) > 0; });
  }

  function build() {
    var filter = session.raw.filter;
    buildChips(nodes.types, visibleChipList('types'), 'types', counts.type);
    buildChips(nodes.diffs, visibleChipList('diffs'), 'diffs', counts.diff);
    buildChips(nodes.chapters, visibleChipList('chapters'), 'chapters', counts.chapter);
    buildChips(nodes.kinds, visibleChipList('kinds'), 'kinds', counts.kind);
    buildKpSelect();

    // 控件取值同步（监听已在 init 时绑好，不在这里重复绑定）
    if (nodes.order) {
      nodes.order.value = (store.get().settings.order) || 'difficulty_desc';
    }
    if (nodes.shuffle) {
      nodes.shuffle.checked = !!(store.get().settings.shuffle);
    }
    if (nodes.wrongonly) {
      nodes.wrongonly.checked = !!filter.onlyWrong;
    }
    if (nodes.favonly) {
      nodes.favonly.checked = !!filter.onlyFavorite;
    }
    if (nodes.kw) {
      nodes.kw.value = filter.kw || '';
    }
  }

  /** 只刷新 chip 的选中态（不重建 DOM），避免输入关键词时闪烁 */
  function syncChips() {
    var filter = session.raw.filter;
    [['types', nodes.types], ['diffs', nodes.diffs], ['chapters', nodes.chapters], ['kinds', nodes.kinds]]
      .forEach(function (pair) {
        var box = pair[1];
        if (!box) return;
        var chips = box.querySelectorAll('.chip');
        var key = pair[0];
        // 每个 chip 的顺序与构建时一致，靠 index 对齐
        var list = visibleChipList(key);
        for (var i = 0; i < chips.length && i < list.length; i++) {
          chips[i].setAttribute('aria-pressed', filter[key].indexOf(list[i].key) >= 0 ? 'true' : 'false');
        }
      });
  }

  function setCount(n) {
    if (nodes.count) nodes.count.textContent = '当前筛选命中 ' + n + ' 题';
  }

  ns.filters = {
    init: init, build: build, tally: tally, syncChips: syncChips, setCount: setCount,
    setCatalog: setCatalog,
    chipList: chipList, chipKeys: chipKeys, visibleChipList: visibleChipList,
    countOf: countOf,
    KIND_LABEL: KIND_LABEL
  };
})(window.QX = window.QX || {});
