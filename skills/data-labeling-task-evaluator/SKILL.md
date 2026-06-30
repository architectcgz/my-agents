---
name: data-labeling-task-evaluator
description: Use when creating or grading data-labeling coding tasks for model evaluation, especially when the user needs repoId, annotator, submission date, Trae sessionId, user prompt, GitHub repo URL, commit id, task type, business domain, modification scope, difficulty, satisfaction, or dissatisfaction reason.
---

# Data Labeling Task Evaluator

## 概览

用这个 skill 完成一条代码生成评测标注的全流程：设计题目，准备或检查 GitHub 仓库，编写给模型的 `user prompt`，等待模型提交结果，再基于证据填写标注字段。

## 工作模式

按两个阶段执行：

1. **出题与建仓**：创建仓库、设计任务、生成 `user prompt`，并返回模型执行前已经确定的字段。
2. **结果评估**：检查模型最终提交的仓库、session、commit 或 diff，填写任务类型、业务领域、修改范围、难度、满意度和不满意原因。

如果用户只要求其中一个阶段，只执行该阶段，并说明哪些字段仍需补充。

## 每日产出规则

规划多条标注任务时遵循这些规则：

- `Bug 修复`、`Feature 迭代`、`0-1 代码生成` 尽量保持 `1:1:1`。
- 代码理解、代码重构、代码测试等辅助任务每日最多 1-2 道，合计占比不超过 40%。
- `Bug 修复` 额度用完后，先新增 `0-1 代码生成` 或 `Feature 迭代` 任务，再继续安排 Bug 修复。
- `Bug 修复` 必须承接前面的 `0-1 代码生成` 或 `Feature 迭代` 上下文，不要独立出无上下文 Bug 修复题。
- 代码理解、代码重构等辅助任务必须新开对话，不要和 `0-1 代码生成` 或 `Feature 迭代` 混在同一轮对话里。
- 正式生产每日目标不少于 20 条有效提交；试做阶段先完成 2-3 道题。

## 必要输入

出题与建仓阶段收集或推断：

- 目标技术栈或种子仓库
- 评测目标，例如 bugfix、feature、refactor、test、UI、backend、docs、security
- 预期难度和允许耗时
- 任务是确定性、开放性还是对抗性
- 是否需要创建 GitHub 远程仓库

结果评估阶段收集：

- repoId
- 做题人
- 提交日期
- Trae sessionId
- GitHub repo URL
- GitHub commit id、branch 或提交 diff
- 实际交给模型的 `user prompt`
- 模型最终回复、日志、测试结果、截图或 reviewer notes

不要编造 ID、日期、sessionId、GitHub URL 或 commit id。缺失字段统一标为 `待补充`。

## 出题与建仓流程

1. 写题前先检查候选仓库，至少阅读 README、构建配置、测试、package manifest 和项目规则。
2. 选择符合仓库实际形态的任务，并确保有可观察的成功条件。优先设计能验证行为的题，不要只做模糊润色。
3. 只做必要的仓库准备：
   - 如果新建仓库，初始化最小可运行项目，补 README 运行说明，并提交 baseline commit。
   - 如果需要 GitHub 远程仓库，优先使用本机 `gh`：先运行 `gh auth status`，确认或推断 repo owner、repo name 和 visibility，再在 baseline commit 存在后执行 `gh repo create ... --source . --remote origin --push`。
   - 如果使用已有仓库，记录 baseline commit，避免无关改动。
4. 编写交给模型的 `user prompt`。Prompt 要包含期望行为、相关文件、约束和验证命令，但不要泄露具体实现方案。
5. 返回出题摘要、`user prompt` 和已知标注字段。

### GitHub 仓库创建

- 当用户要求创建/发布 GitHub 仓库，或标注字段需要 `GitHub repo URL` 时，优先使用 `gh`。
- 本地 baseline commit 完成前，不创建远程仓库。
- repo name 或 visibility 不明确时先确认；如果用户没指定 visibility，评测仓库默认 `private`，除非项目规则要求 public。
- `gh auth status` 失败时停止并说明需要 GitHub 登录；不要索要 token，也不要把 token 写入命令。
- 推送后用 `gh repo view --json url -q .url` 记录 `GitHub repo URL`，用 `git rev-parse HEAD` 记录 baseline `GitHub commit id`。

### GitHub 长链接格式

- 仓库长链接格式：`https://github.com/{owner}/{repo}`，例如 `https://github.com/architectcgz/example-task`。
- commit 长链接格式：`https://github.com/{owner}/{repo}/commit/{40位commitSHA}`，例如 `https://github.com/architectcgz/example-task/commit/76d236d96dc20f0f686d55aba03272fff0672d38`。
- 表格要求 `GitHub repo URL` 时填写仓库长链接；如果平台另有 `commit link` 字段，填写 commit 长链接。
- 表格要求 `GitHub commit id` 时通常填写完整 40 位 SHA；如果审核方要求“GitHub 长链接”，不要填 `git@github.com:owner/repo.git`、短链、短 SHA 或本地路径。

### Prompt 质量规则

