#!/usr/bin/env python3
"""Harness initializer content aar templates."""

from __future__ import annotations


def aar_hook_readme() -> str:
    """Generate README for AAR hooks."""
    return """# After Action Review (AAR) Hook

## 作用

PostToolUse AAR Hook 在任务完成后自动触发，引导 Agent 完成 After Action Review。

## 触发条件

- 检测到任务完成信号：`completed`, `finished`, `done`, `merged`, `task complete`
- 当前 worktree 有激活的 task gate（非琐碎任务）

## AAR 检查清单

1. **新坑检测**：是否踩到新坑？需要记录到 Known Gotchas
2. **规则变化**：核心规则文件是否被修改？
3. **测试结果**：测试是否都通过？
4. **架构决策**：是否有新的架构决策需要记录？
5. **可复用模式**：是否有可以提取到 skill 或 policy 的模式？
6. **文档更新**：哪些文档需要更新？

## 工作流程

```
Task 完成
    ↓
PostToolUse Hook 检测到完成信号
    ↓
生成 AAR 模板 (feedback/aar/<timestamp>-<task-slug>.md)
    ↓
通知 Agent 完成 AAR 检查清单
    ↓
Agent 填写 AAR（手动）
    ↓
归档 task artifacts
```

## 生成的 AAR 文件

**位置**：`feedback/aar/<timestamp>-<task-slug>.md`

**格式**：
- 检查清单（checkboxes）
- 新发现的坑
- 规则变化
- 测试结果
- 架构决策
- 可复用模式
- 文档更新
- 经验教训
- 后续行动

## 配置

### 自定义完成信号

编辑 `harness/hooks/post-tooluse-aar.sh`：

```bash
COMPLETION_SIGNALS=(
  "completed"
  "finished"
  "done"
  "merged"
  "task complete"
  # 添加自定义信号
  "实现完成"
  "bugfix done"
)
```

### 自定义检查清单

编辑 `harness/hooks/post-tooluse-aar.sh`：

```bash
AAR_CHECKLIST=(
  "是否踩到新坑？"
  "规则文件是否被意外修改？"
  # 添加自定义检查项
  "是否更新了 API 文档？"
  "是否需要通知团队？"
)
```

## 与 completion-full gate 的集成

AAR Hook 是 completion-full gate 的一部分：

```
非琐碎任务完成
    ↓
1. 运行 completion validation（技术验证）
    ↓
2. PostToolUse AAR Hook（反思和记录）
    ↓
3. 归档 task artifacts
    ↓
4. 关闭 task gate
```

## 手动触发 AAR

```bash
# 为当前任务手动生成 AAR
bash harness/hooks/post-tooluse-aar.sh "task complete"
```

## 查看历史 AAR

```bash
# 列出所有 AAR
ls -lt feedback/aar/

# 查看最近的 AAR
cat feedback/aar/$(ls -t feedback/aar/ | head -1)
```

## 最佳实践

### 1. 及时填写 AAR
- 任务完成后立即填写，记忆最清晰
- 不要拖延，否则细节会遗忘

### 2. 具体而非抽象
- ❌ "遇到了一些问题"
- ✅ "Vue 组件在 SSR 时访问 window 对象导致报错"

### 3. 记录解决方案
- 不只记录问题，更要记录如何解决
- 包括尝试过的方案和最终方案

### 4. 提取可复用模式
- 如果同样的坑可能被其他人踩到，提取到 Known Gotchas
- 如果同样的解决方案可能被复用，提取到 skill 或 policy

### 5. 更新文档
- AAR 中发现的架构决策应该更新到 docs/architecture/
- 新的约束应该更新到 AGENTS.md 或相关 policy

## 示例 AAR

参见：`feedback/aar/example-aar.md`
"""


