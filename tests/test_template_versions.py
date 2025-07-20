import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_template_version_flow():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "secret", "role": "editor"},
    )
    login = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "secret"},
    )
    token = login.json()["access_token"]
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
        json={"version": "1.1.0", "jinja_body": "Hi {{ name }}"},
        headers=headers,
    )
    assert version_resp.status_code == 201
    version_id = version_resp.json()["id"]

    list_resp = client.get(f"/api/templates/{template_id}/versions")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    preview_resp = client.post(
        f"/api/template-versions/{version_id}/preview",
        json={"params": {"name": "Bob"}},
    )
    assert preview_resp.status_code == 200
    assert preview_resp.json()["result"] == "Hi Bob"

    publish_resp = client.post(
        f"/api/template-versions/{version_id}/publish",
        headers=headers,
    )
    assert publish_resp.status_code == 200

    gen_resp = client.post(
        "/api/generate",
        json={"template_id": template_id, "params": {"name": "Bob"}},
    )
    assert gen_resp.status_code == 200
    assert gen_resp.json()["result"] == "Hi Bob"