- Prompt 必须足够自包含，模型不应依赖隐藏上下文才能做题。
- 仓库支持验证时，Prompt 里写清一个验收标准和一个验证命令。
- 题目难度要和目标一致，不要堆叠互不相关的要求。
- 明确重要约束，例如“不改变 public API”“补充测试”“保持现有布局”。
- 不泄露预期答案、具体文件改法或评分细则，除非任务类型本身需要。
- Prompt 必须由人工编写或深度润色，语言自然，不要直接复制 AI 输出。
- 连续 Prompt 要有实质差异，不要只替换系统名称或关键词；重复文字尽量不超过 50 个中文字符。
- Prompt 中避免大于号、小于号、XML-like tag 等特殊符号，不要粘贴大量代码。
- Prompt 和不满意原因里都不要贴大段代码；用行为、文件名、错误现象或验证结果概括。

## 结果评估流程

1. 确认当前 commit、diff 或 workspace 就是要评估的提交。如果缺少 commit，基于可见 workspace 评估，并把 commit id 标为 `待补充`。
2. 对比 `user prompt`、baseline repo 和提交结果。使用 `git diff`、`git show`、测试命令和必要文件阅读。
3. 能运行验证就运行最小充分验证；不能运行时说明原因。
4. 按下面的分类表填写任务类型、业务领域、修改范围和难度。
5. 满意度根据用户意图和证据判断，不要只因为代码改得多就判满意。
6. `基本满意` 或 `不满意` 时，写清不满意原因，原因必须关联缺失行为、回归、验证失败、范围偏移、质量问题或证据不足。

## 分类表

每个字段选一个主分类；只有在确实能减少歧义时才补充说明。

### 任务类型

- `功能开发`: new user-visible or API behavior
- `Bug 修复`: incorrect behavior corrected
- `重构优化`: internal structure, performance, maintainability, or cleanup without intended behavior change
- `测试补充`: tests, fixtures, CI checks, or verification-only work
- `前端/UI`: visual layout, interaction, component, state, or responsive behavior
- `后端/API`: server routes, services, persistence, auth, jobs, queues, or integrations
- `文档/配置`: README, docs, config, scripts, dependency metadata, or deployment notes
- `安全加固`: vulnerability fix, permission boundary, secret handling, input validation, or supply-chain hardening
- `数据/算法`: data processing, model logic, scoring, search, ranking, analytics, or algorithmic behavior

### 业务领域

选择产品业务领域，不要按技术层分类：

- `通用开发工具`
- `企业管理/SaaS`
- `电商/交易`
- `金融/支付`
- `教育/内容`
- `医疗/健康`
- `社交/社区`
- `游戏/互动娱乐`
- `数据分析/AI`
- `安全/合规`
- `基础设施/DevOps`
- `其他`

### 修改范围

- `单文件`: one source/config/doc file
- `少量文件`: 2-4 related files in one module or layer
- `多文件`: 5+ files or multiple components within one subsystem
- `跨模块`: multiple subsystems, frontend-backend contract, shared library plus callers, or schema plus code
- `项目级`: build system, architecture, CI, dependency strategy, scaffolding, or broad repo organization

### 任务难度

- `简单`: local change, obvious success criteria, low risk, usually <30 minutes
- `中等`: requires repo understanding, tests, several files, or non-trivial state/data flow
- `困难`: cross-module behavior, migration, concurrency, security, complex UI state, integrations, or high regression risk
- `专家`: ambiguous architecture, distributed systems, deep domain constraints, major redesign, or hard-to-verify correctness

## 满意度规则

- `满意`: fulfills the prompt's core behavior, preserves existing behavior, passes relevant verification or has convincing evidence, and keeps scope appropriate.
- `基本满意`: core request is mostly done but has minor omissions, weak tests, small polish gaps, or unverified but plausible behavior.
- `不满意`: misses core behavior, introduces regression, fails relevant tests, ignores key constraints, has unusable quality, or cannot be judged from the submitted artifacts.

`基本满意` 或 `不满意` 必须填写 `不满意原因`。`满意` 时填写 `不满意原因: 无`。

批量任务按培训要求控制比例：不满意率包含产物不满意和过程不满意，应至少 40%；满意率不超过 30%。单条任务仍必须按证据判断，不要编造不满意。如果批次比例偏离，后续通过规划更难或更容易失败的题目来调整。

标记满意前，能本地验证就本地验证，不能验证要说明原因。不要复制 AI 输出作为不满意原因；不满意原因必须经过人工润色，并绑定验证证据。

## 输出模板

每条标注用这个表：

| 字段 | 值 |
|---|---|
| repoId | 待补充 |
| 做题人 | 待补充 |
| 提交日期 | 待补充 |
| Trae sessionId | 待补充 |
| user prompt | 待补充 |
| GitHub repo URL | 待补充 |
| GitHub commit id | 待补充 |
| 任务类型 | 待补充 |
| 业务领域 | 待补充 |
| 修改范围 | 待补充 |
| 任务难度 | 待补充 |
| 任务是否满意 | 待补充 |
| 不满意原因 | 待补充 |

表格后追加简短 `依据`，列出用于分类和满意度判断的文件、diff、测试或日志。

提交到平台或表格时，使用 GitHub 长链接，不要用短链。确保 prompt、session 信息、commit 信息、业务领域和修改范围互相一致。

## 注意事项

- 区分出题阶段事实和评估阶段结论。
- 优先使用具体证据，不用主观印象替代验证。
- 不要因为实现规模大就判满意。
- 不要因为模型没做未要求的工作而扣分，除非该缺失阻塞了题目要求。
- 提交材料不足时，把未知字段标为 `待补充`，并说明证据缺口。
