# 决策记录（ADR）

> 本文件记录平台建设中的关键决策。格式：决策 / 理由 / 后果。改动架构前先来这里查有没有撞车。

## D8 · 数据契约 quiz-platform-subject-v1

**决策**：学科产物 = `data/manifest.json` + `data/chNN[a-c].json` 分片。

- `manifest.json`：`schema`（固定 `quiz-platform-subject-v1`）、`subject{id,name,textbook,bankId,chapters,chapterLabels}`、`sections`（知识点出处表）、`caliber{total,byType,byDifficulty,byChapter,limits}`、`summary{sub,desc,aboutHtml,footerHtml,realExamTagged}`、`shards[{file,chapter,count,sha256}]`。
- 分片：按章导出；**落盘口径**（`json.dumps(indent=1)`）超过 200KB 的章自动对半拆分（曾因紧凑序列化测量与落盘口径不一致导致预算失真，已修）。
- `bank.js` 装载后按（章 → 题型 → 难度）防御性排序并赋 `idx`，与构建侧 `load_bank()` 语义一致。

**理由**：题库单一事实源仍是各学科 qa_bank（D5），manifest 把页面需要的口径/文案/章节名全部随数据下发，子站前端不写死任何题量数字。

## D9 · 门禁自动化与部署解耦（2026-10-31 修订）

**决策**：交付链的终点是**校验全绿的 `dist/` 静态产物**；托管与部署由使用者自行进行，不在本项目范围内。平台仓的 `deploy.yml`（push → 重建 → GitHub Pages）降级为**可选自动化**——它证明了门禁能在 CI 上跑通，但不是交付链的必要环节，可整体删除而不影响任何功能。

**理由**：托管方式属于使用者的基础设施决策（Pages/OSS/Vercel/内网均可，产物是相对路径纯静态）；把部署写进验收标准会让方案绑定特定平台。

**后果**：各轮验收一律以「本地/任意静态服务器上走通演示脚本」为准；`validate_platform.py` 是发布前的最后一道人工可调用门禁。

## D10 · 镜像同步规则（正本 → 镜像，禁止反向）

**决策**：各学科工作区（如 `5-docs\线性代数复习资料\tools`）仍是内容生产**正本**；`sources/<id>/tools` 只是镜像，喂给可选的 CI 门禁（D9）。交付产物的常规路径是本机 `build_all.py --dist`，不依赖镜像推送。同步用文件拷贝（`build_subject.py` 写产物到平台仓后，robocopy/脚本拷贝 tools）。

**后果**：直接改平台仓里的 `sources/` 而不同步回工作区，下次同步会被覆盖——**禁止**在平台仓里直接改源码。

## D11 · 存储命名空间与迁移

**决策**：子站存储键 `quiz-<subjectId>-v2`；从单文件版 `la_quiz_v1` 自动整体迁移（legacy 键保留不动，回退不丢进度）。bankId 不同也照迁——失效会话顺序由 `orderIsStale()` 重建，失效错题渲染时跳过。

## D12 · 主题双源

**决策**：门户与子站各自管理主题偏好（门户存 `quiz-platform-theme`，子站存自身 state.settings.theme），两处只在「跟随系统」初始值上共享同一个系统偏好；不做跨页强制同步。

**理由**：子站主题是既有功能且与作答状态同存；门户独立使用场景多。代价：两页主题可能不一致，接受。

## D13 · 平台版「零外部依赖」条款改写

**决策**：单文件版保留「运行时不发任何网络请求」表述；平台版改为「全站资源自托管，无任何第三方依赖」——fetch 同源数据不算第三方依赖。校验器只拦截外部自动加载资源（script/img/link 等），正文说明性 `<a>` 链接不拦。
