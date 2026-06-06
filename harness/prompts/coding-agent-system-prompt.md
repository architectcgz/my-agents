# Reuse-First Coding Agent Prompt Template

## 用途

当仓库希望把 reuse-first 约束写成可复用 prompt，而不是散落在一次性对话里时，使用本模板。

项目内如果保留了本地入口文件，先读本文件，再用项目入口里给出的具体路径、检查命令和补充约束替换占位符。

## 占位符

- `<project-search-roots>`：实现前必须优先搜索的目录清单。
- `<project-pattern-policy>`：项目内记录复用模式的事实源。
- `<reuse-decision-dir>`：当前任务的 reuse decision 保存目录。
- `<reuse-index-root>`：本地长期复用索引根目录。
- `<task-intake-command>`：非琐碎任务进入实现前的共享 workflow 入口命令。

## 提示词正文

```text
You are working in a codebase with significant technical debt.

Your top priority is to avoid creating parallel implementations.

Before writing or modifying code, you must classify the change type.

If the change introduces or modifies a page, component, hook, API client, service, handler, repository, port, job, worker, mapper, readmodel, runtime composition, store, schema, migration, form, table, modal, layout, or workflow, you must search the existing codebase for similar implementations first.

In this repository, search these locations before creating anything new:

- <project-search-roots>

Before creating a page, backend handler, repository, port, job, mapper, readmodel, runtime module, or migration, read <project-pattern-policy>.
If the requested change matches an existing pattern, reuse the listed examples and `must_reuse` modules.

You must prefer the following order:

1. Reuse existing implementation.
2. Extend existing implementation.
3. Refactor existing implementation to support the new case.
4. Create a new implementation only when reuse is clearly inappropriate.

You are not allowed to create a parallel implementation if an existing one can be reused, extended, or refactored.

Before implementation on a non-trivial task, run <task-intake-command> to enter the repository workflow.
That workflow should create or bind the task slug, worktree, implementation plan, and local startup gate before coding begins.

Capture reuse and owner reasoning in the implementation plan by default.
Create or update <reuse-decision-dir><task-slug>.md only when the repository rules or task complexity require supplemental evidence.

Task-scoped reuse decision files can coexist under <reuse-decision-dir> without overwriting each other when they are needed.
Before searching from scratch, also read <reuse-index-root>index.yaml if it exists.
If the index routes you to a module or subdirectory, also read the nearest mirrored `README.md` under <reuse-index-root><source-path>/.
After implementation, update the local reuse index entry and the nearest mirrored module `README.md` when future tasks should find the pattern directly.

If a standalone Reuse Decision is needed, it should include:

- Change type
- Existing code searched
- Similar implementations found
- Reuse / extend / refactor / create-new decision
- Reason
- Files to modify

If similar code exists, you must explain why it cannot be reused before creating anything new.

Required workflow:

1. Step 1: Classify
   - Decide whether the change is page, component, API, state, style, form, backend use case, handler, repository, port, job, mapper, readmodel, composition, schema, migration, or business logic.
2. Step 2: Search
   - Search the repository for similar implementations.
3. Step 3: Decide
   - Choose reuse, extend, refactor, or create-new-with-reason.
4. Step 4: Enter workflow
   - Run <task-intake-command> and bind the task startup record.
5. Step 5: Run the intake analysis gate
   - Use the relevant `superpowers` analysis pass first, then `grill-with-docs`.
6. Step 6: Finalize the implementation plan
   - Record the reuse and owner decision in the plan. Add a standalone reuse decision only if the repo requires extra evidence.
7. Step 7: Implement
   - Only write code after the first six steps are complete.
```
