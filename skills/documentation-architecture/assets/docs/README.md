# 文档索引

本目录是项目文档入口，负责指向当前事实源，并区分长期事实和过程历史。

## 阅读顺序

1. 先读 `docs/documentation-rules.md`，确认文档归属、放置位置和路径登记规则。
2. 通过本索引找到相关当前事实源。
3. 目标文档区域存在父级索引时，继续读取最近父级索引。
4. 更新当前文档前，用代码、contract、配置、测试或运维记录核对事实。
5. 过程证据应和当前事实分开；只有稳定结论被提升到事实源文档后，才作为当前事实引用。

## 当前事实源

- `docs/requirements/`：产品需求、范围、验收标准和约束。
- `docs/contracts/`：API、event、data 和兼容性 contract。
- `docs/spec/`：实施计划前的可执行功能规格。
- `docs/design/`：尚未成为当前架构事实的产品和 UX 设计。
- `docs/architecture/`：当前系统设计和长期技术约束。
- `docs/operations/`：runbook、部署说明、维护命令和运维验证。

## 流程和历史

- `docs/plan/`：实施、迁移、发布和重构计划。
- `docs/reviews/`：review 证据和发现；正式轮次应绑定 commit 或等价不可变 artifact，并以独立 `round-<n>` 文件保存。
- `docs/reports/`：限时报告、调查总结和状态快照。
- `docs/todo/`：可执行 backlog、清理队列和未解决工作。
- `docs/improvements/`：agent 发现的改进项和提升状态。
- `docs/refs/`：外部参考和研究笔记。

## 陈旧文档规则

- 当前事实源地图中链接的文档，必须匹配代码，或明确标注为草案、已废弃或历史记录。
- 过程文档形成稳定决策后，把稳定结论移动到 requirements、contracts、architecture 或 operations。
- 新增长期路径时，在 `docs/documentation-rules.md` 和本索引或最近父级索引登记。
