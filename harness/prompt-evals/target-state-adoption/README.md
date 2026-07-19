# 目标状态迁移提示词评测

这组评测验证 agent 是否会把用户明确要求的“全面采用 / 全部迁移 / 按推荐方式”缩成调用点适配，也验证用户明确要求分阶段时不会擅自扩大范围。

## 测试层级

1. 静态门禁：确认全局规则和相关 skills 仍包含目标状态、旧路径删除和意图忠实度约束。
2. 决策评测：把 `cases.json` 中的压力场景交给独立模型，检查它是否选择忠于用户目标的迁移边界。
3. 计划生成评测：把 `plan_cases.json` 中的场景交给独立模型，保存完整 implementation plan，并机械检查目标状态、runtime owner、旧路径删除、验证和恢复方案。
4. 真实任务回放：使用曾经失败的 GORM 迁移需求重新生成计划，检查初始化、driver、runtime owner、repository、outbox 和旧依赖删除是否完整。
5. 人机评测：按 `HUMAN_EVAL.md` 在全新会话中检查 agent 是否先调查本地事实和官方资料、形成推荐，再询问真正的用户边界。

## 静态门禁

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/check_rules.py
```

该命令已经接入 `bash ~/.agents/harness/check-agent-home.sh`。

## 决策评测

runner 会把完整评测 prompt 写入子进程 stdin。命令必须从 stdin 读取用户 prompt，并只输出模型最终 JSON。

Claude 示例：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_evals.py -- \
  claude --bare -p --no-session-persistence --tools ''
```

Codex 示例：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_evals.py -- \
  codex exec --ephemeral --skip-git-repo-check -s read-only -m gpt-5.5 -
```

建议至少对计划编写实际使用的模型运行三次。通过标准：

- 所有 case 选择正确；
- 全面迁移 case 同时写出最终生产路径和旧路径删除项；
- 不使用“为了 minimal diff 保留旧 driver/runtime owner”等禁止理由；
- 明确分阶段 case 尊重用户指定边界，并给临时层写出退出条件；
- 三轮运行全部通过，避免偶然命中。

先用确定性 fixture 验证 runner 与评分器本身：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_evals.py -- \
  python3 ~/.agents/harness/prompt-evals/target-state-adoption/fake_decision_agent.py
```

fixture 通过只能证明决策评测工具链可运行，不能替代独立模型行为验证。

## Plan 生成评测

当前包含 10 个 plan 场景：GORM + pgx、Redux → Zustand、Jest → Vitest、AWS SDK v2 → v3、Express → Fastify、logrus → slog、MySQL → PostgreSQL、Compose → Kubernetes、用户明确分阶段的 GORM 迁移，以及范围模糊的 GORM 请求。

Claude 示例：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_plan_evals.py -- \
  claude --bare -p --no-session-persistence --tools ''
```

Codex 示例：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_plan_evals.py -- \
  codex exec --ephemeral --skip-git-repo-check -s read-only -m gpt-5.5 -
```

每轮输出保存到 `results/<timestamp>/`。评分器检查：

- 是否定义最终生产初始化/调用路径和 runtime owner；
- 是否覆盖 driver/provider、关键 adapter、事务或运行期边界；
- 全面迁移是否在“删除清单”中明确删除旧 imports、constructors、adapters、配置和依赖；
- 是否同时给出正向采用验收、负向旧路径清除证明和精确验证命令；
- 是否有失败恢复或回退方案；
- 明确分阶段时是否尊重本期边界并给临时层写出退出条件；
- 范围真正模糊时是否列出待确认决策和不同答案的架构影响。

先用确定性 fixture 验证 runner 与评分器本身：

```bash
python3 ~/.agents/harness/prompt-evals/target-state-adoption/run_plan_evals.py \
  --results-dir /tmp/target-state-plan-fixture -- \
  python3 ~/.agents/harness/prompt-evals/target-state-adoption/fake_plan_agent.py
```

fixture 通过只能证明评测工具链可运行，不能替代独立模型行为验证。目标模型仍应连续运行三轮；10 个场景全部通过，且人工抽查生成 plan 没有用同义表达绕过规则，才能标记行为 GREEN。

## 人机评测

机械正则无法可靠判断 agent 是否真的阅读了官方资料、引用是否支持结论、问题是否属于用户独有信息。因此这部分使用 [HUMAN_EVAL.md](./HUMAN_EVAL.md) 的 5 个对话场景人工检查。它覆盖：用户尚未准确界定问题时先生成研究问题定义、可查技术事实不得反问、用户不懂技术时必须解释并推荐、停机窗口等真实业务边界必须询问，以及用户已明确全面迁移时不得重复确认。

## 当前 RED 证据

2026-07-19 的真实 GORM 迁移计划在旧提示词下把“所有服务按 GORM 推荐方式改造”缩成“repository 使用 GORM，但保留 `sql.Open`、`lib/pq` 和旧 runtime owner”。其合理化理由是降低风险、避免同时迁移 driver、保持 minimal diff。该真实失败是本轮修改的 RED 基线。
