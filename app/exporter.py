from __future__ import annotations

import csv
import json
from pathlib import Path


def export_json(payload: dict, path: str) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(output)


def export_runs_csv(runs: list[dict], path: str) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id",
                "mode",
                "scenario",
                "status",
                "task_success",
                "tool_misuse_risk",
                "policy_coverage",
                "latency_ms",
            ],
        )
        writer.writeheader()
        for run in runs:
            writer.writerow(
                {
                    "run_id": run["run_id"],
                    "mode": run["mode"],
                    "scenario": run["scenario"],
                    "status": run["status"],
                    "task_success": run["evaluation"]["task_success"],
                    "tool_misuse_risk": run["evaluation"]["tool_misuse_risk"],
                    "policy_coverage": run["evaluation"]["policy_coverage"],
                    "latency_ms": run["latency_ms"],
                }
            )
    return str(output)

