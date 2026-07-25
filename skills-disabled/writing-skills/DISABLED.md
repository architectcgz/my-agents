# 已禁用

- 状态：disabled
- 禁用时间：2026-07-25
- 原因：用户要求禁用 `writing-skills`;skill 编写流程改由 `skill-creator`、`authoring-project-skills` 和 `harness-engineering` 分工承接。
- 原位置：
  - `~/.agents/skills/writing-skills` -> `superpowers/writing-skills`
  - `~/.agents/skills/superpowers/writing-skills/`
- 替代路由：
  - 通用 skill 创建、更新与基础验证 → `skill-creator`
  - 项目级 skill 路由结构与演化 → `authoring-project-skills`
  - 仓库级 AGENTS.md、hooks 与机械校验 → `harness-engineering`
- 已迁出内容（2026-07-25）：
  - 结构/质量校验清单、description 触发约束、完成前门禁 → `~/.agents/skills/.system/skill-creator/references/validation-checklist.md`
  - `skill-creator` 的 Step 5 已改为 `quick_validate.py` + 上述 checklist
  - **未迁移**：强制 TDD Iron Law、完整 pressure-test 方法论正文（`testing-skills-with-subagents.md` 等仍只留在本禁用目录作存档）
- 恢复方式：
  1. `mv ~/.agents/skills-disabled/writing-skills ~/.agents/skills/superpowers/writing-skills`
  2. `ln -s superpowers/writing-skills ~/.agents/skills/writing-skills`
  3. 恢复 `~/.agents/skills/superpowers/SKILL.md`、相关 skill 路由和记忆索引中的入口。
  4. 若需恢复 Claude Code 插件副本，将 `~/.claude/plugins/cache/superpowers-dev/superpowers/*/skills-disabled/writing-skills` 移回同版本的 `skills/`。
- 注意：升级或重装 Superpowers 插件可能重新生成插件缓存副本，恢复后需再次检查可发现目录。
