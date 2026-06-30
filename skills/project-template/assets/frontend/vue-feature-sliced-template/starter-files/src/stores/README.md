# stores/

Pinia 客户端状态管理。

## 职责

- **只管理客户端 UI 状态**：认证身份、主题偏好、侧栏开合、通知面板状态
- **不管理服务端数据**：文章列表、评论、通知内容等服务端数据由 API + composable 管理

## 约定

- 每个 store 一个文件
- 使用 Setup Store 语法（`defineStore('name', () => { ... })`）
- 暴露 `readonly` 的 state，通过 action 函数修改
- 不要直接从 store 调用 API 获取列表数据

## 示例

```ts
// stores/theme.ts
export const useThemeStore = defineStore('theme', () => {
  const preference = ref<'light' | 'dark' | 'auto'>('auto')
  // ...
})
```
