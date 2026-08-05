# 已禁用

- 状态：disabled
- 禁用时间：2026-08-05
- 原因：用户要求暂时禁用全局 `code-workflow` skill，避免新会话自动加载该工作流。
- 原位置：`~/.agents/skills/code-workflow/`
- 说明：`~/.agents/harness/workflows/code-workflow/` 底层运行包未删除；显式调用其命令仍可用。
- 恢复方式：
  1. `mv ~/.agents/skills-disabled/code-workflow ~/.agents/skills/code-workflow`
  2. 启动新会话，使 skill 目录重新扫描。

现有会话已经加载的 skill 元数据不会热更新；禁用对新会话生效。
