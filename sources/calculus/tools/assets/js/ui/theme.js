/* ui/theme.js — 主题（亮/暗/跟随系统）+ 字号缩放 + 动效开关
   状态落在 store.settings，UI 只读 store、写 store，不自行保存。 */
(function (ns) {
  'use strict';

  var store = null;
  var media = null;

  function init(deps) {
    store = deps.store;
    try {
      media = window.matchMedia('(prefers-color-scheme: dark)');
    } catch (e) { media = null; }
  }

  function systemPrefersDark() {
    return !!(media && media.matches);
  }

  function resolve(mode) {
    if (mode === 'dark') return 'dark';
    if (mode === 'light') return 'light';
    return systemPrefersDark() ? 'dark' : 'light';
  }

  /** 应用当前设置到 <html> */
  function apply() {
    var st = store.get();
    var s = st.settings || {};
    var root = document.documentElement;
    root.setAttribute('data-theme', resolve(s.theme || 'auto'));
    root.setAttribute('data-motion', s.reduceMotion ? 'off' : 'on');
    var scale = s.fontScale || 1;
    root.style.setProperty('--font-scale', String(scale));
    root.style.fontSize = (16 * scale) + 'px';
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content', resolve(s.theme || 'auto') === 'dark' ? '#14161B' : '#F2F4F7');
    }
  }

  function setTheme(mode) {
    store.set(function (st) { st.settings.theme = mode; });
    apply();
  }

  function cycleTheme() {
    var cur = (store.get().settings || {}).theme || 'auto';
    var next = cur === 'auto' ? 'light' : (cur === 'light' ? 'dark' : 'auto');
    setTheme(next);
    return next;
  }

  function setFontScale(v) {
    store.set(function (st) { st.settings.fontScale = v; });
    apply();
  }

  function setReduceMotion(on) {
    store.set(function (st) { st.settings.reduceMotion = !!on; });
    apply();
  }

  /** 系统主题变化时，若处于 auto 模式则跟随 */
  function bindSystem() {
    if (!media) return;
    var handler = function () {
      var s = store.get().settings || {};
      if ((s.theme || 'auto') === 'auto') apply();
    };
    if (media.addEventListener) media.addEventListener('change', handler);
    else if (media.addListener) media.addListener(handler);
  }

  ns.theme = {
    init: init, apply: apply, setTheme: setTheme, cycleTheme: cycleTheme,
    setFontScale: setFontScale, setReduceMotion: setReduceMotion,
    bindSystem: bindSystem, resolve: resolve, systemPrefersDark: systemPrefersDark
  };
})(window.QX = window.QX || {});
