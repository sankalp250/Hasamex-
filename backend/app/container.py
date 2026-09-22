from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .core.config import Settings
from .llm.gemini import GeminiProvider
from .llm.groq import GroqProvider
from .llm.mock import DeterministicLocalProvider
from .models import Chunk, Transcript
from .parser import parse_transcript
from .retrieval import TfidfRetriever
from .services.analyzer import Analyzer


class ServiceContainer:
    def __init__(self, session_factory, settings: Settings, provider_override=None):
        self.session_factory = session_factory
        self.settings = settings
        self.retriever = TfidfRetriever()
        self.provider = provider_override or self._build_provider()
        self.analyzer: Analyzer | None = None

    def _build_provider(self):
        if self.settings.llm_provider == "gemini" and self.settings.gemini_api_key:
            return GeminiProvider(
                api_key=self.settings.gemini_api_key,
                model=self.settings.gemini_model,
                timeout=self.settings.llm_timeout_seconds,
            )
        if self.settings.llm_provider == "groq" and self.settings.groq_api_key and self.settings.groq_model:
            return GroqProvider(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model,
                timeout=self.settings.llm_timeout_seconds,
            )
        return DeterministicLocalProvider()

    def new_analyzer(self, session: Session) -> Analyzer:
        analyzer = Analyzer(
            session,
            self.retriever,
            self.provider,
            cache_ttl_seconds=self.settings.cache_ttl_seconds,
        )
        if not self.retriever._chunks:
            analyzer.rebuild_index()
        return analyzer

    def ingest(self, session: Session, filename: str, raw_text: str):
        parsed = parse_transcript(raw_text, filename)
        transcript = Transcript(
            id=__import__("uuid").uuid4().hex,
            filename=filename,
            expert_name=parsed.expert_name,
            role=parsed.role,
            market=parsed.market,
            raw_text=raw_text,
        )
        for turn in parsed.turns:
            transcript.chunks.append(
                Chunk(
                    id=turn.id,
                    ordinal=turn.ordinal,
                    timestamp=turn.timestamp,
                    speaker=turn.speaker,
                    text=turn.text,
                    is_interviewer=turn.is_interviewer,
                )
            )
        session.add(transcript)
        session.commit()
        analyzer = self.new_analyzer(session)
        analyzer.rebuild_index()
        return transcript

    def seed_if_empty(self, session: Session, seed_dir: Path) -> None:
        if session.scalar(select(Transcript.id).limit(1)):
            analyzer = self.new_analyzer(session)
            analyzer.rebuild_index()
            return
        for path in sorted(seed_dir.glob("*.txt")):
            raw_text = path.read_text(encoding="utf-8")
            self.ingest(session, path.name, raw_text)
