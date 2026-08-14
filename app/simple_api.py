from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.config import load_settings
from app.demo_agent import run_demo_suite
from app.llm import llm_status
from app.policy import PolicyEngine
from app.schemas import ToolCall


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        settings = load_settings()
        if self.path == "/health":
            self._send({"status": "ok", "service": "agent-reliability-os"})
        elif self.path == "/llm/status":
            self._send(llm_status(settings))
        elif self.path == "/evaluate":
            self._send(run_demo_suite(settings.trace_db_path))
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(raw)
        if self.path == "/policy/decide":
            decision = PolicyEngine().evaluate(
                ToolCall(
                    tool_name=payload["tool_name"],
                    user_goal=payload["user_goal"],
                    arguments=payload.get("arguments", {}),
                    destination=payload.get("destination"),
                )
            )
            self._send(decision.to_dict())
        else:
            self._send({"error": "not found"}, 404)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Agent Reliability OS API running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()

