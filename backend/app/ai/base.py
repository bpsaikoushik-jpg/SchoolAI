"""Abstract base for AI providers (OpenAI, Gemini, Claude, ...).

Every concrete provider implements only the raw `_complete` / `_stream`
calls against its own HTTP API. Retry, timeout, and error normalization
are handled once, here, so every provider behaves the same way from the
caller's perspective (SchoolAI's AI Mentor, Teacher AI, Parent AI, etc.
never need to know which provider answered).
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, List

import httpx

from app.core.config import settings
from app.ai.schemas import AIMessage, AICompletion, AIProviderError

logger = logging.getLogger("schoolai.ai")


class BaseAIProvider(ABC):
    name: str = "base"

    def __init__(
        self,
        timeout: float = settings.AI_REQUEST_TIMEOUT_SECONDS,
        max_retries: int = settings.AI_MAX_RETRIES,
        backoff_seconds: float = settings.AI_RETRY_BACKOFF_SECONDS,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    # -- to be implemented by concrete providers --------------------------
    @abstractmethod
    async def _complete(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AICompletion:
        ...

    @abstractmethod
    async def _stream(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        ...

    def is_configured(self) -> bool:
        """Whether this provider has the credentials it needs to run."""
        return True

    # -- public API used by services (retry + timeout + error recovery) ---
    async def complete(self, messages: List[AIMessage], **kwargs) -> AICompletion:
        if not self.is_configured():
            raise AIProviderError(self.name, "provider is not configured (missing API key)", retriable=False)

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    return await self._complete(client, messages, **kwargs)
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("AI provider %s timed out (attempt %s/%s)", self.name, attempt + 1, self.max_retries + 1)
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                # 429/5xx are transient - worth retrying. 4xx (other than 429) are not.
                if status == 429 or status >= 500:
                    last_error = exc
                    logger.warning("AI provider %s returned %s (attempt %s/%s)", self.name, status, attempt + 1, self.max_retries + 1)
                else:
                    raise AIProviderError(self.name, f"HTTP {status}: {exc.response.text[:300]}", retriable=False) from exc
            except (httpx.TransportError, httpx.ConnectError) as exc:
                last_error = exc
                logger.warning("AI provider %s connection error (attempt %s/%s): %s", self.name, attempt + 1, self.max_retries + 1, exc)

            if attempt < self.max_retries:
                await asyncio.sleep(self.backoff_seconds * (2 ** attempt))

        raise AIProviderError(self.name, f"exhausted retries: {last_error}", retriable=True)

    async def stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        if not self.is_configured():
            raise AIProviderError(self.name, "provider is not configured (missing API key)", retriable=False)

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async for chunk in self._stream(client, messages, **kwargs):
                        yield chunk
                    return
            except httpx.TimeoutException as exc:
                last_error = exc
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 429 or status >= 500:
                    last_error = exc
                else:
                    raise AIProviderError(self.name, f"HTTP {status}: {exc.response.text[:300]}", retriable=False) from exc
            except (httpx.TransportError, httpx.ConnectError) as exc:
                last_error = exc

            if attempt < self.max_retries:
                logger.warning("AI provider %s stream failed, retrying (attempt %s/%s)", self.name, attempt + 1, self.max_retries + 1)
                await asyncio.sleep(self.backoff_seconds * (2 ** attempt))
            else:
                raise AIProviderError(self.name, f"exhausted retries: {last_error}", retriable=True)
