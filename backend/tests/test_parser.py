from pathlib import Path

from app.parser import parse_transcript


ROOT = Path(__file__).resolve().parents[1] / "data" / "transcripts"


def test_parse_france():
    text = (ROOT / "Transcript_1_France.txt").read_text(encoding="utf-8")
    parsed = parse_transcript(text, "Transcript_1_France.txt")
    assert parsed.expert_name == "Dr. Jean Martin"
    assert parsed.role == "Head of Urology"
    assert parsed.market == "France"
    assert len(parsed.turns) == 14
    answer = [turn for turn in parsed.turns if not turn.is_interviewer][0]
    assert answer.timestamp == "00:18"
    assert "Adoption is growing" in answer.text


def test_parse_all_seed_transcripts():
    expected_markets = {"France", "Germany", "United Kingdom"}
    markets = set()
    for path in ROOT.glob("*.txt"):
        parsed = parse_transcript(path.read_text(encoding="utf-8"), path.name)
        markets.add(parsed.market)
        assert parsed.turns
        assert all(turn.timestamp and turn.text for turn in parsed.turns)
    assert markets == expected_markets
