from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.config import Settings


def llm_status(settings: Settings) -> dict:
    if not settings.allow_live_llm:
        return {"configured": False, "ok": False, "message": "Live LLM disabled."}
    api_key = settings.openrouter_api_key if settings.llm_provider == "openrouter" else settings.openai_api_key
    if not api_key:
        return {"configured": False, "ok": False, "message": "Missing API key."}
    return {"configured": True, "ok": True, "provider": settings.llm_provider}


def explain_decision(settings: Settings, decision: dict) -> str:
    status = llm_status(settings)
    if not status["ok"]:
        return f"{decision['decision']}: {', '.join(decision.get('reasons', []))}"

    if settings.llm_provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        model = settings.openrouter_model
        api_key = settings.openrouter_api_key
    else:
        url = "https://api.openai.com/v1/chat/completions"
        model = settings.openai_model
        api_key = settings.openai_api_key

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Explain agent runtime policy decisions in 3 concise bullets."},
            {"role": "user", "content": json.dumps(decision)},
        ],
        "temperature": 0.1,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, TimeoutError) as exc:
        return f"LLM explanation unavailable: {type(exc).__name__}"

