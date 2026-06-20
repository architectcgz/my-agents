# Cross-Tool Compatibility and Composition

Read this file when a skill must survive long sessions / multiple tools, when a project has multiple skills, or when one skill calls another. For the repo-wide harness wiring (AGENTS.md, hook files, CI), use `harness-engineering`.

## 三层防失忆(长会话 + 多任务 + 多次压缩)

自然语言指令("去读 SKILL.md")在上下文压缩时会被当普通描述丢掉;结构化表格 / 清单保留更多。
三层冗余,每层都可能被压缩器丢掉,留给你下一层:
1. **SKILL.md 的 Session Discipline** —— 多任务会话里每个新任务重走路由(见 `skill-structure.md`)。
2. **薄壳 Auto-Triggers**(入口文件,压缩后仍在)。
3. **SessionStart hook** —— `/clear` / compact 后从磁盘自动重注 SKILL.md。

## 薄壳(thin shell)

让一个 skill 在 Claude Code / Cursor / Codex / Gemini 多工具生效,不是复制 N 份 SKILL.md,
而是在每个工具入口文件里放一层薄壳(≤60 行),把**最小可执行路由表内联**进去 —— 压缩后表格仍活着。

薄壳三块(缺一不可):
- **Quick Routing** —— `任务 | 必读文件 | workflow` 三列,必须有兜底行 Other 和多子任务行。压缩后这是 Agent 找"该读哪些文件"的唯一线索。
- **Auto-Triggers** —— 事件→动作;最关键是"同会话新任务 → 重读 SKILL.md 重走路由"。
- **Red Flags — STOP** —— 把"就这一次跳过"这类借口前置拦截(压缩后只剩薄壳时的最后防线)。

反例:`Please read skills/.../SKILL.md before starting`(soft pointer)在长会话里会被摘要掉 →
Agent 没路由表可查,凭感觉动手,用户察觉不到。**用结构化表格,不要只靠一句自然语言指针。**

## hook(机制级护栏,不靠 Agent 自觉)

- **SessionStart hook** 监听 startup / clear / compact,自动读 SKILL.md 注入 context(防遗忘)。
- **PreToolUse hook** 在 Edit 核心规则文件前拦一刀,非 0 退出码直接取消编辑(防违规)。
- 注意:hook 只能一定程度缓解;过多 hook 反而限制发挥,复杂问题建议用 Sonnet 及以上模型。
- 具体 hook 接线、schema(如 Claude Code v2.1+ PreToolUse 只认嵌套格式)交给 `harness-engineering`。

## 一个 skill 干一件事(隔离)

- 不要从 GitHub 拉一堆同类 skill —— 冲突必现,命中率下降。少而精,优先自动触发而非主动引用。
- 多 skill 项目:每个 skill 独立 SKILL.md;跨 skill 通用约定放 `shared/`;
  用 frontmatter `primary: true` 标默认 skill(SessionStart hook 注入 primary 那个);
  不同领域保持独立,合并只会让 description 变"万金油"。
- 每个 skill 用 **Do Not Use** 明确边界,把不属于自己的任务指向正确的 skill。
- 该裂成多 skill 的信号:两领域 Common Tasks 完全不相交;description 要列 10+ 跨领域触发短语;gotchas 自然分成两半。

## skill 组合(组合)

workflow 可以"外包"一段工作给另一个 skill。三种模式:
- **A 嵌入调用**:workflow 某步显式 `Read skills/<other>/SKILL.md` 跟完其某条路由再返回。
- **B 直接路由**:Common Tasks 某类任务直接指向另一个 skill 的 workflow,不写自己的包装。
- **C 子 Agent 委派**:开干净子 Agent 整个隔离执行,只回结构化结果。

反模式:隐式传递依赖(调的 skill 下游不存在 → 静默失败,要 vendor 或"缺 skill 就停下问用户");
循环组合(A 调 B 调 A);匿名调用(不写具体路径,失去复现性);组合当偷懒借口;调完别人就跳过自己的 AAR。

## 自动化校验(防遗忘型错误)

80% 的 skill 失败来自遗忘而非误解,脚本能抓住:
- **smoke-test 思路**:把 SKILL.md 当唯一数据源,自动验证 Common Tasks / Reference Map 引用的文件是否都存在、有无孤儿、行数是否超标。
- **test-trigger 思路**:从 Common Tasks 生成用户可能的真实说法,测 description 命中率。
- 跑的时机:初次写完、改完 SKILL.md / 薄壳后、从上游模板升级后、宣布"完成"前。
- 脚本抓不到语义问题(description 是否够准、路由是否合理),那部分仍要人 / `writing-skills` 的检索测试兜。
