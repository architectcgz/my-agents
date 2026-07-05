# __TASK_TITLE__ 实施计划

> 默认用中文填写本计划；代码、命令、路径、错误信息、协议字段、枚举值、外部专有名词和机器解析字段保持原文。

**Goal:** 待填写

**Architecture:** 待填写

**Tech Stack:** 待填写

---

## Task Metadata

- Task Slug: `__TASK_SLUG__`
- Parent Task Group: `无` <!-- 独立任务写"无"；task group slice 写 parent group slug -->
- Slice Index: `-` <!-- 独立任务写"-"；task group slice 写 "1/5"、"2/5" -->
- Depends On: `无` <!-- 前置依赖 task slug，多个用逗号分隔；无依赖写"无" -->
- Started At: `__STARTED_AT__`
- Worktree: `__WORKTREE_PATH__`
- Branch: `__BRANCH_NAME__`
- Plan Type: `slice` <!-- slice | roadmap -->

## Plan Status

- Status: `draft` <!-- draft | ready-for-implementation | implemented | review-pending | review-passed | archived -->
- 开始编码前必须完成：
  - [ ] 已完成 intake analysis gate
  - [ ] 已完成计划评审 / 架构适配检查
  - [ ] 已填写执行切片和验证计划

## Objective And Non-Goals / 目标与非目标

- 目标：
- 非目标：

## Problem Statement / 问题陈述

- 当前行为 / 结构：
- 目标行为 / 结构：
- 为什么现在需要做：

## Inputs / 输入

- 来源文档：
- 相关架构 / 契约：
- 相关既有工作：

## Acceptance Source Checklist / 验收事实源清单

> 先把事实源中的硬规则展开成可检查条目，再写执行步骤。禁止只写“遵守配置规范”“补错误处理”“完成 runtime wiring”这类概括项。

- 已读取的项目入口 / 路由规则：
- 已读取的架构 / 契约 / 运行期 / 安全 / 配置 / 测试 / review 文档：
- 从事实源抽取的 MUST / MUST NOT：
  - [ ] 待填写：字段 / 状态 / 错误 / 限制 / API 行为 / 脱敏要求必须具体到可测试项
- 不在本计划验收范围内的规则及原因：
- 每条验收规则对应的 slice / 测试 / 验证命令：

## Task Classification

- Classification: `非琐碎任务`
- 判定理由：

## Files

- 新建：
- 修改：
- 查阅：
- 测试：

## 复用与 Owner 决策

- 已搜索的既有模式：
- 复用 / 扩展 / 拆分 / 新建决策：
- Owner 边界：
- 为什么这是最窄安全改动面：

## Intake Analysis Gate

- 适用的 superpowers analysis pass：
- 为什么该 analysis pass 适用：
- grill-with-docs 发现：
- challenge 后的计划调整：

## Execution Slices / 执行切片

### Slice 1: 待填写

- 目标：
- 依赖：
- 文件：
  - 新建：
  - 修改：
  - 查阅：
  - 测试：
- 步骤：
  - [ ] Step 1:
  - [ ] Step 2:
- 验证：
- 评审重点：
- 完成标准 / 验收清单：
  - [ ] 待填写：从“验收事实源清单”展开到本 slice 的具体可观察要求
  - [ ] 待填写：对应测试、命令或后续 slice 验证方式

## Impact And Compatibility / 影响与兼容性

- API / DTO：
- 数据 / migration：
- 状态 / cache / queue / event：
- 运行时 / config：
- 前端 route / state / UX：
- 文档 / contracts：

## Plan Review / Architecture Fit / 计划评审与架构适配

- 目标 owner 边界：
- 复用点 / 落点：
- 触及的已知结构债：
- 本计划如何避免只改行为、不收敛结构：
- 隐藏二次重构风险：
- 评审后决策：

## Documentation Owner / 文档归属

- 当前必须读取的事实源：
- 实现后需要更新的事实源：
- 不得升级为架构事实源的计划内备注：
- 归档条件：

## Validation Plan / 验证计划

- 每个 slice 的命令：
- 集成命令：
- 手工检查：
- 有意跳过的命令及原因：

## Validation Evidence / 验证证据

- Command:
  - Result:
  - Notes:

## Independent Review Handoff / 独立评审交接

- Review target:
- 验证证据摘要：
- 架构 / 契约输入：
- 已知风险 / 评审重点：
- 可考虑的项目本地检查：

## Rollback / Recovery / 回滚与恢复

- 安全回退边界：
- 数据 / 配置 / 运行时恢复说明：
- 不可逆操作：

## Residual Risks / 残余风险

- 风险：
- 为什么可接受：
- 后续 owner（如有）：
