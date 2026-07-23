---
name: feynman-note
description: Use when the user explicitly asks to turn content into a note, knowledge or technical note, learning note, vault or Obsidian note, ordinary record, Feynman note, review card, self-test, knowledge-gap note, or closed-book explanation.
---

# Note Writing Router

Route note requests by explicit style triggers. Style determines how to write; an explicit path determines where to write.

## Mode Selection

Apply the first matching explicit mode:

| Mode | Triggers |
| --- | --- |
| 费曼记录 | `费曼笔记`、`费曼记录`、`整理成费曼`、`复习卡片`、`自测问题`、`知识缺口`、`闭卷复述` |
| 普通记录 | `普通记录`、`原样保存`、`忠实记录`、`不要整理`、`不要总结`、`不要改写`、明确要求写入 `records/` |
| Vault 主题知识笔记 | `知识笔记`、`主题笔记`、`技术笔记`、`学习笔记`、`整理成笔记`、`总结成笔记`、`提炼成笔记`、明确要求写入 `vault/` 或 Obsidian 主题目录 |

Use Vault 主题知识笔记 for generic `记录成笔记`、`写成笔记` when no stronger mode trigger appears and the content is meant to become reusable knowledge. If explicit 费曼 and 普通记录 triggers conflict, ask which style to use. A `vault/` destination alone does not override an explicit style.

Do not activate for standalone `记录一下`、`记一下`、`保存一下`、`总结一下` when the user does not ask for a note.

## Resolve Repository And Destination

1. Resolve the enclosing notes repository from the user's explicit path first; otherwise read applicable `AGENTS.md` or repository documentation. Do not treat a nested topic directory as the repository root or invent a repository.
2. Honor an existing explicit file or directory path exactly. Never append `records/` or `feynman/` to it.
3. For a shorthand or nonexistent path such as `vault/memos`, inspect vault navigation and directories. Map it to one unambiguous existing topic directory and state the mapping; ask only when multiple destinations are equally plausible.
4. Without an explicit destination, use `$NOTES_REPO/vault/<topic>/` for Vault notes, `$NOTES_REPO/records/` for ordinary records, and `$NOTES_REPO/feynman/` for Feynman records.
5. Follow local filename language and naming conventions. Do not force kebab-case inside a human-readable vault.

## Shared Content Rules

- Use the immediately preceding discussion when it contains the source; ask `要记录的正文是哪一段？` only when the source is genuinely missing.
- Do not invent technical details. Verify code paths, commands, and repository facts before recording them.
- Preserve user-specified scope, title, tags, links, and destination.
- Inspect the written file and run available docs-only whitespace or link checks.

## Mode References

- **Vault 主题知识笔记 — REQUIRED:** Read `references/vault-topic-note-style.md` completely. Inspect the target index and at least two peer notes before writing.
- **普通记录 — REQUIRED:** Read `references/ordinary-record-style.md` when creating or editing this mode.
- **费曼记录 — REQUIRED:** Read `references/feynman-note-style.md` when creating or editing this mode.

The selected mode may summarize and reorganize only when its reference permits it. Do not add Feynman self-tests or knowledge gaps to other modes.

## Validation

- Vault: match peer-note conventions, verify H1/navigation/summary/code facts, and update the local `_索引.md` when that directory uses one.
- 普通记录: verify `title`、`tags`、`created`、`type: record`、`source`、`related`.
- 费曼记录: verify `title`、`tags`、`created`、`reviewed`、`next_review`、`confidence`、`type`.
- Confirm that only the requested note and directly related index entry changed.

## Git Policy

Do not commit or push notes unless the user explicitly asks. When requested, use `committing-changes`, stage only the note and its directly related index update, and preserve unrelated worktree changes.

## Common Mistakes

| Mistake | Correct action |
| --- | --- |
| Treating every note request as 普通记录 | Route explicit vault/knowledge requests to Vault 主题知识笔记 |
| Appending `records/` to an explicit vault path | Write to the explicit or unambiguously mapped topic directory |
| Adding YAML because a global template has it | Follow the target mode's reference and local peer conventions |
| Turning a Vault note into a chat transcript | Synthesize around problem, mechanism, evidence, and reusable conclusions |
| Adding self-tests to a non-Feynman note | Add them only when Feynman triggers are explicit |
| Auto-committing a note | Commit only after explicit user authorization |
