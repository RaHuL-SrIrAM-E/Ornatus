"""Builds the Strands model instance from configuration.

This is the one place that knows which model provider Ornatus is running on.
The orchestrator only ever depends on ``get_model()`` -> ``strands.models.Model``,
so switching providers later (e.g. a direct Anthropic API model) means adding
a branch here, not changing the agent or any tool/service code.

"bedrock" (the default) is the real, production provider — Amazon Bedrock,
currently configured for Nova 2 Lite. "local" is a deterministic, rule-based
stand-in with no real model behind it at all, for developing and testing the
agent loop while Bedrock access is unavailable; see
``ornatus.agent.local_model``. Selected via ``ORNATUS_MODEL_PROVIDER``.
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

    if settings.model_provider == "local":
        from ornatus.agent.local_model import LocalDeterministicModel

        return LocalDeterministicModel()

    raise ValueError(f"Unsupported model provider: {settings.model_provider}")
