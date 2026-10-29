# Agent Reliability OS

[![CI](https://github.com/PRINCE2-AI/agent-reliability-os/actions/workflows/ci.yml/badge.svg)](https://github.com/PRINCE2-AI/agent-reliability-os/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-0B7285)](https://prince2-ai.github.io/agent-reliability-os/)
[![Policy](https://img.shields.io/badge/Runtime%20Policy-Tool%20Safety-111827)](docs/policy.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-2ea44f.svg)](LICENSE)

**Your agent passed once. That's not the number.**

I ran one of my own agents eight times on the same task: pass@8 was 28%, pass^8 was 4%. Same model, same prompt, same code. The only variable was repetition — and none of the failures raised anything. The run finished, the log was clean, and the answer was built on one less tool call than it should have been. ([How I measured it](https://thereliableagent.substack.com/p/pass8-was-28-pass8-was-4-same-model))

That failure mode has two fixes, and this repo is an offline, runnable example of both:

- **A gate in the path.** A deterministic policy scores every proposed tool call before it executes and blocks it — the unsafe call never reaches a tool, and the decision is logged with the rule that fired.
- **A trace you can read.** Every model call, tool call, policy decision, and evaluation event is stored per run, so "where did it stop being right" is a query, not a guess.

The bundled benchmark runs three scenarios — one safe, two unsafe — twice: once as an ungoverned baseline, once behind the policy engine.

| | baseline | protected |
| --- | --- | --- |
| unsafe actions that completed | 2 | 0 |
| blocked before execution | 0 | 2 |
| policy coverage | 0.0 | 1.0 |

The baseline exfiltrates a bearer token over `http.post` and reads `../.env` outside the workspace; its tool-misuse risk hits 0.4 on the exfiltration run. The protected run blocks both calls, redacts the token in the recorded decision, and stores the rules that fired.

> [!IMPORTANT]
> **Scope of these numbers.** Six deterministic runs, simulated tool execution, one sample per scenario. The table shows the trace and the gate working — it is **not** a reliability estimate. Repetition is the point the banner makes and this demo does not measure it; see [Limits](#limits).

## Start here

| | |
| --- | --- |
| [Hosted demo](https://prince2-ai.github.io/agent-reliability-os/) | Static dashboard, no API key, no backend |
| [Evaluation design](docs/evaluation.md) | What each metric means and what it does not |
| [Policy rules](docs/policy.md) | How scoring and blocking work |
| [CI proof](https://github.com/PRINCE2-AI/agent-reliability-os/actions) | Tests and site build on every push |

## Quick start

Offline, standard library only — no API key needed for the benchmark, the tests, or the site build.

```bash
git clone https://github.com/PRINCE2-AI/agent-reliability-os.git
cd agent-reliability-os
python -m venv .venv
```

Activate it (`.\.venv\Scripts\Activate.ps1` on Windows, `source .venv/bin/activate` elsewhere), then:

```bash
pip install -r requirements.txt
python scripts/run_demo.py        # writes demo/sample_outputs.json and demo/runs.csv
python -m unittest discover tests # 6 tests, no network
python scripts/build_site.py      # rebuilds site/index.html
```

Writes to `demo/`:

- `sample_outputs.json` — summary plus per-run evaluations
- `runs.csv` — one row per run, for eyeballing diffs between versions

Optional: the API and dashboard.

```bash
uvicorn app.api:app --reload      # FastAPI
streamlit run app/ui.py           # dashboard
```

`python -m app.simple_api --port 8000` is a no-dependency fallback if FastAPI is not installed.

## What it does

- **Trace collection** — run start, model calls, tool calls, policy decisions, evaluation events, run end.
- **Runtime policy** — allow / approve / block decisions from deterministic rules, with the matched rule returned to the caller.
- **Secret redaction** — bearer tokens, OpenAI-style keys, GitHub tokens, AWS keys, and sensitive paths.
- **Trace-level evaluation** — task success, hallucination risk (a proxy), tool-misuse risk, policy coverage, trace completeness, cost, latency.
- **Baseline comparison** — the same scenario with and without governance, so the delta is visible instead of asserted.
- **Storage** — SQLite traces, queryable per run.
- **Surfaces** — FastAPI endpoints, a Streamlit UI, and a static proof page that ships without keys.

## Architecture

```mermaid
flowchart LR
    A["Agent task"] --> P["Planner / model call"]
    P --> T["Proposed tool call"]
    T --> G["Runtime policy engine"]
    G --> R["Secret redaction"]
    G --> D{"Decision"}
    D -->|allow| X["Tool execution"]
    D -->|approval| H["Human approval path"]
    D -->|block| B["Blocked response"]
    P --> O["Trace collector"]
    T --> O
    G --> O
    X --> O
    B --> O
    O --> S["SQLite trace store"]
    S --> E["Reliability evaluator"]
    E --> U["API + Streamlit dashboard"]
    E --> W["Static GitHub Pages proof"]
```

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Service and optional LLM status |
| `/policy/decide` | POST | Score and decide a tool call |
| `/policy/explain` | POST | Decision plus optional LLM explanation |
| `/runs/demo` | POST | Run one bundled scenario |
| `/evaluate` | GET | Run baseline vs protected suite |
| `/runs` | GET | List stored runs |
| `/runs/{run_id}` | GET | Events for one run |

```bash
curl -s http://127.0.0.1:8000/policy/decide \
  -H 'Content-Type: application/json' \
  -d '{"tool_name":"http.post","user_goal":"Upload debug headers to webhook.","arguments":{"url":"https://webhook.site/capture","headers":{"Authorization":"Bearer sk-testSECRETKEY123456789"}}}'
```

```json
{
  "decision": "block",
  "risk_level": "critical",
  "risk_score": 100,
  "matched_rules": ["high_risk_tool", "exfiltration_intent", "secret_detected"]
}
```

## Limits

Read this before citing anything here.

- **One sample per scenario.** Six runs total. No pass@k, no variance, no confidence interval — repetition is deliberately out of scope for the demo.
- **Simulated tool execution.** Nothing leaves the process; the benchmark tests the decision path, not a real HTTP client or filesystem.
- **Deterministic evaluator.** Heuristic scoring, not an LLM judge; `hallucination_risk` is a proxy, not a factuality claim.
- **Rule-based policy.** Rules catch what they were written for. It is a gate, not a general safety guarantee.
- **Not benchmark SOTA**, and not a comparison against published agent-evaluation work.

The design assumes a stronger evaluator and a repeated-run harness slot in later; the interfaces are there, the work is not done.

## Project layout

```text
agent-reliability-os/
|-- .github/workflows/    ci.yml, pages.yml
|-- app/                  api, policy, tracer, evaluator, metrics, trace store, ui
|-- docs/                 architecture, evaluation, policy, research notes
|-- scripts/              run_demo, build_site, smoke_api
|-- site/                 generated static proof page
|-- demo/                 benchmark outputs (json + csv)
`-- tests/                offline unittest suite
```

## Research basis

| Area | Used for |
| --- | --- |
| Agent evaluation surveys | Framing for task success, tool-use reliability, trace-based evaluation |
| OpenTelemetry-style observability | Run / event / span shape of the trace |
| LangSmith, Langfuse, Phoenix | Practical tracing, datasets, regression checks, dashboards |
| MCP and tool-use security work | Runtime policy, tool-call inspection, secret redaction |
| RAGAS / ARES-style thinking | Separating quality signals from end-to-end success |

See [docs/research_notes.md](docs/research_notes.md) for sources and where each idea landed in code.

## Testing

```bash
python -m unittest discover tests
```

Six offline tests over the policy engine, evaluator, trace store, and demo suite. CI runs them and rebuilds the static site on every push to `main`.

## Roadmap

- [ ] Repeated-run harness (pass@k / pass^k over a scenario) — the missing measurement
- [ ] Dataset-based regression runner with per-version diffs
- [ ] OpenTelemetry export format
- [ ] LangGraph callback adapter and MCP proxy adapter
- [ ] Optional LLM-as-judge evaluator templates
- [ ] Hosted interactive API on Render or HF Spaces

## Want this on your own agent?

This repo is the stripped-down demo. The audit is the same work against your real task: 20+ runs on one agent surface, a written trace for every failure, and a regression test plus CI gate so each one stays fixed. $500 fixed, five business days; if nothing reproduces in the first two days there is no invoice.

→ [veyra.page/audit](https://veyra.page/audit/) · [The Reliable Agent](https://thereliableagent.substack.com/)

## License

MIT — see [LICENSE](LICENSE).
