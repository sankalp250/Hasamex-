from __future__ import annotations

from typing import Any

from .http_provider import JsonHttpLLMProvider


class GroqProvider(JsonHttpLLMProvider):
    name = "groq"

    def __init__(self, *, api_key: str, model: str, timeout: float = 30.0) -> None:
        super().__init__(api_key=api_key, model=model, timeout=timeout)

    def extract_text(self, data: dict[str, Any]) -> str:
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Unexpected Groq response shape.") from exc

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        text = await self.post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload,
        )
        return self.parse_json_payload(text)
