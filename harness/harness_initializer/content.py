#!/usr/bin/env python3
"""Harness initializer content template compatibility exports."""

from __future__ import annotations

from .content_core import (
    todo_reminder_script,
    todo_governance_check_script,
    skill_sync_reminder_script,
    agent_entrypoints_check_script,
    script_guard_policy_content,
    script_guard_check_script,
    architecture_guard_paths_policy,
    architecture_guard_commands_policy,
    test_workflow_check_script,
    architecture_guard_script,
    commit_message_policy_content,
    commit_message_check_script,
)

from .content_hooks import post_tooluse_aar_hook_script

from .content_aar import (
    aar_hook_readme,
    aar_example,
    aar_directory_readme,
)

from .content_antipatterns import (
    known_antipatterns_examples,
    known_antipatterns_readme,
)

from .content_trigger_rate import (
    test_trigger_rate_script,
    test_trigger_rate_readme,
)

__all__ = [
    "todo_reminder_script",
    "todo_governance_check_script",
    "skill_sync_reminder_script",
    "agent_entrypoints_check_script",
    "script_guard_policy_content",
    "script_guard_check_script",
    "architecture_guard_paths_policy",
    "architecture_guard_commands_policy",
    "test_workflow_check_script",
    "architecture_guard_script",
    "commit_message_policy_content",
    "commit_message_check_script",
    "post_tooluse_aar_hook_script",
    "aar_hook_readme",
    "aar_example",
    "aar_directory_readme",
    "known_antipatterns_examples",
    "known_antipatterns_readme",
    "test_trigger_rate_script",
    "test_trigger_rate_readme",
]
