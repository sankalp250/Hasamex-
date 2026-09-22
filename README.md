# Hasamex Research Intelligence — Expert Interview Analyzer

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7.1-646CFF.svg?logo=vite)](https://vitejs.dev)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4285F4.svg?logo=google)](https://deepmind.google/technologies/gemini/)

> 🚀 **Live Production Web Application:** [https://hasamex-omega.vercel.app/](https://hasamex-omega.vercel.app/)  
> ⚡ **Backend API & Swagger Docs:** [https://hasamex-backend-s17e.onrender.com/docs](https://hasamex-backend-s17e.onrender.com/docs)  
> 📦 **GitHub Repository:** [https://github.com/sankalp250/Hasamex-](https://github.com/sankalp250/Hasamex-)

A production-grade Retrieval-Augmented Generation (RAG) platform purpose-built for the **Hasamex AI Engineer Case Study**. 

The application ingests timestamped qualitative interview transcripts, synthesizes the 6 core interview-guide benchmarks across European healthcare markets, extracts verified verbatim quotes with source timestamps, performs comparative cross-interview analysis, and provides grounded question-answering with dynamic search scope filtering.

---

## Table of Contents
1. [Core Architectural Innovations](#core-architectural-innovations)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Live Features](#live-features)
5. [Quickstart (Local Development)](#quickstart-local-development)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment Guide (Render & Vercel)](#cloud-deployment-guide-render--vercel)
8. [API Reference](#api-reference)
9. [Automated Testing & Verification](#automated-testing--verification)
10. [Scaling from 3 to 30+ Transcripts](#scaling-from-3-to-30-transcripts)

---

## Core Architectural Innovations

### 1. Interview-Exchange RAG Architecture (Solving the Isolated Chunk Flaw)
In traditional RAG pipelines, transcripts are split into naive text paragraphs. This causes a critical retrieval failure when an interviewer asks *"How important is ROI?"* at `02:02` and the expert answers *"It matters, but the discussion is not always purely financial..."* at `02:07`. Because the expert's answer does not repeat the keyword *"ROI"*, naive chunk-based retrievers return a score of `0.0000`.

**Our Solution:** We group turns into **Interview Exchanges**:
- **Searchable Document:** Combines `Market + Expert + Role + Interviewer Question + Expert Answer`.
- **Evidence Attribution:** Links directly to the expert's answer turn with its verified timestamp (`02:07`) and verbatim quote.

### 2. Multi-Tier Hallucination Elimination
- **Stop-Word Infiltration Filter:** Eliminates false-positive lexical matching on conversational filler.
- **Relevance Score Thresholding (`min_score = 0.01`):** Completely out-of-domain questions (e.g. *"tell me who is david laid"*) trigger an immediate clean refusal with `evidence: []` rather than fabricating citations.
- **Automated Verbatim Quote Verification:** Every quote returned by the LLM is programmatically checked against the raw source transcript using Unicode/NFKC substring validation (`is_exact_quote_supported`).

### 3. Dynamic Search Scope Selector
Users can execute queries across the entire European corpus (`All interviews`) or focus on a specific market (`United Kingdom`, `France`, `Germany`, `Italy`) to eliminate cross-market noise.

---

## System Architecture

```
                    ┌───────────────────────────────────────────────┐
                    │            Vite + React Frontend              │
                    │  Overview │ Interview Guide │ Cross │ Ask     │
                    └───────────────────────┬───────────────────────┘
                                            │ REST / JSON (CORS Enabled)
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │               FastAPI Backend                 │
                    │      (Routes: /transcripts, /guide, /ask)     │
                    └───────┬───────────────────────────────┬───────┘
                            │                               │
                            ▼                               ▼
       ┌──────────────────────────────┐   ┌──────────────────────────────┐
       │   Interview Exchange Index   │   │     Analysis Cache Engine    │
       │   - Question + Answer Pairs  │   │     - Fingerprinted Keys     │
       │   - Sublinear TF-IDF Sparse  │   │     - SQLite (Redis-ready)   │
       │   - Dynamic Scope Filtering  │   └──────────────────────────────┘
       └──────────────┬───────────────┘
                      │ Top-K Scored Exchanges (Market, Expert, Timestamps)
                      ▼
       ┌──────────────────────────────┐
       │     Synthesis & Guardrails   │
       │     - Gemini 2.5 Flash       │
       │     - Verbatim Quote Match   │
       │     - Deterministic Fallback │
       └──────────────────────────────┘
```

---

## Technology Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2 (async-capable ORM), Uvicorn.
- **Data & Storage:** SQLite with WAL mode & foreign key constraints (swappable to PostgreSQL).
- **Retrieval Engine:** Scikit-learn vectorized exchange-level sparse search with cosine scoring.
- **LLM Synthesis:** Google Gemini 2.5 Flash via structured JSON generation; local deterministic fallback for zero-key test environments.
- **Frontend:** React 19, Vite, Vanilla CSS design system, Vitest.
- **Containerization:** Multi-stage Dockerfiles & Docker Compose.

---

## Live Features

- **Pre-Loaded Transcripts:** Auto-seeds European market interviews:
  - 🇫🇷 **France:** Dr. Jean Martin (Chief of Surgery)
  - 🇩🇪 **Germany:** Anna Keller (Head of Procurement)
  - 🇬🇧 **United Kingdom:** Dr. Emily Carter (Consultant Urologist)
  - 🇮🇹 **Italy:** Dr. Marco Rossi (Chief of Colorectal Surgery)
- **Live Transcript Ingestion:** Drag-and-drop or select any `.txt` transcript to parse speakers, turns, and metadata in real-time.
- **Interview Guide Synthesis:** Side-by-side comparative grid answering the 6 mandatory Hasamex market questions.
- **Cross-Analysis Engine:** Automatically extracts consensus themes and market-by-market disagreements (e.g. procurement timelines, economic prioritization).
- **Ask the Corpus:** Free-text Q&A with grounded executive synthesis and relevance-ranked supporting evidence cards.

---

## Quickstart (Local Development)

### 1. Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Node.js 18+ (Node 22 recommended)

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

*(Optional)* Configure your Gemini API key in `backend/.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
> **Note:** If no API key is provided, the backend automatically uses its built-in local deterministic synthesis provider.

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
API runs at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Docker Deployment

You can spin up the entire full-stack application using Docker Compose:

```bash
# From project root
docker compose -f infra/docker-compose.yml up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## Cloud Deployment (Active Live Production)

The project is live in production with decoupled frontend and backend services:

| Component | Platform | Active Live Production URL |
| :--- | :--- | :--- |
| **Frontend Web Application** | **Vercel** | [https://hasamex-omega.vercel.app/](https://hasamex-omega.vercel.app/) |
| **Backend API & Swagger Docs** | **Render** | [https://hasamex-backend-s17e.onrender.com/docs](https://hasamex-backend-s17e.onrender.com/docs) |
| **Healthcheck Endpoint** | **Render** | [https://hasamex-backend-s17e.onrender.com/api/health](https://hasamex-backend-s17e.onrender.com/api/health) |
| **Source Code Repository** | **GitHub** | [https://github.com/sankalp250/Hasamex-](https://github.com/sankalp250/Hasamex-) |

### Reproduction / Deployment Steps:

#### 1. Backend on Render.com (Python 3 Web Service)
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `LLM_PROVIDER`: `gemini`
  - `GEMINI_API_KEY`: `<your-api-key>`
  - `GEMINI_MODEL`: `gemini-2.5-flash`

#### 2. Frontend on Vercel.com (Vite Single Page App)
- **Root Directory:** `frontend`
- **Framework Preset:** `Vite`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment Variable:**
  - `VITE_API_BASE_URL`: `https://hasamex-backend-s17e.onrender.com/api`

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Healthcheck and service readiness |
| `GET` | `/api/transcripts` | Lists all indexed transcripts with metadata |
| `POST` | `/api/transcripts/upload` | Ingests a new `.txt` transcript file |
| `GET` | `/api/guide/questions` | Returns the 6 core interview guide questions |
| `POST` | `/api/guide/analyze` | Generates comparative expert answers for the guide |
| `GET` | `/api/analysis/cross` | Identifies common themes and market differences |
| `POST` | `/api/ask` | Grounded question answering with optional scope |

### Example Request (`POST /api/ask`):
```json
{
  "question": "How important is ROI?",
  "transcript_id": "dbaf989ef90843e1b7997d76e59e8fea"
}
```

### Example Response:
```json
{
  "answer": "ROI matters, but it is not the sole deciding factor. Hospitals consider a broader range of elements beyond purely financial discussions, including patient outcomes, length of stay, surgeon recruitment, and clinical positioning.",
  "evidence": [
    {
      "source_id": "e3a8910f",
      "expert": "Dr. Emily Carter",
      "market": "United Kingdom",
      "timestamp": "02:07",
      "speaker": "Dr. Carter",
      "quote": "It matters, but the discussion is not always purely financial. Hospitals also consider patient outcomes, length of stay, surgeon recruitment and whether the technology improves their clinical position."
    }
  ]
}
```

---

## Automated Testing & Verification

The codebase includes comprehensive test suites across both backend and frontend layers:

```bash
# Run backend test suite (17 passed)
cd backend
pytest -v

# Run frontend test suite (2 passed)
cd frontend
npm test

# Test production build
npm run build
```

---

## Scaling from 3 to 30+ Transcripts

In the technical interview, evaluators will ask how this architecture scales. The system is designed with explicit abstraction boundaries for seamless horizontal scaling:

1. **Retriever Handoff (Sparse to Dense Hybrid):**
   The `TfidfRetriever` interface abstracts storage and scoring. In production, this swaps directly to **pgvector** or **Pinecone** using hybrid dense (e.g. `text-embedding-004`) + BM25 reciprocal rank fusion (RRF).
2. **Distributed Cache Layer:**
   The SQLite `analysis_cache` table is designed to transition to a managed **Redis** cluster with automated TTL invalidation.
3. **Asynchronous Analysis Jobs:**
   For high-volume corpus processing (e.g. 100+ interviews), the synchronous guide and cross-analysis routes decouple into Celery or ARQ background workers with webhook/SSE notifications.
