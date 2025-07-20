import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

client = TestClient(app)

def test_create_and_get_tree():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    root_resp = client.post("/api/taxonomy", json={"slug": "root", "title": "Root"})
    assert root_resp.status_code == 201
    root_id = root_resp.json()["id"]
    child_resp = client.post(
        "/api/taxonomy",
        json={"slug": "child", "title": "Child", "parent_id": root_id},
    )
    assert child_resp.status_code == 201

    tree_resp = client.get("/api/taxonomy/tree")
    assert tree_resp.status_code == 200
    data = tree_resp.json()
    assert len(data) == 1
    assert data[0]["slug"] == "root"
    assert len(data[0]["children"]) == 1
    assert data[0]["children"][0]["slug"] == "child"


def test_update_and_delete_node():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    resp = client.post("/api/taxonomy", json={"slug": "node", "title": "Node"})
    node_id = resp.json()["id"]

    update_resp = client.put(
        f"/api/taxonomy/{node_id}",
        json={"slug": "updated", "title": "Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["slug"] == "updated"

    delete_resp = client.delete(f"/api/taxonomy/{node_id}")
    assert delete_resp.status_code == 204

    tree_resp = client.get("/api/taxonomy/tree")
    assert tree_resp.status_code == 200
    assert tree_resp.json() == []
