from __future__ import annotations

import json
import urllib.request


def main() -> None:
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=10) as response:
        health = json.loads(response.read().decode("utf-8"))
    assert health["status"] == "ok"
    print(json.dumps(health, indent=2))


if __name__ == "__main__":
    main()
