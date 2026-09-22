from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.llm.mock import DeterministicLocalProvider
from backend.app.main import create_app


def main() -> None:
    db_path = Path("/tmp/hasamex-smoke.db")
    if db_path.exists():
        db_path.unlink()
    app = create_app(
        settings=Settings(database_url=f"sqlite:///{db_path}", llm_provider="mock"),
        provider_override=DeterministicLocalProvider(),
    )
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        assert len(client.get("/api/transcripts").json()) == 3
        assert client.post("/api/guide/analyze").status_code == 200
        assert client.get("/api/analysis/cross").status_code == 200
        assert client.post("/api/ask", json={"question": "What are the barriers?"}).status_code == 200
    print("HASAMEX smoke test: PASS")


if __name__ == "__main__":
    main()
