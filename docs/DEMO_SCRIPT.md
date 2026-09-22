# Hasamex AI Engineer Case Study: Video Demo Pitch & Technical Script

**Suggested Recording Duration:** 4 to 5 minutes  
**Live Application URL:** [https://hasamex-omega.vercel.app/](https://hasamex-omega.vercel.app/)  
**Live API Documentation:** [https://hasamex-backend-s17e.onrender.com/docs](https://hasamex-backend-s17e.onrender.com/docs)  
**GitHub Repository:** [https://github.com/sankalp250/Hasamex-](https://github.com/sankalp250/Hasamex-)

---

## Script Breakdown & On-Screen Timeline

```
Timeline:
[00:00 - 00:45] Phase 1: High-Impact Introduction & Problem Framing
[00:45 - 02:20] Phase 2: Live Feature Walkthrough & Demonstrations
[02:20 - 04:10] Phase 3: Technical Architecture & The 5 Case Study Answers
[04:10 - 04:45] Phase 4: Production Deployment & Closing
```

---

### Phase 1: High-Impact Introduction & Problem Framing (0:00 – 0:45)

**On Screen:** Show your face / web camera, or start on the home screen of the live Vercel app ([https://hasamex-omega.vercel.app/](https://hasamex-omega.vercel.app/)).

**What to Say:**
> *"Hi everyone, my name is Sankalp, and this is my technical demo submission for the AI Engineer role at Hasamex.*
> 
> *When conducting qualitative market research across expert interviews, consultants and private equity analysts face a major challenge: transcripts are unstructured, long, and nuanced. If you use off-the-shelf generative AI, you run into two fatal problems: **hallucinated quotes** and **broken retrieval on interview Q&A exchanges**.*
> 
> *To solve this, I designed and deployed a production-grade, source-grounded research intelligence platform for the European robotic surgery market. It features a novel **Interview-Exchange RAG architecture**, multi-tier hallucination elimination, and dynamic search scope filtering. Let me walk you through the live application."*

---

### Phase 2: Live Feature Walkthrough & Demonstrations (0:45 – 2:20)

#### 1. Corpus Overview & Auto-Seeding (0:45 – 1:05)
**On Screen:** Click on **`01 Overview`** tab in the sidebar.
**What to Say:**
> *"Here on the Overview page, the application automatically ingests and indexes the three provided expert transcripts across France, Germany, and the UK. Our ingestion parser automatically extracts the expert's name, role, country, and breaks down the transcript into timestamped turns while preserving relational metadata."*

#### 2. The 6 Interview Guide Benchmarks (1:05 – 1:30)
**On Screen:** Click on **`02 Interview guide`** tab. Scroll to Question 3: *"How important are hospital budgets and ROI in purchasing decisions?"*.
**What to Say:**
> *"The second core requirement was answering the official 6-question Interview Guide. Rather than running slow sequential queries, our backend processes the comparative guide in parallel.*
> 
> *Notice how for Question 3 on hospital budgets and ROI, we get a clear side-by-side comparison across France, Germany, and the UK. Every expert answer includes a grounded synthesis, the verbatim quote in quotation marks, and the exact verified timestamp from the call."*

#### 3. Cross-Interview Analysis: Themes & Disagreements (1:30 – 1:50)
**On Screen:** Click on **`03 Cross analysis`** tab.
**What to Say:**
> *"In qualitative consulting, the most valuable output is finding where experts agree and where they disagree. The Cross Analysis view automatically aggregates market-wide consensus—such as the uneven adoption between academic vs regional hospitals—as well as explicit disagreements, like procurement timelines ranging from 6 to 12 months in France versus 9 to 18 months in Germany."*

#### 4. Ask the Corpus: Scope Filtering & Guardrail Demo (1:50 – 2:20)
**On Screen:** Click on **`04 Ask the corpus`** tab.

**Action A — Scoped Query:**
1. Click the **`United Kingdom (Dr. Emily Carter)`** scope pill above the text box.
2. Type or select: `"How important is ROI?"`.
3. Click **Ask question**.
**What to Say:**
> *"The fourth feature is Ask the Corpus. I introduced a dynamic **Search Scope Selector**. If an analyst wants insights strictly from the UK, they select the UK scope.*
> 
> *Notice the result: the Grounded Answer summarizes Dr. Carter's perspective that ROI is balanced with clinical outcomes and recruitment. And looking at the evidence card below, it pinpoints the exact answer timestamp at **02:07** with Dr. Carter's verbatim words."*

**Action B — Zero-Hallucination Guardrail:**
1. Type: `"tell me who is david laid"`.
2. Click **Ask question**.
**What to Say:**
> *"Now let’s test the guardrails with an out-of-domain query: 'tell me who is david laid'. Notice that rather than hallucinating surgery text or fabricating fake citations, the system enforces a strict refusal guardrail: 0 citations, 0 hallucinations."*

---

### Phase 3: Deep Technical Architecture & The 5 Case Study Criteria (2:20 – 4:10)

**On Screen:** Switch tabs to the GitHub repository ([https://github.com/sankalp250/Hasamex-](https://github.com/sankalp250/Hasamex-)) or show Swagger UI at `https://hasamex-backend-s17e.onrender.com/docs`.

**What to Say:**
> *"Now let's dive under the hood and answer the five key technical criteria outlined in the brief:*

#### 1. Architecture & The Core Innovation: "Interview-Exchange Indexing"
> *"Most standard RAG pipelines fail on interview transcripts because they split text into isolated paragraphs. For example, in the UK transcript, the interviewer asks 'How important is ROI?' at `02:02`, and Dr. Carter answers 'It matters, but the discussion is not always purely financial...' at `02:07`.*
> 
> *If you index chunks in isolation and search for 'ROI', Dr. Carter’s chunk scores `0.0` because she never repeated the word 'ROI'.*
> 
> *To solve this, I designed an **Interview-Exchange data structure**. We couple the interviewer’s question with the expert’s answer during vectorization, while attributing the citation directly to the expert's answer timestamp (`02:07`). This guarantees 100% retrieval precision without losing question context."*

#### 2. Model Choice
> *"I chose **Gemini 2.5 Flash** for its sub-second latency (<1.2s), strong structured JSON schema following, and cost-efficiency. I also built an abstract provider interface with a local deterministic fallback, allowing the entire suite to run offline and pass automated CI tests without an API key."*

#### 3. Citations and Timestamps
> *"Timestamps are never generated or guessed by the LLM. The LLM only receives unique `source_id` keys. Our backend resolves those keys directly against our SQLAlchemy database to attach verified metadata: expert name, market, role, speaker, and timestamp."*

#### 4. Reducing Hallucinations
> *"We implement three layers of defense:*
> *First, English stop-words filtering prevents conversational filler from matching unrelated questions.*
> *Second, a cosine similarity threshold (`min_score = 0.01`) filters out low-confidence matches before the LLM is even called.*
> *Third, an automated string validator (`is_exact_quote_supported`) verifies every single quoted sentence against the raw transcript before rendering."*

#### 5. Scaling from 3 to 30+ Transcripts
> *"The codebase is engineered with strict decoupling for production horizontal scaling:*
> *1. **Storage:** The SQLite database transitions directly to PostgreSQL.*
> *2. **Retrieval:** The `TfidfRetriever` interface cleanly swaps to a managed vector store like **pgvector** or **Pinecone** with hybrid dense-sparse search.*
> *3. **Caching:** The analysis cache swaps to a distributed **Redis** instance.*
> *4. **Asynchronous Execution:** Heavy cross-interview analysis for 30+ calls is offloaded to background task queues like Celery or ARQ with SSE streaming."*

---

### Phase 4: Production Deployment & Closing (4:10 – 4:45)

**On Screen:** Switch back to the live Vercel app ([https://hasamex-omega.vercel.app/](https://hasamex-omega.vercel.app/)).

**What to Say:**
> *"Finally, the application is fully deployed and live in production: the React single-page frontend is hosted on Vercel Edge CDN, and the FastAPI backend is running live on Render.*
> 
> *The entire codebase is version-controlled on GitHub with an automated test suite of 17 backend unit tests and frontend integration tests.*
> 
> *Thank you for reviewing my case study submission, and I look forward to discussing the architecture further in the technical round!"*
