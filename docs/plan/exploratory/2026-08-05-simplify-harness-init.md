# Harness 初始化精简实施计划

**目标：** 将新项目 harness 初始化收缩为基础导航和文档骨架；检查脚本、项目 hooks 与共享 `code-workflow` 改为显式启用，并清理已发现项目中的旧空壳。

**架构：** `harness/init-project.sh` 负责 CLI 选项和 workflow 选择，`harness/harness-initializer.py` 负责项目骨架与入口文件，`harness_initializer/profile_*` 负责 default / strict-reference 文档。检查脚本及 hooks 继续保留在全局模板中，由 `--with-checks` 生成；默认路径不再复制或接入它们。

**成功标准：**

- 不带额外选项运行 `init-project.sh` 时，不生成 `.arccgz-harness/scripts/checks/`、`.arccgz-harness/scripts/hooks/`、`.arccgz-harness/scripts/tests/`、`.githooks/`，也不默认同步 workflow。
- `--with-checks` 仍能生成检查脚本和 hooks；`--workflow <name>` 才同步共享 workflow；`--full-check` 显式启用 checks 并执行完整检查。
- 默认生成的 `AGENTS.md`、strict-reference 文档和 README 不引用默认不存在的检查入口或已关闭的 workflow。
- `OmniParser`、`Raven`、`sz-metaclaw-admin` 中的旧空壳 hooks、hook 配置和 Raven 的嵌套空目录被清理；现有业务文档、项目 policy、state 和未提交业务改动保持不变。
- 初始化器测试覆盖默认最小模式与显式 checks 模式；运行 shell 语法检查、针对性测试和最终路径盘点。

**约束：** 不删除已有项目的业务 harness 文档、反馈、state、reuse policy 或项目自有脚本；脏工作区中的无关改动不暂存、不提交。全局检查模板保留为显式选项，不在本次删除。

**测试立场：** Regression / mechanical migration。

**状态：** 已完成（2026-08-05）。

## 文件

- 新增：`docs/plan/exploratory/2026-08-05-simplify-harness-init.md`
- 修改：`docs/README.md`
- 修改：`harness/init-project.sh`
- 修改：`harness/harness-initializer.py`
- 修改：`harness/harness_initializer/app.py`
- 修改：`harness/harness_initializer/scaffold.py`
- 修改：`harness/harness_initializer/profile_common.py`
- 修改：`harness/harness_initializer/profile_default.py`
- 修改：`harness/harness_initializer/profile_strict.py`
- 修改：`harness/harness_initializer/docs_content.py`
- 修改：`harness/tests/test-init-project-defaults.sh`
- 修改：`README.md`
- 修改：`skills/harness-engineering/SKILL.md`
- 清理：`D:/projects/OmniParser/.githooks/`
- 清理：`D:/projects/Raven/.githooks/`、`D:/projects/Raven/.arccgz-harness/.arccgz-harness/`
- 清理：`D:/projects/sz-metaclaw-admin/.githooks/`

## 任务

### 任务 1：收缩初始化默认路径

**状态：** 已完成。

**意图：** 让默认初始化只建立项目级 harness 基础结构和 `CLAUDE.md -> AGENTS.md` 入口。

**做法：** 为初始化器增加 `with_checks` 参数；仅在显式开启时写入 checks、hooks、tests、相关 policy、AAR hook 和 Git hook 接入。默认 workflow 改为跳过，`--workflow` 显式启用；同步调整生成文档和 `.gitignore` managed block。

**验收：** 默认路径不产生检查/hook/workflow；显式选项仍保留原能力；生成文档没有悬空命令。

### 任务 2：更新模板与回归测试

**状态：** 已完成。

**意图：** 让 default / strict-reference 两种 profile 的文档、路由和测试反映新的默认边界。

**做法：** 移除默认路由对 `code-workflow`、`harness-router`、`test-driven-development` 和 check 命令的硬编码；在 strict-reference 的检查说明中标明可选；扩展初始化测试覆盖默认与 `--with-checks`。

**验收：** 模板生成结果与 CLI 行为一致，测试能区分默认最小模式和显式 checks 模式。

### 任务 3：清理已有项目残留

**状态：** 已完成。

**意图：** 删除已初始化项目中不再承担功能的空壳 hooks 和旧配置，同时保留业务 harness 资料。

**做法：** 仅处理盘点出的 `.githooks`、空 checks/hooks/tests 目录、Raven 嵌套空目录和本地 `core.hooksPath`；不触碰未提交业务文件和项目自有 harness policy。

**验收：** 三个项目不再启用 `.githooks`，目标残留路径不存在，业务 harness 内容仍在。

## 验证

- 运行 `bash -n harness/init-project.sh`。
- 运行 `python -m compileall -q harness/harness-initializer.py harness/harness_initializer`。
- 运行 `bash harness/tests/test-init-project-defaults.sh`。
- 对默认、`--with-checks` 和 strict-reference 临时仓库检查生成路径、Git hook 配置与默认文档路由。
- 对 `--full-check` 分支确认其会启用 checks、hooks 并调用完整一致性检查；当前 Windows/WSL 环境执行完整检查时，既有 `harness/checks/check-project-agent-entrypoints.sh` 的 CRLF 造成 Bash 兼容性错误，未将该 smoke 计为通过。
- 盘点三个已有项目的目标残留路径，并分别检查 Git 工作区状态。
