"""Builds the Strands model instance from configuration.

This is the one place that knows which model provider Ornatus is running on.
The orchestrator only ever depends on ``get_model()`` -> ``strands.models.Model``,
so switching providers later (e.g. a direct Anthropic API model) means adding
a branch here, not changing the agent or any tool/service code.
"""

from strands.models.model import Model

from ornatus.config.settings import get_settings


def get_model() -> Model:
    settings = get_settings()

    if settings.model_provider == "bedrock":
        from strands.models.bedrock import BedrockModel

        return BedrockModel(
            model_id=settings.bedrock_model_id,
            region_name=settings.bedrock_region,
        )

    raise ValueError(f"Unsupported model provider: {settings.model_provider}")
