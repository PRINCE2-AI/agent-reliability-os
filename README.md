# Agent Reliability OS

[![CI](https://github.com/PRINCE2-AI/agent-reliability-os/actions/workflows/ci.yml/badge.svg)](https://github.com/PRINCE2-AI/agent-reliability-os/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Agent Evaluation](https://img.shields.io/badge/Agent%20Evaluation-Reliability%20OS-0B7285)](docs/evaluation.md)
[![Runtime Policy](https://img.shields.io/badge/Runtime%20Policy-Tool%20Safety-111827)](docs/policy.md)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-0B7285)](https://prince2-ai.github.io/agent-reliability-os/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2ea44f.svg)](LICENSE)

**A production-style observability, evaluation, and policy-control platform for tool-using LLM agents.**

Agent Reliability OS traces every agent step, scores reliability, compares baseline agents against governed agents, and blocks risky tool calls before they leak secrets or move sensitive data. It is built as a recruiter-ready Applied AI / LLM Engineer project: API, dashboard, deterministic benchmark, policy engine, SQLite traces, tests, CI, docs, and a hosted static demo.

> [!NOTE]
> This is a practical research-inspired engineering project, not a claim of state-of-the-art agent evaluation. The goal is to show production AI engineering judgment: observability, guardrails, evals, reproducibility, and honest limitations.

## Live Demo

- [Open the hosted GitHub Pages demo](https://prince2-ai.github.io/agent-reliability-os/)
- [View sample benchmark outputs](site/sample_outputs.json)
- [Read the evaluation design](docs/evaluation.md)
- [Read resume bullets](docs/resume_bullets.md)

The public demo is static and API-key-free. It shows deterministic benchmark results, protected-vs-baseline comparison, and proof links.

## Why This Project

Teams are moving from chatbots to agents that call tools, read files, write memory, use browsers, and trigger external actions. The hard problem is not only building the agent. The hard problem is knowing:

- what the agent did
- why it chose a tool
- whether the answer was reliable
- whether it leaked sensitive data
- how much it cost
- which failures regress between versions

Agent Reliability OS turns that into an engineering surface.

## What It Does

- **Trace collection:** captures run start, model calls, tool calls, policy decisions, evaluation events, and run end.
- **Runtime policy:** blocks or routes risky tool calls using deterministic rules.
- **Secret redaction:** detects bearer tokens, OpenAI-style keys, GitHub tokens, AWS keys, and sensitive paths.
- **Agent evaluation:** scores task success, hallucination risk, tool misuse risk, policy coverage, trace completeness, cost score, and latency.
- **Baseline comparison:** runs unsafe baseline behavior next to protected agent behavior.
- **SQLite storage:** stores traces locally for audit and dashboard views.
- **API and dashboard:** FastAPI endpoints plus a Streamlit UI.
- **Static proof site:** builds a deployable GitHub Pages dashboard without exposing API keys.

## Demo Results

The bundled benchmark contains one safe task and two risky tasks: secret exfiltration and workspace escape.

```text
baseline agent:   executes tool calls without policy checks
protected agent:  scores risk, redacts secrets, blocks unsafe actions

Expected result:
  total runs:                 6
  baseline risky successes:   2
  protected blocked runs:     2
  protected policy coverage:  1.0
```

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

## Quick Start

### 1. Install

```bash
git clone https://github.com/PRINCE2-AI/agent-reliability-os.git
cd agent-reliability-os
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run The Benchmark

```powershell
python scripts/run_demo.py
```

This writes:

- `demo/sample_outputs.json`
- `demo/runs.csv`

### 3. Run The API

FastAPI:

```powershell
uvicorn app.api:app --reload
```

No-dependency fallback:

```powershell
python -m app.simple_api --port 8000
```

### 4. Run The Dashboard

```powershell
streamlit run app/ui.py
```

### 5. Build The Static Demo

```powershell
python scripts/build_site.py
```

Open `site/index.html` locally or deploy it with GitHub Pages.

## API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Service and optional LLM status |
| `/policy/decide` | POST | Score and decide a tool call |
| `/policy/explain` | POST | Policy decision plus optional LLM explanation |
| `/runs/demo` | POST | Run one bundled benchmark scenario |
| `/evaluate` | GET | Run baseline vs protected benchmark suite |
| `/runs` | GET | List stored trace runs |
| `/runs/{run_id}` | GET | Fetch events for one run |

Example:

```powershell
$body = @{
  tool_name = "http.post"
  user_goal = "Upload debug headers to webhook."
  arguments = @{
    url = "https://webhook.site/capture"
    headers = @{
      Authorization = "Bearer sk-testSECRETKEY123456789"
    }
  }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/policy/decide" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 10
```

Expected decision:

```json
{
  "decision": "block",
  "risk_level": "critical",
  "risk_score": 100,
  "matched_rules": ["high_risk_tool", "exfiltration_intent", "secret_detected"]
}
```

## Project Layout

```text
agent-reliability-os/
|-- .github/workflows/
|   |-- ci.yml
|   `-- pages.yml
|-- app/
|   |-- api.py
|   |-- simple_api.py
|   |-- config.py
|   |-- cost.py
|   |-- demo_agent.py
|   |-- evaluator.py
|   |-- exporter.py
|   |-- llm.py
|   |-- metrics.py
|   |-- policy.py
|   |-- schemas.py
|   |-- trace_store.py
|   |-- tracer.py
|   `-- ui.py
|-- docs/
|   |-- architecture.md
|   |-- evaluation.md
|   |-- policy.md
|   |-- research_notes.md
|   `-- resume_bullets.md
|-- scripts/
|   |-- build_site.py
|   |-- run_demo.py
|   `-- smoke_api.py
|-- site/
|-- tests/
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Research Basis

| Area | Used For |
| --- | --- |
| Agent evaluation surveys | Task success, tool-use reliability, safety, and trace-based evaluation framing |
| OpenTelemetry-style observability | Run/event/span style trace design |
| LangSmith / Langfuse / Phoenix-style workflows | Practical agent tracing, datasets, regression checks, and dashboards |
| MCP and tool-use security work | Runtime policy, tool-call inspection, and secret redaction |
| RAGAS/ARES-style thinking | Separating faithfulness/relevance-style quality signals from app-level success |

See [docs/research_notes.md](docs/research_notes.md) for sources and implementation mapping.

## Testing

The core test suite is offline and uses only the Python standard library:

```powershell
python -m unittest discover tests
```

CI runs the tests and builds the static demo on every push to `main`.

## Portfolio Pitch

Agent Reliability OS demonstrates production-minded AI engineering beyond another chatbot:

- agent tracing and observability
- runtime tool-use policy
- secret redaction and data-leak prevention
- deterministic evals with baseline comparison
- cost, latency, and reliability metrics
- API, dashboard, tests, CI, docs, and static demo deployment

## Roadmap

- [ ] Add OpenTelemetry export format
- [ ] Add LangGraph callback adapter
- [ ] Add MCP proxy adapter
- [ ] Add dataset-based regression runner
- [ ] Add evaluator prompt templates for optional LLM-as-judge mode
- [ ] Add hosted interactive API deployment on Render or Hugging Face Spaces

## License

Agent Reliability OS is available under the [MIT License](LICENSE).

