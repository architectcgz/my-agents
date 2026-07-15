#!/usr/bin/env python3
"""从 Claude Code 的 session 历史中提取指定日期的对话，供日报总结使用。

用法:
  python extract_sessions.py --date 2026-07-13 [--projects-dir DIR] [--out FILE]

行为:
- 遍历 <projects-dir> 下所有项目子目录里的 *.jsonl（每个项目一个子目录，
  目录名是被编码过的工作区路径，如 D--projects）。
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
from datetime import datetime, timezone

# 用户消息里这些前缀/子串属于工具或框架噪音，不代表真实工作意图，过滤掉
USER_NOISE_MARKERS = (
    "Base directory for this skill",  # skill 注入
    "tool_result",
    "<command-name>",
    "<local-command",
    "[Request interrupted",
)


def text_of(content):
    """把 message.content（可能是 str 或 content-block 列表）折叠成纯文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
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


def extract_file(path, target_date):
    """从单个 jsonl 中提取属于 target_date 的 user/assistant 文本事件。"""
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
                    if t.startswith("<") or any(k in t for k in USER_NOISE_MARKERS):
                        continue
                    events.append((ts_raw, "U", t[:600]))
                elif role == "assistant":
                    events.append((ts_raw, "A", t[:600]))
    except Exception:
        return []
    return events


def default_projects_dir():
    """默认 ~/.claude/projects。"""
    return os.path.join(os.path.expanduser("~"), ".claude", "projects")


def main():
    ap = argparse.ArgumentParser(description="提取指定日期的 Claude session 对话")
    ap.add_argument("--date", required=True, help="目标本地日期 YYYY-MM-DD")
    ap.add_argument("--projects-dir", default=None,
                    help="Claude projects 根目录，默认 ~/.claude/projects")
    ap.add_argument("--out", default=None, help="输出文件路径；缺省则打印到 stdout")
    args = ap.parse_args()

    pdir = args.projects_dir or default_projects_dir()
    if not os.path.isdir(pdir):
        raise SystemExit(f"projects 目录不存在: {pdir}")

    # 每个项目一个子目录；也兼容根目录直接散落 jsonl 的情况
    project_dirs = [d for d in glob.glob(os.path.join(pdir, "*")) if os.path.isdir(d)]
    project_dirs.append(pdir)

    out_lines = []
    total_events = 0
    for proj in sorted(set(project_dirs)):
        proj_name = os.path.basename(proj.rstrip("/\\")) or proj
        files = glob.glob(os.path.join(proj, "*.jsonl"))
        proj_events = []  # (ts, role, text, session_basename)
        for f in sorted(files):
            evs = extract_file(f, args.date)
            for ts, role, t in evs:
                proj_events.append((ts, role, t, os.path.basename(f)))
        if not proj_events:
            continue
        proj_events.sort(key=lambda x: x[0])
        total_events += len(proj_events)
        out_lines.append("=" * 90)
        out_lines.append(f"PROJECT: {proj_name}  events={len(proj_events)}")
        out_lines.append("=" * 90)
        last_session = None
        for ts, role, t, sess in proj_events:
            if sess != last_session:
                out_lines.append(f"\n--- session {sess} ---")
                last_session = sess
            out_lines.append(f"[{role} {local_hhmmss(ts)}] {t}")
            out_lines.append("")

    header = [
        f"# 提取结果  date={args.date}  projects_dir={pdir}",
        f"# 命中项目数={sum(1 for _ in out_lines if _.startswith('PROJECT:'))}  事件总数={total_events}",
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
