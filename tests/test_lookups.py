import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_create_and_get_lookup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    resp = client.post(
        "/api/lookups/currencies",
        json={"items": ["USD", "EUR"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["items"] == ["USD", "EUR"]

    get_resp = client.get("/api/lookups/currencies")
    assert get_resp.status_code == 200
    assert get_resp.json()["items"] == ["USD", "EUR"]

