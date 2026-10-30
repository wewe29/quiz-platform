# 决策记录（ADR）

> 本文件记录平台建设中的关键决策。格式：决策 / 理由 / 后果。改动架构前先来这里查有没有撞车。

## D8 · 数据契约 quiz-platform-subject-v1

**决策**：学科产物 = `data/manifest.json` + `data/chNN[a-c].json` 分片。

- `manifest.json`：`schema`（固定 `quiz-platform-subject-v1`）、`subject{id,name,textbook,bankId,chapters,chapterLabels}`、`sections`（知识点出处表）、`caliber{total,byType,byDifficulty,byChapter,limits}`、`summary{sub,desc,aboutHtml,footerHtml,realExamTagged}`、`shards[{file,chapter,count,sha256}]`。
- 分片：按章导出；**落盘口径**（`json.dumps(indent=1)`）超过 200KB 的章自动对半拆分（曾因紧凑序列化测量与落盘口径不一致导致预算失真，已修）。
- `bank.js` 装载后按（章 → 题型 → 难度）防御性排序并赋 `idx`，与构建侧 `load_bank()` 语义一致。

**理由**：题库单一事实源仍是各学科 qa_bank（D5），manifest 把页面需要的口径/文案/章节名全部随数据下发，子站前端不写死任何题量数字。

## D9 · CI 就是部署者

**决策**：平台仓的 `deploy.yml` 每次 push 从 `sources/<id>/tools` 镜像重新构建全部学科（含完整内容门禁），产物写入 `subjects/<id>/`，校验通过后组装 `dist/` 部署 Pages。仓库里已提交的产物只是最近一次构建的快照。

**理由**：不存在「本地改了源码忘同步」造成的漂移——CI 构建失败就不会部署。代价：`sources/` 镜像必须由同步脚本维护（见 D10）。

## D10 · 镜像同步是唯一发布通道

**决策**：各学科工作区（如 `5-docs\线性代数复习资料\tools`）仍是内容生产正本；发布 = 同步镜像到 `sources/<id>/tools` + 推送平台仓。当前同步用文件拷贝（`build_subject.py` 写产物到平台仓后，手动/脚本拷贝 tools）。

**后果**：直接改平台仓里的 `sources/` 而不同步回工作区，下次同步会被覆盖——**禁止**在平台仓里直接改源码。

## D11 · 存储命名空间与迁移

**决策**：子站存储键 `quiz-<subjectId>-v2`；从单文件版 `la_quiz_v1` 自动整体迁移（legacy 键保留不动，回退不丢进度）。bankId 不同也照迁——失效会话顺序由 `orderIsStale()` 重建，失效错题渲染时跳过。

## D12 · 主题双源

**决策**：门户与子站各自管理主题偏好（门户存 `quiz-platform-theme`，子站存自身 state.settings.theme），两处只在「跟随系统」初始值上共享同一个系统偏好；不做跨页强制同步。

**理由**：子站主题是既有功能且与作答状态同存；门户独立使用场景多。代价：两页主题可能不一致，接受。

## D13 · 平台版「零外部依赖」条款改写

**决策**：单文件版保留「运行时不发任何网络请求」表述；平台版改为「全站资源自托管，无任何第三方依赖」——fetch 同源数据不算第三方依赖。校验器只拦截外部自动加载资源（script/img/link 等），正文说明性 `<a>` 链接不拦。
