# entities/

业务实体层。定义项目中最稳定的核心数据模型。

## 职责

- 定义业务对象的 TypeScript 类型（interface / type）
- 提供纯函数工具（格式化、校验、计算派生字段）
- **不包含** API 调用、store 操作、UI 渲染逻辑

## 约定

- 按实体拆分子目录：`user/`、`post/`、`comment/`、`tag/` ...
- 每个实体目录下 `model/` 放类型定义和纯函数
- 类型导出通过 `index.ts` 统一再导出

## 示例

```ts
// entities/post/model/post.ts
export interface Post {
  id: string
  title: string
  content: string
  authorId: string
  createdAt: string
}

export function getPostSummary(post: Post, maxLength: number): string {
  return post.content.slice(0, maxLength) + '...'
}
```
