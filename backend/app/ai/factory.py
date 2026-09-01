"""Gemini-only AI client used by all AI-powered services."""

import logging
from typing import AsyncIterator, List

from app.ai.schemas import AIMessage, AICompletion
from app.ai.providers.gemini_provider import GeminiProvider


logger = logging.getLogger("schoolai.ai")


class AIClient:
    """AI client that uses Gemini only."""

    def __init__(self):
        self.provider = GeminiProvider()

    async def complete(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AICompletion:

        try:
            return await self.provider.complete(
                messages,
                **kwargs
            )

        except Exception as exc:
            logger.error(
                "Gemini provider failed: %s",
                exc
            )
            raise

    async def stream(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:

        try:
            async for chunk in self.provider.stream(
                messages,
                **kwargs
            ):
                yield chunk

        except Exception as exc:
            logger.error(
                "Gemini provider failed while streaming: %s",
                exc
            )
            raise


def get_ai_client() -> AIClient:
    """Return the Gemini-only AI client."""
    return AIClient()
