# shared/ui

通用 UI 组件。项目内最原子的展示层。

## 职责

- 跨领域可复用的 UI 原语（按钮、输入框、卡片、弹窗、布局）
- 不包含业务语义（不清楚什么场景复用）
- 通过 props + slots 暴露所有定制点

## 与 widgets/ 的区别

| 维度 | shared/ui | widgets/ |
|---|---|---|
| 业务语义 | 无 | 强 |
| 复用范围 | 全项目 | 特定页面或模块 |
| 例子 | AppLayout、Button、Modal | PostListCard、UserProfileCard |
