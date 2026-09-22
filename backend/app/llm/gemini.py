from __future__ import annotations

from typing import Any

from .base import LLMError
from .http_provider import JsonHttpLLMProvider


class GeminiProvider(JsonHttpLLMProvider):
    name = "gemini"

    def __init__(self, *, api_key: str, model: str, timeout: float = 30.0) -> None:
        super().__init__(api_key=api_key, model=model, timeout=timeout)

    def extract_text(self, data: dict[str, Any]) -> str:
        try:
            return "".join(
                part.get("text", "")
                for part in data["candidates"][0]["content"]["parts"]
                if isinstance(part, dict)
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Unexpected Gemini response shape.") from exc

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
            },
        }
        text = await self.post_json(url, {"Content-Type": "application/json"}, payload)
        return self.parse_json_payload(text)
