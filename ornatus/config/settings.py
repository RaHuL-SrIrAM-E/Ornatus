"""Application configuration.

All runtime configuration is read from the environment (optionally via a
``.env`` file). Nothing here is Bedrock-specific beyond the ``model_provider``
switch: swapping providers later means adding a branch in
``ornatus.agent.model_provider``, not touching this file.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ORNATUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model provider selection. "bedrock" (default) is the real, production
    # provider. "local" is a deterministic, rule-based stand-in — not a
    # real LLM — for developing/testing the agent loop without AWS access;
    # see ornatus.agent.local_model. Swapping providers is a config change
    # (this field) plus a branch in ornatus.agent.model_provider, nothing
    # elsewhere.
    model_provider: Literal["bedrock", "local"] = "bedrock"
    bedrock_model_id: str = "global.amazon.nova-2-lite-v1:0"
    bedrock_region: str = "us-west-2"

    # Single-user for Phase 1 — no auth/multi-tenancy yet. Tools bind to
    # this id internally rather than asking the model to supply it.
    current_user_id: str = "demo-user"

    # Persistence
    db_path: str = "ornatus.db"

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
