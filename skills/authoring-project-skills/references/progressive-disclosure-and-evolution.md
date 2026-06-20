# Progressive Disclosure and Self-Evolution

Read this file when deciding what loads into context up front, and how a skill captures / prunes lessons over time.

## 三级渐进式加载(Progressive Disclosure)

矛盾:信息越多越好,但 context 窗口有限。解法 —— 分层,只把"始终需要"的放顶层:
1. **第 1 级**:`description`(触发判断)。
2. **第 2 级**:SKILL.md 正文(导航 + Always Read)。
3. **第 3 级**:`references/*.md`、`workflows/*.md`,Agent 命中后**按需**读。

只读当前任务相关的引用文件,不要把所有内容塞进 context。
Context 三个常见病:太少(看不到规范) / 太大(后面指令被静默忽略) / 混乱(无关信息干扰判断)。

## 激活优于存储

一个坑点仅记录在 `references/` 里**不算捕获**。高代价坑必须同时:
- **存储**在正确文件里;
- **激活**在会触发它的任务路径上(SKILL.md 的 Known Gotchas / workflow 的完成检查 / rules 摘要)。

判断:"下次 Agent 走正常任务路径时,会自然读到这条经验吗?" 不会 → 只是"记下来了",还没"生效"。

坑点的最佳平衡:**SKILL.md 一句话 + 锚点**,详情在 references。全放 SKILL.md 会变坑点百科,
全放 references 又会让 Agent 在任务路径上看不到。

## 录入标准(Recording Threshold,2/3)

不是所有发现都值得记。录入前过三问,至少中 2 条:
- **可重复?**(会再次出现,不是一次性)
- **代价高?**(不提前知道会浪费大量时间)
- **代码不可见?**(光看代码看不出来,如时序 / 注册顺序依赖)

通过的典型:框架生命周期坑、隐藏的注册顺序依赖、非显而易见的同步 / 状态重置、跨层交互陷阱。
不通过的典型:一次性 workaround、看代码就懂的事、轻微风格偏好、官方文档已充分覆盖的内容。

## 泛化规则(Generalization)

记录的内容必须脱离当前项目上下文也能看懂:
`具体发现 → 抽象为通用 pattern → 说明不遵守的后果`。不要抄会话叙事。

## 录入位置表

| 内容类型 | 目标位置 |
|---|---|
| 稳定约束 / 通用原则 | `rules/` |
| 陷阱、架构笔记、生命周期坑 | `references/` |
| 有序步骤 / 完成检查清单 | `workflows/` |
| 会话历史 / 调试过程 | **不要写进 skill** —— 用 git / CHANGELOG |

录入格式选最轻的:一句话 bullet → 加一小段到现有文件 → 新文件(通常不需要)。

## 防日记本(文件边界)

不要让 Agent 把"记录教训"扩成"把会话存档"。`references/2026-xx-xx-session-notes.md`
这类整份删除 —— 每行都是项目叙事,不是规则 / 流程 / 可复用坑点。真要会话日志放 `docs/`,不放 `references/`。

## 规则清退与自维护

只增不减的规则会变屎山。错误被纠正后:先搜索是否已有规则 → 分类根因:
- 规则缺失 → 过录入标准后新增。
- 规则过时 → **直接更新**(过时规则比缺失规则更有害,无需门槛)。
- 规则废弃 → 走清退(相关技术已移除直接删;迁移中加作用域标注;不确定加 `<!-- DEPRECATED: reason, date -->` 保留一个周期)。
- 规则没被遵循 → 检查醒目度(可能要从 references 上浮到 SKILL.md Known Gotchas 或薄壳)。

评估式拆分(文件超标):话题可分离? 导航困难? 拆后各部分能独立? 三个都 Yes 才拆。
评估式合并(碎片过多):话题相关? 合并后更好找? 合并后不超标? 三个都 Yes 才合并。
