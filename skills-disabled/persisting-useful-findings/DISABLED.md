# 已禁用

- 状态：disabled
- 禁用时间：2026-07-25
- 原因：用户要求移除 `persisting-useful-findings`；之后由用户自行记录记忆与可复用发现，agent 不再主动走该 skill 沉淀。
- 原位置：
  - `~/.agents/skills/persisting-useful-findings/`
  - 经父目录软链对 Claude/Codex 可见：`~/.claude/skills`、`~/.codex/skills` → `~/.agents/skills`
- 替代约定：
  - 用户自己维护 `~/.agents/memory/`、项目文档或个人笔记
  - agent 默认不主动写全局/项目记忆，除非用户明确要求“记录/记住”
  - 可复制 prompt 存档仍在 `~/.agents/prompts/discover-and-persist-issues-prompt.md`（仅参考，不再作为默认 skill 入口）
- 恢复方式：
  1. `mv ~/.agents/skills-disabled/persisting-useful-findings ~/.agents/skills/persisting-useful-findings`
  2. 确认 `~/.claude/skills` 与 `~/.codex/skills` 仍指向 `~/.agents/skills`
- 注意：不要在各 agent 入口目录单独再放一份正文；主体始终在 `~/.agents/`。
