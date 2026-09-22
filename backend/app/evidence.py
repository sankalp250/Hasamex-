from __future__ import annotations

import re
import unicodedata


def normalize_for_match(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.casefold()


def is_exact_quote_supported(quote: str, source_text: str) -> bool:
    if not quote.strip() or not source_text.strip():
        return False
    return normalize_for_match(quote) in normalize_for_match(source_text)
