from __future__ import annotations

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install requirements.txt to run the FastAPI app.") from exc

from app.config import load_settings
from app.demo_agent import SCENARIOS, DemoAgent, run_demo_suite
from app.llm import explain_decision, llm_status
from app.policy import PolicyEngine
from app.schemas import ToolCall
from app.trace_store import TraceStore

app = FastAPI(title="Agent Reliability OS", version="0.1.0")
settings = load_settings()
store = TraceStore(settings.trace_db_path)


class ToolCallRequest(BaseModel):
    tool_name: str
    user_goal: str
    arguments: dict
    destination: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "agent-reliability-os", "llm": llm_status(settings)}


@app.post("/policy/decide")
def decide(request: ToolCallRequest) -> dict:
    decision = PolicyEngine().evaluate(
        ToolCall(
            tool_name=request.tool_name,
            user_goal=request.user_goal,
            arguments=request.arguments,
            destination=request.destination,
        )
    )
    return decision.to_dict()


@app.post("/policy/explain")
def explain(request: ToolCallRequest) -> dict:
    decision = decide(request)
    return {"decision": decision, "explanation": explain_decision(settings, decision)}


@app.post("/runs/demo")
def demo_run(mode: str = "protected", scenario: str = "secret_exfiltration") -> dict:
    selected = next((item for item in SCENARIOS if item.name == scenario), SCENARIOS[1])
    return DemoAgent(store).run(selected, mode=mode)


@app.get("/evaluate")
def evaluate() -> dict:
    return run_demo_suite()


@app.get("/runs")
def runs() -> dict:
    return {"runs": store.list_runs()}


@app.get("/runs/{run_id}")
def run_detail(run_id: str) -> dict:
    return {"run_id": run_id, "events": store.get_events(run_id)}

