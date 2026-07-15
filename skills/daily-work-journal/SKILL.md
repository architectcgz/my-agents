---
name: daily-work-journal
description: >
  Use when the user wants to init a daily work folder / journal, or asks to
  summarize today's (or a given day's) work from Claude Code session history.
  Two commands — `init` creates the date folder plus empty work.md template and
  summary.md; `summary` extracts that day's sessions across all projects under
  ~/.claude/projects and fills summary.md. Triggers include phrases like
  "初始化日报 / 建今天的工作文件夹 / init 日期文件夹" and
  "总结今天的工作 / 从 session 总结 / 生成日报".
---

# Daily Work Journal（每日工作日报）

管理按日期归档的工作日报。两条命令:`init` 建当天目录与文件骨架;`summary` 从 Claude session 历史里还原当天工作并写入 summary。

## 目录与命名约定

- **base 目录**:默认 `D:\daily-work\`。用户指定了别的根目录就用用户的。
- **日期文件夹**:`M-D`(月-日,不补零),如 `7-13`、`12-5`。
- **两个文件**(前缀用 `M.D`):
  - `M.D-work.md` — 当天工作**计划/意图**,由用户手写,`init` 只生成空模板(可预填「承接昨日」)。
  - `M.D-summary.md` — 当天工作**总结**,由 `summary` 命令从 session 填充,并对照 `work.md` 收口。

例:2026-07-13 → `D:\daily-work\7-13\7.13-work.md` + `7.13-summary.md`。

日期默认取**本机今天**。用户可显式指定某一天(如"总结 7-12 的工作"),则用户日期优先。

---

## 命令一:init（生成日期文件夹 + 文件骨架）

目标:为目标日期创建 `M-D/` 目录、空的 `work.md` 模板、空的 `summary.md`。

步骤:
1. 确定 base 目录(默认 `D:\daily-work\`)和目标日期(默认本机今天)。
2. 若 `base/M-D/` 不存在则创建。
3. **不覆盖已存在文件**。若 `M.D-work.md` / `M.D-summary.md` 已存在且非空,保留原内容,只报告并跳过;仅对缺失或空文件写入骨架。
4. `M.D-work.md` 写入空模板(见下),`M.D-summary.md` 创建为空文件(留给 `summary` 填)。
5. **预填「承接昨日」(best-effort)**:找上一个有 `M.D-summary.md` 的日期(通常是前一天),把它「遗留 / 待办」小节里未完成的条目,誊抄到今天 `work.md` 的「承接昨日」下,每条尾部标注来源日期(如 `(来自 7.13)`)。找不到上一天 summary、或该小节为空时,保留空占位,不要编造。
   - **去重**:若某条本质是"缺依赖 / 缺权限 / 等他人 / 等运维"这类不靠自己就能推进的事项,归到「阻塞 / 待协调」而非「承接昨日」,同一条不要两处都放。「承接昨日」只留靠自己能推进的待办。
6. 报告创建了哪些、跳过了哪些、承接了几条。

`M.D-work.md` 模板(标题日期替换成实际日期):

```markdown
# M.D 工作计划

## 今日目标
<!-- 按优先级排,一条 = 一个可交付结果;用 [ ] 便于晚上对照勾稽 -->
- [ ]

## 承接昨日
<!-- 上一天 summary「遗留 / 待办」的延续;init 可自动预填 -->
-

## 阻塞 / 待协调
<!-- 卡在哪、缺什么、需要谁(缺依赖 / 缺权限 / 等他人 / 等运维);不写进「今日目标」 -->
-

