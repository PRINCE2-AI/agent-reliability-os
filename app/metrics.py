from __future__ import annotations


def aggregate_runs(runs: list[dict]) -> dict:
    if not runs:
        return {
            "total_runs": 0,
            "avg_task_success": 0,
            "avg_tool_misuse_risk": 0,
            "avg_trace_completeness": 0,
            "avg_latency_ms": 0,
            "blocked_runs": 0,
        }
    return {
        "total_runs": len(runs),
        "avg_task_success": round(
            sum(run["evaluation"]["task_success"] for run in runs) / len(runs), 3
        ),
        "avg_tool_misuse_risk": round(
            sum(run["evaluation"]["tool_misuse_risk"] for run in runs) / len(runs), 3
        ),
        "avg_trace_completeness": round(
            sum(run["evaluation"]["trace_completeness"] for run in runs) / len(runs), 3
        ),
        "avg_latency_ms": round(sum(run["latency_ms"] for run in runs) / len(runs), 1),
        "blocked_runs": sum(1 for run in runs if run["status"] == "blocked"),
    }

