from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_today

FIXED_TODAY = date(2026, 11, 9)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_DB_PATH", str(tmp_path / "test.db"))
    app.dependency_overrides[get_today] = lambda: FIXED_TODAY
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
