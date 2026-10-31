/* core/bus.js — 极简事件总线（无 DOM 依赖）
   UI 层只发事件、只读状态；业务层不直接调 UI。 */
(function (ns) {
  'use strict';

  var handlers = {};

  function on(event, fn) {
    if (!handlers[event]) handlers[event] = [];
    handlers[event].push(fn);
    return function off() {
      var arr = handlers[event] || [];
      var i = arr.indexOf(fn);
      if (i >= 0) arr.splice(i, 1);
    };
  }

  function emit(event, payload) {
    var arr = handlers[event] || [];
    for (var i = 0; i < arr.length; i++) {
      try {
        arr[i](payload);
      } catch (e) {
        // 一个监听器抛错不能打断其它监听器
        if (ns.console && ns.console.error) {
          ns.console.error('[bus] handler error on "' + event + '":', e);
        }
      }
    }
  }

  ns.bus = { on: on, emit: emit };
})(window.QX = window.QX || {});
