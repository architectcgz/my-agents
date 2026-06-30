# api/

后端 API 适配器层。

## 职责

- 封装 HTTP 请求（基于 `src/api/request.ts` 提供的 Axios 实例）
- 定义每个 API 方法的入参、返回值类型
- 处理请求参数序列化与响应数据提取

## 约定

- 按业务领域拆分文件（`auth.ts`、`post.ts`、`comment.ts` ...）
- 每个模块导出一个类或一组函数
- 不在这里做数据规范化，规范化逻辑放在 API 调用方或专用 adapter 中
- 不在这里管理请求状态（loading / error），状态管理交给调用方 composable

## 示例

```ts
// api/post.ts
import { getAxiosInstance } from './request'
import type { Post } from '@/entities/post'

export async function getPost(id: string): Promise<Post> {
  const res = await getAxiosInstance().get<Post>(`/posts/${id}`)
  return res.data
}
```
