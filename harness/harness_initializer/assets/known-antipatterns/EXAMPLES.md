# Known Antipatterns — Real Examples

## 硬约束

**这张表只能从真实失败里抄，不能凭空想象。**

每个反例必须包含：
- 真实的 before/after 代码
- 明确的为什么错、如何改
- 可追溯的来源（commit hash、PR、issue）

---

## 反模式目录

### 代码质量
- [过度设计：用户只要修 bug，Agent 加了无关改动](#过度设计用户只要修-bug-agent-加了无关改动)
- [过早抽象：一个用例就抽象成通用组件](#过早抽象一个用例就抽象成通用组件)

### 测试
- [测试锁定实现细节而非行为](#测试锁定实现细节而非行为)
- [前端测试只断言 class 名](#前端测试只断言-class-名)

### 架构
- [跨层重复 normalize/default/validate](#跨层重复-normalizedefaultvalidate)
- [frontend entities 反向依赖 features](#frontend-entities-反向依赖-features)

---

## 代码质量反模式

### 过度设计：用户只要修 bug，Agent 加了无关改动

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
修复登录按钮点击无响应的 bug
```

**❌ Before（违反 Surgical Changes）**：
```typescript
// 用户要求的修复 ✅
- 修复登录按钮事件绑定

// Agent 自己加的"改善" ❌
+ 添加 loading 状态显示
+ 添加按钮防抖
+ 添加错误重试逻辑
+ 添加日志记录
+ 重构按钮组件为通用组件
```

**为什么错**：
- 只有第一项是用户要求的
- loading、防抖、重试、日志、重构都是 Agent 自己加的
- 用户无法干净地"撤销最后一个功能"（因为混在一起了）

**✅ After（正确做法）**：
```typescript
// 只修复用户要求的
- 修复登录按钮事件绑定

// 其他"改善"应该：
// 1. 先问用户是否需要
// 2. 或者分成独立的 commit/PR
// 3. 或者完全不做（用户没要求）
```

**检验句**：
- 每一行改动都能追溯到用户的请求吗？ → **否**
- 如果用户说"撤销最后一个功能"，是否能干净删除？ → **否**

---

### 过早抽象：一个用例就抽象成通用组件

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
添加用户列表页面
```

**❌ Before（违反 Avoid Premature Abstraction）**：
```typescript
// 创建了"通用" DataTable 组件
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onSort?: (key: keyof T) => void;
  onFilter?: (filters: Record<string, any>) => void;
  onPaginate?: (page: number) => void;
  loading?: boolean;
  error?: Error;
  // ... 30 行接口定义
}

// 创建了"通用" usePagination hook
// 创建了"通用" useFilter hook

// 只有一个用例：用户列表
```

**为什么错**：
- 只有一个用例（用户列表），但抽象了"通用"组件
- 接口比要解决的问题更复杂
- 通用接口有 30 行，但用户列表只用了 5 行

**✅ After（正确做法）**：
```typescript
// 第一个用例：直接实现，不抽象
<table>
  <thead>...</thead>
  <tbody>
    {users.map(user => <tr>...</tr>)}
  </tbody>
</table>

// 第二个用例：仍然直接实现，寻找共同点

// 第三个用例：现在有 3 个实例，可以抽象了
// 提取真正共同的部分（通常比第一次想象的简单得多）
```

**检验句**：
- 这个抽象是为几个用例设计的？ → **1 个**（过早）
- 这个接口是否比它要解决的问题更复杂？ → **是**

---

## 测试反模式

### 测试锁定实现细节而非行为

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
测试用户登录功能
```

**❌ Before（锁定实现细节）**：
```typescript
test('login flow', () => {
  const spy = vi.spyOn(authService, 'login')

  render(<LoginForm />)
  fireEvent.input(emailInput, 'user@example.com')
  fireEvent.input(passwordInput, 'password123')
  fireEvent.click(submitButton)

  // 测试实现细节：调用了哪个函数
  expect(spy).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'password123'
  })

  // 测试实现细节：内部状态
  expect(component.state.isLoading).toBe(true)
})
```

**为什么错**：
- 测试关心"调用了 authService.login"（实现）
- 测试关心"isLoading 状态"（实现）
- 重构内部实现时测试会失败，即使行为没变

**✅ After（测试行为）**：
```typescript
test('successful login redirects to dashboard', async () => {
  // Mock API 响应
  server.use(
    http.post('/api/login', () => {
      return HttpResponse.json({ token: 'abc123' })
    })
  )

  render(<LoginForm />)

  // 用户行为
  await userEvent.type(screen.getByLabelText('Email'), 'user@example.com')
  await userEvent.type(screen.getByLabelText('Password'), 'password123')
  await userEvent.click(screen.getByRole('button', { name: 'Login' }))

  // 验证结果：用户看到什么
  await waitFor(() => {
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
```

**检验句**：
- 这个测试是在验证行为还是在验证实现？ → **行为**
- 重构内部实现后，测试是否仍然通过？ → **是**

---

### 前端测试只断言 class 名

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
测试按钮组件
```

**❌ Before（锁定 class 名）**：
```typescript
test('button has correct classes', () => {
  const { container } = render(<Button variant="primary">Click</Button>)

  expect(container.firstChild).toHaveClass('btn')
  expect(container.firstChild).toHaveClass('btn-primary')
  expect(container.firstChild).toHaveClass('px-4')
  expect(container.firstChild).toHaveClass('py-2')
  expect(container.firstChild).toHaveClass('rounded-md')
})
```

**为什么错**：
- 测试只证明"源码里包含这些 class"
- 改用不同的 CSS 方案（Tailwind → CSS Modules）时测试全炸
- 没有测试任何用户可见的行为

**✅ After（测试行为和可见状态）**：
```typescript
test('primary button is visually distinct and clickable', async () => {
  const handleClick = vi.fn()
  render(<Button variant="primary" onClick={handleClick}>Click</Button>)

  const button = screen.getByRole('button', { name: 'Click' })

  // 测试用户可见的行为
  await userEvent.click(button)
  expect(handleClick).toHaveBeenCalledOnce()

  // 如果需要测试样式，测试计算后的样式
  expect(button).toHaveStyle({
    backgroundColor: 'rgb(59, 130, 246)', // primary color
  })
})
```

**检验句**：
- 这个测试是否只锁定 class 名/markup 细节？ → **否**
- 改用不同的 CSS 方案后，测试是否仍然有效？ → **是**

---

## 架构反模式

### 跨层重复 normalize/default/validate

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
实现分页查询 API
```

**❌ Before（跨层重复）**：
```go
// Handler 层
func (h *Handler) ListUsers(c *gin.Context) {
  page := c.DefaultQuery("page", "1")  // normalize + default
  pageNum, _ := strconv.Atoi(page)
  if pageNum < 1 { pageNum = 1 }       // validate + default

  users, _ := h.service.ListUsers(pageNum, 10)
  c.JSON(200, users)
}

// Service 层
func (s *Service) ListUsers(page, pageSize int) ([]User, error) {
  if page < 1 { page = 1 }            // 重复 validate + default
  if pageSize < 1 { pageSize = 10 }   // 重复 validate + default

  return s.repo.ListUsers(page, pageSize)
}

// Repository 层
func (r *Repo) ListUsers(page, pageSize int) ([]User, error) {
  if page < 1 { page = 1 }            // 重复 validate + default
  if pageSize < 1 { pageSize = 10 }   // 重复 validate + default

  offset := (page - 1) * pageSize
  // ...
}
```

**为什么错**：
- 同一个语义（"page 至少为 1"）在三层都重复
- 不是"安全兜底"，是"没有明确 owner"
- 修改默认值时需要改三个地方

**✅ After（单一 owner）**：
```go
// Handler 层：负责 normalize + default + validate
func (h *Handler) ListUsers(c *gin.Context) {
  req, err := parseListUsersRequest(c)  // 唯一 owner
  if err != nil {
    c.JSON(400, gin.H{"error": err.Error()})
    return
  }

  users, _ := h.service.ListUsers(req)
  c.JSON(200, users)
}

func parseListUsersRequest(c *gin.Context) (*ListUsersRequest, error) {
  page := c.DefaultQuery("page", "1")
  pageNum, err := strconv.Atoi(page)
  if err != nil || pageNum < 1 {
    return nil, errors.New("invalid page")
  }

  return &ListUsersRequest{Page: pageNum, PageSize: 10}, nil
}

// Service 层：只接收已验证的请求
func (s *Service) ListUsers(req *ListUsersRequest) ([]User, error) {
  // 不需要重复校验，req 已经是有效的
  return s.repo.ListUsers(req.Page, req.PageSize)
}

// Repository 层：只接收已验证的参数
func (r *Repo) ListUsers(page, pageSize int) ([]User, error) {
  // 不需要重复校验，参数已经是有效的
  offset := (page - 1) * pageSize
  // ...
}
```

**检验句**：
- 这个 normalize/default/validate 逻辑是在唯一 owner 层吗？ → **是**
- 改默认值时需要改几个地方？ → **1 个**

---

### frontend entities 反向依赖 features

**来源**：[填写 commit hash 或 PR 链接]

**用户请求**：
```
在用户列表中显示用户卡片
```

**❌ Before（反向依赖）**：
```typescript
// entities/user/ui/UserCard.vue
<script setup>
import { useRouter } from 'vue-router'
import { useUserActions } from '@/features/user-management/composables'

// entities 依赖了 features 的具体实现
const router = useRouter()
const { deleteUser, editUser } = useUserActions()

const handleEdit = () => {
  router.push(`/users/${props.user.id}/edit`)  // 知道具体路由
}
</script>
```

**为什么错**：
- `entities/user` 应该只表达"用户是什么"
- 现在它知道了"用户管理功能的路由"和"用户管理功能的操作"
- 反向依赖：entities → features（违反依赖方向）

**✅ After（正确的依赖方向）**：
```typescript
// entities/user/ui/UserCard.vue
<script setup>
// entities 不知道具体的 features
// 只暴露事件，由 features 决定如何处理
const emit = defineEmits<{
  edit: [userId: string]
  delete: [userId: string]
}>()
</script>

<template>
  <div class="user-card">
    <span>{{ user.name }}</span>
    <button @click="emit('edit', user.id)">Edit</button>
    <button @click="emit('delete', user.id)">Delete</button>
  </div>
</template>

// features/user-management/ui/UserListPage.vue
<script setup>
import UserCard from '@/entities/user/ui/UserCard.vue'
import { useRouter } from 'vue-router'
import { useDeleteUser } from '../api'

// features 决定如何处理 entities 的事件
const router = useRouter()
const { mutate: deleteUser } = useDeleteUser()

const handleEdit = (userId: string) => {
  router.push(`/users/${userId}/edit`)
}
</script>

<template>
  <UserCard
    v-for="user in users"
    :key="user.id"
    :user="user"
    @edit="handleEdit"
    @delete="deleteUser"
  />
</template>
```

**检验句**：
- `entities/*` 中的内容是否反向依赖了具体 feature？ → **否**
- 依赖方向是否是 features → entities？ → **是**

---

## 如何使用这个文件

### 1. 踩到坑时立即记录

```bash
# 创建新的反例条目
# 格式：### [简短标题]
# 必填：来源（commit hash/PR）、before/after、为什么错、检验句
```

### 2. 定期回顾

```bash
# 每月回顾 feedback/aar/，提取高频反模式
grep -h "## 新发现的坑" feedback/aar/*.md | sort | uniq -c | sort -rn
```

### 3. 集成到 skills

高频反模式应该：
- 更新对应 skill 的 SKILL.md
- 添加到 Red Flags 表
- 添加到检验句清单

### 4. 集成到 code review

code reviewer 可以引用这个文件：
```markdown
这个改动违反了 [Known Antipattern: 过度设计](#过度设计)
```

---

## 贡献指南

### 添加新反例的标准

1. **必须是真实失败**
   - 有 commit hash、PR 或 issue 可追溯
   - 不能是"理论上可能出错"

2. **必须有 before/after 代码**
   - Before：真实的错误代码
   - After：正确的修复代码
   - 不能只有文字描述

3. **必须说明为什么错**
   - 不是"不符合最佳实践"
   - 而是"导致了具体问题 X"

4. **必须有检验句**
   - 提供可验证的检查点
   - 让 Agent 在生成后能真的去问

### 反例质量检查清单

- [ ] 有可追溯的来源（commit hash/PR/issue）
- [ ] 有真实的 before/after 代码
- [ ] 说明了为什么错（具体问题，不是抽象原则）
- [ ] 提供了检验句（Agent 可以真的去检查）
- [ ] 归类到正确的章节

---

## 统计

- **总反例数**：[自动更新]
- **最近添加**：[自动更新]
- **最高频反模式**：[从 AAR 中统计]
