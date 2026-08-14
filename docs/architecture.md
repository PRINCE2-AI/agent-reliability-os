# Architecture

Agent Reliability OS is designed around one simple idea: every agent action should become an auditable event before it becomes a production incident.

## Pipeline

```text
Task -> Planner/model call -> Proposed tool call -> Policy engine
     -> Redaction -> Decision -> Tool execution/block
     -> Trace store -> Evaluator -> API/dashboard/static proof
```

## Components

| Component | File | Responsibility |
| --- | --- | --- |
| Trace schema | `app/schemas.py` | Dataclasses for events, tool calls, policy decisions, and eval results |
| Trace collector | `app/tracer.py` | Captures lifecycle, model, tool, policy, eval, and final events |
| Trace store | `app/trace_store.py` | SQLite persistence for run events |
| Policy engine | `app/policy.py` | Deterministic risk scoring, allow/block/approval decisions, redaction |
| Evaluator | `app/evaluator.py` | Scores trace completeness, task success, risk, coverage, latency |
| Demo agent | `app/demo_agent.py` | Baseline vs protected benchmark scenarios |
| API | `app/api.py` | FastAPI service for health, policy, runs, and evaluation |
| Dashboard | `app/ui.py` | Streamlit interface for scenarios and trace inspection |
| Static demo | `scripts/build_site.py` | GitHub Pages proof without secrets or backend hosting |

## Design Choices

- Core logic uses the Python standard library so tests and CI are stable.
- FastAPI and Streamlit are wrappers, not required for the benchmark logic.
- Policy is deterministic before optional LLM explanations. This keeps safety decisions auditable.
- The public demo is static to avoid exposing API keys.
- Evaluation is lightweight and transparent rather than hidden behind a black-box judge.

## Extension Points

- Add a LangGraph callback handler that maps graph node events into `TraceEvent`.
- Add OpenTelemetry export for trace interoperability.
- Add MCP proxy mode to inspect live tool calls.
- Add dataset-backed regression runs.
- Add optional LLM-as-judge scoring for answer quality.

