# Hasamex AI Engineer Case Study — Project Master Plan

## 1. Purpose of this document

This document is the single source of truth for the Hasamex AI Engineer case-study implementation.

It explains:

- what Hasamex is asking us to build,
- what our final product is supposed to do,
- what we are adding beyond the minimum brief,
- why we selected the current technology stack,
- how the application is architected,
- how information moves through the system,
- how we control hallucinations and preserve evidence,
- what the database and APIs are responsible for,
- how the UI is organized,
- how the MVP can evolve into a larger production system,
- what we need to test,
- and what the final submission/demo should prove.

This is a build plan and product/engineering specification, not just a README.

---

## 2. Original Hasamex assignment — what they actually want

Hasamex provided three expert-call transcripts from the European robotic-surgery market plus an interview guide.

The required application is expected to:

1. Upload/read the three transcripts.
2. Answer the interview-guide questions for each expert.
3. Extract useful exact quotes.
4. Show the source timestamp for each answer/quote.
5. Identify common themes and disagreements across all three experts.
6. Let a user ask questions across all transcripts.
7. Avoid invented information.
8. Make every important answer traceable to the transcript.
9. Keep the UI simple and usable.

For the technical demo, Hasamex specifically wants us to explain:

- our architecture,
- model choice,
- how citations/timestamps are handled,
- how hallucinations are reduced,
- and how the solution would scale from 3 transcripts to 30+.

Submission requirements include:

- a working application or local-run instructions,
- the source-code repository,
- and a short README.

The case pack contains three markets:

- France — Dr. Jean Martin, Head of Urology
- Germany — Anna Keller, Former Hospital Procurement Director
- United Kingdom — Dr. Emily Carter, Consultant Urologist

The interview guide contains six core questions covering adoption, barriers, economics/ROI, training and clinical outcomes, the 3–5 year outlook, and purchasing timelines.

---

## 3. Our end goal

The end goal is to build a polished **AI-powered expert-interview research assistant**.

A user should be able to open the application and immediately:

1. See the three provided interviews already loaded.
2. Review answers to the six interview-guide questions across all experts.
3. See concise summaries supported by exact transcript evidence.
4. See the original timestamp for every evidence item.
5. Compare markets and experts.
6. See cross-interview themes and differences.
7. Ask a natural-language question across the entire transcript corpus.
8. Add another `.txt` interview and automatically make it available for future questions and analysis.

The product should feel less like a generic chatbot and more like a **traceable research analysis tool**.

The key product principle is:

> The transcript is the source of truth. The LLM is a synthesis layer, not the source of facts.

---

## 4. Our selected technology stack — finalized

### Frontend

**React + Vite**

Why:

- proper separation between UI and backend,
- reusable component architecture,
- strong fit for a production-style web application,
- easier to make a polished professional interface,
- straightforward future deployment.

### Backend

**Python + FastAPI**

Why:

- the requested Python backend direction,
- excellent fit for AI/ML services,
- typed request/response models with Pydantic,
- clean API boundaries,
- asynchronous support for future long-running tasks,
- easy integration with model providers and retrieval systems.

### Database

**SQLite for the current case-study MVP**

Why:

- zero infrastructure overhead,
- reliable local development,
- sufficient for the supplied corpus and case-study scale,
- keeps the architecture simple.

The code is structured so that SQLite can later be replaced by PostgreSQL without changing the product architecture.

### Retrieval

A lightweight local retrieval layer is used for the MVP.

The retrieval abstraction is intentionally separated from the rest of the application so that it can later move to:

- PostgreSQL + pgvector,
- Qdrant,
- Pinecone,
- Weaviate,
- or another persistent vector store.

### LLM

The application supports an LLM provider through an abstraction layer.

Supported direction:

- Gemini
- Groq
- deterministic/mock fallback for local tests

The provider is selected through environment configuration rather than hardcoded into business logic.

### Validation

Pydantic + backend source validation.

### Deployment direction

Local Docker-based deployment for the case-study environment, with a production path that can later use managed infrastructure.

---

## 5. What we are adding beyond the minimum requirement

The following are deliberate product/engineering additions.

### A. Add Transcript / Upload `.txt`

The provided three transcripts are preloaded, but the UI will also let the evaluator upload another `.txt` file.

