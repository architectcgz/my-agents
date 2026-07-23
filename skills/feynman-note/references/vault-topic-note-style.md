# Vault Topic Knowledge Note Style

Use this style for reusable knowledge stored in an Obsidian or topic-oriented `vault/`. Treat the target directory as the style authority.

## Before Writing

1. Read the target `_索引.md` or navigation note.
2. Read at least two nearby notes, preferring one short and one substantial example.
3. Identify their filename language, title style, navigation block, heading depth, link syntax, and frontmatter convention.
4. Read the actual source material or code before making claims.

Do not impose YAML, kebab-case filenames, fixed tags, or a records template when peer notes do not use them.

## Default Shape

Use this only when it matches peer notes:

```markdown
# <precise topic title>

> 目录：[[<topic index>|<topic name>]] · 总导航：[[<vault index>]]
>
> 前置 / 相关：[[<related note>]]

**一句话：** <conclusion first>

<repository or evidence anchor when useful>

---

## 1. <problem or boundary>

## 2. <mechanism or why>

## 3. <flow, implementation, or comparison>

## 4. <trade-offs and reusable rules>

一句话收束：

> <compact recall sentence>
```

Do not force every section. Keep only the sections the topic needs.

## Content Principles

- Lead with the answer, then explain evidence and mechanism.
- Convert conversation into durable knowledge; do not narrate “we discussed” or reproduce the chat turn by turn.
- Prefer the sequence `问题边界 → 原因/机制 → 数据流或代码链路 → 取舍 → 可复用原则`.
- Preserve exact identifiers, paths, commands, protocol fields, and error messages.
- Distinguish verified repository facts from inference.
- Link existing notes with Obsidian wikilinks when the relationship is real.
- End with a short synthesis or reusable rules, not generic encouragement.

## Visual And Code Choices

Use the smallest representation that clarifies the relationship:

| Need | Format |
| --- | --- |
| Compare alternatives or semantics | Markdown table |
| Explain a runtime/data sequence | Compact `text` flow |
| Show a hierarchy or payload shape | Small tree |
| Anchor an implementation detail | Focused code block |

Avoid decorative diagrams, oversized code dumps, and repeated examples.

## Naming And Navigation

- Infer a concise, human-readable title from the actual topic.
- Follow the directory's filename convention; vault notes commonly keep readable Chinese titles.
- Keep the H1 aligned with the filename, allowing punctuation that Windows filenames cannot use.
- Add the note to `_索引.md` using the existing ordering and annotation style.
- Do not rewrite unrelated index entries.

## Quality Gate

Before finishing, verify:

- The note has no accidental record/Feynman frontmatter or sections.
- The opening provides navigation and a one-sentence conclusion when peers do.
- Each section contributes a distinct idea.
- Tables, flows, and code blocks materially clarify the topic.
- All technical claims come from supplied content or inspected sources.
- The local index links to the exact filename.
- Only the note and its index entry changed.
