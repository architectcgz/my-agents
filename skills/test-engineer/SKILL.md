---
name: test-engineer
description: Use when designing, writing, refactoring, reviewing, or running automated tests; choosing unit, integration, contract, runtime, or end-to-end coverage; deciding whether a failing/red test or TDD is warranted; reducing fake, fixture, mock, flaky-test, or duplicated-signal decay; or collecting verification evidence after implementation.
---

# Test Engineer

## 定位

把测试视为可执行行为 contract 和回归保护，而不是覆盖率、测试行数或流程合规指标。优先保留高信号、低维护成本、分层正确且可重复执行的测试。

先读取项目自己的 `AGENTS.md`、测试文档、质量门禁和最窄验证命令。项目规则、用户明确要求和已发布 contract 优先于本 skill 的默认值。

## Reference 路由

- 设计新项目测试体系、判断是否需要红测、治理测试膨胀或腐化、选择测试层级、设计 fake / fixture、建立 CI 门禁时，必须读取 `references/sustainable-testing-strategy.md`。
- 不在此 skill 重复 backend、Go、frontend 或 runtime 的专属规则；由调用方已经加载的语言/领域 skill 负责这些边界，避免 skill 之间循环路由。
- Review 测试充分性时同时使用 `reviewer` 的 test strategy reference；不要把实现验证和独立 review 混成一次心智检查。

## 工作流程

1. 明确本次要保护的可观察行为、失败模式和已发布 contract。
2. 读取现有测试，确定该行为的唯一主要 owner；不要默认新增一层重复测试。
3. 按风险选择测试节奏：
   - 文档、纯展示或机械重构不强制红测。
   - 已有测试清楚覆盖的小改动可运行现有最窄测试。
   - 新 contract、新 use case、新 repository 或新错误语义必须有 focused test，推荐 test-first。
   - Bugfix、事务、幂等、并发、worker、migration 和数据一致性默认先写失败回归测试或 characterization test；无法先复现时说明原因。
4. 在拥有行为的最窄层级编写或调整测试，先证明结果、状态、副作用或 contract，不只证明 mock 被调用。
5. 运行最窄相关测试；需要真实数据库、broker、浏览器、端口或进程时，再升级到 integration、runtime 或 system 验证。
6. 绿灯后重构测试：合并同失败信号、拆分超长文件、提取重复 fixture、删除已迁移到更合适 owner 的重复断言。
7. 报告实际执行的命令、结果、失败原因和未覆盖风险；没有执行就不能声称通过。

## 核心规则

- 一条行为 contract 只设一个主要测试 owner。多层覆盖时，每层必须证明不同事实。
- 一个测试只证明一个行为 contract；同一规则的多个输入使用 table test，不把不同权限、状态、副作用或错误语义塞入同一张表。
- 优先断言外部结果、状态变化、持久化结果、事件、错误码、幂等效果或生命周期，而不是宽泛的调用次数和调用顺序。
- 只有调用次数或顺序本身属于 contract 时才断言它们。
- 不为了降低测试/生产代码比例、提高覆盖率或让 CI 变绿而删除信号、放宽断言或修改 fixture 迁就错误实现。
- Coverage 只用于发现盲区和趋势，不把全仓高比例作为主要质量目标。
- 不用 `sleep` 作为同步；使用 context、channel、fake clock、hook、await/poll with deadline 或可观察状态。
- 不允许 flaky test 依赖“失败后自动重跑直到成功”；先定位非确定性 owner。

## Test Double 规则

- 优先定义消费方需要的窄接口；不要让单个 use case 的 fake 实现无关的大接口。
- 对 Go 使用函数字段式 fake 或小型 function adapter；未配置的方法必须立即失败，不能静默返回零值。
- 捕获 slice、map、`[]byte` 或指针可变对象时按需要复制，避免别名污染断言。
- 少量测试数据可内联；重复出现后再提取 package-local builder / fixture。
- 只有稳定 helper 被多个文件持续复用且不承载业务规则时，才提升到共享 testkit。
- Mock 外部边界时仍断言业务可见结果；不要让测试只证明 mock 配置正确。

## 真实依赖边界

- Repository 测试使用真实目标数据库证明 SQL、约束、事务、锁、nullable、JSON/array 和错误翻译；不要用 mock ORM 代替数据库 contract。
- Migration 至少证明正式 `up` 可执行；可逆 migration 验证回滚路径。
- Cache、queue、broker、对象存储或浏览器行为只有在 fake 无法证明关键语义时才升级到真实 integration/runtime 测试。
- Schema setup 放在正式 migration、临时 integration fixture 或共享测试 helper；不要为测试把 schema mutation 塞进生产启动路径。

## 验证模式

- 用户只要求验证或诊断时，保持只读；区分实现缺陷、测试缺陷、环境缺陷和 harness 缺陷。
- 用户要求补测试时，只修改目标行为需要的测试和 helper；测试暴露生产缺陷但用户未授权修复时，报告缺陷而不放宽测试。
- 用户要求修复时，先保留能复现问题的失败测试，再实施最小正确修复并重新验证。
- 完成时列出实际命令、通过项、失败项、证据和残余风险。
