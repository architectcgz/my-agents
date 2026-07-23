# Ordinary Record Style

Use this mode when the user wants faithful storage rather than a synthesized knowledge note.

## Default Destination

```text
$NOTES_REPO/records/<kebab-case-filename>.md
```

For an explicit destination, use that path without appending `records/`.

## Template

Prefer `$NOTES_REPO/.templates/record-note-template.md` when available:

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

## Rules

- Preserve wording as directly as possible.
- Do not summarize, reorganize, polish, expand, add examples, conclusions, knowledge gaps, or self-test questions.
- Only repair broken Markdown such as list indentation or missing code fences.
- Use the user's supplied source; ask for the missing passage rather than inventing it.

## Validation

Confirm the required frontmatter fields and that the body remains faithful to the supplied text. Do not add `reviewed`, `next_review`, or `confidence`.
