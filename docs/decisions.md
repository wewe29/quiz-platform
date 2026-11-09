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

**决策**：把高数正本 `5-docs\高等数学复习资料` 的**全部源码**同步进镜像 `sources/calculus/`（此前只有 `qa_bank/` + 6 个构建脚本），与线代镜像的形态一致（线代镜像本来就带 `assets/`、`template.html`、`research/`）。同步的不是整个正本根目录，而是**正本根下的若干块**（`sync_mirror.py` 的 `SUBJECTS.pairs`）：`tools/`（全部源码）、`site_pages/`（已上线的指路页与离线下载页的页面源）、`交付说明.md`；构建产物（`_site_v2/`、单文件成品 HTML、`research/_cache`）不入库。同步由常驻脚本 `tools/platform/sync_mirror.py` 执行（新增 `--subject` 登记与 `--check` 漂移模式），默认排除 `__pycache__`、`*.pyc`、`_cache`（高数 `research/_cache` 实测 156 MB 外部抓取缓存）、`_drops*.jsonl`（2 MB 日志）。

**理由**：高数站的前端源码——`assets/js/**`（21 个文件，含刚修完 BUG-12 的 `ui/render.js`）、`build_static.py`、`build_single.py`、`template_v2.html`、三道 JS 门禁（`check_keyboard_contract.js` 等）、`tests/**`、以及 676 道真题的出题脚本 `research/build_kaoyan_bank.py` 等——**只存在于裸目录，任何版本控制里都没有**；`5-docs` 下只有 `quiz-platform` 是 git 仓，线代与高数正本都是裸目录。磁盘一坏，刚验完的 BUG-12 修复和新门禁就永久丢失。D10 已经把「镜像是正本 tools 的拷贝」写成决策，**高数镜像缺的那部分不是设计选择，是漏同步**——所以另立一个仓会直接违反 D10。

**后果**：
- 高数镜像 88 → **179 文件**，与正本内容一致（`sync_mirror.py --check` 退出 0）；补进前端 201 KB、出题与审计脚本约 1.3 MB、`tests/` 32 KB，以及两个已上线页面的源文件与交付文档。
- **换行符按内容判定，不按字节判定**：仓内由 `.gitattributes` 统一成 LF（D21），而正本是裸目录、换行符不统一（实测 4 个 v1 遗留文件 `assets/app.js`、`build_quiz.py`、`template.html`、`verify_quiz.py` 在正本是 CRLF，仓内 blob 是 LF）。所以 `--check` 把两侧 CRLF 归一后再比，并分三档报告「逐字节相同 / 仅换行符差异 / 真差异」——**只有缺文件与真差异算漂移**。若按字节硬比，重新 checkout 后会误报 4 处假漂移。
- 镜像对 CI **完全惰性**：`build_all.py` 只调用各学科 `build_subject.py`，高数那份只读 `qa_bank/` 与门禁脚本，从不读 `assets/`；`validate_platform.py` 的外链检查显式跳过 `sources/` 与 `tools/`。⇒ 补镜像不改变 `dist/` 与 `subjects/` 的任何字节。
- `sources/*/tools/research/_cache/` 已进 `.gitignore` 兜底。
- **判据与反向测试**：`sync_mirror.py --check` 在镜像漂移时退出 1（本次实测：同步前报「缺 88 个」并退出 1，同步后 0 差异并退出 0）。反向测试**随仓入库**：`tools/platform/test_sync_mirror.py`，16 项断言全绿（改内容 → 退出 1；删文件 → 退出 1；**仅换行符差异 → 退出 0（不误报）**；单文件对与目录对各自的内容差异/缺失都能检出；排除规则确认 `__pycache__`/`_cache` 不进镜像），并已接进 CI 的 self-tests 步骤——**门禁自己也要有门禁**，测试放在仓里而不是本机临时目录（D:\Temp 会被清空）。

## D23 路 mcode 渠道核验改为**节点台账制**（2026-11-03）

