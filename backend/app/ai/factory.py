"""Provider factory and the AIClient facade used by every AI-powered service.

Never hardcode a provider in a service - always go through `get_ai_client()`,
which reads `settings.AI_PROVIDER` / `settings.AI_FALLBACK_PROVIDERS` so the
active provider can be changed purely via configuration (env vars).
"""
import logging
from typing import AsyncIterator, List, Optional

from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIMessage, AICompletion, AIProviderError, AIAllProvidersFailedError
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.claude_provider import ClaudeProvider

logger = logging.getLogger("schoolai.ai")

_PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
}


def _build_provider(name: str) -> BaseAIProvider:
    cls = _PROVIDER_REGISTRY.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown AI provider '{name}'. Valid options: {list(_PROVIDER_REGISTRY)}")
    return cls()


class AIClient:
    """Provider-agnostic entry point with automatic fallback.

    Tries `settings.AI_PROVIDER` first; if it fails (after its own internal
    retries/timeouts), tries each provider in `settings.AI_FALLBACK_PROVIDERS`
    in order before giving up.
    """

    def __init__(self, primary: Optional[str] = None, fallbacks: Optional[List[str]] = None):
        self.provider_chain: List[str] = [primary or settings.AI_PROVIDER, *(fallbacks or settings.AI_FALLBACK_PROVIDERS)]
        # de-dupe while preserving order
        seen = set()
        self.provider_chain = [p for p in self.provider_chain if not (p in seen or seen.add(p))]

    def _providers(self) -> List[BaseAIProvider]:
        return [_build_provider(name) for name in self.provider_chain]

    async def complete(self, messages: List[AIMessage], **kwargs) -> AICompletion:
        errors: List[AIProviderError] = []
        for provider in self._providers():
            try:
                return await provider.complete(messages, **kwargs)
            except AIProviderError as exc:
                logger.error("AI provider '%s' failed: %s", provider.name, exc)
                errors.append(exc)
                continue
        raise AIAllProvidersFailedError(errors)

    async def stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        errors: List[AIProviderError] = []
        for provider in self._providers():
            try:
                async for chunk in provider.stream(messages, **kwargs):
                    yield chunk
                return
            except AIProviderError as exc:
                logger.error("AI provider '%s' failed while streaming: %s", provider.name, exc)
                errors.append(exc)
                continue
        raise AIAllProvidersFailedError(errors)


def get_ai_client(primary: Optional[str] = None, fallbacks: Optional[List[str]] = None) -> AIClient:
    return AIClient(primary=primary, fallbacks=fallbacks)
