# Architecture

## 1. System architecture

```text
┌─────────────────────────── Browser ───────────────────────────┐
│ React + Vite                                                  │
│  Dashboard | Guide | Cross-analysis | Ask | Upload           │
└─────────────────────────────┬────────────────────────────────┘
                              │ HTTPS/JSON
                              ▼
┌────────────────────────── FastAPI ────────────────────────────┐
│ API layer                                                     │
│  Validation / auth boundary / rate-limit boundary            │
│              │                                                │
│              ▼                                                │
│      Application services                                     │
│  parser · retrieval · analysis · evidence validation         │
│              │                │                               │
│              ├───────────────►│ LLM provider abstraction      │
│              │                │ Gemini / Groq / local         │
│              ▼                ▼                               │
│        SQLAlchemy        Analysis cache                       │
└────────────┬──────────────────┬───────────────────────────────┘
             │                  │
             ▼                  ▼
       SQLite (MVP)       TF-IDF sparse index (MVP)

Scale path:
SQLite -> PostgreSQL
local text -> object storage
TF-IDF -> vector/hybrid search service
DB cache -> Redis
single process -> stateless API replicas + workers
```

## 2. Data flow

1. User uploads `.txt`.
2. Parser extracts expert, role, market, timestamp, speaker and text.
3. Transcript and timestamp-preserving chunks are stored in SQL.
4. Retrieval index is rebuilt in-process for the MVP.
5. A guide question or user question is converted to a retrieval query.
6. Top evidence chunks are selected, optionally per expert.
7. LLM receives only the selected evidence.
8. LLM returns structured answer + source IDs + exact quote candidates.
9. Backend resolves source IDs and validates quotes against original chunk text.
10. React renders answer, evidence and timestamps.

## 3. Database schema

### transcripts

- `id` UUID-like string primary key
- `filename`
- `expert_name`
- `role`
- `market`
- `raw_text`
- `created_at`
- `updated_at`

### chunks

- `id` stable source ID
- `transcript_id` foreign key
- `ordinal`
- `timestamp`
- `speaker`
- `text`
- `is_interviewer`
- index on `(transcript_id, ordinal)`

### analysis_cache

- `cache_key` primary key
- `kind`
- `response_json`
- `created_at`
- `expires_at`

## 4. API design

### `GET /api/health`
Readiness/health response.

### `GET /api/transcripts`
Returns loaded transcript metadata and chunk counts.

### `POST /api/transcripts/upload`
Multipart `.txt` upload. Re-parses and indexes the document.

### `GET /api/guide/questions`
Returns the six case-study interview-guide questions.

### `POST /api/guide/analyze`
Runs all six questions. Each result is grouped by expert and includes validated evidence.

### `GET /api/analysis/cross`
Synthesizes common themes and factual differences across the loaded corpus.

### `POST /api/ask`
Grounded Q&A across all loaded transcripts.

## 5. Caching strategy

The MVP stores analysis responses in SQLite with a corpus fingerprint in the cache key. A new upload changes the fingerprint and naturally invalidates old responses.

At scale, use Redis with TTLs and include:

- corpus version
- normalized request
- model/provider
- prompt version

in the cache key.

## 6. Reliability / hallucination controls

- The transcript is the source of truth.
- The model receives only retrieved evidence.
- The model must return source IDs.
- Backend resolves metadata from the database, not from model-generated timestamps.
- Candidate quotes are checked against the original chunk after whitespace normalization.
- When provider configuration is absent, a deterministic local fallback returns extracted evidence instead of fabricating unsupported content.

## 7. Scalability path

For millions of users, keep the React frontend static/CDN-hosted and make FastAPI stateless. Store uploads in object storage, metadata in PostgreSQL, retrieval in a durable vector/hybrid search service, cache hot reads in Redis, and move long-running analyses to a queue/worker layer. The current interfaces intentionally isolate those infrastructure decisions.
