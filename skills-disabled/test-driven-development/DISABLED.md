# 暂时禁用

- 状态：disabled（临时）
- 禁用时间：2026-07-23
- 原因：用户要求暂时禁用 TDD skill
- 原位置：
  - `~/.agents/skills/test-driven-development` -> `superpowers/test-driven-development`
  - `~/.agents/skills/superpowers/test-driven-development/`
- 恢复方式：
  1. `mv ~/.agents/skills-disabled/test-driven-development ~/.agents/skills/superpowers/test-driven-development`
  2. `ln -s superpowers/test-driven-development ~/.agents/skills/test-driven-development`
  3. 恢复 `~/.agents/skills/superpowers/SKILL.md` 中的 test-driven-development 条目与路由说明（如已注释）
- 注意：Claude Code 插件缓存 `~/.claude/plugins/cache/superpowers-dev/superpowers/*/skills/test-driven-development` 是独立副本；若会话仍能发现该 skill，需额外禁用/移除插件侧副本。
