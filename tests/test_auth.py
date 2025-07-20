import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_register_and_login():
    resp = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "secret", "role": "editor"},
    )
    assert resp.status_code == 201
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "secret"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    refresh = login_resp.json()["refresh_token"]
    refresh_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert refresh_resp.status_code == 200
    assert refresh_resp.json()["access_token"]
    assert refresh_resp.json()["refresh_token"]
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "user@example.com"
    assert me_resp.json()["role"] == "editor"
