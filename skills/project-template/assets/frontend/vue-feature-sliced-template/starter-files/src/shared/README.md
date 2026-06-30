# shared/

通用共享层。放置与项目业务解耦的纯工具性代码。

## 职责

- 通用 UI 组件（按钮、输入框、弹窗、布局壳等纯展示组件）
- 基础工具函数（不与业务绑定的格式化、校验）
- 通用 TypeScript 类型、枚举、常量

## 约定

- `shared/` 不能依赖 `features/`、`widgets/`、`pages/`、`entities/` 中的任何代码
- 所有 `shared/` 中的代码在任意层都可以引用

## 目录

- `shared/ui/`：通用 UI 组件
- `shared/lib/`：通用工具函数（按需创建）
