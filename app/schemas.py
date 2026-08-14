from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from time import time
from typing import Any
from uuid import uuid4


class EventType(str, Enum):
    RUN_START = "run_start"
    MODEL_CALL = "model_call"
    TOOL_CALL = "tool_call"
    POLICY_DECISION = "policy_decision"
    EVALUATION = "evaluation"
    RUN_END = "run_end"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decision(str, Enum):
    ALLOW = "allow"
    APPROVAL = "approval"
    BLOCK = "block"


@dataclass(slots=True)
class TraceEvent:
    run_id: str
    event_type: EventType
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data


@dataclass(slots=True)
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    user_goal: str
    destination: str | None = None


@dataclass(slots=True)
class PolicyDecision:
    decision: Decision
    risk_level: RiskLevel
    risk_score: int
    reasons: list[str]
    redacted_arguments: dict[str, Any]
    matched_rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["decision"] = self.decision.value
        data["risk_level"] = self.risk_level.value
        return data


@dataclass(slots=True)
class EvalResult:
    task_success: float
    hallucination_risk: float
    tool_misuse_risk: float
    policy_coverage: float
    trace_completeness: float
    cost_score: float
    latency_ms: int
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunSummary:
    run_id: str
    mode: str
    task: str
    final_answer: str
    status: str
    latency_ms: int
    total_events: int
    total_cost_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

