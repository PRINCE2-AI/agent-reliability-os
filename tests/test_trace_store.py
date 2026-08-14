import tempfile
import unittest
from pathlib import Path

from app.schemas import EventType, TraceEvent
from app.trace_store import TraceStore


class TraceStoreTests(unittest.TestCase):
    def test_trace_store_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TraceStore(str(Path(tmp) / "trace.sqlite3"))
            event = TraceEvent(run_id="run-1", event_type=EventType.RUN_START, name="start")
            store.append(event)
            events = store.get_events("run-1")
            runs = store.list_runs()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "start")
        self.assertEqual(runs[0]["run_id"], "run-1")


if __name__ == "__main__":
    unittest.main()
