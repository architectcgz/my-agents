# __tests__/

跨切面架构级测试。

## 职责

- 只放架构边界、设计系统 guard、跨领域回归防线
- 无法归属到单一 feature / page / shared owner 的测试

## 约定

- 新增测试文件之前必须能说明为什么不能贴近具体 owner 目录
- 大多数测试应放在对应 owner 目录的 `__tests__/` 中，而非这里