Example:

```text
France
Germany
UK

+ Add Transcript
```

This means the evaluator can test the application using a fourth interview without modifying source code.

The upload flow will:

1. validate the file type,
2. read the transcript,
3. parse speakers and timestamps,
4. extract metadata where available,
5. store the transcript/chunks,
6. update retrieval,
7. make the new transcript available for Q&A and analysis.

### B. Evidence-first answers

Every AI answer should expose the evidence used to produce it.

### C. Timestamp preservation

Timestamps are stored during parsing and are never generated by the LLM.

### D. Exact-quote validation

A quote shown as verified evidence must be present in the original source text/chunk.

### E. Filters

The UI can provide filters by:

- market,
- expert,
- transcript,
- and analysis area.

### F. Separate cross-analysis experience

Common themes and disagreements get their own product surface instead of being buried inside a chatbot.

### G. Local deterministic test mode

The application can run without an API key so that basic tests and the deterministic pipeline are reproducible.

### H. Provider abstraction

Gemini/Groq integration is isolated so a future provider can be added without rewriting the application.

---

## 6. Product scope — MVP versus future scale

### Must-have MVP

- 3 preloaded transcripts.
- `.txt` upload.
- Transcript parsing.
- Interview guide analysis.
- Exact quotes.
- Original timestamps.
- Common themes.
- Differences/disagreements.
- Cross-transcript Q&A.
- React frontend.
- FastAPI backend.
- SQLite storage.
- LLM integration abstraction.
- Source validation.
- Tests.
- README and demo documentation.

### Nice-to-have after the core is stable

- Export analysis to JSON/CSV/PDF.
- Saved analysis sessions.
- Search highlighting.
- Multiple file formats.
- Background processing queue.
- Authentication.
- Team workspaces.
- Usage analytics.

We should not sacrifice the required features for speculative features.

---

## 7. Core user journey

### Initial experience

```text
Open application
      ↓
See existing transcripts
      ↓
Choose Interview Guide / Cross Analysis / Ask
```

### Add transcript journey

```text
Click Add Transcript
      ↓
Select .txt file
      ↓
Backend validates file
      ↓
Parser extracts timestamped chunks
      ↓
Database stores transcript + chunks
      ↓
Retrieval index is updated
      ↓
New transcript becomes searchable
```

### Interview-guide journey

```text
Choose a guide question
      ↓
Retrieve evidence for each expert
      ↓
LLM synthesizes a grounded answer
      ↓
Backend resolves source IDs
      ↓
Backend validates quotes
      ↓
UI shows summary + exact quote + timestamp
```

### Q&A journey

```text
User asks a question
      ↓
Retrieval finds relevant transcript chunks
      ↓
LLM receives only relevant evidence
      ↓
LLM returns structured answer + source IDs
      ↓
Backend resolves/validates evidence
      ↓
UI displays answer with sources
```

---

## 8. High-level system architecture

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         │  Dashboard / Search  │
                         └──────────┬───────────┘
                                    │ HTTP/JSON
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │    API Layer         │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
       │ Transcript   │      │ Retrieval    │      │ LLM Provider │
       │ Parser       │      │ Service      │      │ Adapter      │
       └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
       │ SQLite       │      │ Vector /     │      │ Gemini /     │
       │ Metadata +   │      │ Semantic     │      │ Groq / Mock  │
       │ Chunks       │      │ Retrieval    │      │              │
       └──────────────┘      └──────────────┘      └──────────────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │ Evidence     │
                             │ Validation   │
                             └──────────────┘
```

---

## 9. Data model

### Transcript

Represents an uploaded interview file.

Suggested fields:

- id
- filename
- expert_name
- role
- market
- source_hash
- created_at
- updated_at

### TranscriptChunk

Represents the smallest useful unit of evidence.

Suggested fields:

- id
- transcript_id
- sequence_number
- timestamp
- speaker
- text
- chunk_hash

### AnalysisResult

Stores generated/validated analysis when persistence is required.

Suggested fields:

- id
- analysis_type
- question
- answer
- created_at

### Evidence

Connects an analysis result to a source chunk.

Suggested fields:

- id
- analysis_id
- chunk_id
- quote
- validated

This separation gives us a traceability chain:

```text
Answer
  ↓
