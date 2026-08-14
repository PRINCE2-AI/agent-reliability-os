from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Iterable

from app.schemas import TraceEvent


class TraceStore:
    def __init__(self, db_path: str = ".data/agent_reliability.sqlite3") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trace_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_run ON trace_events(run_id)")
            conn.commit()

    def append(self, event: TraceEvent) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO trace_events(event_id, run_id, event_type, name, payload, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.event_type.value,
                    event.name,
                    json.dumps(event.payload, sort_keys=True),
                    event.timestamp,
                ),
            )
            conn.commit()

    def append_many(self, events: Iterable[TraceEvent]) -> None:
        for event in events:
            self.append(event)

    def get_events(self, run_id: str) -> list[dict]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT event_id, run_id, event_type, name, payload, timestamp
                FROM trace_events
                WHERE run_id = ?
                ORDER BY timestamp ASC
                """,
                (run_id,),
            ).fetchall()
        return [
            {
                "event_id": row[0],
                "run_id": row[1],
                "event_type": row[2],
                "name": row[3],
                "payload": json.loads(row[4]),
                "timestamp": row[5],
            }
            for row in rows
        ]

    def list_runs(self) -> list[dict]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT run_id,
                       MIN(timestamp) AS started_at,
                       MAX(timestamp) AS ended_at,
                       COUNT(*) AS total_events
                FROM trace_events
                GROUP BY run_id
                ORDER BY started_at DESC
                """
            ).fetchall()
        return [
            {
                "run_id": row[0],
                "started_at": row[1],
                "ended_at": row[2],
                "total_events": row[3],
            }
            for row in rows
        ]

    def clear(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute("DELETE FROM trace_events")
            conn.commit()
