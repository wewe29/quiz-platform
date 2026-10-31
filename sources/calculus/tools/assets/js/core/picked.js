/* core/picked.js — 选择缓冲状态机（未提交的选项 / 填空值）
   规则：**只有切题才重置**。

   真实踩过的坑：选完选项后 UI 会立刻重渲染，若每次渲染都清空缓冲，
   用户刚点中的字母会被自己抹掉 —— 表现为「点 A 没反应、提交时提示
   还没作答」。所以这里用 qid 记住缓冲属于哪道题：
     · qid 变了（切题）→ 重置，并从已有作答记录回填已选项；
     · qid 没变（同题重渲染）→ 原样保留。
   抽成独立模块是为了能单测这条规则。 */
(function (ns) {
  'use strict';

  /**
   * 把缓冲对齐到题目 q。
   * @param {object} st      缓冲状态（{qid, picked}）
   * @param {object|null} q  当前题
   * @param {object} answers {qid: record} 作答记录表
   * @returns {Array} 当前已选项
   */
  function sync(st, q, answers) {
    var qid = q ? q.id : null;
    if (qid === st.qid) return st.picked;
    st.qid = qid;
    st.picked = [];
    var rec = (q && answers) ? answers[q.id] : null;
    if (rec) {
      if (q.type === 'blank') {
        st.picked = [(rec.value || [])[0] || ''];
      } else if (q.type !== 'term' && q.type !== 'short' && q.type !== 'calc') {
        st.picked = (rec.value || []).slice();
      }
    }
    return st.picked;
  }

  /** 手动清空已选项（重做本题用） */
  function clear(st) {
    st.picked = [];
    return st.picked;
  }

  ns.picked = { sync: sync, clear: clear };
})(window.QX = window.QX || {});
