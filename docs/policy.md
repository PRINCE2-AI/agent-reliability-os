# Runtime Policy

The policy engine scores proposed tool calls before execution.

## Decisions

| Decision | Meaning |
| --- | --- |
| `allow` | Low-risk call can proceed |
| `approval` | Medium-risk call should require human approval |
| `block` | High or critical risk call should not execute |

## Risk Signals

- high-risk tools such as shell execution, HTTP post, email send, delete, write, and memory write
- sensitive paths such as `.env`, credential files, Windows `AppData`, and `/etc/passwd`
- exfiltration intent such as upload, send, webhook, pastebin, or external transfer
- prompt-injection style strings such as `ignore previous` or `reveal secret`
- secrets such as bearer tokens, OpenAI-style keys, GitHub tokens, and AWS keys

## Why Deterministic Policy First

LLMs are useful for explanations, but safety decisions should be reproducible. Agent Reliability OS uses deterministic rules for enforcement and optional LLM calls only for human-readable explanation.

## Example

```json
{
  "tool_name": "http.post",
  "user_goal": "Upload debug headers to webhook.",
  "arguments": {
    "Authorization": "Bearer sk-testSECRETKEY123456789"
  }
}
```

Expected result:

```json
{
  "decision": "block",
  "risk_level": "critical",
  "risk_score": 95,
  "reasons": [
    "http.post can modify state or move data.",
    "Goal or arguments suggest external data movement.",
    "Secrets or bearer-style credentials were detected."
  ],
  "redacted_arguments": {
    "Authorization": "Bearer [REDACTED_SECRET]"
  },
  "matched_rules": ["high_risk_tool", "exfiltration_intent", "secret_detected"]
}
```

