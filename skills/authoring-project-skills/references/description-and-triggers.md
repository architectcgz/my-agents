# Description and Triggers

Read this file when writing or fixing a skill's `description`, name, or discoverability.
For the deeper CSO (Claude Search Optimization) rules, also read `writing-skills`.

## Description = 触发条件,不是摘要

`description` 是 Agent 判断"要不要激活这个 skill"的**最重要依据**。写不好 = skill 等于不存在。

- 只描述**何时用**(触发短语、症状、场景),**不要**总结 skill 的流程 / 做什么。
- 模型天然倾向 undertrigger(保守激活),所以要**主动覆盖用户可能的各种说法**,
  包括用户没明说技能名时的口语表达。
- 第三人称(会被注入系统提示);以 "Use when..." 开头。

```yaml
# ❌ 摘要 / 功能说明 —— 命不中,且 Agent 可能照 description 抄近路跳过正文
description: API development helper
description: 创建专业 Word 文档,先读模板再生成章节再校验

# ✅ 只写触发条件 + 覆盖多种说法
description: >
  Use when the user asks to "add a new API endpoint", "write controller logic",
  "fix a backend bug", or "add a database migration". Activate when the task
  involves REST routes, request validation, service layer logic, or mapper changes.
```

陷阱:description 一旦总结了工作流,会制造一条"捷径"——Agent 照 description 做,
把 skill 正文当成可跳过的文档。**永远不要在 description 里写流程。**

## 关键词覆盖

用 Agent 会搜索的词:
- 报错原文(`Hook timed out`、`race condition`)
- 症状(flaky、hanging、白屏、命不中)
- 同义词(timeout/hang/freeze、cleanup/teardown)
- 工具 / 命令 / 库名 / 文件类型

## 命名

用动词优先的主动式、描述"做什么 / 核心洞察":
- ✅ `condition-based-waiting` 优于 `async-test-helpers`
- ✅ `creating-skills` 优于 `skill-creation`
- 处理类用动名词(-ing)。

## 各工具入口 description 必须一致

如果同一 skill 在多个工具注册(Claude `.claude/skills`、Cursor `.cursor/skills`、Codex 等),
各入口的 description **必须完全一致**;否则两边判据不同 = 激活随机化。

## 质量自检
- ✓Check:把 description 念给没看过 skill 的人,他能判断"什么时候该用"吗?
- ✓Check:用户最可能的 3–5 种口语说法,是否都被触发短语覆盖?
- ✓Check:description 里有没有混入"怎么做"的流程?有就删。
