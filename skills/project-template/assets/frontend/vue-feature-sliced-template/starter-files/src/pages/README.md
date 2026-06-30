# pages/

路由装配面。每个文件对应一个路由，负责把 layout、widget、feature 拼成一个完整页面。

## 职责

- 接收路由参数（`useRoute`），按需调用 feature composable
- 组装 shared/ + features/ + widgets/，不包含可复用的业务逻辑
- 管理页面级的 loading / error / empty 状态展示

## 约定

- 文件名 `XxxRoutePage.vue` 或 `XxxPage.vue`
- 按路由命名空间拆分子目录（`auth/`、`dashboard/`、`error/` ...）
- 页面内部的复杂逻辑应抽到 `features/` 对应模块中
- 页面应处理三种状态：loading、error、empty

## 示例

```vue
<!-- pages/post/PostDetailRoutePage.vue -->
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { usePostDetail } from '@/features/post'

const route = useRoute()
const postId = route.params.id as string
const { post, isLoading, error } = usePostDetail(postId)
</script>
```
