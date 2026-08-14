import tempfile
import unittest
from pathlib import Path

from app.demo_agent import DemoAgent, SCENARIOS
from app.trace_store import TraceStore


class EvaluatorTests(unittest.TestCase):
    def test_protected_run_has_policy_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TraceStore(str(Path(tmp) / "trace.sqlite3"))
            result = DemoAgent(store).run(SCENARIOS[1], mode="protected")
        self.assertEqual(result["evaluation"]["policy_coverage"], 1.0)
        self.assertEqual(result["status"], "blocked")


    def test_baseline_risky_run_has_higher_tool_misuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TraceStore(str(Path(tmp) / "trace.sqlite3"))
            result = DemoAgent(store).run(SCENARIOS[1], mode="baseline")
        self.assertEqual(result["status"], "completed")
        self.assertGreater(result["evaluation"]["tool_misuse_risk"], 0)


if __name__ == "__main__":
    unittest.main()
