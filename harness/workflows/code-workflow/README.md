# code-workflow package

`code-workflow` 的实现只保存在这个全局目录，不向项目复制 workflow 脚本、模板或运行器。

## 入口

```bash
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> <command>
```

常用命令：

```bash
# 为项目准备 workflow 状态目录；不复制实现文件
bash ~/.agents/harness/workflow-installer.sh <repo-root> code-workflow

# 迁移旧版本：移除带 Managed by code-workflow package 标记的项目内副本
bash ~/.agents/harness/workflow-sync.sh <repo-root> code-workflow

# 检查全局运行时、任务状态目录和残留副本
bash ~/.agents/harness/workflow-sync-check.sh <repo-root> code-workflow

# 创建非琐碎任务的 worktree、计划和 startup gate
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> start <topic-or-slug>
```

## 项目边界

项目只保存自身事实和可变状态：

- `.arccgz-harness/state/session-gates/`：任务 startup gate 状态，默认 gitignore。
- `.arccgz-harness/`：项目文档、策略、检查与其他 harness 资产。
- `.arccgz-harness/harness/workflow-plugins/code-workflow/<stage>.d/*.sh`：可选的项目专属 stage 插件；初始化器不会预制或复制该目录。

共享实现（任务 intake、worktree 创建、startup gate、stage runner、归档、清理和计划模板）全部由本目录的 `workflow.sh` 与 `managed/` 运行。

## Stage 与 Review

共享 stage runner 支持 `pre-commit-quick`、`completion-full` 和 `workflow-governance`。如项目注册了可选插件，使用：

```bash
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> stage completion-full
```

`completion-full` 只提供实现上下文的验证证据。后续必须由独立 `code-reviewer` 执行真实 review gate，才进入 workflow-governance、归档和交付。

任务完成后：

```bash
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> archive
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> cleanup
```

startup gate 状态依次为 `active`、`ready_to_merge` 和终态 `archived`。独立 review 的交接协议见 `independent-review-protocol.md`。