Evidence record
  ↓
Transcript chunk
  ↓
Original transcript
```

---

## 10. Transcript parsing strategy

The provided files follow a simple timestamp + speaker + content pattern.

The parser should preserve:

- timestamp,
- speaker,
- text,
- expert,
- role,
- market.

Example normalized record:

```json
{
  "id": "france_002",
  "expert": "Dr. Jean Martin",
  "role": "Head of Urology",
  "market": "France",
  "timestamp": "01:20",
  "speaker": "Dr. Martin",
  "text": "The biggest issue is still capital budget approval..."
}
```

The important design decision is that timestamps are attached to the source record **before** any LLM call.

---

## 11. Retrieval design

The retrieval system is responsible for finding relevant transcript evidence.

For a user question such as:

> What are the main barriers to adoption?

the retrieval layer should locate relevant chunks from France, Germany and the UK.

The LLM should not receive the entire corpus blindly for every query.

Instead:

```text
User question
      ↓
Query representation
      ↓
Top-k relevant chunks
      ↓
Grounded LLM prompt
```

For the small case-study corpus, a lightweight local retrieval implementation is enough.

For production scale, the retrieval interface can be backed by a persistent vector store.

---

## 12. LLM design

The LLM performs synthesis, not source-of-truth storage.

The model is responsible for tasks such as:

- summarizing retrieved evidence,
- answering a user question from retrieved evidence,
- identifying themes,
- identifying differences,
- mapping evidence to an interview-guide question.

The model should produce structured output, for example:

```json
{
  "answer": "...",
  "sources": [
    {
      "source_id": "france_002"
    },
    {
      "source_id": "germany_002"
    }
  ]
}
```

The backend then resolves the source IDs to the database records.

This prevents the model from becoming responsible for factual metadata such as timestamps.

---

## 13. Hallucination-control strategy

This is one of the strongest engineering aspects of the project.

### Rule 1 — Retrieval first

The model receives relevant transcript evidence rather than being asked to rely on general knowledge.

### Rule 2 — Source IDs

The model returns identifiers for the evidence it used.

### Rule 3 — Server-side resolution

The backend resolves the IDs to the actual stored transcript chunks.

### Rule 4 — Timestamp ownership

The backend obtains timestamps from stored transcript data.

### Rule 5 — Quote validation

Before displaying an exact quote as verified evidence, the backend checks that it exists in the original source text/chunk.

### Rule 6 — No evidence, no strong claim

If the retrieval layer cannot produce supporting evidence, the system should avoid presenting an unsupported factual claim as transcript-derived.

The system therefore follows:

```text
LLM proposes evidence
        ↓
Backend verifies evidence
        ↓
Backend attaches authoritative metadata
        ↓
UI displays verified result
```

---

## 14. Interview-guide analysis

The six guide questions become structured application prompts.

For each question we analyze each expert separately.

Target structure:

```text
Question
 ├── France
 │    ├── Summary
 │    └── Evidence + timestamp
 │
 ├── Germany
 │    ├── Summary
 │    └── Evidence + timestamp
 │
 └── UK
      ├── Summary
      └── Evidence + timestamp