def aar_example() -> str:
    """Generate example AAR file."""
    return """# After Action Review — example-task

Date: 2026-06-20
Task: example-task

## 检查清单

- [x] 是否踩到新坑？需要记录到 Known Gotchas 或 feedback/
- [x] 规则文件是否被意外修改？检查 AGENTS.md 和 harness/policies/
- [x] 测试是否都通过？运行相关测试命令
- [x] 是否有新的架构决策需要记录到 docs/architecture/？
- [ ] 是否有可复用的模式需要提取到 skill 或 policy？
- [x] 是否有需要更新的文档？

## 新发现的坑（Known Gotchas）

### Vue 组件在 SSR 时访问 window 对象

- **现象**：开发环境正常，SSR 构建时报错 `ReferenceError: window is not defined`
- **原因**：Vue 组件在 `<script setup>` 顶层直接访问了 `window.innerWidth`
- **解决方案**：将访问 `window` 的代码移到 `onMounted()` 生命周期钩子中
- **预防措施**：
  - 在 AGENTS.md 中添加规则：前端组件不得在顶层访问浏览器全局对象
  - 添加 ESLint 规则检测这类问题

## 规则变化

- [x] AGENTS.md — 添加了 SSR 兼容性规则
- [ ] harness/policies/
- [ ] docs/文档规范.md
- [ ] .agents/skills/*/SKILL.md

## 测试结果

```bash
# 执行的测试命令
npm run test:unit
npm run build:ssr

# 测试结果
✓ 单元测试全部通过
✓ SSR 构建成功
```

## 架构决策

**决策**：前端组件统一使用 Composition API，避免在 `<script setup>` 顶层访问浏览器 API

**理由**：
- 保证 SSR 兼容性
- 更好的生命周期管理
- 更容易测试

**影响**：
- 需要更新现有组件（约 5 个）
- 需要在 AGENTS.md 中添加规则

**记录位置**：`docs/architecture/frontend-ssr-compatibility.md`

## 可复用模式

**模式**：SSR 安全的浏览器 API 访问

可以提取到 `frontend-engineer` skill 中：

```markdown
## SSR 兼容性

- 不要在 `<script setup>` 顶层访问 `window`、`document`、`navigator` 等浏览器全局对象
- 浏览器 API 访问必须在 `onMounted()` 或 `onBeforeMount()` 生命周期钩子中
- 使用条件判断：`if (typeof window !== 'undefined')`
```

## 文档更新

- [x] `docs/architecture/frontend-ssr-compatibility.md` — 新增
- [x] `AGENTS.md` — 添加 SSR 兼容性规则
- [ ] `code/frontend/README.md` — 补充 SSR 注意事项

## 经验教训

### 做得好的

- 及时发现问题，在 SSR 构建阶段拦截
- 快速定位根因（`window` 访问）
- 提取了可复用的架构规则

### 需要改进的

- 应该在开发初期就建立 SSR 兼容性检查
- 缺少 ESLint 规则自动检测这类问题
- 文档中没有提前说明 SSR 约束

### 下次注意

- 新增前端组件时，先检查是否有浏览器 API 访问
- 在 AGENTS.md 中明确 SSR 兼容性要求
- 添加自动化检查（ESLint 规则）

## 后续行动

- [ ] 更新现有的 5 个组件，修复 `window` 访问
- [ ] 添加 ESLint 规则：`no-restricted-globals` for `window`, `document`
- [ ] 在 CI 中添加 SSR 构建检查
- [ ] 更新 `frontend-engineer` skill，添加 SSR 兼容性规则
"""


def aar_directory_readme() -> str:
    """Generate README for feedback/aar/ directory."""
    return """# After Action Review (AAR) Archive

本目录存放任务完成后的 After Action Review (AAR) 记录。

## 目录结构

```
feedback/aar/
├── README.md                           # 本文件
├── example-aar.md                      # AAR 示例
├── 20260620-143000-task-slug.md       # 实际 AAR
└── ...
```

## AAR 文件命名

格式：`<timestamp>-<task-slug>.md`

示例：
- `20260620-143000-implement-pagination.md`
- `20260621-093000-fix-ssr-bug.md`

## AAR 触发

PostToolUse AAR Hook 在检测到任务完成信号时自动生成 AAR 模板：

```bash
# 自动触发（通过 Hook）
[Agent 完成任务] → PostToolUse Hook → 生成 AAR 模板

# 手动触发
bash harness/hooks/post-tooluse-aar.sh "task complete"
```

## AAR 内容结构

每个 AAR 包含：

1. **检查清单** — 标准化的反思项目
2. **新发现的坑** — Known Gotchas
3. **规则变化** — 核心规则文件的修改
4. **测试结果** — 验证结果
5. **架构决策** — 新的架构决策
6. **可复用模式** — 可以提取到 skill 或 policy 的模式
7. **文档更新** — 需要更新的文档
8. **经验教训** — 做得好的、需要改进的、下次注意的
9. **后续行动** — 待办事项

## 使用 AAR

### 查看最近的 AAR

```bash
cat feedback/aar/$(ls -t feedback/aar/*.md | head -1)
```

### 搜索特定主题的 AAR

```bash
grep -l "SSR" feedback/aar/*.md
grep -l "Vue" feedback/aar/*.md
```

### 提取 Known Gotchas

```bash
# 查看所有新发现的坑
grep -A 10 "## 新发现的坑" feedback/aar/*.md
```

### 提取可复用模式

```bash
# 查看所有可复用模式
grep -A 10 "## 可复用模式" feedback/aar/*.md
```

## AAR 生命周期

```
1. 任务完成
   ↓
2. PostToolUse Hook 生成 AAR 模板
   ↓
3. Agent 填写 AAR
   ↓
4. 保存到 feedback/aar/
   ↓
5. 定期回顾（每月/每季度）
   ↓
6. 提取到 Known Gotchas / Skills / Policies
   ↓
7. 归档（保留在 feedback/aar/ 或移到 archive/）
```

## 定期回顾

建议每月或每季度回顾 AAR：

```bash
# 查看本月的所有 AAR
ls feedback/aar/$(date +%Y%m)*.md

# 统计高频问题
grep "## 新发现的坑" feedback/aar/*.md | wc -l
```

## 提取到其他位置

### 提取到 Known Gotchas

如果同样的坑被多个 AAR 提到，提取到：
- `harness/known-antipatterns/EXAMPLES.md`
- 或项目特定的 gotchas 文档

### 提取到 Skills

如果发现可复用的模式，提取到：
- `.agents/skills/<skill-name>/`
- 或更新现有 skill

### 提取到 Policies

如果发现新的约束，提取到：
- `harness/policies/<policy-name>.yaml`
- 或更新 `AGENTS.md`

## 最佳实践

1. **及时填写**：任务完成后立即填写，记忆最清晰
2. **具体而非抽象**：记录具体现象和解决方案
3. **提取可复用模式**：主动思考是否可以防止其他人踩坑
4. **更新文档**：AAR 中的发现应该反映到文档中
5. **定期回顾**：每月回顾，提取高频问题

## 示例

参见：`example-aar.md`
"""