**决策**：把 mcode 的线上核验从「按站点类型写死的 if/elif 分支」改成**节点台账制**——
新增 `5-docs\高等数学复习资料\tools\mcode_nodes.json`（node_id / URL / 基准产物的唯一事实源，
5 个节点），判据核心抽到 `tools\online_judge.py`，核验器 `tools\verify_mcode_online.py` 只按台账跑。
判据统一为：**剥掉宿主遥测块后，线上与当前 HEAD 的成品逐字节相同**。

**理由**：2026-11-03 查明此前**核验器漏了线代单文件站**（按类型写分支，漏了这个类型）——
而它恰恰就是落后 HEAD 两天的那个站。**漏核验 = 漂移可以潜伏**：判据再对，没被核验到的节点等于没有门禁。
另外三点：
- **字节级判据覆盖语义级断言**：基准文件就是当前 HEAD 的成品，所以「线上是否含某个修复」不必再单独断言
  （字节相同 ⇒ 修复在位；字节不同 ⇒ 失败），比堆一串零散断言更严，也少一处口径。
- **埋块大小不是常数**（高数站 6,530 B、线代站 1,523 B）⇒ 只能用「差异只有一块连续插入且含 minimax 标记」
  来定位，不能写「线上 = 本地 + N」。
- **CDN 会骗人** ⇒ 核验 URL 一律追加 `?cb=<随机>`。

**后果**：
- 覆盖从「抽查若干文件」升级为**整棵树逐文件比对**：2026-11-03 实测 281 个文件
  （平台 221 + 高数 56 + 指路页 1 + 下载页 2 + 线代 1）全部与当前 HEAD 成品逐字节一致。
- **反向测试随仓入库**：`tools/test_online_judge.py`，48 项断言全绿——正文被改 / 被截断 / 被塞垃圾 /
  多出非遥测内容 / **带遥测标记但正文同时被改** / 两处改动 ⇒ 一律必须判失败；
  台账必须含线代单文件站（漏核验的回归锁）。
  ⚠ 其中「带遥测标记但正文同时被改」是最关键的一项：只看「有没有遥测标记」会**误判通过**，
  所以判据必须是「剥块后再逐字节比」，不是「看标记」。
- 台账的 `roots` 写本机绝对路径；换机器用 `--root NAME=PATH` 覆盖，**不要改这张表**。
  ⇒ 这也是它将来能直接被 CI 复用的原因（CI 只需覆盖 roots，不必改判据）。
- 三个文件同步进平台仓镜像 `sources/calculus/tools/`（`sync_mirror.py --subject calculus`，
  实测镜像 182 个文件零漂移）。**尚未接进 CI**：mcode 渠道是否纳入正式发布流程待定，
  见下。

## D24 路 mcode 渠道纳入正式发布流程 + 行尾污染根因修复（2026-11-07）

**决策一：mcode 渠道纳入正式发布流程。**
两个仓各加一个 CI job「**线上核验：mcode 渠道是否已跟上 HEAD**」：
push 后自动跑「剥掉宿主埋块后，线上 == 当前 HEAD 成品」的逐字节比对。
- 台账给每个核验项标 `ci`：**CI 上拿得到基准的才标 true**，拿不到的标 false 并写明原因
  （高数 v2 静态站与它的单文件包，构建链依赖项目外的 KaTeX 资源，CI 重建不出来）——
  **不假装覆盖**，那两项仍由本地核验覆盖。
- 基准用 CI 自己构建的产物；平台仓额外断言「CI 重建的 `subjects/` == 仓内 HEAD 成品」，
  这样「CI 构建 == HEAD」本身也是机器验过的。
- **job 红 = mcode 渠道待补发**（mcode 是手动补发渠道，`website_deploy` 要在本机跑，
  无法自动发布），所以只报警、**不阻塞** Pages 发布；代码健康看 `build-and-deploy` / `content-gates`。
- 每个 job 都带「**自证有牙齿**」步骤：对故意注入漂移的副本跑一次核验器，**必须报红**，
  否则 job 失败 —— 门禁自己也要有门禁。

