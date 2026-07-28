# Go 中间件 / 装饰器模式

## 概述

中间件（Middleware）是 Go 中常见的装饰器模式实现，用于为函数或方法添加横切关注点（日志、超时、重试、panic 恢复等），而不修改原始业务逻辑。

核心形式：**一个函数接收一个 Handler，返回一个包裹了额外行为的新 Handler。**

```go
type Middleware func(Handler) Handler
type Handler func(ctx context.Context) error
```

## 洋葱模型

多个中间件组合后形成洋葱（Onion）模型——从外到内包裹，从内到外返回：

```
Chain(A, B, C)(handler)
```

```
A                ← 最外层
│
B                ← 中间层
│
C                ← 内层
│
handler          ← 原始 handler
```

执行顺序：

```
A 进入 → B 进入 → C 进入 → handler → C 返回 → B 返回 → A 返回
```

**每一层在调用 `next(ctx)` 前执行前置逻辑，在 `next(ctx)` 返回后执行后置逻辑。**

## 完整示例

以下是一个 Go 调度器中的中间件实现，包含了三种典型的中间件：

### 类型定义

```go
// Middleware 装饰器模式：接收一个 JobHandler，返回包裹了额外行为的新 JobHandler。
type Middleware func(JobHandler) JobHandler

// JobHandler 是 job 的核心类型——一个接收 context 并返回 error 的函数。
type JobHandler func(ctx context.Context) error
```

### Chain：组合多个中间件

```go
// Chain 将多个中间件组合成一个，从左到右排列，从外到内包裹。
// 使用 slices.Backward 倒序遍历，确保第一个中间件在最外层。
func Chain(middlewares ...Middleware) Middleware {
    return func(handler JobHandler) JobHandler {
        // 倒序遍历：[A, B, C] → C 先包 → B 再包 → A 最后包
        // 结果：A(B(C(handler)))
        for _, middleware := range slices.Backward(middlewares) {
            handler = middleware(handler)
        }
        return handler
    }
}
```

### Logging：执行日志

```go
// Logging 在 job 执行前后插入日志。
//
// 三层嵌套对应三个职责：
//   Logging(logger)               → 返回 Middleware（工厂）
//     return func(next JobHandler) → 返回 JobHandler（装饰器）
//       return func(ctx) error   ← 这就是 JobHandler 的具体值
func Logging(logger Logger) Middleware {
    return func(next JobHandler) JobHandler {
        return func(ctx context.Context) error {
            jobName := getJobName(ctx)
            start := time.Now()

            logger.Info("Job started", "job", jobName)

            err := next(ctx)
            duration := time.Since(start)

            if err != nil {
                logger.Error("Job failed", "job", jobName, "duration", duration, "error", err)
            } else {
                logger.Info("Job completed", "job", jobName, "duration", duration)
            }

            return err  // 透传 error，不吞掉
        }
    }
}
```

### Recovery：panic 恢复

```go
// Recovery 通过 defer/recover 捕获下游 handler 的 panic，转换成 error 返回，
// 防止单个 job panic 导致整个进程崩溃。
func Recovery(onPanic func(jobName string, recovered interface{})) Middleware {
    return func(next JobHandler) JobHandler {
        return func(ctx context.Context) (err error) {
            defer func() {
                if r := recover(); r != nil {
                    jobName := getJobName(ctx)
                    if onPanic != nil {
                        onPanic(jobName, r)   // 告警或指标上报
                    }
                    err = errors.Errorf("job %q panicked: %v", jobName, r)
                }
            }()
            return next(ctx)
        }
    }
}
```

### Timeout：超时控制

```go
// Timeout 使用 context.WithTimeout 为 job 设置超时上限。
func Timeout(duration time.Duration) Middleware {
    return func(next JobHandler) JobHandler {
        return func(ctx context.Context) error {
            ctx, cancel := context.WithTimeout(ctx, duration)
            defer cancel()

            done := make(chan error, 1)
            go func() {
                done <- next(ctx)
            }()

            select {
            case err := <-done:
                return err              // 正常完成
            case <-ctx.Done():
                return errors.Errorf("job %q timed out after %v", getJobName(ctx), duration)
            }
        }
    }
}
```

### 组合使用

```go
handler := Chain(
    Recovery(onPanic),
    Logging(logger),
    Timeout(5*time.Minute),
)(myJob)

handler(ctx)
```

## 关键设计点

| 要点 | 说明 |
|---|---|
| **`next(ctx)` 前后分离** | 中间件的核心——调用 `next` 前做前置逻辑，调用后做后置逻辑 |
| **透传返回值** | 中间件不应吞掉 handler 的返回值，除非有明确的语义理由 |
| **工厂 + 装饰器 + Handler** | 三层嵌套：外层工厂接收依赖，中层装饰器接收 `next`，内层是实际执行逻辑 |
| **执行顺序 vs 声明顺序** | 第一个声明的中间件在最外层（最后执行），最后一个在最内层（最先执行） |
| **context 传参** | job 元数据（如名称）通过 context 传递，不依赖全局状态 |

## 适用场景

- **日志**：执行前记录开始，执行后记录耗时和结果
- **超时**：为 handler 设置执行时限
- **重试**：失败时自动重试
- **panic 恢复**：防止单个任务崩溃导致整个进程退出
- **指标**：记录执行次数、耗时分布
- **鉴权/限流**：执行前检查权限或配额
- **事务**：为 handler 包裹数据库事务

## 与 HTTP 中间件的类比

这和 Gin、Chi、echo 等 HTTP 框架的中间件是同一个模式：

```go
// HTTP 框架中的中间件形式
type Middleware func(Context)        // 类比：接收 Context，不返回（写入响应）
type HandlerFunc func(Context)

// 调度器中的中间件形式
type Middleware func(JobHandler) JobHandler       // 装饰器模式
type JobHandler func(ctx context.Context) error
```

区别只在于 Handler 签名和是否必须返回 error，结构完全一致。

## 对比其他模式

| 模式 | 形式 | 特点 |
|---|---|---|
| **装饰器/中间件** | `func(Handler) Handler` | 组合横切关注点，洋葱模型 |
| **职责链** | 每个 handler 决定是否传给下一个 | 可中断，过滤链 |
| **管道** | `func(ctx, input) (output, error)` | 数据转换，无包裹关系 |
| **插件** | 通过接口回调 | 松耦合但类型擦除 |
