/* core/bank.js — 题库加载（无 DOM 依赖）
   两种运行模式，同一套调用：
     多文件站：fetch('data/index.json') + fetch('data/chNN.json')
     单文件包：window.__BANK__ 已内联全部数据，直接读内存

   坏题不拖垮整站：校验不通过的题进 quarantine，其余题照常可用。 */
(function (ns) {
  'use strict';

  var catalog = { chapters: [], secKeys: [], typeGroups: [], diffs: [] };
  var inline = null;                 // window.__BANK__（单文件包）
  var index = null;                  // index.json 内容
  var chapters = {};                 // n -> Question[]
  var loaded = {};                   // n -> true
  var quarantine = [];               // 被隔离的坏题
  var errors = {};                   // n -> Error
  var loading = {};                  // n -> Promise
  var basePath = 'data/';

  function hasInline() { return !!(inline && inline.questions); }

  /**
   * 接入内联题库（单文件包）。
   * 顺带把 catalog 立刻合并进去 —— catalog 是在 loadIndex() 里合并的，
   * 但万一调用方 setInline 之后没走 loadIndex()，筛选维度就会是空壳。
   */
  function setInline(bank) {
    inline = bank || null;
    if (inline && inline.catalog) setCatalog(inline.catalog);
  }

  /**
   * 更新 catalog。**就地合并**而不是整体替换：
   * filters 在 init() 时就拿到了 catalog 的引用（那时 index 还没加载完，
   * catalog 还是空壳），若这里换成新对象，filters 会永远握着空壳 ——
   * 表现为题型/难度/章节/知识点/出处类型五组筛选 chip 全都不渲染。
   */
  function setCatalog(c) {
    if (!c) return catalog;
    Object.keys(catalog).forEach(function (k) { delete catalog[k]; });
    Object.keys(c).forEach(function (k) { catalog[k] = c[k]; });
    return catalog;
  }

  function getCatalog() { return catalog; }
  function getIndex() { return index; }
  function getQuarantine() { return quarantine; }
  function getErrors() { return errors; }
  function isLoaded(n) { return !!loaded[n]; }
  function getChapter(n) { return chapters[n] || null; }

  function fetchJSON(url) {
    return fetch(url, { cache: 'no-cache' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' @ ' + url);
      return r.json();
    });
  }

  /** 载入索引。返回 Promise<index>。 */
  function loadIndex() {
    if (hasInline()) {
      index = inline.index || {
        bank: { id: inline.id, title: inline.title },
        chapters: [],
        total: (inline.questions || []).length
      };
      if (inline.catalog) setCatalog(inline.catalog);
      return Promise.resolve(index);
    }
    return fetchJSON(basePath + 'index.json').then(function (data) {
      index = data;
      if (data.catalog) setCatalog(data.catalog);
      return data;
    });
  }

  function checkQuestions(list) {
    var ok = [], bad = [];
    (list || []).forEach(function (q) {
      var res = ns.schema.validate(q, catalog.secKeys);
      if (res.ok) {
        ok.push(ns.schema.normalize(q));
      } else {
        var item = ns.schema.normalize(q);
        item.__errors = res.errors;
        bad.push(item);
        quarantine.push(item);
      }
    });
    return { ok: ok, bad: bad };
  }

  /**
   * 载入某一章。重复调用返回同一个 Promise。
   * 失败时把错误记进 errors 并**重新抛出**——调用方决定是重试还是降级。
   */
  function loadChapter(n) {
    var key = String(n);
    if (loaded[key]) return Promise.resolve(chapters[key] || []);
    if (loading[key]) return loading[key];
    var p;
    if (hasInline()) {
      var list = (inline.questions || []).filter(function (q) {
        return String(q.chapter) === key;
      });
      var res = checkQuestions(list);
      chapters[key] = res.ok;
      loaded[key] = true;
      p = Promise.resolve(res.ok);
    } else {
      var url = basePath + 'ch' + (n < 10 ? '0' + n : String(n)) + '.json';
      p = fetchJSON(url).then(function (data) {
        var r = checkQuestions(data.questions || data);
        chapters[key] = r.ok;
        loaded[key] = true;
        delete errors[key];
        return r.ok;
      }).catch(function (e) {
        errors[key] = e;
        throw e;
      });
    }
    loading[key] = p;
    return p;
  }

  /** 载入全部章节（单文件包是同步的，多文件站并发 fetch）。 */
  function loadAll() {
    if (hasInline()) {
      var res = checkQuestions(inline.questions || []);
      return Promise.resolve(res.ok);
    }
    var ns_ = (index && index.chapters) ? index.chapters.map(function (c) { return c.n; }) : [];
    if (!ns_.length) return Promise.resolve([]);
    return Promise.all(ns_.map(function (n) {
      return loadChapter(n).catch(function () { return []; });
    })).then(function () {
      return Object.keys(chapters).reduce(function (acc, k) {
        return acc.concat(chapters[k]);
      }, []);
    });
  }

  /** 清空缓存（用于「重试」按钮） */
  function reset() {
    chapters = {}; loaded = {}; loading = {}; errors = {}; quarantine = [];
  }

  ns.bank = {
    setInline: setInline,
    hasInline: hasInline,
    setCatalog: setCatalog,
    getCatalog: getCatalog,
    getIndex: getIndex,
    loadIndex: loadIndex,
    loadChapter: loadChapter,
    loadAll: loadAll,
    getChapter: getChapter,
    getQuarantine: getQuarantine,
    getErrors: getErrors,
    isLoaded: isLoaded,
    reset: reset,
    setBasePath: function (p) { basePath = p; }
  };
})(window.QX = window.QX || {});
