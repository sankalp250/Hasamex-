from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

TIMESTAMP_RE = re.compile(r"^(?P<timestamp>\d{2}:\d{2})\s*$")
HEADER_EXPERT_RE = re.compile(r"^Expert\s+\d+\s*[–-]\s*(?P<expert>.+?)\s*$")
HEADER_ROLE_RE = re.compile(r"^Role:\s*(?P<role>.+?)\s*$")
HEADER_MARKET_RE = re.compile(r"^Market:\s*(?P<market>.+?)\s*$")
SPEAKER_RE = re.compile(r"^(?P<speaker>[^:]{1,100}):\s*(?P<text>.*)$")


@dataclass(frozen=True)
class ParsedTurn:
    id: str
    ordinal: int
    timestamp: str
    speaker: str
    text: str
    is_interviewer: bool


@dataclass(frozen=True)
class ParsedTranscript:
    expert_name: str
    role: str
    market: str
    turns: list[ParsedTurn]


def parse_transcript(text: str, filename: str) -> ParsedTranscript:
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]
    expert_name = "Unknown Expert"
    role = "Unknown Role"
    market = "Unknown Market"
    for line in lines[:10]:
        if match := HEADER_EXPERT_RE.match(line):
            expert_name = match.group("expert")
        elif match := HEADER_ROLE_RE.match(line):
            role = match.group("role")
        elif match := HEADER_MARKET_RE.match(line):
            market = match.group("market")

    turns: list[ParsedTurn] = []
    i = 0
    ordinal = 0
    while i < len(lines):
        timestamp_match = TIMESTAMP_RE.match(lines[i])
        if not timestamp_match:
            i += 1
            continue
        timestamp = timestamp_match.group("timestamp")
        body: list[str] = []
        i += 1
        while i < len(lines) and not TIMESTAMP_RE.match(lines[i]):
            if lines[i]:
                body.append(lines[i])
            i += 1
        if not body:
            continue
        speaker_match = SPEAKER_RE.match(body[0])
        if speaker_match:
            speaker = speaker_match.group("speaker").strip()
            text_part = speaker_match.group("text").strip()
            continuation = " ".join(body[1:]).strip()
            text_value = " ".join(part for part in [text_part, continuation] if part)
        else:
            speaker = "Unknown"
            text_value = " ".join(body).strip()
        if not text_value:
            continue
        raw_id = f"{filename}:{ordinal}:{timestamp}:{speaker}:{text_value}".encode("utf-8")
        chunk_id = hashlib.sha1(raw_id).hexdigest()[:24]
        turns.append(
            ParsedTurn(
                id=chunk_id,
                ordinal=ordinal,
                timestamp=timestamp,
                speaker=speaker,
                text=text_value,
                is_interviewer=speaker.lower() == "interviewer",
            )
        )
        ordinal += 1
    if not turns:
        raise ValueError("No timestamped transcript turns were found in the uploaded file.")
    return ParsedTranscript(expert_name=expert_name, role=role, market=market, turns=turns)


def read_txt_file(path: Path) -> tuple[str, ParsedTranscript]:
    text = path.read_text(encoding="utf-8")
    return text, parse_transcript(text, path.name)
