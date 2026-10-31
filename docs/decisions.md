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

## D18 · 门户文案也走「口径单一事实源」（2026-10-31）

**决策**：门户 `index.html` 的 `<meta name="description">` **不再手写**，由 `tools/platform/portal_meta.py` 从 `subjects/registry.json` 生成；`build_all.py` 每次构建自动重写它，`validate_platform.py` 逐字比对、不一致即 FAIL。

**理由**：本轮实测的过时文案——「机器学习、数据可视化接计划接入」，而这两科早已上线，线上对外文案是错的，而**全部门禁全绿**：没有任何一道门禁看这句文案。`portal.js` 早已数据驱动（读 registry.json），只有 `index.html` 是手写 HTML，于是它成了唯一的漂移点。

**后果**：加学科/改题量后文案自动跟随；手改 meta 会被门禁拦下（实测：反向测试把 registry 换掉，门禁立刻报「期望 vs 实际」两行）。

## D19 · 答案键 ↔ 解析**数值**一致性门禁（2026-10-31）

**决策**：新增 `audit_value.py` 作为第七道门禁（同时挂进 `update_site.py` 的 GATES 与 `check_new.py` 的 S9）。规则只管高置信的一小块：**单选题**且**答案选项是纯数值**时，答案选项的数值必须能在解析里读到。

**理由**：`audit_choice.py` 只认「解析里点名字母」（"A 正确"/"B 错"），实测 250 道客观题里**只有 44 道（17.6%）**的解析点了名，其余 206 道在字母规则下**无保护**。本轮实测的真实缺陷 q-039（答案键 B，解析自己算出 A）正落在这 206 道里——而且它的 `verify` 写的是与本题无关的占位算式 `M([[1,2],[3,4]]).det()`，SymPy 复核一路绿灯。

**精度证据**：500 题里命中该规则的有 30 道，**真实误报 0**（另 1 条是 `re.ASCII` 之前的假阳性，已修）；改回错值 B 立刻报错（反向测试）。长陈述型选项（多选为主）解析换个说法就匹配不上，**一律不管**——宁可漏报不可误报。

**配套纪律**：`verify` 项必须是**本题实际计算**。占位式 verify（换个无关算式凑数）让 SymPy 门禁变成摆设，q-039 就是这么混过去的。

## D20 · 构建门禁必须比对「本次刚构建的产物」（2026-10-31）

**决策**：`diff_bank.py` 用 `QUIZ_HTML` 环境变量定位成品；`update_site.py` 的门禁链**显式传 `QUIZ_HTML=本次的 PRODUCT`**，不再依赖「tools 的上一级」这个兜底路径。

**理由**：平台构建把成品写到 `QUIZ_PROJECT_DIR`，而 `diff_bank` 兜底找的是 `sources/linalg/`——平台构建**从不设** `QUIZ_HTML`，于是「源码 ↔ 成品逐字段一致」这道门禁长期拿一份**旧成品**做比对（那份旧成品还恰好被提交进了仓库），**形同虚设**。它之所以一直「通过」，只是因为源码也一直没变。

**后果**：仓库里冻结的旧成品已取消跟踪并加入 `.gitignore`（`sources/*/01《线性代数》题库刷题网页.html`）；反向测试确认：指向旧成品 → 报 2 处差异并退出 1；指向新成品 → 0 差异。**教训**：一道门禁「一直绿」本身就要怀疑——它可能在比一个不会变的东西。

## D21 · 换行符钉死 LF（2026-10-31）

**决策**：平台仓加 `.gitattributes`（`* text=auto eol=lf` + 二进制资源豁免），并把本机 `core.autocrlf=false` / `core.eol=lf` 写进仓库配置。

**理由**：本机 Git 默认 `core.autocrlf=true`，工作区文件会在下次 checkout 被改成 CRLF；而 GitHub Pages 直接服务仓库 blob（LF）。一旦工作区被转成 CRLF，**本机构建的 dist 字节就与线上不一致——而页面照跑，肉眼完全看不出来**。单文件版仓已经为同一件事付过一次代价（线上多出 1706 字节）。

**后果**：本地构建产物与线上 blob 逐字节一致，可用 SHA 直接比对，不用再靠「目测没差别」。

## D22 · 镜像补全为「正本 tools 全量」（2026-10-31）

**决策**：把高数正本 `5-docs\高等数学复习资料\tools` 的**全部源码**同步进镜像 `sources/calculus/tools/`（此前只有 `qa_bank/` + 6 个构建脚本），与线代镜像的形态一致（线代镜像本来就带 `assets/`、`template.html`、`research/`）。同步由常驻脚本 `tools/platform/sync_mirror.py` 执行（新增 `--subject` 登记与 `--check` 漂移模式），默认排除 `__pycache__`、`*.pyc`、`_cache`（高数 `research/_cache` 实测 156 MB 外部抓取缓存）、`_drops*.jsonl`（2 MB 日志）。

**理由**：高数站的前端源码——`assets/js/**`（21 个文件，含刚修完 BUG-12 的 `ui/render.js`）、`build_static.py`、`build_single.py`、`template_v2.html`、三道 JS 门禁（`check_keyboard_contract.js` 等）、`tests/**`、以及 676 道真题的出题脚本 `research/build_kaoyan_bank.py` 等——**只存在于裸目录，任何版本控制里都没有**；`5-docs` 下只有 `quiz-platform` 是 git 仓，线代与高数正本都是裸目录。磁盘一坏，刚验完的 BUG-12 修复和新门禁就永久丢失。D10 已经把「镜像是正本 tools 的拷贝」写成决策，**高数镜像缺的那部分不是设计选择，是漏同步**——所以另立一个仓会直接违反 D10。

**后果**：
- 高数镜像 88 → **176 文件**，与正本内容一致（`sync_mirror.py --check` 退出 0）；补进前端 201 KB、出题与审计脚本约 1.3 MB、`tests/` 32 KB。
- **换行符按内容判定，不按字节判定**：仓内由 `.gitattributes` 统一成 LF（D21），而正本是裸目录、换行符不统一（实测 4 个 v1 遗留文件 `assets/app.js`、`build_quiz.py`、`template.html`、`verify_quiz.py` 在正本是 CRLF，仓内 blob 是 LF）。所以 `--check` 把两侧 CRLF 归一后再比，并分三档报告「逐字节相同 / 仅换行符差异 / 真差异」——**只有缺文件与真差异算漂移**。若按字节硬比，重新 checkout 后会误报 4 处假漂移。
- 镜像对 CI **完全惰性**：`build_all.py` 只调用各学科 `build_subject.py`，高数那份只读 `qa_bank/` 与门禁脚本，从不读 `assets/`；`validate_platform.py` 的外链检查显式跳过 `sources/` 与 `tools/`。⇒ 补镜像不改变 `dist/` 与 `subjects/` 的任何字节。
- `sources/*/tools/research/_cache/` 已进 `.gitignore` 兜底。
- **判据与反向测试**：`sync_mirror.py --check` 在镜像漂移时退出 1（本次实测：同步前报「缺 88 个」并退出 1，同步后 0 差异并退出 0）。沙盒反向测试 12 项全绿：改内容 → 退出 1；删文件 → 退出 1；**仅换行符差异 → 退出 0（不误报）**；排除规则确认 `__pycache__`/`_cache` 不进镜像。

