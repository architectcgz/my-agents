# Feynman Record Style

Use this mode when the user explicitly asks for Feynman learning, review, self-test, knowledge gaps, or closed-book explanation.

## Default Destination

```text
$NOTES_REPO/feynman/<kebab-case-filename>.md
```

For an explicit destination, use that path without appending `feynman/`.

## Frontmatter

Copy `$NOTES_REPO/.templates/feynman-note-template.md` first when available, then require:

```yaml
---
title: "<topic>"
tags: [tag1, tag2]
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
next_review: YYYY-MM-DD
confidence: 2/5
type: permanent
related: []
---
```

Set `next_review` to tomorrow and `confidence` to `2/5`.

## Structure

Use the template sections:

- `# 核心问题`
- `# 我的解释（闭卷复述）`
- `# 知识缺口`
- `# 关键细节`：什么、为什么、何时用、验证方法
- `# 反向问题（自测）`
- `# 关联`
- `# 一句话总结`

## Rules And Validation

- Organize supplied content for review, but do not invent unsupported gaps or answers.
- Confirm all required frontmatter fields, the review date, and the self-test sections.
- Keep technical claims tied to the supplied source or inspected evidence.
