from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from ..evidence import is_exact_quote_supported
from ..guide import INTERVIEW_GUIDE, QUERY_EXPANSIONS
from ..llm.base import BaseLLMProvider, LLMError
from ..models import AnalysisCache, Chunk, Transcript
from ..retrieval import RetrievalResult, TfidfRetriever
from ..schemas import Evidence


SYSTEM_PROMPT = """You are a careful qualitative research analyst. Use ONLY the supplied transcript evidence. Never invent facts, timestamps, experts, or quotes. Return JSON only. Every quote must be copied verbatim from a supplied source chunk. If the evidence does not support a conclusion or the question is unrelated to the supplied evidence, state clearly in the answer that the supplied transcripts do not contain this information, and return an empty evidence list []."""



def _context_block(results: list[RetrievalResult]) -> str:
    lines = []
    for item in results:
        chunk = item.chunk
        transcript = getattr(chunk, "transcript", None)
        expert = transcript.expert_name if transcript else chunk.speaker
        market = transcript.market if transcript else ""
        header = (
            f"SOURCE_ID={chunk.id} | EXPERT={expert} | MARKET={market} | "
            f"TIMESTAMP={chunk.timestamp} | SPEAKER={chunk.speaker}"
        )
        if item.question_text:
            header += f"\nINTERVIEWER QUESTION: {item.question_text}"
        lines.append(f"{header}\nEXPERT ANSWER: {chunk.text}")
    return "\n\n".join(lines)


def _hash_key(*parts: str) -> str:
    return hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()


