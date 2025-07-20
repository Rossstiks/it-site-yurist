import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_audit_logs_created():
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
            "code": "tmpl",
            "title": "Template",
            "jinja_body": "Hello",
            "taxonomy_id": taxonomy_id,
            "version": "1.0.0",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    template_id = resp.json()["id"]

    version_resp = client.post(
        f"/api/templates/{template_id}/versions",
        json={"version": "1.1.0", "jinja_body": "Hi"},
        headers=headers,
    )
    assert version_resp.status_code == 201
    version_id = version_resp.json()["id"]

    publish_resp = client.post(
        f"/api/template-versions/{version_id}/publish",
        headers=headers,
    )
    assert publish_resp.status_code == 200

    logs_resp = client.get("/api/audit")
    assert logs_resp.status_code == 200
    data = logs_resp.json()
    assert len(data) >= 3  # template create, version create, publish
