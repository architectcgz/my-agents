# widgets/

页面级组合块。将 entities、features、shared 中的内容组合成有业务含义的大块 UI。

## 职责

- 组装多个底层组件或数据源，产出一个完整的功能区块
- 可跨页面复用（如在首页和分类页都展示"热门文章"）
- 有自己的 loading / error / empty 状态处理

## 与 shared/ui 的区别

| 维度 | shared/ui | widgets/ |
|---|---|---|
| 业务语义 | 无 | 强，有明确业务含义 |
| 复用范围 | 全项目 | 特定页面或模块 |
| 例子 | Button、Modal、AppLayout | PostListCard、UserProfileCard |

## 示例

```vue
<!-- widgets/post/PostListWidget.vue -->
<script setup lang="ts">
import { usePosts } from '@/features/post'
import PostCard from '@/shared/ui/PostCard.vue'

const { posts, isLoading } = usePosts()
</script>

<template>
  <div class="post-list" v-if="!isLoading">
    <PostCard v-for="p in posts" :key="p.id" :post="p" />
  </div>
</template>
```
