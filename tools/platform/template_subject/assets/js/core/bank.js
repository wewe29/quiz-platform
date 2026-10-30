/* core/bank.js — 题库装载：manifest + 按章分片（契约 quiz-platform-subject-v1）。
   装载策略：linalg 全库 500 题，筛选/统计/答案位置面板都需要全量数据，
   故 meta + 全部分片并行拉取后合并（传输体积 = 单文件版去掉 KaTeX 内联）。
   分片的意义在于 SW 缓存粒度与后续大体量学科按需加载（接口不变，loadStrategy 预留）。 */
(function (ns) {
  'use strict';

  var TYPE_RANK = { single: 0, multi: 1, judge: 2, blank: 3, term: 4, short: 5, calc: 6 };
  var DIFF_RANK = { basic: 0, medium: 1, hard: 2 };

  function getJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + ' HTTP ' + r.status);
      return r.json();
    });
  }

  ns.load = function (cfg) {
    var base = cfg.dataDir;
    return getJSON(base + 'manifest.json').then(function (manifest) {
      if (manifest.schema !== 'quiz-platform-subject-v1') {
        throw new Error('manifest schema 不兼容：' + manifest.schema);
      }
      var shards = manifest.shards || [];
      if (!shards.length) throw new Error('manifest 没有任何分片');
      return Promise.all(shards.map(function (s) {
        return getJSON(base + s.file).then(function (data) {
          var qs = (data && data.questions) || [];
          if (qs.length !== s.count) {
            throw new Error('分片 ' + s.file + ' 题数 ' + qs.length + ' != manifest 声明 ' + s.count);
          }
          return qs;
        });
      })).then(function (groups) {
        var questions = [];
        groups.forEach(function (g) { questions = questions.concat(g); });
        // 防御性排序：与构建侧 load_bank 同一语义（章 → 题型 → 难度），保证 idx 稳定
        questions.sort(function (a, b) {
          if (a.chapter !== b.chapter) return a.chapter - b.chapter;
          var ta = TYPE_RANK[a.type], tb = TYPE_RANK[b.type];
          if (ta !== tb) return ta - tb;
          var da = DIFF_RANK[a.difficulty], db = DIFF_RANK[b.difficulty];
          if (da !== db) return da - db;
        });
        for (var i = 0; i < questions.length; i++) questions[i].idx = i;
        if (questions.length !== manifest.caliber.total) {
          throw new Error('题库题数 ' + questions.length + ' != 口径 ' + manifest.caliber.total);
        }
        return { meta: manifest, questions: questions };
      });
    });
  };
})(window.LABank = window.LABank || {});
