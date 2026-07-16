import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "extract_sessions.py"
SPEC = importlib.util.spec_from_file_location("extract_sessions", SCRIPT_PATH)
extract_sessions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extract_sessions)


class CodexSessionExtractionTest(unittest.TestCase):
    def test_extracts_user_and_assistant_messages_from_codex_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp) / "rollout.jsonl"
            records = [
                {
                    "timestamp": "2026-07-15T04:00:00Z",
                    "type": "session_meta",
                    "payload": {"cwd": "D:\\projects\\Raven"},
                },
                {
                    "timestamp": "2026-07-15T04:00:01Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "developer",
                        "content": [{"type": "input_text", "text": "system instructions"}],
                    },
                },
                {
                    "timestamp": "2026-07-15T04:00:02Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "分析 Raven 项目"}],
                    },
                },
                {
                    "timestamp": "2026-07-15T04:00:03Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "已完成项目分析"}],
                    },
                },
            ]
            session.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

            project, events = extract_sessions.extract_codex_file(str(session), "2026-07-15")

        self.assertEqual(project, "D:\\projects\\Raven")
        self.assertEqual([(role, text) for _, role, text in events], [
            ("U", "分析 Raven 项目"),
            ("A", "已完成项目分析"),
        ])


class Utf8OutputTest(unittest.TestCase):
    def test_configures_reconfigurable_output_as_utf8(self):
        class Output:
            def __init__(self):
                self.kwargs = None

            def reconfigure(self, **kwargs):
                self.kwargs = kwargs

        output = Output()

        extract_sessions.configure_utf8_output(output)

        self.assertEqual(output.kwargs, {"encoding": "utf-8"})


if __name__ == "__main__":
    unittest.main()
