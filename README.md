# 复习刷题平台（quiz-platform）

多学科大学课程刷题小应用：**门户 + 学科子站 + 统一数据契约 + 门禁流水线自动部署**。
实施方案与迭代计划见《线性代数复习资料/应用化实施方案与迭代计划.md》，决策记录见 [docs/decisions.md](docs/decisions.md)。

## 在线

- 平台门户：https://wewe29.github.io/quiz-platform/
- 线性代数单文件离线版（保留渠道）：https://wewe29.github.io/linear-algebra-quiz/

## 目录

```
index.html                 门户（学科卡片 + 跨学科进度汇总，读 registry.json）
assets/                    门户样式与脚本 + 全局设计令牌 tokens.css
subjects/<id>/             学科子站（构建产物，CI 会重建）
  index.html               子站壳
  data/manifest.json       数据契约 quiz-platform-subject-v1（口径/文案/分片清单/SHA256）
  data/chNN[a-c].json      按章分片题库（单分片 ≤200KB）
  assets/js/               subject.js（配置）+ core/{store,bank}.js + app.js
  assets/vendor/katex/     自托管 KaTeX（woff2 裁剪版）
subjects/registry.json     门户注册表（build_all 生成）
sources/<id>/tools/        各学科工具链镜像（内容生产正本在各学科工作区，见 D10）
tools/platform/            build_all.py（总构建）/ validate_platform.py（平台门禁）/ katex_assets.py
docs/decisions.md          架构决策记录
```

## 发布流程（以线性代数为例）

```powershell
# 1. 在学科工作区改题库/界面后，跑门禁并导出平台产物：
cd D:\workspace\5-docs\线性代数复习资料
python tools\build_subject.py                # 完整门禁 → subjects/linalg/data

# 2. 同步工具链镜像到平台仓（正本→镜像，禁止反向）：
robocopy tools D:\workspace\5-docs\quiz-platform\sources\linalg\tools /MIR /XD __pycache__

# 3. 推送平台仓 → CI 重新构建全部门禁并部署：
cd D:\workspace\5-docs\quiz-platform
git add -A && git commit -m "..." && git push
```

本机快速验证：`python tools/platform/build_all.py --dist` 后 `python -m http.server -d dist`。

## 门禁

- **内容门禁**（build_subject.py 内，与单文件版同一套）：构建三道内建门禁 + verify_quiz（SymPy 542 条）+ audit_choice + audit_open + scan_escapes + diff_bank + check_html。
- **平台门禁**（validate_platform.py）：manifest schema 与 SHA256、分片结构与题数、逐题字段完整性、壳/门户/分片体积预算、外部自动加载资源扫描。
- CI 里任何一步失败都不会部署（D9）。

## 新增学科的步骤

1. 学科工作区建 `tools/`（题库源 + build_subject.py，参照线性代数）；
2. `robocopy` 镜像到 `sources/<id>/tools`；
3. `build_all.py` 自动发现并构建，门户自动出现新卡片。
