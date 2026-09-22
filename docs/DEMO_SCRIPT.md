# 5–7 minute demo flow

## 1. Product (30–45 sec)

"This is a source-grounded interview intelligence tool. It loads the three supplied European robotic surgery interviews, answers the six interview-guide questions, compares themes and differences, and supports questions across the corpus."

## 2. Show the corpus (30 sec)

Open Overview. Point out the three seeded interviews and the Add Transcript control.

## 3. Interview guide (60–90 sec)

Open Interview guide. Show one question across France, Germany and the UK. Click through the evidence cards and explain that timestamps come from the database, not from the LLM.

## 4. Cross analysis (45–60 sec)

Show common themes and differences. Call out that summaries stay attached to source evidence.

## 5. Ask the corpus (60 sec)

Ask: "What are the main barriers to adoption?" Show answer plus evidence. Ask one follow-up about purchase timelines.

## 6. Upload (30 sec)

Upload another `.txt` transcript. Return to Overview and show that the corpus count increases.

## 7. Architecture (90 sec)

Explain: React -> FastAPI -> SQLAlchemy/SQLite -> retrieval -> LLM provider -> evidence validation -> React. Then explain that the scale path swaps SQLite for Postgres, local search for durable hybrid/vector search, and the local cache for Redis without changing API contracts.

## 8. Hallucination controls (30 sec)

"The transcript remains the source of truth. The LLM receives retrieved evidence and returns source IDs. FastAPI resolves those IDs and validates candidate quotes against the original text before the UI displays them."
