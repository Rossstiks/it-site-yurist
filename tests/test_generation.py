import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_generate_document():
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

    resp = client.post(
        "/api/templates",
        json={
            "code": "greeting",
            "title": "Greeting",
            "jinja_body": "Hello {{ name }}",
            "taxonomy_id": taxonomy_id,
            "version": "1.0.0",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    template_id = resp.json()["id"]

    gen_resp = client.post(
        "/api/generate",
        json={"template_id": template_id, "params": {"name": "Alice"}},
    )
    assert gen_resp.status_code == 200
    assert gen_resp.json()["result"] == "Hello Alice"
