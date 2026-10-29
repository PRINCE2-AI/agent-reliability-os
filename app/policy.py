from __future__ import annotations

import re
from typing import Any

from app.schemas import Decision, PolicyDecision, RiskLevel, ToolCall


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{12,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

HIGH_RISK_TOOLS = {
    "filesystem.write",
    "filesystem.delete",
    "shell.exec",
    "http.post",
    "email.send",
    "memory.write",
}

SENSITIVE_PATH_HINTS = (".env", "..", "id_rsa", "credentials", "AppData", "/etc/passwd")
EXFIL_WORDS = ("upload", "send", "post", "webhook", "pastebin", "external", "exfiltrate")
INJECTION_WORDS = ("ignore previous", "system prompt", "developer message", "reveal secret")


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{k} {_flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    return str(value)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if not isinstance(value, str):
        return value
    for pattern in SECRET_PATTERNS:
        value = pattern.sub("[REDACTED_SECRET]", value)
    return value


class PolicyEngine:
    """Deterministic runtime policy for tool-using agents."""

    def evaluate(self, call: ToolCall) -> PolicyDecision:
        text = f"{call.tool_name} {call.user_goal} {_flatten(call.arguments)}".lower()
        reasons: list[str] = []
        matched: list[str] = []
        score = 10

        if call.tool_name in HIGH_RISK_TOOLS:
            score += 25
            matched.append("high_risk_tool")
            reasons.append(f"{call.tool_name} can modify state or move data.")

        if any(hint.lower() in text for hint in SENSITIVE_PATH_HINTS):
            score += 50
            matched.append("sensitive_path")
            reasons.append("Arguments reference sensitive files or credential paths.")

        if any(word in text for word in EXFIL_WORDS):
            score += 25
            matched.append("exfiltration_intent")
            reasons.append("Goal or arguments suggest external data movement.")

        if any(word in text for word in INJECTION_WORDS):
            score += 20
            matched.append("prompt_injection")
            reasons.append("Text contains prompt-injection style instructions.")

        if any(pattern.search(_flatten(call.arguments)) for pattern in SECRET_PATTERNS):
            score += 35
            matched.append("secret_detected")
            reasons.append("Secrets or bearer-style credentials were detected.")

        if not reasons:
            reasons.append("No blocking policy matched.")

        if score >= 80:
            decision = Decision.BLOCK
            level = RiskLevel.CRITICAL
        elif score >= 55:
            decision = Decision.BLOCK
            level = RiskLevel.HIGH
        elif score >= 35:
            decision = Decision.APPROVAL
            level = RiskLevel.MEDIUM
        else:
            decision = Decision.ALLOW
            level = RiskLevel.LOW

        return PolicyDecision(
            decision=decision,
            risk_level=level,
            risk_score=min(score, 100),
            reasons=reasons,
            redacted_arguments=redact(call.arguments),
            matched_rules=matched,
        )
