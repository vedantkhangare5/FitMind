import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_connection
import os
import tempfile

@pytest.fixture(scope="module")
def setup_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["FITMIND_DB_PATH"] = path
    init_db(path)
    yield path

def test_data_isolation_two_clients(setup_db):
    client_a = TestClient(app)
    client_b = TestClient(app)

    # Register User A
    resp = client_a.post("/api/auth/register", json={"email": "usera2@test.com", "password": "passwordA"}, headers={"X-FitMind-CSRF": "1"})
    assert resp.status_code == 200
    
    # Save User A profile
    resp = client_a.put("/api/profile", json={
        "age": 25, "sex": "female", "height_cm": 160, "weight_kg": 60, "activity_level": "sedentary", "goal": "maintain"
    }, headers={"X-FitMind-CSRF": "1"})
    assert resp.status_code == 200

    # User A adds progress
    resp = client_a.post("/api/progress", json={"weight_kg": 60.0}, headers={"X-FitMind-CSRF": "1"})
    assert resp.status_code == 200

    # Register User B
    resp = client_b.post("/api/auth/register", json={"email": "userb2@test.com", "password": "passwordB"}, headers={"X-FitMind-CSRF": "1"})
    assert resp.status_code == 200

    # User B gets profile - SHOULD BE 404 (not 25/female/60)
    resp = client_b.get("/api/profile")
    
    # User B gets progress - SHOULD BE EMPTY
    resp_prog = client_b.get("/api/progress")

    # Let's see what they actually return!
    assert resp.status_code == 404, f"User B got User A's profile! {resp.json()}"
    assert len(resp_prog.json().get("entries", [])) == 0, f"User B got User A's progress! {resp_prog.json()}"
