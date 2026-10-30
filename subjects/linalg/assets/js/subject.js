/* 线性代数子站配置 —— 数据契约由 data/manifest.json 提供，这里只放「位置」信息。
   改题量/章节/文案去改题库源（平台仓 sources/linalg/tools），构建流水线会重新生成 manifest。 */
window.SUBJECT = {
  id: 'linalg',
  name: '线性代数',
  dataDir: 'data/',
  storageKey: 'quiz-linalg-v2',
  /* 单文件离线版（linear-algebra-quiz 站）的进度迁移来源：同名题库（bankId 一致），整体搬迁 */
  legacyKeys: ['la_quiz_v1'],
  portalUrl: '../../',
  katex: 'assets/vendor/katex/'
};
