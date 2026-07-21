---
name: feynman-note
description: Use when the user explicitly asks to turn content into a note, such as “记录成笔记”“记成笔记”“整理成笔记”“写成笔记”, or explicitly requests a “普通记录” or “费曼笔记/费曼记录”. Do not use for standalone “记录一下”“记一下”“保存一下” or “总结一下”.
---

# Feynman Note Skill

Create notes in the notes repo declared by the applicable global or project `AGENTS.md`. Do not assume or hardcode a notes repo. Choose **普通记录** or **费曼记录** first, then apply only that mode's structure and constraints.

## Mode Selection

Default to **普通记录** when the user says:

- `记录到 note`
- `记一下`
- `记录下来`
- `保存一下`
- `记录知识点`

Use **费曼记录** only when the user explicitly says:

- `费曼笔记`
- `费曼记录`
- `整理成费曼`
- `复习卡片`
- `自测问题`
- `知识缺口`
- `闭卷复述`

If the user asks for `总结`、`整理`、`提炼`, summarize first only if requested, then record the summarized result. Do not silently convert 普通记录 into 费曼记录.

## Shared Rules

- Resolve the notes repo before writing: honor an explicit user-provided path first, otherwise read the applicable project and global `AGENTS.md` files for the declared notes repo. Store the resolved path in `NOTES_REPO` for commands below.
- If no notes repo is declared and the user did not provide one, ask for the path before writing; do not invent or fall back to a default repo.
- Use today's date for `created` and `reviewed`.
- If content to record is missing or ambiguous, ask `要记录的正文是哪一段？`.
- If content exists in the immediately preceding discussion, do not ask; infer a short title and tags.
- Do not invent technical details from general knowledge.
- After writing, validate frontmatter fields relevant to the selected mode.
- Commit and push the notes repo after creating the note unless the user asks not to.

## 普通记录

普通记录的目标是“忠实保存可直接阅读的内容”，不是学习卡片。

### Directory

Save to:

```bash
$NOTES_REPO/records/<kebab-case-filename>.md
```

Create `records/` if it does not exist.

### Template

Prefer copying the template first:

```bash
cp "$NOTES_REPO/.templates/record-note-template.md" \
   "$NOTES_REPO/records/<kebab-case-filename>.md"
```

### Standard Framework

```markdown
---
title: "<topic>"
tags: [tag1, tag2]
created: YYYY-MM-DD
type: record
source: chat
related: []
---

# <topic>

<原文或用户指定内容>
```

### Rules

- Preserve the source wording as directly as possible.
- Do not summarize, reorganize, polish, expand, add examples, add conclusions, or add self-test questions.
- Only fix obvious Markdown breakage, such as broken list indentation or missing code fences.
- If the source is the assistant's previous answer, record that answer's content, not a new answer.
- Do not set `next_review` or `confidence`; those are 费曼记录特性.

## 费曼记录

费曼记录的目标是“帮助复习和自测”，可以结构化整理，但仍不能编造未提供的内容。

### Directory

Save to:

```bash
$NOTES_REPO/feynman/<kebab-case-filename>.md
```

### Template

MUST copy the template first:

```bash
cp "$NOTES_REPO/.templates/feynman-note-template.md" \
   "$NOTES_REPO/feynman/<kebab-case-filename>.md"
```

Then fill:

```yaml
---
title: "<topic>"
tags: [tag1, tag2]
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
next_review: YYYY-MM-DD   # tomorrow
confidence: 2/5
type: permanent
related: []
---
```

### Standard Framework

Use the template sections as intended:

- `# 核心问题`: one question the note answers.
- `# 我的解释（闭卷复述）`: user's explanation or explicitly requested summary.
- `# 知识缺口`: unclear points, only from user-provided content or explicit analysis request.
- `# 关键细节`: `什么`、`为什么`、`何时用`、`验证方法`.
- `# 反向问题（自测）`: self-test questions.
- `# 关联`: related notes.
- `# 一句话总结`: concise recall sentence.

### Iron Rules

- `next_review` MUST be tomorrow's date.
- `confidence` MUST start at `2/5`.
- Do not choose a longer interval.
- Do not set confidence from perceived difficulty.
- Do not add self-test questions or knowledge gaps unless the user asked for 费曼记录 or asked to summarize/extract them.

## Validation

For 普通记录:

```bash
head -20 records/<filename>.md | grep -E "^(title|tags|created|type|source|related):"
```

Required fields: `title`, `tags`, `created`, `type: record`, `source`, `related`.

For 费曼记录:

```bash
head -20 feynman/<filename>.md | grep -E "^(title|tags|created|reviewed|next_review|confidence|type):"
```

Required fields: `title`, `tags`, `created`, `reviewed`, `next_review`, `confidence`, `type`.

## Git Workflow

```bash
cd "$NOTES_REPO"
git add records/<filename>.md  # 普通记录
git add feynman/<filename>.md  # 费曼记录
git commit -m "docs(note): 记录 <topic>"
git push
```

Use exact paths. Do not stage unrelated notes.

## Common Mistakes

| Mistake | Why Wrong | Correct Action |
| --- | --- | --- |
| Putting 普通记录 under `feynman/` | It will enter Feynman review reminders | Save to `records/` |
| Adding `next_review` to 普通记录 | Review scheduling is a Feynman feature | Omit review fields |
| Rewriting a record request | User asked to save readable content | Preserve wording |
| Creating self-test questions for 普通记录 | Adds unrequested Feynman traits | Only add in 费曼记录 |
| Treating all notes as Feynman notes | Mixes two workflows | Select mode first |

## Red Flags

Stop and switch to 普通记录 if you think:

- "They said record, so I should make it more complete."
- "All notes should use the Feynman template."
- "A record needs knowledge gaps and reverse questions."
- "I can put it in `feynman/` and leave sections blank."

Stop and ask if you cannot identify what content should be recorded.
