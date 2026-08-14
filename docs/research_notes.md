# Research Notes

Agent Reliability OS is inspired by the shift from simple LLM apps to production agent systems. The implementation maps research and practitioner ideas into a small, runnable portfolio project.

## Research And Practitioner Threads

| Thread | Implementation Mapping |
| --- | --- |
| Agent evaluation surveys | Trace-level metrics for task success, tool-use reliability, safety, latency, and reliability |
| OpenTelemetry-style observability | Events behave like spans: lifecycle, model, tool, policy, eval, and final state |
| LangSmith / Langfuse / Phoenix-style agent observability | Run inspection, datasets, regression checks, and dashboard-friendly traces |
| MCP/tool-use security | Tool-call policy, redaction, high-risk tool checks, exfiltration detection |
| RAGAS/ARES-style evaluation thinking | Separate quality dimensions instead of one vague pass/fail result |

## Practical Sources To Read

- LangChain State of Agent Engineering
- LangSmith tracing and evaluation documentation
- Langfuse tracing and evaluations documentation
- Arize Phoenix tracing and eval documentation
- OpenTelemetry tracing concepts
- MCP client best practices
- OWASP guidance around LLM/tool risks

## Scope Boundary

This project is not a paper reproduction. It is a practical engineering system that demonstrates:

- how to observe an agent
- how to gate risky tools
- how to compare baseline and protected behavior
- how to expose results through API, dashboard, tests, CI, and static proof

