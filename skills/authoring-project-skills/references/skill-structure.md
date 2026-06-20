# Skill Structure

Read this file when deciding a skill's shape (single file vs folder) and how its SKILL.md routes.

## 从单文件起步

最小的 skill 就是一个 `SKILL.md` + 几条行为准则,没有 `rules/`、`workflows/`、`references/`。
不要一上来就摆全套目录 —— 每个子目录只放一两行占位符,反而维护成本更高。

设计结构前先回答三问:
- 这个 skill 有多少个不同主题的内容?(少于 3 → 单文件够)
- 绑定了多少种任务流程?(没有 → 不需要 `workflows/`)
- 预期会随项目持续演进更新吗?(不会 → 不需要自演化机制)

三个都"否" → 单文件就是最优解。**结构服务于内容,不用结构撑完整性。**

## 文件夹化的信号

出现以下任意一条,单文件就该裂成文件夹:
- 多主题:SKILL.md 开始出现"### X 相关""### Y 相关"分节。
- 任务路由:不同任务要读不同规则(加 Controller 和修 bug 读的不是同一套)。
- 需要沉淀教训:同一个坑第二次踩,但没有地方记录。
- 多人协作 / 多项目复用:规则开始有变体,需要分文件管理。

> 2000 行的 SKILL.md 不是"内容丰富",是 Agent 每次都要读完整本书。

## 三类内容严格分离(按形式决定去处)

- **"你必须做 X"(指令性)** → `rules/`
- **"小心 X"(警告性)** → `references/gotchas.md`(或对应 reference)
- **第 1 步、第 2 步(流程性)** → `workflows/`

迷茫时自问:
- "我能做 X 吗?" → rules
- "这个坑怎么避?" → references
- "我现在该做什么?" → workflows

会话历史 / 调试过程 **不进 skill**,用 git / CHANGELOG(见 `progressive-disclosure-and-evolution.md` 防日记本)。

## SKILL.md 是导航中心,不是百科

SKILL.md 应当很短(**≤100 行**),只告诉 Agent **读什么 / 什么时候读**。核心板块:

- **Always Read** —— 每次任务都读的 2–3 个文件(只放"任何任务都必须遵守"的通用约束;
  领域特定规则不放这,交给 Common Tasks 路由)。
- **Common Tasks** —— 按任务类型路由,每条列**精确文件路径**;控制在 5–10 条,超出按领域分组;
  必须有 "Other / unlisted task" 兜底条目;多子任务任务指向 subagent workflow。
- **Known Gotchas** —— 最高价值板块,一句话 + 锚点指向 references 详情。
- **Core Principles / ✓Check** —— 项目特有原则,每条带可执行检验。

多文件 skill 实践:用一张 **Reference Map 路由表**(`任务涉及 → 读哪个 reference`)代替散落的
soft pointer,让 Agent 命中后再按需读对应文件。

## 文件大小是信号不是命令

单个文件过大不可避免会让 Agent 读不到正确内容,所以超标要触发**评估**是否拆分;
但同一模块的内容即使超过参考行数也不应硬拆。行数是信号,不是自动拆分命令。
(评估式拆分 / 合并标准见 `progressive-disclosure-and-evolution.md`。)
