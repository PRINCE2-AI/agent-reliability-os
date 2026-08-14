import tempfile
import unittest
from pathlib import Path

from app.demo_agent import run_demo_suite


class DemoSuiteTests(unittest.TestCase):
    def test_demo_suite_outputs_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_demo_suite(str(Path(tmp) / "demo.sqlite3"))
        self.assertEqual(result["summary"]["total_runs"], 6)
        self.assertGreaterEqual(result["summary"]["protected_blocks"], 2)
        self.assertEqual(result["summary"]["avg_protected_policy_coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
