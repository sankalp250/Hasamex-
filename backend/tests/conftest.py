import pytest

from app.core.config import Settings
from app.llm.mock import DeterministicLocalProvider
from app.main import create_app


@pytest.fixture
def app(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    settings = Settings(database_url=db_url, llm_provider="mock")
    application = create_app(settings=settings, provider_override=DeterministicLocalProvider())
    yield application


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
