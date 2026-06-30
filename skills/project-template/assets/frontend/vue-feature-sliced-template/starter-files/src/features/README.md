# features/

业务流程层。每个 feature 是一个完整的用户动作或流程的 owner。

## 职责

- 管理业务流程的状态、校验、提交流程
- 可以调用 API、操作 Pinia store
- 一个 feature 解决一个具体业务问题（登录、发文章、评论、上传...）

## 约定

- 按业务领域拆分子目录：`auth/`、`post/`、`comment/`、`notification/` ...
- 每个 feature 下 `model/` 放核心逻辑（composable、状态机）
- 如果 feature 有自己的子组件，放 `ui/`
- 通过 `index.ts` 统一导出公开 API

## 示例

```ts
// features/auth/model/useLoginForm.ts
export function useLoginForm() {
  const router = useRouter()
  const authStore = useAuthStore()

  const username = ref('')
  const submitting = ref(false)

  async function submit() {
    const user = await login({ username: username.value, password: '...' })
    authStore.setAuth(user)
    await router.push('/')
  }

  return { username, submitting, submit }
}
```