class Analyzer:
    def __init__(self, session: Session, retriever: TfidfRetriever, provider: BaseLLMProvider, *, cache_ttl_seconds: int = 1800):
        self.session = session
        self.retriever = retriever
        self.provider = provider
        self.cache_ttl_seconds = cache_ttl_seconds

    def rebuild_index(self) -> None:
        chunks = list(self.session.scalars(select(Chunk).options(joinedload(Chunk.transcript))).all())
        self.retriever.fit(chunks)

    def corpus_fingerprint(self) -> str:
        transcripts = list(self.session.scalars(select(Transcript).order_by(Transcript.id)).all())
        raw = "|".join(f"{item.id}:{item.filename}:{len(item.chunks)}" for item in transcripts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        item = self.session.get(AnalysisCache, key)
        if not item:
            return None
        expires_at = item.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            self.session.execute(delete(AnalysisCache).where(AnalysisCache.cache_key == key))
            self.session.commit()
            return None
        return json.loads(item.response_json)

    def _cache_set(self, key: str, kind: str, payload: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc)
        self.session.merge(
            AnalysisCache(
                cache_key=key,
                kind=kind,
                response_json=json.dumps(payload, ensure_ascii=False),
                created_at=now,
                expires_at=now + timedelta(seconds=self.cache_ttl_seconds),
            )
        )
        self.session.commit()

    def _evidence(self, source_ids: list[str], chunks_by_id: dict[str, Chunk]) -> list[Evidence]:
        output: list[Evidence] = []
        for source_id in source_ids:
            chunk = chunks_by_id.get(source_id)
            if not chunk:
                continue
            output.append(
                Evidence(
                    source_id=chunk.id,
                    expert=chunk.transcript.expert_name,
                    market=chunk.transcript.market,
                    timestamp=chunk.timestamp,
                    speaker=chunk.speaker,
                    quote=chunk.text,
                )
            )
        return output

    @staticmethod
    def _deterministic_answer(results: list[RetrievalResult]) -> str:
        if not results:
            return "The supplied transcripts do not contain enough evidence to answer this question."
        top = results[:2]
        if len(top) == 1:
            return top[0].chunk.text
        return " ".join(item.chunk.text for item in top)

    async def _llm_answer(self, question: str, results: list[RetrievalResult]) -> tuple[str, list[str]]:
        if not results:
            return "The supplied transcripts do not contain enough evidence to answer this question.", []
        source_ids = [item.chunk.id for item in results]
        context = _context_block(results)
        user_prompt = f"""Question: {question}

Evidence:
{context}

Return exactly this JSON shape:
{{"answer":"grounded synthesis","evidence":[{{"source_id":"existing source id","quote":"exact quote copied from that source"}}]}}
If the question is unrelated to the evidence or the evidence does not contain the answer, state that clearly in the answer and return an empty evidence list []."""
        try:
            payload = await self.provider.generate_json(SYSTEM_PROMPT, user_prompt)
            answer = str(payload.get("answer", "")).strip()
            evidence_items = payload.get("evidence", [])
            valid_ids: list[str] = []
            chunk_map = {item.chunk.id: item.chunk for item in results}
            for evidence in evidence_items if isinstance(evidence_items, list) else []:
                if not isinstance(evidence, dict):
                    continue
                source_id = str(evidence.get("source_id", ""))
                quote = str(evidence.get("quote", ""))
                chunk = chunk_map.get(source_id)
                if chunk and is_exact_quote_supported(quote, chunk.text):
                    valid_ids.append(source_id)
            if answer:
                score_map = {item.chunk.id: item.score for item in results}
                valid_ids.sort(key=lambda sid: score_map.get(sid, 0.0), reverse=True)
                return answer, valid_ids
        except (LLMError, ValueError, TypeError):
            pass
        return self._deterministic_answer(results), source_ids[:2]

    async def _analyze_single_guide_question(
        self,
        idx: int,
        question: str,
        transcripts: list[Transcript],
    ) -> dict[str, Any]:
        query = question + " " + " ".join(QUERY_EXPANSIONS.get(idx, []))
        grouped: dict[str, list[RetrievalResult]] = {}
        for transcript in transcripts:
            grouped[transcript.id] = self.retriever.search(query, top_k=3, transcript_id=transcript.id)

        all_results = [item for results in grouped.values() for item in results]
        prompt_context = "\n\n".join(
            f"EXPERT_TRANSCRIPT_ID={transcript.id} | EXPERT={transcript.expert_name} | MARKET={transcript.market}\n"
            + _context_block(grouped.get(transcript.id, []))
            for transcript in transcripts
        )
        llm_results: dict[str, Any] | None = None
        if all_results:
            user_prompt = f"""Question: {question}

{prompt_context}

Return exactly this JSON shape:
{{
  "answers": [
    {{"transcript_id": "existing expert transcript id", "answer": "grounded synthesis", "evidence": [{{"source_id": "existing source id", "quote": "exact quote copied from that source"}}]}}
  ]
}}
Include one answer object for every expert transcript with evidence, and use only supplied evidence."""
            try:
                payload = await self.provider.generate_json(SYSTEM_PROMPT, user_prompt)
                if isinstance(payload.get("answers"), list):
                    llm_results = payload
            except (LLMError, ValueError, TypeError):
                llm_results = None

        answers = []
        for transcript in transcripts:
            results = grouped.get(transcript.id, [])
            if not results:
                continue
            chunk_map = {chunk.id: chunk for chunk in transcript.chunks}
            selected = next((item for item in (llm_results or {}).get("answers", []) if item.get("transcript_id") == transcript.id), None)
            valid_source_ids: list[str] = []
            answer = ""
            if selected:
                answer = str(selected.get("answer", "")).strip()
                evidence_items = selected.get("evidence", [])
                for evidence in evidence_items if isinstance(evidence_items, list) else []:
                    if not isinstance(evidence, dict):
                        continue
                    source_id = str(evidence.get("source_id", ""))
                    quote = str(evidence.get("quote", ""))
                    chunk = chunk_map.get(source_id)
                    if chunk and is_exact_quote_supported(quote, chunk.text):
                        valid_source_ids.append(source_id)
            if not answer or not valid_source_ids:
                answer = self._deterministic_answer(results)
                valid_source_ids = [item.chunk.id for item in results[:2]]
            answers.append(
                {
                    "transcript_id": transcript.id,
                    "expert": transcript.expert_name,
                    "market": transcript.market,
                    "role": transcript.role,
                    "answer": answer,
                    "evidence": [e.model_dump() for e in self._evidence(valid_source_ids, chunk_map)],
                }
            )
        return {"question": question, "answers": answers}

    async def analyze_guide(self) -> dict[str, Any]:
        corpus = self.corpus_fingerprint()
        key = _hash_key("guide", corpus, self.provider.name)
        cached = self._cache_get(key)
        if cached:
            return cached

        transcripts = list(self.session.scalars(select(Transcript).order_by(Transcript.market)).all())
        question_tasks = [
            self._analyze_single_guide_question(idx, question, transcripts)
            for idx, question in enumerate(INTERVIEW_GUIDE)
        ]
        questions = await asyncio.gather(*question_tasks)

        payload = {"questions": list(questions)}
        self._cache_set(key, "guide", payload)
        return payload

    async def ask(self, question: str, transcript_id: str | None = None) -> dict[str, Any]:
        corpus = self.corpus_fingerprint()
        normalized = " ".join(question.lower().split())
        scope_key = transcript_id or "all"
        key = _hash_key("ask", corpus, self.provider.name, scope_key, normalized)
        cached = self._cache_get(key)
        if cached:
            return cached
        results = self.retriever.search(question, top_k=8, transcript_id=transcript_id)
        if not results:
            payload = {
                "answer": "The supplied transcripts do not contain any evidence to answer this question. Please ask a question related to European robotic surgery adoption.",
                "evidence": [],
            }
            self._cache_set(key, "ask", payload)
            return payload

        answer, source_ids = await self._llm_answer(question, results)
        chunk_map = {item.chunk.id: item.chunk for item in results}
        payload = {
            "answer": answer,
            "evidence": [e.model_dump() for e in self._evidence(source_ids, chunk_map)],
        }
        self._cache_set(key, "ask", payload)
        return payload


    async def cross_analysis(self) -> dict[str, Any]:
        corpus = self.corpus_fingerprint()
        key = _hash_key("cross", corpus, self.provider.name)
        cached = self._cache_get(key)
        if cached:
            return cached

        theme_specs = [
            ("Growing but uneven adoption", "adoption growing uneven hospitals access procedures standard"),
            ("Economic case, utilisation and capital pressure", "ROI budget cost total cost ownership utilisation procedure volume finance economics"),
            ("Training and operational capacity", "training surgeons staff theatre capacity utilisation"),
            ("Procurement cycles and purchase timelines", "procurement purchase decision funding capital cycle months"),
        ]
        difference_topics = [
            ("Expected growth", "15 20 percent high single digits low double digits above 15 percent procedure volumes growth"),
            ("Purchase timeline", "six twelve months nine eighteen months six nine months funding capital cycle"),
            ("Role of economics", "economic case finance ROI clinical strategy balanced outcomes"),
        ]

        theme_results = [(name, self.retriever.search(query, top_k=4)) for name, query in theme_specs]
        diff_results = [(topic, self.retriever.search(query, top_k=6)) for topic, query in difference_topics]
        all_results = []
        for _, results in theme_results + diff_results:
            all_results.extend(results)
        unique_results = []
        seen = set()
        for item in all_results:
            if item.chunk.id not in seen:
                seen.add(item.chunk.id)
                unique_results.append(item)
        context = _context_block(unique_results[:24])

        llm_payload = None
        try:
            prompt = f"""Using only the source evidence below, identify common themes and factual differences among the experts. Do not rank experts or add outside knowledge. Use source IDs for evidence.

{context}

Return exactly this JSON shape:
{{
  "themes": [{{"name": "theme", "summary": "grounded synthesis", "evidence": [{{"source_id": "existing id", "quote": "exact quote"}}]}}],
  "differences": [{{"topic": "topic", "summary": "grounded comparison", "evidence": [{{"source_id": "existing id", "quote": "exact quote"}}]}}]
}}"""
            maybe = await self.provider.generate_json(SYSTEM_PROMPT, prompt)
            if isinstance(maybe.get("themes"), list) and isinstance(maybe.get("differences"), list):
                llm_payload = maybe
        except (LLMError, ValueError, TypeError):
            llm_payload = None

        chunk_map = {item.chunk.id: item.chunk for item in unique_results}
        if llm_payload:
            def normalize_section(items, key_name):
                output = []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    evidence = []
                    for candidate in item.get("evidence", []) if isinstance(item.get("evidence", []), list) else []:
                        if not isinstance(candidate, dict):
                            continue
                        source_id = str(candidate.get("source_id", ""))
                        quote = str(candidate.get("quote", ""))
                        chunk = chunk_map.get(source_id)
                        if chunk and is_exact_quote_supported(quote, chunk.text):
                            evidence.append(Evidence(
                                source_id=chunk.id,
                                expert=chunk.transcript.expert_name,
                                market=chunk.transcript.market,
                                timestamp=chunk.timestamp,
                                speaker=chunk.speaker,
                                quote=chunk.text,
                            ).model_dump())
                    if evidence and str(item.get("summary", "")).strip():
                        cleaned = {
                            key_name: str(item.get(key_name, item.get("name", item.get("topic", "Theme")))),
                            "summary": str(item.get("summary")).strip(),
                            "evidence": evidence,
                        }
                        output.append(cleaned)
                return output

            themes = normalize_section(llm_payload.get("themes", []), "name")
            differences = normalize_section(llm_payload.get("differences", []), "topic")
            if themes and differences:
                payload = {
                    "themes": themes,
                    "differences": differences,
                    "corpus_count": self.session.query(Transcript).count(),
                }
                self._cache_set(key, "cross", payload)
                return payload

        themes = []
        for name, results in theme_results:
            unique = []
            seen_local = set()
            for item in results:
                if item.chunk.id not in seen_local:
                    seen_local.add(item.chunk.id)
                    unique.append(item)
            evidence = [Evidence(
                source_id=item.chunk.id, expert=item.chunk.transcript.expert_name, market=item.chunk.transcript.market,
                timestamp=item.chunk.timestamp, speaker=item.chunk.speaker, quote=item.chunk.text,
            ).model_dump() for item in unique[:3]]
            themes.append({"name": name, "summary": self._deterministic_answer(unique[:3]), "evidence": evidence})

        differences = []
        for topic, results in diff_results:
            evidence = [Evidence(
                source_id=item.chunk.id, expert=item.chunk.transcript.expert_name, market=item.chunk.transcript.market,
                timestamp=item.chunk.timestamp, speaker=item.chunk.speaker, quote=item.chunk.text,
            ).model_dump() for item in results[:6]]
            differences.append({"topic": topic, "summary": self._deterministic_answer(results[:4]), "evidence": evidence})

        payload = {
            "themes": themes,
            "differences": differences,
            "corpus_count": self.session.query(Transcript).count(),
        }
        self._cache_set(key, "cross", payload)
        return payload

