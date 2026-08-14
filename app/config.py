from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    trace_db_path: str = ".data/agent_reliability.sqlite3"
    llm_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    allow_live_llm: bool = False


def load_settings() -> Settings:
    return Settings(
        trace_db_path=os.getenv("TRACE_DB_PATH", ".data/agent_reliability.sqlite3"),
        llm_provider=os.getenv("LLM_PROVIDER", "openrouter"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        allow_live_llm=os.getenv("ALLOW_LIVE_LLM", "false").lower() == "true",
    )

