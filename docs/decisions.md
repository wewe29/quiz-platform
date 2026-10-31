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

## D14 · 主观题满分 = Σ采分点分值（跨学科规则，2026-10-31）

**决策**：平台子站的主观题（term/short/calc）满分 = 该题采分点 `partial` 之和，不再按题型写死 4/6/8。

**理由**：线代采分点数固定（term2/short3/calc4 点 × 2 分 → 4/6/8），但高数 calc 采分点 **1–6 点不等**（160 题仅 1 点）——固定满分会让这些题永远到不了「满分」，错题本被系统性污染。Σpartial 对线代是恒等变换（8/6/4 不变），对高数给出正确满分。

**后果**：采分点「数量口径」由各学科自己的门禁管（线代 2/3/4、高数只要求 ≥1 且 Σpartial>0）；平台端只保证满分可计算。另：高数旧版存储（`hx_quiz_v2`，含 favorites/fontScale 等差异字段，VERSION≠1）**不做自动迁移**——旧 v2 站保留访问，官方跨设备路径是迭代 3 的导出/导入。

## D15 · 学科壳防分叉（模板盖章制，2026-10-31）

**决策**：`tools/platform/template_subject/` 是子站壳的唯一正本（index.html 模板 + app.js + core/store.js + core/bank.js + subject.css + VERSION）。`new_subject.py` 盖章生成/重盖 `subjects/<id>`（index.html 替换 `__SUBJECT_NAME__`/`__SUBJECT_DESC__`），并写 `.stamp.json`（模板版本 + 替换参数）。`validate_platform.py` 逐字节比对：共享文件必须与模板一致、index.html 必须等于模板重放替换的结果。

**理由**：两科共用一套前端是平台的核心承诺；没有字节级门禁，fork 会静默发生（StudyDesk 旧项目 91% 未接线符号的教训）。

**流程**：改共享前端 → 改模板 → `new_subject.py --id <每个学科> --restamp` → 构建校验会拒绝任何未 restamp 的漂移。subject.js（学科配置）与 data/（构建产物）不归模板管。

## D16 · 高数核验执行器的三条铁律（2026-10-31）

**决策**：`sources/calculus/tools/build_subject.py` 的 SymPy 核验器（93 项）：

1. **每项独立命名空间**——核验项里的赋值（`z=…; y=…`）不得泄漏到后续项，否则前一项把 `y` 赋成表达式，后一项 `diff/integrate` 会拿到「变量位置上是表达式」的错参数；
2. **sympy.abc 注入后必须恢复常量**——abc 的希腊字母 `pi/E/I` 是同名**符号**，会覆盖 `sympy.pi` 等常量，导致 `cos(2*pi)` 永不求值；
3. **三级比较**——字符串 → 浮点 → `simplify(val - expected) == 0`（处理 `sin(pi/2)**2/8` 与 `1/8` 这类数学等价但形态不同的结果）。

**理由**：三条都是本轮真实踩到并修掉的缺陷；执行器行为差异会造成「数据其实没错、门禁却拦」或反向漏拦。

## D17 · 进度导出/导入契约与 SW 策略（2026-10-31，迭代 3）

**导出/导入契约**（`quiz-platform-progress` v1）：
- 导出 = `{kind, version:1, subject, bankId, exportedAt, stats, checksum, state}`；
  `state` 只含 `v/sessions/wrongBook`（settings 与 stats 不走文件——stats 由会话重算，settings 属本机偏好）；
- `checksum` = 对 `JSON.stringify({v, sessions, wrongBook})` 的 djb2（32 位 hex）。导入端对解析后的 state
  重新序列化再校验——键序即原文件键序，跨设备成立；
- 合并规则：会话按 id 取 `updatedAt` 较新者；错题本按键合并（错次取大、订正状态取或、时间取新）；
  settings 保留本机。bankId 不同也允许导入（失效题号在渲染层自动跳过）；
- 导入入口为**粘贴文本**（模态框 textarea），不依赖 file input——IAB/部分内嵌浏览器禁文件选择器，
  粘贴路径全环境可用；下载 `.json` 仅是导出侧的便利副本。

**SW 策略**：导航 network-first（更新可达）+ 同域 assets/data 走 stale-while-revalidate（首访后离线可用）；
activate 清旧缓存；`SKIP_WAITING` + 页面「检测到新版本」横幅 + controllerchange 自动刷新。
注册仅在 HTTPS 或 localhost 生效——纯 HTTP 托管自动降级为普通网页（见实施方案迭代 3 约束）。
Lighthouse 打分留给托管方自测；平台门禁只拦结构性缺失（manifest 字段/图标存在/sw 清理逻辑/注册与横幅齐备）。
