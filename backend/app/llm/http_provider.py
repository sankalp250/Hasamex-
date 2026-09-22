from __future__ import annotations

import json
from typing import Any

import httpx

from .base import BaseLLMProvider, LLMError


class JsonHttpLLMProvider(BaseLLMProvider):
    def __init__(self, *, api_key: str, model: str, timeout: float = 30.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @staticmethod
    def parse_json_payload(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                value = json.loads(cleaned[start : end + 1])
            else:
                raise LLMError("LLM did not return valid JSON.") from exc
        if not isinstance(value, dict):
            raise LLMError("LLM JSON response must be an object.")
        return value

    async def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMError(f"LLM provider request failed: {exc}") from exc
        return self.extract_text(data)

    def extract_text(self, data: dict[str, Any]) -> str:
        raise NotImplementedError
