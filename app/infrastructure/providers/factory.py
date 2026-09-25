from app.core.config import settings
from app.infrastructure.providers.base import AiProvider
from app.infrastructure.providers.gemini_provider import GeminiProvider
from app.infrastructure.providers.mock_provider import MockAiProvider
from app.infrastructure.providers.openai_provider import OpenAIProvider

_provider_instances: dict[str, AiProvider] = {}


def get_ai_provider(provider_name: str | None = None) -> AiProvider:
    name = (provider_name or settings.DEFAULT_PROVIDER).lower()

    if name in _provider_instances:
        return _provider_instances[name]

    if name == "openai":
        provider = OpenAIProvider(fallback_provider=MockAiProvider())
    elif name == "gemini":
        provider = GeminiProvider(fallback_provider=MockAiProvider())
    else:
        provider = MockAiProvider()

    _provider_instances[name] = provider
    return provider
