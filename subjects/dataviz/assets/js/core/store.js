/* core/store.js — 本地存储引导：读取新命名空间，必要时从 legacy 键整体迁移。
   迁移规则（见 docs/decisions.md D7）：
     新键 quiz-<id>-v2 不存在时，按顺序读 legacyKeys，取第一个 v===1 的状态原样迁入新键；
     legacy 键保留不动（用户回退到旧版站点进度不丢）。bankId 不同也照迁——
     会话顺序由 app.js 的 orderIsStale() 重建，错题本里失效的题号在渲染时自动跳过。 */
(function (ns) {
  'use strict';

  function readRaw(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }

  function parse(key) {
    var raw = readRaw(key);
    if (!raw) return null;
    try {
      var data = JSON.parse(raw);
      if (data && data.v === 1) return data;
    } catch (e) { /* 坏数据当不存在 */ }
    return null;
  }

  /** 返回 {state, migratedFrom}；state 可能仍为 null（全新用户）。 */
  ns.bootstrap = function (cfg) {
    var state = parse(cfg.storageKey);
    if (state) return { state: state, migratedFrom: null };
    for (var i = 0; i < (cfg.legacyKeys || []).length; i++) {
      var legacy = parse(cfg.legacyKeys[i]);
      if (legacy) {
        try { window.localStorage.setItem(cfg.storageKey, JSON.stringify(legacy)); } catch (e) {}
        return { state: legacy, migratedFrom: cfg.legacyKeys[i] };
      }
    }
    return { state: null, migratedFrom: null };
  };
})(window.LAStore = window.LAStore || {});
