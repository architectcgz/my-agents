#!/usr/bin/env python3
"""从 Claude Code 与 Codex 的 session 历史中提取指定日期的对话，供日报总结使用。

用法:
  python extract_sessions.py --date 2026-07-13 [--projects-dir DIR]
      [--codex-sessions-dir DIR] [--out FILE]

行为:
- 遍历 Claude <projects-dir> 下所有项目子目录里的 *.jsonl。
- 遍历 Codex <codex-sessions-dir> 下的 rollout JSONL，并按 session 的 cwd 分组。
- 按消息的顶层 timestamp（UTC）转换到本机本地时区后，筛出属于目标日期的消息。
- 只保留 user / assistant 的文本内容，跳过工具结果、命令回显、skill 注入等噪音。
- 按项目分组、按时间排序输出 UTF-8 文本，供上层 agent 阅读并归纳。

设计要点:
- 日期按“本机本地日期”判断（timestamp 是 UTC，带 Z，需先转本地再取 date），
  避免把凌晨的工作错分到前一天。
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

# 用户消息里这些前缀/子串属于工具或框架噪音，不代表真实工作意图，过滤掉
USER_NOISE_MARKERS = (
    "Base directory for this skill",  # skill 注入
    "tool_result",
    "<command-name>",
    "<local-command",
    "[Request interrupted",
    "# AGENTS.md instructions",
    "<skill>",
)


def text_of(content):
    """把 message.content（可能是 str 或 content-block 列表）折叠成纯文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") in ("text", "input_text", "output_text"):
                parts.append(c.get("text", ""))
        return "\n".join(parts)
    return ""


def local_date_of(ts_raw):
    """把 ISO8601（UTC，带 Z）时间戳转成本机本地日期字符串 YYYY-MM-DD。"""
    if not ts_raw:
        return None
    try:
        # Python 3.11+ 的 fromisoformat 支持 Z；旧版做个兜底替换
        try:
            dt = datetime.fromisoformat(ts_raw)
        except ValueError:
            dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d")
    except Exception:
        return None


def local_hhmmss(ts_raw):
    try:
        try:
            dt = datetime.fromisoformat(ts_raw)
        except ValueError:
            dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%H:%M:%S")
    except Exception:
        return "??:??:??"


def is_user_noise(text):
    return text.startswith("<") or any(marker in text for marker in USER_NOISE_MARKERS)


def extract_claude_file(path, target_date):
    """从单个 Claude JSONL 中提取属于 target_date 的 user/assistant 文本事件。"""
    events = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("type") not in ("user", "assistant"):
                    continue
                ts_raw = r.get("timestamp", "")
                if local_date_of(ts_raw) != target_date:
                    continue
                m = r.get("message", {})
                role = m.get("role")
                t = text_of(m.get("content")).strip()
                if not t:
                    continue
                if role == "user":
                    if is_user_noise(t):
                        continue
                    events.append((ts_raw, "U", t[:600]))
                elif role == "assistant":
                    events.append((ts_raw, "A", t[:600]))
    except Exception:
        return []
    return events


def extract_codex_file(path, target_date):
    """提取单个 Codex rollout JSONL，并读取 session cwd 作为项目归属。"""
    events = []
    project = "Codex"
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    continue

                payload = record.get("payload", {})
                if record.get("type") == "session_meta":
                    project = payload.get("cwd") or project
                    continue
                if record.get("type") != "response_item" or payload.get("type") != "message":
                    continue

                ts_raw = record.get("timestamp", "")
                if local_date_of(ts_raw) != target_date:
                    continue
                role = payload.get("role")
                text = text_of(payload.get("content")).strip()
                if not text:
                    continue
                if role == "user":
                    if is_user_noise(text):
                        continue
                    events.append((ts_raw, "U", text[:600]))
                elif role == "assistant":
                    events.append((ts_raw, "A", text[:600]))
    except Exception:
        return project, []
    return project, events


def default_projects_dir():
    """默认 ~/.claude/projects。"""
    return os.path.join(os.path.expanduser("~"), ".claude", "projects")


