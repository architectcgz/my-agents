---
name: python-naming
description: Use when choosing, reviewing, or refactoring Python package, module, class, function, variable, constant, exception, protocol, adapter, parser, provider, coordinator, or test names; especially when deciding whether a generic suffix such as Service, Manager, Handler, or Util matches the real ownership boundary.
---

# Python Naming

在新增或重命名 Python 标识符前，先读取仓库的 `AGENTS.md`、现有模块命名和目标目录边界；本 skill 提供默认规则，项目已有稳定约定优先。

## 基础规则

| 对象 | 默认命名 | 示例 |
| --- | --- | --- |
| 包、模块、测试文件 | 小写 `snake_case`；保持短且表达领域 | `file_parser.py`、`test_file_parser.py` |
| 类、异常、类型别名 | `CapWords`；异常以 `Error` 或 `Exception` 结尾 | `DocumentPipeline`、`ParseError` |
| 函数、方法、变量 | 小写 `snake_case`；动作使用动词开头 | `parse_batch()`、`source_name` |
| 布尔值 | `is_`、`has_`、`can_`、`should_`、`enable_` 等可读前缀 | `is_ready`、`enable_chart` |
| 模块级常量 | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE_MB` |
| 私有实现 | 单下划线前缀；仅 Python 特殊协议使用双下划线 | `_parse_pdf()`、`__enter__()` |

遵循 PEP 8 的包/模块、类、函数/变量和常量命名规则；不要为了形式统一破坏仓库已有的稳定缩写。缩写应在同一项目内保持一种写法，例如不要在 `BaiduOcr`、`BaiduOCR` 之间来回切换。

## 按职责选类名

- `Parser`：拥有一种格式或解析能力，并把输入变成解析结果，例如 `FileParser`、`PdfParser`。
- `Coordinator`：协调多个 parser、provider、limiter 或结果步骤；跨文件编排优先使用它，例如 `FileParsingCoordinator`。
- `Router`：只负责按类型或策略分派，不承担完整业务流程。
- `Pipeline`：表达有明确阶段顺序的处理链，例如 `DocumentPipeline`。
- `Source` / `Fetcher`：把外部输入物化为本地文件或输入对象，不负责解析，例如 `MultipartUploadSource`、`S3FileFetcher`。
- `Provider`：封装一个外部能力或厂商 API，例如 `BaiduOcr`；provider 不决定上层 fallback 策略。
- `Assembler`：按稳定规则合并或组装结果；`Limiter`：拥有资源准入或并发闸门。

不要默认使用 `Service`、`Manager`、`Handler`、`Util`、`Helper` 或 `Common`。只有在框架/外部 contract 已固定名称，或对象确实是无法用更具体角色命名的应用服务边界时才保留；应在代码注释或计划中说明原因。不要仅通过改名掩盖职责过宽，先判断是否需要拆分模块。

## 决策检查

1. 类名是否能说明它拥有的能力或协调的对象？如果只能说“处理服务”，继续找更具体的名词。
2. 模块名是否能表达主要 owner？不要用 `utils.py` 或把多个边界塞入一个泛化模块。
3. 方法名是否表达动作和输入粒度？批处理用 `parse_batch`、`fetch_many` 等明确后缀。
4. 缩写、私有前缀和复数形式是否与相邻代码一致？搜索同目录调用方和导出名后再改名。
5. 改名是否会改变导入路径、配置键、序列化字段或外部 API？若会，先记录兼容边界，不把语法命名问题误当成行为重构。

## 本项目落地提示

- `main.py` 这类组合根保留入口语义；跨 REST/MCP 的解析编排使用 `FileParsingCoordinator`，不要新增泛化的 `FileParsingService`。
- `DocumentPipeline` 继续表示结构化 PDF/图片的阶段链；`InnerExecutor` 继续表示单文件内部的分片并发与合并。
- `BaiduOcr` 只表示 OCR provider；“结构化失败后调用通用解析”属于 coordinator 或 fallback policy，不属于 OCR provider。
- 结果排序和跨文件汇总可由 `ResultAssembler` 拥有；协议顶层 JSON 仍由 `http_server.py` / `mcp_server.py` 序列化。

参考：PEP 8 的 [Naming Conventions](https://peps.python.org/pep-0008/)，尤其是 Package and Module Names、Class Names、Function and Variable Names 和 Constants 小节。
