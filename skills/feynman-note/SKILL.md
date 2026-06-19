---
name: feynman-note
description: Use when creating, validating, or managing Feynman learning notes with proper format, git workflow, and review scheduling.
---

# Feynman Note Skill

Create and manage structured learning notes using the Feynman technique with automated review reminders.

## When to Use

- User asks to create a new learning note / 费曼笔记
- User asks to record knowledge / 记录知识点
- User mentions Feynman method / 费曼学习法
- After a technical discussion that should be preserved for review

## Notes Repository Location

Default: `/home/azhi/workspace/projects/notes`

Check if this path exists. If not, ask user for the correct notes repository location.

## Workflow

### 1. Gather Information

Ask the user (in one question, not separately):
- **主题/标题**：What is the topic? (e.g., "Gin HTTP 解码层级")
- **标签**：What tags to add? (e.g., `[后端, Go, HTTP]`)
- **核心问题**：What is the core question this note answers?

Do NOT ask for confidence level or review dates — those are auto-generated.

### 2. Create the Note

Use the template at: `/home/azhi/workspace/projects/notes/.templates/feynman-note-template.md`

**Frontmatter auto-fill rules:**
- `created`: current date `YYYY-MM-DD`
- `reviewed`: current date `YYYY-MM-DD`
- `next_review`: **tomorrow** (current date + 1 day)
- `confidence`: `2/5` (default starting confidence)
- `type`: `permanent` (default)

**Content sections:**
- Fill "核心问题" from user input
- Fill "我的解释" based on the discussion context or ask user to provide
- Leave "知识缺口" with 2-3 empty checkboxes for user to fill later
- Fill "关键细节" if information is available from discussion
- Generate 3-4 "反向问题" based on the topic
- Leave "关联" empty (user fills as they create more notes)
- Generate "一句话总结"

**File naming:**
- Use lowercase kebab-case
- Chinese pinyin for Chinese topics (e.g., `gin-http-decoding.md`)
- Save to: `feynman/<filename>.md`

### 3. Validate Format

After creating, check:
- [ ] YAML frontmatter is valid (no syntax errors)
- [ ] All required fields present: `title`, `tags`, `created`, `reviewed`, `next_review`, `confidence`, `type`
- [ ] Date format is `YYYY-MM-DD`
- [ ] Tags are array format: `[tag1, tag2]`
- [ ] Confidence is `X/5` format

If validation fails, fix automatically before proceeding.

### 4. Git Workflow

```bash
cd /home/azhi/workspace/projects/notes
git add feynman/<filename>.md
git commit -m "Add: <topic> 笔记

- 费曼学习法整理 <核心内容一句话>
- 记录知识缺口：<列出2-3个缺口>
- 关联主题：<相关概念>"

git push
```

### 5. Confirm Completion

Report to user:
- ✅ Note created: `feynman/<filename>.md`
- ✅ Committed and pushed to GitHub
- 📅 Next review scheduled: `<next_review date>`
- 📝 Current confidence: `<confidence>`

Remind user:
- GitHub Actions will send review reminder on `<next_review date>`
- After reviewing, update `next_review` and `confidence` fields
- Fill in knowledge gaps as you research them

## Format Validation Script

Use this to check note format (optional):

```bash
cd /home/azhi/workspace/projects/notes
# Check YAML frontmatter
for file in feynman/*.md; do
  echo "Checking $file..."
  head -20 "$file" | grep -A 10 "^---$" | grep -E "^(title|tags|created|reviewed|next_review|confidence|type):" || echo "⚠️  Missing fields in $file"
done
```

## Common Issues

### Issue: User provides raw discussion text
**Solution**: Extract key points and structure them into the template sections. Don't dump raw conversation into "我的解释".

### Issue: Topic is too broad (e.g., "学习 Go")
**Solution**: Ask user to narrow down to a specific concept (e.g., "Go 的 channel 关闭行为").

### Issue: Notes repo doesn't exist
**Solution**: Ask user if they want to create a new notes repository or specify existing location.

## Related Skills

- Use `todo` skill for non-learning task tracking
- Use `code-workflow` for development tasks that need documentation

## Example Interaction

**User**: "我想把刚才讨论的 Gin 解码记录下来"

**Assistant**: 
"好的，我来创建费曼笔记。快速确认一下：
- 主题：Gin 框架的 HTTP 解码层级
- 标签：[后端, Go, HTTP, 性能优化]
- 核心问题：Gin 是否处理了应用层 HTTP 报文解码？

这样可以吗？"

*(User confirms)*

*(Create note, validate, commit, push)*

"✅ 笔记已创建并同步到 GitHub
📝 文件：`feynman/gin-http-decoding.md`
📅 明天（2026-06-20）会收到复习提醒"