```

This makes the final result easy for a researcher to compare.

---

## 15. Cross-interview analysis

The cross-analysis experience should identify:

### Common themes

Examples visible in the supplied transcripts include:

- adoption is increasing,
- adoption is uneven across hospitals,
- economics matter,
- utilization/procedure volume matters,
- training matters,
- purchasing can take many months.

### Differences

The system should identify where the experts emphasize different factors or give different outlooks.

For example, the UK interview places substantial emphasis on balancing economics with clinical strategy, while the France and Germany interviews put stronger emphasis on the economic/business case.

The system should show the supporting evidence for such observations rather than turning them into unsupported labels.

---

## 16. React UI architecture

The frontend should be organized around reusable components rather than putting the entire UI into one component.

Suggested structure:

```text
App
├── Sidebar / Navigation
├── Header
├── Overview
│   ├── MetricCard
│   ├── TranscriptList
│   └── Activity/Status
├── InterviewGuide
│   ├── QuestionSelector
│   ├── ExpertAnswerCard
│   └── EvidenceCard
├── CrossAnalysis
│   ├── ThemeCard
│   ├── DifferenceCard
│   └── ComparisonTable
├── AskCorpus
│   ├── QuestionInput
│   ├── AnswerPanel
│   └── SourceList
└── AddTranscriptModal
```

### UI principles

- professional and restrained visual language,
- mostly neutral colors,
- good typography hierarchy,
- generous whitespace,
- no unnecessary gradients or loud colors,
- responsive layout,
- clear loading states,
- clear empty states,
- useful error messages,
- keyboard-accessible controls,
- strong evidence/source visibility.

---

## 17. API design

Suggested API surface:

### Health

```http
GET /api/health
```

### List transcripts

```http
GET /api/transcripts
```

### Upload transcript

```http
POST /api/transcripts/upload
Content-Type: multipart/form-data
```

### Get interview guide

```http
GET /api/guide
```

### Analyze guide question

```http
POST /api/guide/analyze
```

### Cross-analysis

```http
GET /api/analysis/cross
```

### Ask corpus

```http
POST /api/ask
```

The exact request/response models live in the FastAPI schema layer.

---

## 18. Error and loading states

A production-style UI cannot assume every request succeeds.

### Loading

Show a purposeful loading state such as:

```text
Analyzing evidence…
```

not a frozen interface.

### Empty corpus

Show:

```text
No transcripts yet.
Upload a .txt interview to begin.
```

### Unsupported file

Show:

```text
Please upload a .txt transcript.
```

### LLM unavailable

The system should degrade gracefully and show a useful message rather than crashing.

### No evidence found

Return a grounded message explaining that the available transcripts did not provide enough evidence to answer.

---

## 19. Caching strategy

### Current MVP

For this tiny corpus, avoid unnecessary caching complexity.

Cacheable items include:

- parsed transcript data,
- retrieval/index state,
- stable interview-guide analysis results.

### Production direction

At larger scale:

```text
CDN/cache
   ↓
API cache
   ↓
Persistent database
   ↓
Vector store
```

Potential technologies later:

- Redis for request/result caching,
- object storage for source files,
- PostgreSQL for relational metadata,
- pgvector or a dedicated vector database for semantic retrieval.

---

## 20. Scaling from 3 transcripts to 30+

The current implementation is intentionally small, but its interfaces should support growth.

### Current

```text
Local files
SQLite
Local retrieval
One FastAPI process
```

### Future

```text
               Load Balancer
                     ↓
              FastAPI instances
          ┌──────────┼──────────┐
          ↓          ↓          ↓
      PostgreSQL   Redis     Vector DB
          │                     │
          └─────────┬───────────┘
                    ↓
                LLM Provider
                    ↓
              Object Storage
```

For much larger usage, transcript ingestion/embedding should become an asynchronous job rather than blocking an HTTP request.

Example future path:

```text
Upload
  ↓
Object Storage
  ↓
Job Queue
  ↓
Parser Worker
  ↓
Embedding Worker
  ↓
Index Ready
```

---

## 21. Security and production considerations

Even though this is a case study, the implementation should follow sensible production habits.

- Never commit API keys.
- Keep secrets in environment variables.
- Validate uploaded file types.
- Limit upload size.
- Do not trust client-provided metadata.
- Sanitize file names.
- Use structured validation for API input.
- Avoid returning internal stack traces to the browser.
- Use CORS restrictions in deployed environments.
- Rate-limit expensive LLM endpoints at production scale.
- Add authentication before exposing private research data publicly.

---

## 22. Testing strategy

### Unit tests

Test:

- transcript parsing,
- timestamp extraction,
- speaker extraction,
- quote validation,
- retrieval,
- LLM response parsing.

### API tests

Test:

- health endpoint,
- transcript listing,
- upload flow,
- guide analysis,
- cross-analysis,
- Q&A.

### Integration tests

Test the path:

```text
Upload → Parse → Store → Retrieve → Generate → Validate → Return
```

### UI tests

Test:

- rendering,
- tab/navigation behavior,
- upload state,
- loading state,
- empty state,
- answer rendering,
- source rendering.

### Evaluation tests

Create known questions with expected source regions.

For example:

```text
Question: What is the typical purchase timeline?

