from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from app.cost import estimate_cost
from app.schemas import EventType, EvalResult, PolicyDecision, TraceEvent
from app.trace_store import TraceStore


class AgentTracer:
    def __init__(self, store: TraceStore, mode: str, task: str) -> None:
        self.store = store
        self.mode = mode
        self.task = task
        self.run_id = str(uuid4())
        self.started = perf_counter()
        self.total_cost = 0.0

    def record(self, event_type: EventType, name: str, payload: dict) -> TraceEvent:
        event = TraceEvent(
            run_id=self.run_id,
            event_type=event_type,
            name=name,
            payload=payload,
        )
        self.store.append(event)
        return event

    def start(self) -> None:
        self.record(EventType.RUN_START, "run.started", {"mode": self.mode, "task": self.task})

    def model_call(self, model: str, prompt: str, output: str) -> None:
        cost = estimate_cost(model, prompt, output)
        self.total_cost += cost
        self.record(
            EventType.MODEL_CALL,
            "model.call",
            {
                "model": model,
                "prompt_preview": prompt[:300],
                "output_preview": output[:300],
                "estimated_cost_usd": cost,
            },
        )

    def tool_call(self, tool_name: str, arguments: dict, result: dict) -> None:
        self.record(
            EventType.TOOL_CALL,
            "tool.call",
            {"tool_name": tool_name, "arguments": arguments, "result": result},
        )

    def policy(self, decision: PolicyDecision) -> None:
        self.record(EventType.POLICY_DECISION, "policy.decision", decision.to_dict())

    def evaluation(self, result: EvalResult) -> None:
        self.record(EventType.EVALUATION, "run.evaluation", result.to_dict())

    def end(self, final_answer: str, status: str) -> int:
        latency_ms = int((perf_counter() - self.started) * 1000)
        self.record(
            EventType.RUN_END,
            "run.ended",
            {
                "final_answer": final_answer,
                "status": status,
                "latency_ms": latency_ms,
                "estimated_cost_usd": round(self.total_cost, 6),
            },
        )
        return latency_ms

