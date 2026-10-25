import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.config import Settings
from app.schemas import EventType, TraceEvent
from app.trace_store import TraceStore


class ApiEvaluationTests(unittest.TestCase):
    def test_evaluate_endpoint_keeps_existing_trace_store(self) -> None:
        from app import api

        with tempfile.TemporaryDirectory() as tmp:
            main_db = str(Path(tmp) / "main.sqlite3")
            main_store = TraceStore(main_db)
            main_store.append(
                TraceEvent(
                    run_id="existing-run",
                    event_type=EventType.RUN_START,
                    name="run.started",
                )
            )
            with mock.patch.object(api, "settings", Settings(trace_db_path=main_db)), \
                    mock.patch.object(api, "store", main_store):
                result = api.evaluate()
                remaining = main_store.list_runs()
        self.assertEqual(result["summary"]["total_runs"], 6)
        self.assertEqual([run["run_id"] for run in remaining], ["existing-run"])


if __name__ == "__main__":
    unittest.main()