**决策二：修掉工作区的 CRLF 污染（这是决策一的必要前置）。**
实测：本地构建与 CI 构建的产物差 1,716 字节（`app.js`）。根因链：
1. 高数正本是裸目录，13 个文件是 CRLF；
2. `sync_mirror.py` 用 `copyfile` 原样复制 → 镜像工作区也带 CRLF；
3. git 提交时按 `text=auto` 把 blob 归一成 LF ⇒ **工作区与 blob 不同字节**；
4. 而 index 的 **stat cache 记的就是 CRLF 尺寸** ⇒ git 连内容都不读就判「未变」
   ⇒ `git diff` 报「无差异」、`git status` 报「干净」，**污染对 git 完全隐形**；
5. 构建读的是工作区 ⇒ 本地产物是 CRLF 字节，CI 产物（从 blob）是 LF 字节
   ⇒ 本地 dist 与线上 GitHub Pages 差 1,716 字节。页面照跑、渲染一模一样，肉眼与普通 diff 全都看不出来。

**修法**：
- 同步器在**边界上**把文本文件归一成 LF；不变式改成「**镜像 == 归一后的正本**」
  （只写「镜像 == 正本的原始字节」会被「正本 CRLF + 镜像 CRLF」骗过去，那正是污染形态）。
- 新增 `tools/platform/check_worktree_eol.py`：逐字节比工作区与 blob。
  **这是 git 给不了的检查**——git 的语义是「内容相同就算干净」，
  本门禁的语义是「字节相同才算干净」，正是被 git 归一掉的那一类差异。
  它自带 `--fix`（从 blob 重写），且 `--fix` **只修行尾污染、不碰真差异**
  （那可能是未提交的工作；实测踩到过：门禁把自己尚未提交的新版本覆盖成了旧版）。
- 修复**不能**靠 `git checkout -- .`（stat cache 会短路，实测跑完污染依旧）。

**后果**：
- 修完后实测：**本地 dist（Windows 构建）== CI 构建（Ubuntu）== 线上 GitHub Pages，
  221 个文件逐字节一致** ⇒ 三条渠道终于同源，CI 核验 job 的基准才可信。
- 平台主站因此**原地重发一次**（node `458302907191686`，URL 不变）：5 个 `app.js` 的
  CRLF → LF（8,580 字节）。**纯行尾归一，内容语义与页面行为零变化**。
- `sync_mirror.py --check` 仍不把「仅行尾形态不同」当内容漂移（退出 0），但会点名报 `EOLF` 并给修法。
- 核验器 `fetch` 加**重试**（3 次 + 退避）：实测本机到 github.io 的 DNS 会间歇性抽风，
  没有重试的核验器 = 不稳定的门禁（CI runner 上同样会抖）。

## D25 路 消除高数 v2 构建链的项目外依赖 ⇒ CI 核验覆盖补完（2026-11-08）

**决策**：把高数正本 `katex_assets.py` 里**硬编码的 KaTeX 绝对路径**改成按优先级查找：
`KATEX_DIR` 环境变量 → **平台仓共享 vendor `tools/vendor/katex/dist`（已入库）** →
学科自带 `tools/vendor/katex/dist` → 本机 node_modules（兜底）。

**理由**：D24 给 mcode 渠道加了 CI 核验 job，但台账里有两个核验项标着 `ci:false` ——
高数 v2 静态站（56 文件）与它的单文件包。原因是**高数正本的 KaTeX 路径写死在
`D:\workspace\5-docs\exam\数据库\node_modules\katex\dist`**，那是 5-docs 下唯一的
git 仓之外的外部依赖 ⇒ **CI 上根本重建不出基准**，这两个节点只能靠本地每日核验覆盖。
⇒ 这不是「不假装覆盖」能接受的长期状态：覆盖不全 = 漂移仍有盲区。

**关键前提（先验证再动手）**：**仓内那份 KaTeX 与本机 node_modules 那份逐字节相同**
（83 个文件 / 2,966,601 B，每个文件 sha256 都一样）⇒ **换源不改变任何产物字节**。
实测：重建的 `_site_v2`（56 文件）与单文件包（3,430,226 B）都与正本**逐字节相同**，
平台 `dist/`（221 文件）也**字节未变** ⇒ **高数专站与离线下载页不需要重发**，零公开改动。

