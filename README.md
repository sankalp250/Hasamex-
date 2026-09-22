# Hasamex Expert Interview Analyzer

A production-minded AI research MVP for the Hasamex AI Engineer case study.

The application ingests timestamped expert-call transcripts, answers the interview guide, surfaces exact evidence with source timestamps, compares themes/disagreements across experts, and supports grounded questions across the corpus.

## Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI + SQLAlchemy 2
- **Local database:** SQLite (easy local development; Postgres is the intended production swap)
- **Retrieval:** TF-IDF sparse retrieval with a clean retriever interface so it can be replaced by a vector database/embedding service at scale
- **LLM:** Provider abstraction for Gemini or Groq, plus a deterministic local fallback for development/tests
- **Testing:** Pytest + Vitest + production frontend build

## Features

- Preloads the three supplied France/Germany/UK transcripts
- Upload additional `.txt` transcripts from the UI
- Preserves expert, role, market, speaker, and timestamp metadata
- Interview-guide analysis for all 6 supplied questions
- Exact quote validation against the original transcript text
- Cross-interview themes and differences
- Grounded question answering across all loaded transcripts
- Source chips showing expert, market and timestamp
- Local fallback mode so the app runs without an API key
- Optional LLM mode using Gemini or Groq

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows cmd
# cp .env.example .env   # macOS/Linux
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:8000` for the API.

## LLM configuration

The app is intentionally runnable without a key. Set these in `backend/.env` when you want model-generated synthesis:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

or:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=your_model_here
```

If the selected provider is not configured, the backend automatically uses the deterministic local provider and still returns source-grounded results.

## API

- `GET /api/health`
- `GET /api/transcripts`
- `POST /api/transcripts/upload`
- `GET /api/guide/questions`
- `POST /api/guide/analyze`
- `GET /api/analysis/cross`
- `POST /api/ask`

Interactive API docs are available at `/docs`.

## Architecture

See `docs/ARCHITECTURE.md` for the current MVP architecture and the scale-out path.

## Testing

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```

## Production scale path

The implementation deliberately keeps the local developer experience small. At higher scale, the interfaces allow these swaps without redesigning the API surface:

- SQLite -> PostgreSQL
- local transcript storage -> object storage
- in-process retrieval -> managed vector/search infrastructure
- local cache -> Redis
- single FastAPI process -> horizontally scaled stateless API workers
- direct provider calls -> queued background jobs for long analyses
