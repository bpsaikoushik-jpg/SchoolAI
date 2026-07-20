import json
from typing import AsyncIterator, List

import httpx

from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIMessage, AICompletion


class ClaudeProvider(BaseAIProvider):
    name = "claude"

    def is_configured(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    def _headers(self) -> dict:
        return {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _split_system(messages: List[AIMessage]):
        system_parts = [m.content for m in messages if m.role == "system"]
        turns = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        return "\n\n".join(system_parts) if system_parts else None, turns

    def _payload(self, messages: List[AIMessage], stream: bool, **kwargs) -> dict:
        system, turns = self._split_system(messages)
        payload = {
            "model": kwargs.get("model", settings.ANTHROPIC_MODEL),
            "messages": turns,
            "max_tokens": kwargs.get("max_tokens", settings.AI_MAX_OUTPUT_TOKENS),
            "temperature": kwargs.get("temperature", 0.4),
            "stream": stream,
        }
        if system:
            payload["system"] = system
        return payload

    async def _complete(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AICompletion:
        resp = await client.post(
            f"{settings.ANTHROPIC_BASE_URL}/messages",
            headers=self._headers(),
            json=self._payload(messages, stream=False, **kwargs),
        )
        resp.raise_for_status()
        data = resp.json()
        content = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return AICompletion(
            content=content,
            provider=self.name,
            model=data.get("model", settings.ANTHROPIC_MODEL),
            raw=data,
            usage=data.get("usage"),
        )

    async def _stream(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        async with client.stream(
            "POST",
            f"{settings.ANTHROPIC_BASE_URL}/messages",
            headers=self._headers(),
            json=self._payload(messages, stream=True, **kwargs),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if not data_str:
                    continue
                try:
                    event = json.loads(data_str)
                    if event.get("type") == "content_block_delta":
                        text = event.get("delta", {}).get("text")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue
