import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def test_user_admin():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reg = client.post(
        "/api/auth/register",
        json={"email": "admin@example.com", "password": "secret", "role": "admin"},
    )
    assert reg.status_code == 201
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "secret"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    create = client.post(
        "/api/users",
        json={"email": "user2@example.com", "password": "pass", "role": "viewer"},
        headers=headers,
    )
    assert create.status_code == 201
    list_resp = client.get("/api/users", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

