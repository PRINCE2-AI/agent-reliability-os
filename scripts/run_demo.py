from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.demo_agent import run_demo_suite
from app.exporter import export_json, export_runs_csv


def main() -> None:
    result = run_demo_suite(".data/demo.sqlite3")
    export_json(result, "demo/sample_outputs.json")
    export_runs_csv(result["runs"], "demo/runs.csv")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
