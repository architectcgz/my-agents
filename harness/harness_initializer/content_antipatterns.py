#!/usr/bin/env python3
"""Known antipattern scaffold templates."""

from __future__ import annotations

from pathlib import Path


def _read_asset(relative_path: str) -> str:
    path = Path(__file__).parent / "assets" / relative_path
    return path.read_text(encoding="utf-8")


def known_antipatterns_examples() -> str:
    return _read_asset("known-antipatterns/EXAMPLES.md")


def known_antipatterns_readme() -> str:
    """Generate README for harness/known-antipatterns/ directory."""
    return """# Known Antipatterns

本目录存放从真实失败中提取的反模式案例。

## 硬约束

**这张表只能从真实失败里抄，不能凭空想象。**

## 文件结构

```
harness/known-antipatterns/
├── README.md          # 本文件
└── EXAMPLES.md        # 反例库（主文件）
```

## 反例来源

### 1. 从 AAR 中提取

```bash
# 查看所有"新发现的坑"
grep -A 10 "## 新发现的坑" feedback/aar/*.md

# 提取高频问题
grep -h "###" feedback/aar/*.md | sort | uniq -c | sort -rn
```

### 2. 从 Code Review 中提取

```bash
# 查看所有 review findings
ls docs/reviews/*/findings.md
```

### 3. 从 Git 历史中提取

```bash
# 查找修复类提交
git log --grep="fix:" --grep="bug:" --oneline

# 查看修复前后的 diff
git show <commit-hash>
```

## 如何添加反例

### 标准模板

```markdown
### [简短标题]

**来源**：[commit hash / PR链接 / issue链接]

**用户请求**：
```
[用户的原始请求]
```

**❌ Before（为什么错）**：
```[language]
[真实的错误代码]
```

**为什么错**：
- [具体问题1]
- [具体问题2]

**✅ After（正确做法）**：
```[language]
[修复后的代码]
```

**检验句**：
- [检验句1] → [结果]
- [检验句2] → [结果]
```

### 质量检查

添加前确认：
- [ ] 有可追溯的来源
- [ ] 有真实的代码（不是伪代码）
- [ ] 说明了具体问题（不是抽象原则）
- [ ] 提供了检验句

## 使用场景

### 1. Agent 自查

完成代码后，Agent 可以：
```bash
# 搜索相关反模式
grep -i "抽象" harness/known-antipatterns/EXAMPLES.md
```

### 2. Code Review 引用

Reviewer 可以引用：
```markdown
这个改动违反了 [Known Antipattern: 过度设计](harness/known-antipatterns/EXAMPLES.md#过度设计)
```

### 3. 更新 Skills

高频反模式应该：
- 更新到对应 skill
- 添加到 Red Flags
- 添加到检验句清单

## 定期维护

### 每月回顾

1. 回顾本月的 AAR
2. 提取高频反模式
3. 添加到 EXAMPLES.md
4. 更新相关 skills

### 统计

```bash
# 反例总数
grep -c "^###" harness/known-antipatterns/EXAMPLES.md

# 最近添加
git log --oneline harness/known-antipatterns/EXAMPLES.md | head -5
```

## 参考

- AAR 目录：`feedback/aar/`
- 检验句指南：`~/.agents/harness/docs/verification-questions-guide.md`
- Code Review：`docs/reviews/`
"""
