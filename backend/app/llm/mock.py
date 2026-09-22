from __future__ import annotations

from typing import Any

from .base import BaseLLMProvider


class DeterministicLocalProvider(BaseLLMProvider):
    """No-network fallback used for local development and automated tests."""

    name = "mock"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        # Analyzer owns the exact deterministic behavior. This provider is only
        # instantiated to satisfy the provider interface when no key is configured.
        return {"answer": "", "evidence": []}
