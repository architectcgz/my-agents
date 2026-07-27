# 可持续测试策略

## 目录

1. [目标与非目标](#目标与非目标)
2. [风险分级与测试节奏](#风险分级与测试节奏)
3. [测试层级与唯一 owner](#测试层级与唯一-owner)
4. [测试写法](#测试写法)
5. [Fake、Stub、Mock 与 Fixture](#fakestubmock-与-fixture)
6. [错误映射测试分层](#错误映射测试分层)
7. [真实基础设施测试](#真实基础设施测试)
8. [确定性、并发与时间](#确定性并发与时间)
9. [把测试纳入重构](#把测试纳入重构)
10. [规模与复用门槛](#规模与复用门槛)
11. [Coverage 策略](#coverage-策略)
12. [CI 与验证分层](#ci-与验证分层)
13. [从零初始化项目](#从零初始化项目)
14. [Review 清单](#review-清单)

## 目标与非目标

测试体系的目标是以可接受的维护成本保护重要行为、contract 和失败模式。

优先优化以下指标：

- 行为发生回归时，测试能否稳定失败。
- 失败信息能否定位到明确 contract 和 owner。
- 新增行为时，是否只需构造该用例真正需要的依赖。
- 测试能否在本地和 CI 中可重复执行。
- 删除、迁移或合并测试时，是否能证明信号没有丢失。

不要把以下数字设为单独成功条件：

- 测试代码必须少于生产代码。
- 所有包必须达到相同的覆盖率。
- 每个 production function 都必须有一个对应测试函数。
- 测试数量或断言数量持续增长。

测试/生产代码接近 `1:1` 或更高并不自动表示病态。真正的腐化信号通常是重复失败信号、巨型 fake、失焦 fixture、过度 mock、flaky、超长文件和慢到没人愿意运行的反馈循环。

## 风险分级与测试节奏

测试要求由行为风险、现有覆盖和回归价值决定，不由 diff 行数决定。

| 等级 | 常见场景 | 新增测试 | 是否要求先红 |
| --- | --- | --- | --- |
| R0 | 文档、注释、索引、纯展示文本或样式 | 不要求 | 否；执行结构、构建或视觉验证 |
| R1 | 无行为变化的重命名、移动、拆文件、fake 改写、机械重构 | 不强制 | 否；改前确认现有最窄测试为绿，改后重跑 |
| R2 | 小行为调整，且已有测试明确覆盖目标行为 | 不强制新增 | 否；指出覆盖来源并运行它 |
| R3 | 新 endpoint、use case、repository、错误码、字段 contract、权限或过滤 | 必须有 focused test | 推荐 test-first，但不为流程制造无意义红测 |
| R4 | Bugfix、事务、幂等、并发、worker、consumer、migration、数据一致性、安全边界 | 必须有回归或 contract test | 默认先写失败测试或 characterization test；无法先复现时说明原因 |

遵守以下边界：

- “不要求红测”不等于“不要求验证”。
- 机械重构中若顺带改变业务语义，立即按更高风险重新分类。
- 无法自动化验证时，记录手动输入、步骤、观察结果和无法自动化的原因。
- 用户或项目明确要求更严格 test-first 时遵守其要求。

## 测试层级与唯一 owner

先判断行为由哪一层拥有，再选择测试位置。

| 层级 | 主要证明 | 不应主要证明 |
| --- | --- | --- |
| Domain | 不变量、值对象、状态机、纯算法和领域拒绝 | HTTP envelope、数据库 driver 行为 |
| Application / use case | 权限、业务决策、事务编排、幂等、事件和跨端口副作用 | Router、JSON decode、ORM 内部实现 |
| Handler / transport | Path、method、请求解析、身份映射、公开错误 envelope 和响应 DTO | 全部业务分支和 repository 查询语义 |
| Repository | 查询过滤、约束、事务、锁、错误翻译和持久化结果 | Application 权限和 HTTP status |
| Adapter / client | Provider contract 适配、序列化、超时/错误翻译 | 调用方完整业务策略 |
| Worker / consumer | Claim、ack/nack、retry、dead、幂等、取消和恢复 | 无关 HTTP 行为 |
| System / E2E | 少量关键用户流程和真实依赖协作 | 每个边界值和每个 domain 分支 |
| Architecture / static | 依赖方向、禁止 import、目录或源码约束 | 运行时业务正确性 |

多层覆盖同一场景时，明确不同信号。例如：

- Mapper table 证明每个内部错误对应哪个公开 status/code。
- Handler test 证明 endpoint 使用了正确 mapper 和 operation。
- System test 证明部署后的外部 API 真实返回该 envelope。

如果三层只是复制同一组输入和断言，保留最合适 owner，删除重复信号。

## 测试写法

遵守以下规则：

- 让测试名描述 subject 和 observable behavior。
- 让一个测试只证明一个行为 contract 或一个失败信号。
- 对同一规则的多个输入使用 table test。
- 对不同权限、状态机、副作用、错误语义或 endpoint 使用独立测试。
- 优先断言返回结果、状态、持久化数据、事件、错误码和幂等效果。
- 只在顺序或次数本身是 contract 时断言调用顺序或次数。
- 让 helper 调用测试框架的 helper 标记能力，例如 Go 的 `t.Helper()`。
- 在失败信息中包含关键输入、实际结果和预期结果。
- 避免只断言“不报错”“非空”或“mock 被调用”。

新增测试前先做删除实验的心智检查：如果删除核心 production 分支，测试是否一定失败？如果仍会通过，测试信号过弱。

## Fake、Stub、Mock 与 Fixture

### 收窄消费方接口

让测试 double 贴近被测用例实际消费的能力。不要因为一个具体 repository 实现拥有许多方法，就让所有用例依赖同一个宽接口。

对 Go，优先声明 consumer-side interface：

```go
type CreateOrderRepository interface {
	Create(ctx context.Context, input CreateOrderInput) (OrderRecord, error)
}
```

同一个 PostgreSQL repository 可以实现多个窄接口；Runtime 可以把同一实例注入多个 use case。只有 production consumer 的字段或构造参数也改成窄接口时，测试成本才会真正下降。

### 使用函数字段式 fake

避免为每个方法维护 `calls/input/result/error` 四元组：

```go
type fakeCreateOrderRepository struct {
	createFn func(context.Context, CreateOrderInput) (OrderRecord, error)
}

func (f *fakeCreateOrderRepository) Create(
	ctx context.Context,
	input CreateOrderInput,
) (OrderRecord, error) {
	if f.createFn == nil {
		panic("unexpected Create call")
	}
	return f.createFn(ctx, input)
}
```

在测试闭包中只捕获当前 contract 需要的输入、次数或副作用。让未配置方法立即失败，不要静默返回零值。

### 处理可变输入

捕获以下值时按需要复制：

- slice
- map
- `[]byte`
- 指针指向的可变 struct
- 可复用 buffer

避免被测代码在调用后继续修改对象，使断言读取到别名后的新值。

### 控制 Fixture 扩张

- 少量数据直接内联。
- 同一文件重复两次后提取局部 builder / fixture。
- 多个测试文件稳定复用后提升到 package-local helper。
- 只有跨包复用且不携带业务规则时，才提升到共享 testkit。
- 不建立一个初始化所有 repository、client、clock、queue 和 cache 的“万能 fixture”。

### Mock 的边界

Mock 适合隔离昂贵、不可控或不属于当前 contract 的外部边界。不要用它替代当前层真正负责的语义：

- 不用 mock ORM 证明 SQL 和数据库约束。
- 不用 mock HTTP client 证明 provider 的真实 wire contract，除非另有 contract/integration test。
- 不只验证 mock 被调用；继续验证调用产生的业务结果。

## 错误映射测试分层

集中错误映射时，拆成三个 owner：

| Owner | 证明内容 |
| --- | --- |
| Mapping table | error + operation 到 status/code/message/details，包括 wrapped error 和 fallback |
| Error writer | 映射结果正确序列化成 envelope，details/trace 等字段不丢失 |
| Handler | endpoint 把 service error 交给正确 mapper/operation，并保留鉴权和解析边界 |

Mapping table 至少覆盖：

- 所有公开 sentinel 或 typed error。
- `errors.Is` / `errors.As` 可识别的 wrapped error。
- Operation-sensitive 分支。
- Validation details、truncated 和默认 validation error。
- Cancellation、deadline 和未知错误 fallback。

先建立集中 mapping / writer 证据，再删除 handler 中的重复对照表。只新增集中测试但保留所有重复测试，不算完成维护成本优化。

## 真实基础设施测试

Repository、migration 和 driver 语义优先用真实目标基础设施验证。

数据库测试应覆盖与改动相关的：

- 唯一约束、外键和 check constraint。
- 事务提交、rollback 和隔离语义。
- Lock、并发 claim 和条件更新。
- Nullable、JSON、array、time 和 numeric 映射。
- Empty result 和具体 driver/ORM 错误翻译。
- Migration `up`，以及可逆 migration 的 `down`。

使用 disposable database、container 或临时 schema。Schema owner 仍是正式 migration；测试 helper 可以建立隔离环境，但不能推动生产启动路径自动改 schema。

对 Redis、MQ、对象存储、搜索引擎和浏览器采用同一原则：单元测试用 fake 证明业务决策；只有真实协议、ack/retry、TTL、serialization、locking 或 rendering 行为重要时才增加 integration/runtime 测试。

## 确定性、并发与时间

保持测试可重复：

- 不使用固定 `sleep` 等待异步结果。
- 使用 channel、context、fake clock、hook、latch、eventually with deadline 或可观察状态。
- 随机测试固定 seed，并在失败信息中打印 seed。
- 不依赖测试执行顺序、共享全局状态或上一个测试留下的数据。
- 为 goroutine、worker、cache、共享 map 和并发状态运行 race detector 或等价工具。
- 为 parser、validator、decoder、协议输入和安全敏感输入增加 seed regression 或 focused fuzz test。

Flaky test 出现时：

1. 先复现并分类为 production race、测试同步缺陷、环境资源问题或外部依赖不稳定。
2. 修复 owner，而不是放宽断言或增加 sleep。
3. 如必须暂时 quarantine，记录 owner、原因、影响和退出条件。
4. 不把“自动重跑后通过”作为长期绿灯策略。

## 把测试纳入重构

红-绿后的 refactor 同时整理 production 和测试代码：

1. 合并同失败信号的输入例子。
2. 删除过时、重复或实现耦合的断言。
3. 把 fixture 留在最窄稳定 owner。
4. 拆分混合多个 endpoint、use case、query 或 worker concern 的文件。
5. 确认失败信息仍能定位关键 contract。

测试可以删除或合并的合法条件：

- 信号已由更合适层级接管。
- 行为 contract 已被明确删除。
- 测试只耦合实现细节且不再保护外部行为。
- 多个测试具有完全相同的失败信号。
- 测试已过时或持续产生无业务意义的噪声。

删除时说明替代 owner；不要只写“减少测试行数”。

## 规模与复用门槛

项目没有既有规则时，可用以下默认起点：

- 单个测试文件目标不超过 400 行。
- 单个测试文件超过 800 行设为机械失败。
- 单个测试函数目标不超过 80 行。
- 文件超过目标时，先按 endpoint、use case、repository query、worker behavior 或 fixture owner 拆分。
- 第一步优先移动顶层测试；不要立即进行跨包 testkit 大抽取。

这些数字是结构报警器，不是鼓励通过压缩可读性规避门禁。项目已有更合适门槛时遵守项目规则。

## Coverage 策略

Coverage 用于回答“哪些代码从未被执行”，不能单独回答“关键行为是否被保护”。

推荐：

- 观察 package、风险模块和 changed code 的趋势。
- 对安全、权限、事务、幂等和关键状态机维护显式场景清单。
- 如果设置 coverage floor，使用温和的报警阈值，避免为了数字测试 getter、setter 或 mock 调用。
- Review coverage 下降时先判断是否暴露真实盲区，再决定补测试。

不要把统一的全仓高覆盖率当成测试质量替代品。

## CI 与验证分层

建立快速反馈和高风险验证两层。

每个 PR 的快速门禁通常包括：

- 单元、application 和 handler tests。
- Static analysis、lint 和 architecture checks。
- Test file size 或重复结构 guard。
- 构建或类型检查。

按改动风险追加：

- Repository / migration integration tests。
- Race detector。
- Real broker/cache/storage runtime tests。
- 少量 system / E2E tests。
- Fuzz seed corpus 或 security regression。

Go 项目的入口可从以下命令演进：

```bash
go test ./...
go vet ./...
go test -race ./path/...
```

把昂贵测试拆成独立 job 时，确保高风险改动在合并前仍必须通过对应 job。不要因为慢就永久跳过最能证明真实 contract 的测试。

验证报告只列实际执行的命令和结果。区分：

- Passed
- Failed due to implementation
- Failed due to test harness
- Blocked by environment
- Not run and why

## 从零初始化项目

新项目至少建立以下基线：

1. 创建一份项目级测试策略，写明风险分级、测试层级、目录 owner 和验证命令。
2. 为 domain、application、transport、repository、system 和 architecture tests 约定落点。
3. 建立最窄测试命令和统一交付命令。
4. 为需要真实依赖的测试准备 disposable environment，而不是默认 mock 一切。
5. 约定 consumer-side interface、函数字段 fake 和 fixture 提升门槛。
6. 设置测试文件和函数规模 guard。
7. 规定 flaky test、skip/quarantine、测试删除和覆盖率下降的处理方式。
8. 让 CI 默认运行快速门禁，并按风险触发 integration、race、runtime 或 E2E。
9. 在 PR / review 模板中要求说明：行为变化、测试 owner、实际命令和未覆盖风险。
10. 在前十几个真实用例出现后复盘 fixture 和 fake 形状；不要在没有重复证据时提前设计万能 testkit。

最重要的初始化规则：把防腐机制写进项目文档和自动化门禁，不依赖团队长期记住口头约定。

## Review 清单

- [ ] 测试保护的是可观察行为或 contract，而不是实现细节。
- [ ] 行为有明确主要 owner，多层测试证明不同事实。
- [ ] 风险等级和 test-first 深度匹配。
- [ ] Bugfix、事务、幂等、并发、migration 和安全边界有回归证据。
- [ ] Table test 中的每一行属于同一条规则。
- [ ] Fake 未实现无关宽接口，未配置调用立即失败。
- [ ] Fixture 没有初始化大量无关依赖。
- [ ] Repository 关键语义由真实目标数据库证明。
- [ ] 没有固定 sleep、顺序依赖或隐藏 flaky 的自动重跑。
- [ ] 没有用 mock 调用断言替代业务结果断言。
- [ ] 删除或合并的测试有明确替代 owner。
- [ ] Coverage 没有被当成唯一质量指标。
- [ ] 已运行最窄充分验证，并准确报告结果和未覆盖风险。