France: 06:08
Germany: 06:05
UK: 05:04
```

This lets us catch retrieval or source-mapping regressions.

---

## 23. What success looks like

A successful submission should let an evaluator do this in a few minutes:

```text
Open app
  ↓
See 3 interviews loaded
  ↓
Open Interview Guide
  ↓
Pick a question
  ↓
See all 3 expert answers
  ↓
See exact quotes + timestamps
  ↓
Open Cross Analysis
  ↓
See common themes + differences
  ↓
Ask a new question
  ↓
Get a grounded answer + sources
  ↓
Upload a 4th .txt transcript
  ↓
See it become part of the corpus
```

If that flow works smoothly, the core assignment has been fulfilled and our additional product thinking is visible.

---

## 24. Demo narrative

The technical demo should explain the product in this order:

### Part 1 — Problem

"The input is a set of expert interviews. The goal is to turn unstructured transcript data into traceable market insights."

### Part 2 — Product

Show the UI and demonstrate:

- guide analysis,
- evidence,
- cross-analysis,
- Q&A.

### Part 3 — Upload extensibility

Upload another `.txt` transcript and explain that the system was designed as a corpus rather than a hardcoded three-file demo.

### Part 4 — Architecture

Show:

```text
React → FastAPI → Parser/Retrieval → LLM → Validation → Response
```

### Part 5 — Reliability

Explain:

- timestamps are stored from source data,
- quotes are validated,
- source IDs are resolved by the backend,
- the LLM does not invent evidence.

### Part 6 — Scalability

Explain the transition from local SQLite/local retrieval to PostgreSQL/Redis/vector DB/object storage/workers if the corpus grows.

---

## 25. Strong engineering talking points for the interview

These are the ideas we should be ready to explain clearly.

### Why not just put the entire transcript into the prompt?

Because retrieval makes the system more scalable, makes grounding explicit, and reduces unnecessary context.

### Why are timestamps not generated by the LLM?

Because timestamps are source metadata and should come from the original transcript data.

### How do we reduce hallucinations?

Retrieval + source IDs + server-side source resolution + exact quote validation + evidence-first prompting.

### Why SQLite now?

Because it minimizes infrastructure while being sufficient for a small case-study corpus. The persistence layer is isolated so it can later move to PostgreSQL.

### Why React instead of Streamlit?

Because we want to demonstrate a production-style web frontend and clean frontend/backend separation.

### Why not build microservices now?

Because the corpus and user load do not justify the operational complexity. The code is modular so service boundaries can be introduced later where they actually add value.

---

## 26. Definition of done

The project is ready for submission when all of the following are true:

- [ ] Three supplied transcripts load correctly.
- [ ] Interview-guide analysis works.
- [ ] Exact quotes are displayed.
- [ ] Original timestamps are displayed.
- [ ] Quotes are validated against source text.
- [ ] Common themes are displayed.
- [ ] Differences/disagreements are displayed.
- [ ] Cross-transcript Q&A works.
- [ ] Additional `.txt` upload works.
- [ ] React UI is visually polished.
- [ ] FastAPI endpoints are tested.
- [ ] Core parser/retrieval/evidence logic is tested.
- [ ] No API keys are committed.
- [ ] README has local setup instructions.
- [ ] Demo script is prepared.
- [ ] Final demo recording clearly explains architecture and engineering decisions.

---

## 27. Final product statement

> **Hasamex Expert Interview Analyzer** is a source-grounded AI research application that transforms expert-call transcripts into structured, traceable insights. It combines a React interface, a FastAPI AI backend, lightweight persistent metadata storage, retrieval, and an interchangeable LLM layer. The system preserves original transcript evidence, validates generated quotes, exposes timestamps, compares expert perspectives, and supports new transcript uploads so the same workflow can extend beyond the initial three interviews.

The most important engineering principle remains:

> **Generate with the model, verify with the source.**

---

## 28. Current implementation status

At the time of this document, the project structure and backend test suite are already present in the repository.

The supplied France, Germany, and UK transcripts are included as the initial case corpus.

The backend has deterministic test support so development does not depend on an external API key.

The production/demo path can enable Gemini or Groq through environment variables without changing the application architecture.

Before submission, we should run the complete frontend build in a normal network-enabled environment, verify the final browser experience, and record the demo against the exact version being submitted.