## 备注
-
```

> 分区意图:`今日目标` 是今天要产出的**可交付结果**;`承接昨日` 让上一天的尾巴自然流进来;`阻塞 / 待协调` 专门收纳"不是我一个人能推进"的事项(缺依赖、缺权限、等他人),避免这类内容和真实进展混在一起。

---

## 命令二:summary（从 session 总结当天工作）

目标:扫描当天**所有项目**的 Claude session,还原做了什么,写入 `M.D-summary.md`。

### 为什么用提取脚本
session 是 `~/.claude/projects/<编码后的工作区路径>/*.jsonl`,量大、含大量工具噪音,直接 `cat` 会因 GBK/UTF-8 混编在终端显示乱码。用配套脚本可靠解析:按**本地日期**过滤(timestamp 是 UTC,脚本已转本地时区,避免凌晨工作错分到前一天)、跨所有项目目录聚合、剔除工具结果/命令回显/skill 注入,输出干净的 UTF-8 中间文件。

### 步骤

1. **确定日期与 base 目录**。默认本机今天;用户指定则用用户的。

2. **确保目标目录存在**。若 `base/M-D/` 不存在,先按 `init` 建好(至少建目录和空 summary)。

3. **跑提取脚本**,把当天所有项目的对话导出到临时中间文件:
   ```bash
   python ~/.agents/skills/daily-work-journal/scripts/extract_sessions.py \
     --date <YYYY-MM-DD> --out "<base>/M-D/_sessions_dump.txt"
   ```
   - `--date` 用 ISO 格式(如 `2026-07-13`),不是 `M-D`。
   - 需要覆盖 projects 根目录时加 `--projects-dir`。
   - 脚本会打印命中项目数与事件总数。若为 0,说明当天无 session,如实告知用户,不要编造。

4. **读中间文件并归纳**。用 Read 读 `_sessions_dump.txt`(UTF-8,不会乱码)。按主题/项目归并成结构化中文总结,而非流水账。建议结构:
   - **总体成果**(3~5 条):当天最值得说的产出,动词匹配真实完成度。
   - **按项目 / 主题分节**:每个项目/主题一节,写清具体改动、决策、提交/分支/MR、验证到哪一步。
   - **阻塞 / 待协调进展**:对照 `work.md`「阻塞 / 待协调」,写今天有没有推进、是否解除、是否仍卡着(缺依赖/权限/等他人)。
   - **遗留 / 待办**:今天没做完、明确推迟或新冒出来的事项。这一节是**下一天 `work.md`「承接昨日」的数据源**,尽量每条自包含(带上下文、路径、编号),别只写"继续 xxx"。

5. **写入 `M.D-summary.md`,并与 `work.md` 收口**。开头注明"依据当天 Claude session 历史还原"。若同目录已有 `M.D-work.md` 且用户写了计划:
   - 对照「今日目标」逐条标注完成度(✅ 完成 / ⏳ 进行中 / ❌ 未做 / ➕ 计划外新增),形成「对照工作计划」小节。
   - 对照「阻塞 / 待协调」,标注每条是否解除。
   - 计划里没有、但 session 里确实做了的事,单独列为计划外产出,不要硬塞进原计划条目。

6. **清理中间文件**:删除 `_sessions_dump.txt`。

7. 报告:总结了几个项目、几条 session、写到哪个文件。

### 总结质量要求(与全局规范一致)

- **不夸大**:session 里明确"未执行/未验证/被打断"的事,总结里如实标注,不要写成已完成。动词匹配真实完成度(参照 `committing-changes` 的措辞范围约束)。
- **不臆造**:只写 session 里有据可查的内容。提取结果为空就说没有,不要脑补。
- **区分意图与产出**:`[U]` 是用户意图,`[A]` 是实际操作/结论;以实际产出为准,别把"计划要做"写成"已做"。
- **保留关键事实**:提交号、分支、MR 编号、文件路径、决策项、遗留 todo 等具体信息尽量保留。

---

## 边界与安全

- `init` / `summary` 都**不覆盖**用户已写的非空 `work.md`。
- session 历史可能含敏感信息(密钥、内网地址);总结时按 key 名引用,不誊抄密钥明文。
- base 目录、日期歧义时才问用户;其余按默认(本机今天 + `D:\daily-work\`)直接执行。
