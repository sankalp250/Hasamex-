def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seeded_transcripts(client):
    response = client.get("/api/transcripts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {item["market"] for item in data} == {"France", "Germany", "United Kingdom"}


def test_guide_questions(client):
    response = client.get("/api/guide/questions")
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 6


def test_upload_txt(client):
    content = """Expert 4 – Alex Morgan\nRole: Hospital Operations Lead\nMarket: Spain\n\n00:00\nInterviewer: How would you describe adoption?\n\n00:14\nAlex Morgan: Adoption is early, but interest is increasing.\n"""
    response = client.post(
        "/api/transcripts/upload",
        files={"file": ("Transcript_4_Spain.txt", content.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["market"] == "Spain"


def test_reject_non_txt(client):
    response = client.post(
        "/api/transcripts/upload",
        files={"file": ("notes.pdf", b"nope", "application/pdf")},
    )
    assert response.status_code == 400


def test_guide_analysis(client):
    response = client.post("/api/guide/analyze")
    assert response.status_code == 200
    body = response.json()
    assert len(body["questions"]) == 6
    first = body["questions"][0]["answers"]
    assert len(first) == 3
    assert first[0]["evidence"]
    assert first[0]["evidence"][0]["timestamp"]


def test_cross_analysis(client):
    response = client.get("/api/analysis/cross")
    assert response.status_code == 200
    body = response.json()
    assert body["corpus_count"] == 3
    assert len(body["themes"]) >= 3
    assert len(body["differences"]) == 3


def test_grounded_ask(client):
    response = client.post("/api/ask", json={"question": "What are the main barriers to adoption?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["evidence"]) >= 1
    quotes = [item["quote"] for item in body["evidence"]]
    assert any("capital budget approval" in quote.lower() or "cost is the first barrier" in quote.lower() or "training capacity" in quote.lower() for quote in quotes)


def test_grounded_ask_scoped_uk(client):
    transcripts = client.get("/api/transcripts").json()
    uk_t = next(t for t in transcripts if t["market"] == "United Kingdom")
    response = client.post(
        "/api/ask",
        json={"question": "How important is ROI?", "transcript_id": uk_t["id"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["evidence"]) >= 1
    # Evidence must come from UK and have timestamp 02:07
    first_evidence = body["evidence"][0]
    assert first_evidence["market"] == "United Kingdom"
    assert first_evidence["timestamp"] == "02:07"
    assert "It matters, but the discussion is not always purely financial" in first_evidence["quote"]
