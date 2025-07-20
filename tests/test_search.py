import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_search_templates():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "secret", "role": "editor"},
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "secret"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    node_resp = client.post("/api/taxonomy", json={"slug": "docs", "title": "Docs"})
    assert node_resp.status_code == 201
    taxonomy_id = node_resp.json()["id"]

    client.post(
        "/api/templates",
        json={
            "code": "contract",
            "title": "Contract",
            "jinja_body": "",
            "taxonomy_id": taxonomy_id,
            "version": "1.0.0",
        },
        headers=headers,
    )
    client.post(
        "/api/templates",
        json={
            "code": "agreement",
            "title": "Agreement",
            "jinja_body": "",
            "taxonomy_id": taxonomy_id,
            "version": "1.0.0",
        },
        headers=headers,
    )

    resp = client.get("/api/search/templates", params={"q": "cont"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["code"] == "contract"
