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

    # Model provider selection. Bedrock is the only implementation for now;
    # the literal exists so adding a provider is a type-checked, additive change.
    model_provider: Literal["bedrock"] = "bedrock"
    bedrock_model_id: str = "global.amazon.nova-2-lite-v1:0"
    bedrock_region: str = "us-west-2"

    # Persistence
    db_path: str = "ornatus.db"

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
