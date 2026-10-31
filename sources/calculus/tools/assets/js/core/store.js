/* core/store.js — 持久化层（无 DOM 依赖）
   状态存 localStorage，键 hx_quiz_v2；v1 键并存不覆盖。
   存储不可用时降级为内存态，功能不中断，只提示「关闭后不保留」。 */
(function (ns) {
  'use strict';

  var KEY = 'hx_quiz_v2';
  var LEGACY_KEY = 'hx_quiz_v1';
  var VERSION = 2;
  var DEBOUNCE_MS = 400;

  var mem = {};              // 存储不可用时的内存兜底
  var storageOk = true;
  var timer = null;
  var pending = false;
  var state = null;

  function now() { return Date.now(); }

  function blankState(bankId) {
    return {
      v: VERSION,
      bank: bankId || 'advanced-math-tj7-v1',
      updatedAt: 0,
      sessions: {},
      wrongBook: {},
      favorites: {},
      stats: {
        byType: {}, byDifficulty: {}, byChapter: {}, byKnowledgePoint: {},
        answerPosition: { A: 0, B: 0, C: 0, D: 0 },
        multiLetter: { A: 0, B: 0, C: 0, D: 0 },
        totalAnswered: 0, totalCorrect: 0, totalEarned: 0, totalFull: 0
      },
      settings: {
        order: 'difficulty_desc',
        shuffle: false,
        theme: 'auto',
        fontScale: 1,
        reduceMotion: false,
        lastChapter: null
      }
    };
  }

  function readRaw(key) {
    try {
      var v = window.localStorage.getItem(key);
      if (v !== null) return v;
    } catch (e) { storageOk = false; }
    return Object.prototype.hasOwnProperty.call(mem, key) ? mem[key] : null;
  }

  function writeRaw(key, val) {
    try {
      window.localStorage.setItem(key, val);
      mem[key] = val;
      return true;
    } catch (e) {
      storageOk = false;
      mem[key] = val;   // 降级：内存里继续用
      return false;
    }
  }

  function mergeWrongBook(mine, theirs) {
    Object.keys(theirs || {}).forEach(function (k) {
      var o = theirs[k], m = mine[k];
      if (!m) { mine[k] = o; return; }
      m.wrongCount = Math.max(m.wrongCount || 0, o.wrongCount || 0);
      m.resolved = !!(m.resolved || o.resolved);
      if ((o.lastWrongAt || 0) > (m.lastWrongAt || 0)) m.lastWrongAt = o.lastWrongAt;
      if (!(m.firstWrongAt)) m.firstWrongAt = o.firstWrongAt;
    });
  }

  function load(bankId) {
    var raw = readRaw(KEY);
    var data = null;
    if (raw) {
      try { data = JSON.parse(raw); } catch (e) { data = null; }
    }
    if (data && data.v !== VERSION) {
      // 版本不匹配：旧串另存一份，不覆盖用户历史
      try { window.localStorage.setItem(KEY + '-legacy-' + (data.v || 'x'), raw); }
      catch (e) { /* 存储不可用时忽略 */ }
      // v1 -> v2：只迁移统计与收藏，不迁移进行中的会话
      var legacy = null;
      var lraw = readRaw(LEGACY_KEY);
      if (lraw) { try { legacy = JSON.parse(lraw); } catch (e2) { legacy = null; } }
      state = blankState(bankId);
      if (legacy && legacy.v === 1) {
        if (legacy.stats) {
          state.stats = Object.assign(state.stats, legacy.stats);
          state.stats.answerPosition = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.answerPosition || {});
          state.stats.multiLetter = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.multiLetter || {});
        }
        if (legacy.settings) {
          state.settings.order = legacy.settings.order || state.settings.order;
          state.settings.shuffle = !!legacy.settings.shuffle;
        }
      }
    } else if (!data) {
      state = blankState(bankId);
    } else {
      var b = blankState(bankId);
      state = {
        v: VERSION,
        bank: bankId || data.bank,
        updatedAt: data.updatedAt || 0,
        sessions: data.sessions || {},
        wrongBook: data.wrongBook || {},
        favorites: data.favorites || {},
        stats: Object.assign(b.stats, data.stats || {}),
        settings: Object.assign(b.settings, data.settings || {})
      };
      state.stats.answerPosition = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.answerPosition || {});
      state.stats.multiLetter = Object.assign({ A: 0, B: 0, C: 0, D: 0 }, state.stats.multiLetter || {});
      state.stats.byKnowledgePoint = Object.assign({}, state.stats.byKnowledgePoint || {});
    }
    return state;
  }

  function save() {
    if (!state) return false;
    state.updatedAt = now();
    var ok = writeRaw(KEY, JSON.stringify(state));
    pending = false;
    return ok;
  }

  /** 多标签页保护：写入前合并外部更新的 wrongBook / favorites / sessions */
  function saveMerged() {
    if (!state) return false;
    var raw = readRaw(KEY);
    if (raw) {
      try {
        var other = JSON.parse(raw);
        if (other && other.v === VERSION && (other.updatedAt || 0) > (state.updatedAt || 0)) {
          mergeWrongBook(state.wrongBook, other.wrongBook);
          Object.keys(other.favorites || {}).forEach(function (k) {
            state.favorites[k] = other.favorites[k];
          });
          Object.keys(other.sessions || {}).forEach(function (k) {
            if (!state.sessions[k]) state.sessions[k] = other.sessions[k];
          });
        }
      } catch (e) { /* 外部数据损坏：忽略，保留本地 */ }
    }
    return schedule();
  }

  /** 400ms 去抖写盘；作答/切题高频调用时不拖慢交互 */
  function schedule() {
    if (!state) return false;
    pending = true;
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () { timer = null; save(); }, DEBOUNCE_MS);
    return true;
  }

  /** 强制立即落盘（页面隐藏 / 关闭前调用） */
  function flush() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (pending || state) return save();
    return true;
  }

  function get() { return state; }
  function set(mutator) {
    if (mutator && state) mutator(state);
    return saveMerged();
  }
  function isStorageOk() { return storageOk; }

  ns.store = {
    KEY: KEY,
    VERSION: VERSION,
    blankState: blankState,
    load: load,
    save: save,
    saveMerged: saveMerged,
    schedule: schedule,
    flush: flush,
    get: get,
    set: set,
    isStorageOk: isStorageOk,
    readRaw: readRaw,
    writeRaw: writeRaw
  };
  /** 供测试注入：强制内存态 */
  ns.store._forceMemoryMode = function () { storageOk = false; };
})(window.QX = window.QX || {});
