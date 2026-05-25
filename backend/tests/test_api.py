from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.session import Base, get_db
from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


def test_register_login_and_upload(client: TestClient) -> None:
    user = {"email": "player@tonemind.ai", "password": "strong-password"}
    register_response = client.post("/auth/register", json=user)
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json=user)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    upload_response = client.post(
        "/audio/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("riff.mp3", b"fake mp3 data", "audio/mpeg")},
    )
    assert upload_response.status_code == 201
    payload = upload_response.json()
    assert payload["detected_key"]
    assert payload["bpm"] > 0
    assert payload["chords"]
