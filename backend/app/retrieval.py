from __future__ import annotations

import re
from dataclasses import dataclass
from threading import RLock

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from .models import Chunk

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float
    question_text: str = ""
    question_timestamp: str = ""


@dataclass(frozen=True)
class InterviewExchange:
    answer_chunk: Chunk
    question_chunk: Chunk | None
    question_text: str
    question_timestamp: str
    transcript_id: str
    market: str
    expert_name: str
    role: str
    search_text: str


class TfidfRetriever:
    """Production-grade interview exchange retriever.

    Pairs interviewer questions with expert answers into semantic exchanges
    so queries matching the interviewer's question (e.g. 'How important is ROI?')
    accurately retrieve the expert's answer and citation timestamp (e.g. 02:07).
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._exchanges: list[InterviewExchange] = []
        self._chunks: list[Chunk] = []

    @staticmethod
    def _normalize_query(query: str) -> str:
        return " ".join(TOKEN_RE.findall(query.lower()))

    def fit(self, chunks: list[Chunk]) -> None:
        sorted_chunks = sorted(chunks, key=lambda c: (c.transcript_id or "", c.ordinal))
        exchanges: list[InterviewExchange] = []
        current_interviewer: Chunk | None = None
        current_transcript_id: str | None = None

        for chunk in sorted_chunks:
            if chunk.transcript_id != current_transcript_id:
                current_transcript_id = chunk.transcript_id
                current_interviewer = None

            if chunk.is_interviewer:
                current_interviewer = chunk
            else:
                transcript = getattr(chunk, "transcript", None)
                market = transcript.market if transcript else ""
                expert_name = transcript.expert_name if transcript else chunk.speaker
                role = transcript.role if transcript else ""
                q_text = current_interviewer.text if current_interviewer else ""
                q_ts = current_interviewer.timestamp if current_interviewer else ""

                search_text = (
                    f"Market: {market} | Expert: {expert_name} | Role: {role} | "
                    f"Speaker: {chunk.speaker} | Question: {q_text} | Answer: {chunk.text}"
                )
                exchanges.append(
                    InterviewExchange(
                        answer_chunk=chunk,
                        question_chunk=current_interviewer,
                        question_text=q_text,
                        question_timestamp=q_ts,
                        transcript_id=chunk.transcript_id,
                        market=market,
                        expert_name=expert_name,
                        role=role,
                        search_text=search_text,
                    )
                )

        texts = [exc.search_text for exc in exchanges]
        with self._lock:
            self._exchanges = exchanges
            self._chunks = [exc.answer_chunk for exc in exchanges]
            if not texts:
                self._vectorizer = None
                self._matrix = None
                return
            self._vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
                stop_words="english",
            )
            self._matrix = self._vectorizer.fit_transform(texts)

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        transcript_id: str | None = None,
        min_score: float = 0.01,
    ) -> list[RetrievalResult]:
        with self._lock:
            if self._vectorizer is None or self._matrix is None or not self._exchanges:
                return []
            filtered = list(enumerate(self._exchanges))
            if transcript_id:
                filtered = [(idx, exc) for idx, exc in filtered if exc.transcript_id == transcript_id]
            if not filtered:
                return []
            normalized = self._normalize_query(query)
            if not normalized:
                return []
            indices = [idx for idx, _ in filtered]
            query_vector = self._vectorizer.transform([normalized])
            scores = linear_kernel(query_vector, self._matrix[indices]).flatten()
            ranked = sorted(
                zip(scores.tolist(), filtered, strict=False),
                key=lambda item: item[0],
                reverse=True,
            )
            return [
                RetrievalResult(
                    chunk=exc.answer_chunk,
                    score=float(score),
                    question_text=exc.question_text,
                    question_timestamp=exc.question_timestamp,
                )
                for score, (_, exc) in ranked[:top_k]
                if float(score) >= min_score
            ]
