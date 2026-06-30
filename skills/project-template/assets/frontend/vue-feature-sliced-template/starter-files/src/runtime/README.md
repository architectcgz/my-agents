# runtime/

全局运行时基础设施。

## 职责

- HTTP 401 拦截 → 自动登出跳转
- Vue `app.config.errorHandler` → 未捕获异常的全局兜底
- Router `onError` → 路由错误的全局兜底
- 后续可扩展：性能监控、Sentry 上报、全局 loading 条

## 约定

- 在 `main.ts` 中通过 `setupGlobalErrorRuntime()` 一次性注册
- 各部分可独立替换：传入自定义 `ErrorRuntimeOptions` 覆盖默认行为
