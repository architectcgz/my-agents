# router/

Vue Router 配置。路由定义 + 全局守卫。

## 结构

- `index.ts`：创建 router 实例，组装所有路由模块
- `guards.ts`：全局导航守卫（认证、权限、标题）
- `routes/`：按命名空间拆分的路由定义（`authRoutes.ts`、`errorRoutes.ts` ...）

## 约定

- 所有路由使用 `() => import(...)` 懒加载
- 需要认证的路由设置 `meta.requiresAuth: true`
- 新增路由模块后在路由数组统一注册
