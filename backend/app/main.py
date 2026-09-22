import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .container import ServiceContainer
from .core.config import Settings, get_settings
from .db import Base, build_engine, build_session_factory, get_db
from .guide import INTERVIEW_GUIDE
from .models import Chunk, Transcript
from .schemas import AskRequest, AskResponse, CrossAnalysisOut, GuideAnalysisOut, TranscriptOut


def create_app(settings: Settings | None = None, provider_override=None) -> FastAPI:
    settings = settings or get_settings()
    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)
    container = ServiceContainer(session_factory, settings, provider_override)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        Base.metadata.create_all(engine)
        seed_dir = Path(__file__).resolve().parents[1] / "data" / "transcripts"
        with session_factory() as session:
            container.seed_if_empty(session, seed_dir)

        # Automatic keep-alive task to prevent Render free-tier from idling down
        keep_alive_task = None
        external_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("KEEP_ALIVE_URL")
        if external_url:
            async def _keep_alive_loop():
                health_url = f"{external_url.rstrip('/')}/api/health"
                while True:
                    await asyncio.sleep(600)  # Ping every 10 mins (Render sleeps after 15 mins)
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            await client.get(health_url)
                    except Exception:
                        pass
            keep_alive_task = asyncio.create_task(_keep_alive_loop())

        yield

        if keep_alive_task:
            keep_alive_task.cancel()

    app = FastAPI(
        title="Hasamex Expert Interview Analyzer",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.container = container

    def db_session() -> Session:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "hasamex-analyzer"}

    @app.get("/api/transcripts", response_model=list[TranscriptOut])
    def list_transcripts(session: Session = Depends(db_session)):
        stmt = (
            select(
                Transcript.id,
                Transcript.filename,
                Transcript.expert_name,
                Transcript.role,
                Transcript.market,
                func.count(Chunk.id).label("chunk_count"),
                Transcript.created_at,
            )
            .outerjoin(Chunk, Chunk.transcript_id == Transcript.id)
            .group_by(Transcript.id)
            .order_by(Transcript.market)
        )
        return [dict(row._mapping) for row in session.execute(stmt).all()]

    @app.post("/api/transcripts/upload", response_model=TranscriptOut, status_code=status.HTTP_201_CREATED)
    async def upload_transcript(file: UploadFile = File(...)):
        if not file.filename or not file.filename.lower().endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt transcript files are supported.")
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="Transcript exceeds the configured upload limit.")
        try:
            raw_text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Transcript must be UTF-8 encoded text.") from exc
        with session_factory() as session:
            try:
                transcript = container.ingest(session, file.filename, raw_text)
                return {
                    "id": transcript.id,
                    "filename": transcript.filename,
                    "expert_name": transcript.expert_name,
                    "role": transcript.role,
                    "market": transcript.market,
                    "chunk_count": len(transcript.chunks),
                    "created_at": transcript.created_at,
                }
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/guide/questions")
    def guide_questions():
        return {"questions": INTERVIEW_GUIDE}

    @app.post("/api/guide/analyze", response_model=GuideAnalysisOut)
    async def guide_analyze(session: Session = Depends(db_session)):
        analyzer = container.new_analyzer(session)
        return await analyzer.analyze_guide()

    @app.get("/api/analysis/cross", response_model=CrossAnalysisOut)
    async def cross_analysis(session: Session = Depends(db_session)):
        analyzer = container.new_analyzer(session)
        return await analyzer.cross_analysis()

    @app.post("/api/ask", response_model=AskResponse)
    async def ask(payload: AskRequest, session: Session = Depends(db_session)):
        analyzer = container.new_analyzer(session)
        return await analyzer.ask(payload.question, transcript_id=payload.transcript_id)

    dist_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist_dir.exists():
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")

    return app



app = create_app()
