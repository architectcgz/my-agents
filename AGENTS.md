# 全局协作规范

## 0. AGENTS 层级归属
- `~/.agents/AGENTS.md` 是共享全局入口，只放跨项目、跨工作区、跨 agent 都必须生效的总则和路由。
- `~/.codex/AGENTS.md`、`~/.claude/AGENTS.md` 默认只作为 agent 入口层，应回链到 `~/.agents/AGENTS.md`，不要各自维护一份正文。
- `~/.codex/CLAUDE.md`、`~/.claude/CLAUDE.md` 默认保持 `CLAUDE.md -> AGENTS.md` 软链接，作为各入口目录内的发现别名。
- `~/.gemini/AGENTS.md` 是 Antigravity / Gemini 入口层，应回链到 `~/.agents/AGENTS.md`；`~/.gemini/GEMINI.md` 如存在，只作为 `AGENTS.md` 的兼容发现别名，不承载独立正文。
- `~/AGENTS.md` 只用于在 home 目录本身工作时的轻量说明，不承载全局规则，也不复制本文件内容。
- `~/workspace/projects/AGENTS.md` 只约束 workspace 根目录和非 Git 子目录；进入具体 Git 项目后，项目根 `AGENTS.md` 才是项目规则入口。
- 项目内 `AGENTS.md` 只写该项目的事实、命令、架构边界、文档归属和覆盖规则；不要重复全局沟通、Git、安全和输出风格规则。
- 更深层目录的 `AGENTS.md` 只补充目录局部规则；不要回写与上层相同的通用约束。
- 共享 skill、共享 harness、共享 agents 的主体默认放在 `~/.agents/` 下维护，例如 `~/.agents/skills/`、`~/.agents/harness/`、`~/.agents/codex-agents/`、`~/.agents/claude-agents/`。
- `~/.codex/skills/`、`~/.codex/agents/`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.gemini/skills/` 默认只作为入口或软链接层；除非某项内容明确只属于单一 agent，否则不要在这些入口层分别维护一份正文。
- 当共享 skill / harness / agent 需要修改时，默认直接修改 `~/.agents/` 下的主体，再检查各入口软链接是否仍然正确；不要先改 `.codex` 再回填。

## 1. 全局总则
- 新项目初始化、README、AGENTS.md、docs、部署说明和长期 Markdown 正文默认使用中文；代码标识、命令、路径、包名、API / 协议字段和外部专有名词保持原文。
- 新增或修改代码时必须为关键业务逻辑补充注释，方便人类维护者理解意图；注释应解释业务规则、领域不变量、状态转换、权限判断、幂等/补偿、跨服务副作用或非显然取舍，避免只复述语法或实现步骤。
- TDD 只对行为、状态、数据流、权限、校验、异步流程、算法、接口契约或可复现 bug 等逻辑承载改动默认适用；简单 UI / 展示层改动（布局、间距、颜色、排版、静态文案、控件位置迁移且不改变状态语义）不默认使用 TDD，改用最小充分的类型、构建、组件渲染、截图或人工验证。
- subagent 默认不绑定具体模型，继承父会话中已验证可用的 provider 和模型；角色能力由 agent instructions 与 skills 保证。任务对模型只有偏好时，可以优先选择目标模型，但不可用时应回退到父会话模型并明确说明；只有任务确实依赖特定模型能力时才允许硬绑定，调用前必须确认 provider 支持，失败时不得静默换模，应改由主 agent 完成或向用户说明限制。
- 通过 shell、评测 runner 或其他自动化调用外部 agent CLI 时，模型和模型别名由当前 provider 配置决定，不在全局规则中覆盖；除非用户明确指定费用上限，否则不要擅自添加 `--max-budget-usd` 或同类预算参数，尤其不要用未经验证足够的低预算中断独立 review、评测或其他长任务。
- skill 和专门 agent 按需调用：用户点名或任务明确命中 description 时，才读取并使用对应 skill。
- Python 脚本在读写文本文件（含 JSON / JSONL / YAML / CSV / Markdown 等）时必须显式传 `encoding='utf-8'`，不得依赖默认编码。此规则适用于所有平台：Windows 默认编码为 gbk（会崩溃），WSL/Linux/macOS 默认为 utf-8（显式传是安全的无操作）。
- 在 Windows 上通过 Bash 工具运行 `python -c` 内联命令时，stdout/stderr 默认编码为 gbk，输出中文会乱码。必须设 `PYTHONIOENCODING=utf-8` 前置变量，或脚本内执行 `sys.stdout.reconfigure(encoding='utf-8')`；仅 `open()` 传 encoding 无法解决 print 输出的编码问题。
- 以下专题文档是本文件的延伸正文；命中对应场景时，必须继续读取对应文档，而不是只看本文件摘要。

## 2. 专题路由
- 协作基线、工作哲学、提问边界：
  [docs/agent-rules/collaboration-basics.md](/home/azhi/.agents/docs/agent-rules/collaboration-basics.md)
- 验证、运行安全、后台进程和大范围扫描：
  [docs/agent-rules/runtime-safety.md](/home/azhi/.agents/docs/agent-rules/runtime-safety.md)
- 本机固定工具路径与环境事实：
  [docs/agent-rules/local-environment.md](/home/azhi/.agents/docs/agent-rules/local-environment.md)
- Git、worktree、提交、推送和 shared workflow 同步：
  [docs/agent-rules/git-workspace.md](/home/azhi/.agents/docs/agent-rules/git-workspace.md)
- 文档归属、专题规则沉淀和结构性改动流程：
  [docs/agent-rules/documentation-boundaries.md](/home/azhi/.agents/docs/agent-rules/documentation-boundaries.md)
- 高风险操作确认细则：
  [docs/agent-rules/risky-operations.md](/home/azhi/.agents/docs/agent-rules/risky-operations.md)
- 默认输出风格：
  [docs/agent-rules/output-style.md](/home/azhi/.agents/docs/agent-rules/output-style.md)

## 3. 文档入口
- `docs/documentation-rules.md` 是 `~/.agents/docs/` 的归属规则源：
  [docs/documentation-rules.md](/home/azhi/.agents/docs/documentation-rules.md)
- `docs/README.md` 是 `~/.agents/docs/` 的导航索引：
  [docs/README.md](/home/azhi/.agents/docs/README.md)