def configure_utf8_output(output):
    """让 Windows 控制台或管道稳定输出会话中的 Unicode 文本。"""
    reconfigure = getattr(output, "reconfigure", None)
    if reconfigure:
        reconfigure(encoding="utf-8")


def default_codex_sessions_dir():
    """默认 ~/.codex/sessions。"""
    return os.path.join(os.path.expanduser("~"), ".codex", "sessions")


def collect_claude_projects(projects_dir, target_date):
    """按 Claude 项目目录汇总当日事件。"""
    if not os.path.isdir(projects_dir):
        return {}
    project_dirs = [d for d in glob.glob(os.path.join(projects_dir, "*")) if os.path.isdir(d)]
    project_dirs.append(projects_dir)
    projects = {}
    for project_dir in sorted(set(project_dirs)):
        project_name = os.path.basename(project_dir.rstrip("/\\")) or project_dir
        events = []
        for file_path in sorted(glob.glob(os.path.join(project_dir, "*.jsonl"))):
            for timestamp, role, text in extract_claude_file(file_path, target_date):
                events.append((timestamp, role, text, os.path.basename(file_path)))
        if events:
            projects[project_name] = events
    return projects


def collect_codex_projects(sessions_dir, target_date):
    """按 Codex session cwd 汇总当日事件，递归扫描以覆盖跨午夜的会话文件。"""
    if not os.path.isdir(sessions_dir):
        return {}
    projects = {}
    for file_path in sorted(glob.glob(os.path.join(sessions_dir, "**", "*.jsonl"), recursive=True)):
        project, events = extract_codex_file(file_path, target_date)
        if not events:
            continue
        bucket = projects.setdefault(project, [])
        for timestamp, role, text in events:
            bucket.append((timestamp, role, text, os.path.basename(file_path)))
    return projects


def main():
    configure_utf8_output(sys.stdout)
    ap = argparse.ArgumentParser(description="提取指定日期的 Claude Code 与 Codex session 对话")
    ap.add_argument("--date", required=True, help="目标本地日期 YYYY-MM-DD")
    ap.add_argument("--projects-dir", default=None,
                    help="Claude projects 根目录，默认 ~/.claude/projects")
    ap.add_argument("--codex-sessions-dir", default=None,
                    help="Codex sessions 根目录，默认 ~/.codex/sessions")
    ap.add_argument("--out", default=None, help="输出文件路径；缺省则打印到 stdout")
    args = ap.parse_args()

    claude_dir = args.projects_dir or default_projects_dir()
    codex_dir = args.codex_sessions_dir or default_codex_sessions_dir()
    claude_projects = collect_claude_projects(claude_dir, args.date)
    codex_projects = collect_codex_projects(codex_dir, args.date)
    if not claude_projects and not codex_projects:
        raise SystemExit(
            f"未找到当天 session: Claude={claude_dir}; Codex={codex_dir}")

    out_lines = []
    total_events = 0
    project_count = 0
    for source, projects in (("Claude Code", claude_projects), ("Codex", codex_projects)):
        for project_name, project_events in sorted(projects.items()):
            project_events.sort(key=lambda item: item[0])
            total_events += len(project_events)
            project_count += 1
            out_lines.append("=" * 90)
            out_lines.append(
                f"SOURCE: {source}  PROJECT: {project_name}  events={len(project_events)}")
            out_lines.append("=" * 90)
            last_session = None
            for timestamp, role, text, session_name in project_events:
                if session_name != last_session:
                    out_lines.append(f"\n--- session {session_name} ---")
                    last_session = session_name
                out_lines.append(f"[{role} {local_hhmmss(timestamp)}] {text}")
                out_lines.append("")

    header = [
        f"# 提取结果  date={args.date}",
        f"# Claude projects_dir={claude_dir}",
        f"# Codex sessions_dir={codex_dir}",
        f"# 命中项目数={project_count}  事件总数={total_events}",
        "# 说明: [U]=用户消息(工作意图), [A]=助手回复(操作/结论)。仅供总结阅读，非最终产物。",
        "",
    ]
    result = "\n".join(header + out_lines)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(result)
        print(f"OK 提取 {total_events} 条事件 -> {args.out}")
    else:
        print(result)


if __name__ == "__main__":
    main()
