from pathlib import Path

from app.parser import parse_transcript
from app.retrieval import TfidfRetriever


def test_retrieval_finds_barriers(tmp_path):
    from app.models import Chunk, Transcript

    path = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "Transcript_2_Germany.txt"
    parsed = parse_transcript(path.read_text(encoding="utf-8"), path.name)
    transcript = Transcript(
        id="test-transcript",
        filename=path.name,
        expert_name=parsed.expert_name,
        role=parsed.role,
        market=parsed.market,
        raw_text=path.read_text(encoding="utf-8"),
    )
    chunks = [
        Chunk(
            id=turn.id,
            transcript_id=transcript.id,
            ordinal=turn.ordinal,
            timestamp=turn.timestamp,
            speaker=turn.speaker,
            text=turn.text,
            is_interviewer=turn.is_interviewer,
        )
        for turn in parsed.turns
    ]
    retriever = TfidfRetriever()
    retriever.fit(chunks)
    results = retriever.search("capital cost utilization barriers", top_k=3)
    assert results
    assert any("Cost is the first barrier" in item.chunk.text for item in results)


def test_retrieval_uk_roi_matches_correct_answer_timestamp():
    from app.models import Chunk, Transcript

    path = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "Transcript_3_UK.txt"
    parsed = parse_transcript(path.read_text(encoding="utf-8"), path.name)
    transcript = Transcript(
        id="uk-transcript",
        filename=path.name,
        expert_name=parsed.expert_name,
        role=parsed.role,
        market=parsed.market,
        raw_text=path.read_text(encoding="utf-8"),
    )
    chunks = [
        Chunk(
            id=turn.id,
            transcript_id=transcript.id,
            ordinal=turn.ordinal,
            timestamp=turn.timestamp,
            speaker=turn.speaker,
            text=turn.text,
            is_interviewer=turn.is_interviewer,
        )
        for turn in parsed.turns
    ]
    for c in chunks:
        c.transcript = transcript

    retriever = TfidfRetriever()
    retriever.fit(chunks)
    results = retriever.search("How important is ROI?", top_k=1)
    assert len(results) == 1
    top = results[0]
    assert top.chunk.timestamp == "02:07"
    assert "It matters, but the discussion is not always purely financial" in top.chunk.text
    assert top.question_text == "How important is ROI?"
    assert top.question_timestamp == "02:02"


def test_retrieval_scope_filtering():
    from app.models import Chunk, Transcript

    t1_path = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "Transcript_1_France.txt"
    t3_path = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "Transcript_3_UK.txt"

    p1 = parse_transcript(t1_path.read_text(encoding="utf-8"), t1_path.name)
    p3 = parse_transcript(t3_path.read_text(encoding="utf-8"), t3_path.name)

    t1 = Transcript(id="fr-id", filename=t1_path.name, expert_name=p1.expert_name, role=p1.role, market=p1.market, raw_text="")
    t3 = Transcript(id="uk-id", filename=t3_path.name, expert_name=p3.expert_name, role=p3.role, market=p3.market, raw_text="")

    chunks = []
    for turn in p1.turns:
        c = Chunk(id=turn.id, transcript_id=t1.id, ordinal=turn.ordinal, timestamp=turn.timestamp, speaker=turn.speaker, text=turn.text, is_interviewer=turn.is_interviewer)
        c.transcript = t1
        chunks.append(c)
    for turn in p3.turns:
        c = Chunk(id=turn.id, transcript_id=t3.id, ordinal=turn.ordinal, timestamp=turn.timestamp, speaker=turn.speaker, text=turn.text, is_interviewer=turn.is_interviewer)
        c.transcript = t3
        chunks.append(c)

    retriever = TfidfRetriever()
    retriever.fit(chunks)

    # Scoped to UK only
    uk_results = retriever.search("How important is ROI?", transcript_id="uk-id", top_k=5)
    assert uk_results
    assert all(r.chunk.transcript_id == "uk-id" for r in uk_results)
    assert uk_results[0].chunk.timestamp == "02:07"
