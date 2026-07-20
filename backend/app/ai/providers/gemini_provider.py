import json
from typing import AsyncIterator, List

import httpx

from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIMessage, AICompletion


class GeminiProvider(BaseAIProvider):
    name = "gemini"

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    @staticmethod
    def _split_system(messages: List[AIMessage]):
        system_parts = [m.content for m in messages if m.role == "system"]
        turns = [m for m in messages if m.role != "system"]
        system_instruction = "\n\n".join(system_parts) if system_parts else None
        contents = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
            for m in turns
        ]
        return system_instruction, contents

    def _payload(self, messages: List[AIMessage], **kwargs) -> dict:
        system_instruction, contents = self._split_system(messages)
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.4),
                "maxOutputTokens": kwargs.get("max_tokens", settings.AI_MAX_OUTPUT_TOKENS),
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        return payload

    async def _complete(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AICompletion:
        model = kwargs.get("model", settings.GEMINI_MODEL)
        url = f"{settings.GEMINI_BASE_URL}/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
        resp = await client.post(url, json=self._payload(messages, **kwargs))
        resp.raise_for_status()
        data = resp.json()
        content = "".join(
            part.get("text", "") for part in data["candidates"][0]["content"]["parts"]
        )
        return AICompletion(
            content=content,
            provider=self.name,
            model=model,
            raw=data,
            usage=data.get("usageMetadata"),
        )

    async def _stream(self, client: httpx.AsyncClient, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        model = kwargs.get("model", settings.GEMINI_MODEL)
        url = f"{settings.GEMINI_BASE_URL}/models/{model}:streamGenerateContent?alt=sse&key={settings.GEMINI_API_KEY}"
        async with client.stream("POST", url, json=self._payload(messages, **kwargs)) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if not data_str:
                    continue
                try:
                    chunk = json.loads(data_str)
                    for part in chunk["candidates"][0]["content"]["parts"]:
                        text = part.get("text")
                        if text:
                            yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
