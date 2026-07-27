# 已禁用

- 状态：disabled
- 禁用时间：2026-07-26
- 原因：用户要求全局禁用 `subagent-driven-development`，避免在实施计划时自动采用多 agent 开发与多轮 review 流程。
- 原位置：
  - `~/.agents/skills/superpowers/subagent-driven-development/`
- 恢复方式：
  1. `mv ~/.agents/skills-disabled/subagent-driven-development ~/.agents/skills/superpowers/subagent-driven-development`
  2. `ln -s superpowers/subagent-driven-development ~/.agents/skills/subagent-driven-development`
  3. 恢复 `superpowers`、`executing-plans`、`writing-plans` 和工具说明中的活跃路由。
  4. 启动新会话，重新加载 skill 目录。

现有会话的已加载 skill 元数据不会热更新；禁用对新会话生效。
