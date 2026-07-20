import json
from typing import AsyncIterator, List

import httpx

from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIMessage, AICompletion


class OpenAIProvider(BaseAIProvider):
    name = "openai"

    def is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

    def _payload(self, messages: List[AIMessage], stream: bool, **kwargs) -> dict:
        return {
            "model": kwargs.get("model", settings.OPENAI_MODEL),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", 0.4),
            "max_tokens": kwargs.get("max_tokens", settings.AI_MAX_OUTPUT_TOKENS),
            "stream": stream,
        }

    async def _complete(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AICompletion:
        resp = await client.post(
            f"{settings.OPENAI_BASE_URL}/chat/completions",
            headers=self._headers(),
            json=self._payload(messages, stream=False, **kwargs),
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return AICompletion(
            content=content,
            provider=self.name,
            model=data.get("model", settings.OPENAI_MODEL),
            raw=data,
            usage=data.get("usage"),
        )

    async def _stream(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        async with client.stream(
            "POST",
            f"{settings.OPENAI_BASE_URL}/chat/completions",
            headers=self._headers(),
            json=self._payload(messages, stream=True, **kwargs),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
