import pytest

from app.llm.http_provider import JsonHttpLLMProvider


def test_parse_json_payload():
    assert JsonHttpLLMProvider.parse_json_payload('{"answer":"ok"}') == {"answer": "ok"}
    assert JsonHttpLLMProvider.parse_json_payload("```json\n{\"answer\":\"ok\"}\n```") == {"answer": "ok"}


def test_parse_json_payload_rejects_invalid():
    with pytest.raises(Exception):
        JsonHttpLLMProvider.parse_json_payload("not json")
