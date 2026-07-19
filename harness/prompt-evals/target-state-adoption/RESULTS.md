# 目标状态迁移提示词评测结果

## 2026-07-19 RED

- 场景：用户要求所有 Go 服务按 GORM 推荐方式全面迁移。
- 实际失败：计划只把 repository 查询切到 GORM，保留 `sql.Open`、`lib/pq` 和旧 runtime owner。
- 合理化理由：minimal diff、降低风险、避免同时迁移 driver、保留已验证 timeout/pool wiring。
- 结论：旧提示词没有把用户明确目标放在既有模式和 minimal diff 之前，也没有要求最终生产路径与旧路径删除证明。

## 2026-07-19 GREEN 静态验证

- `check_rules.py`：通过，目标状态规则覆盖全局入口、协作规则、brainstorming、architect、writing-plans、plan reviewer 和 development pipeline。
- `check-agent-home.sh`：通过，并已包含目标状态规则静态门禁。
- `cases.json`：JSON 语法通过。
- `run_evals.py`：Python 编译通过；使用 `fake_decision_agent.py` 时 4/4 case 通过，证明 runner 的输入、解析和评分链路可运行。

## 2026-07-19 Plan 评测扩展

- 新增 `plan_cases.json`，包含 10 个完整 implementation plan 场景，不再只检查 A/B/C 选择。
- 新增 `run_plan_evals.py`，保存每个 Markdown plan，并检查必需章节、最终生产路径、runtime owner、关键迁移面、旧路径删除、精确验证命令、恢复方案和分阶段退出条件。
- 新增 `fake_plan_agent.py` 确定性 fixture，用于验证 runner 和评分逻辑，不作为真实模型通过证据。
- fixture 首轮暴露了否定句误判：计划写“禁止本期迁移 pgx”仍被宽泛禁止规则命中。已把规则收窄为只拒绝“本期同时/直接/一并迁移 pgx”，说明评分器确实经过一次 RED → GREEN 修订，而不是只验证预期成功路径。
- 确定性 fixture：10/10 plan 场景通过。

## 独立模型行为验证状态

当前未完成，不能宣称行为 GREEN：

- Claude CLI 请求无模型输出并最终进入 `aborted_streaming`。
- Codex CLI 使用 `gpt-5.5` 时因本机 API key 返回 `401 Unauthorized`。
- 协作 subagent API 对自动选择的 `gpt-5.4` 返回“不支持所选模型”。

凭证或模型路由恢复后，必须按 `README.md` 分别运行决策评测和 plan 生成评测，并对目标模型连续运行三轮；只有全部 case 通过且人工抽查 plan 语义完整，才能把提示词行为标记为 GREEN。

## 2026-07-19 调研后提问规则

- 用户纠正：真实方案不能只在识别到歧义后反问；agent 应先检查项目并查询官方资料，给出有依据的推荐，再询问用户真正拥有或必须决定的边界。
- 共享规则已覆盖全局入口、协作基线、architect、brainstorming 和 writing-plans。
- `ambiguous_gorm_adoption` 已增加“调研依据”和“推荐方案”要求。
- 新增 `HUMAN_EVAL.md`，用 5 个场景、每场景三轮检查本地调查、Web/官方来源、推荐质量、提问边界和反效果。
- 当前只完成静态与 fixture 验证；真实模型人机测试尚未执行，不能标记行为 GREEN。
- 用户提供了数据库 timeout 调研的正向范例：先概括 timeout ownership 核心矛盾，再拆分 Application/transaction/query/PostgreSQL/连接池机制、入口与查询场景、不同 Go 数据访问栈和候选决策模型，说明资料来源与交付物，最后只确认问题定义是否符合预期。该结构已作为 gold example 的判定标准加入人机评测场景 0。