**后果**：
- 台账两个遗留项升级为 `ci:true`（`ci_local` 指向 `calculus:ci-build/...`，
  CI 里把两件产物构建到 `sources/calculus/ci-build/` 下；**用 ASCII 路径**，
  避免 YAML 与 shell 里的中文文件名风险）⇒ **6 个核验项全部有 CI 覆盖**（此前 4/6）。
- 平台仓 CI 的核验 job 新增 `setup-node`（v2 构建要用真实 `render.js` 跑渲染层门禁）
  与「构建高数 v2 两件产物」一步。
- 「不假装覆盖」的纪律依然成立：拿不到基准就标 `ci:false` 并写明原因；
  但**能拿到的就必须去拿到**，而不是停在「做不到」上。

## D26 把「壳」变成构建产物 + 给壳名加有牙齿的身份门禁（2026-11-08）

**触发事件**：本轮按 D23/D24 的规矩做「字节一致之外的验收」（浏览器实答），
在平台主站 `subjects/probstat/` 点进去就发现：浏览器标签标题是
「大学《概率论与数理统计》题库刷题」，**但页面上那颗大标题是「大学《》题库刷题」**——
括号里是空的。五个学科子站全中（高数/数可视化/线代/机器学习/概率论）。

**根因（查到 2026-11-01 的提交为止）**：`e5dddc9`「restamp 五学科壳」执行了
`new_subject.py --restamp` 却**漏传 `--name`**；而当时的 `--restamp` 写的是
`stamp(args.id, args.name or "", args.desc or "")` ⇒ 五个学科的壳名被写成空字符串，
并同步写进了 `subjects/<id>/index.html` 的 `<title>` 与 `<h1>`。
**这个缺陷在线上存活了五天，期间所有门禁全绿。**

**为什么门禁没抓到**：当时的 `check_subject_shell` 只做「拿盖戳清单里的参数去重放模板，
比对 index.html 是否等于重放结果」——这是**自洽式校验**：盖戳参数本身错了，
重放当然也错得一模一样，于是判定通过。
**自洽式校验没有牙齿**：它只能发现「壳与盖戳不一致」，发现不了「盖戳本身是错的」。

**决策**：
1. **壳是构建产物，不是手工维护的文件**。`build_all.py` 在构建完题库后自动重盖五学科的壳；
   壳名与描述的唯一来源 = 该学科 `manifest`（`subject.name` / `summary.desc`），
   manifest 是构建产物 ⇒ 题量变了、描述变了，壳自动跟着变，不会停在旧题量上。
2. `new_subject.py` 解析不出名字就**报错退出**，绝不写空壳；命令行参数只作兜底。
3. 离线链接从模板里**移出来**，改由平台级 `tools/platform/offline_links.json` 给
   （原来写死 `linear-algebra-quiz`，导致四个学科的页脚都指向线代的离线版；
   现在高数指向自己的离线单文件页，无离线版的学科页脚不出现该从句）。
4. 子站 `meta description` 整体取自 `manifest.summary.desc`，
   不再套「六题型、三难度……」的固定样板句——数据可视化与机器学习只有三型，
   样板句把它们写成了六型（与 2026-10-31 门户 meta 过期同一病根：文案不跟数据走）。
5. `app.js` 运行时也用 manifest 赋值 `<h1>`（静态壳 + 运行时双保险）。
6. **新门禁 `check_subject_identity`**：壳名非空且等于 manifest、
   `index.html` 的 `<title>`/`<h1>` 真的带着它、不含「大学《》」、
   描述不陈旧、页脚离线链接与台账一致——**全部与独立事实源对账**，不再自洽式重放。

**配套**：反向测试新增 T5–T12（空名/错名/空壳/陈旧描述/错离线链接/解析优先级/拒绝写空壳），
平台自检 27 项全绿；模板 `VERSION` 2 → 3，模板一改即强制全部重盖。

**顺带确立的一条纪律**：**凡是「拿参数重放自己」的门禁，都要再加一道「与独立事实源对账」**——
前者只能防漂移，后者才能防错值。字节级门禁（线上 == HEAD）同样如此：
它保证「线上没落后」，但不保证「HEAD 里的东西是对的」。这两件事要分开验。


