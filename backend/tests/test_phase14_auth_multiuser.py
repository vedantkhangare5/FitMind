import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_connection, init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Ensure tables exist
    init_db()
    # Clear tables before each test
    conn = get_connection()
    try:
        conn.execute("DELETE FROM fitness_profile")
        conn.execute("DELETE FROM progress_history")
        conn.execute("DELETE FROM nutrition_logs")
        conn.execute("DELETE FROM workout_logs")
        conn.execute("DELETE FROM users")
        conn.commit()
    finally:
        conn.close()

def test_register_success():
    res = client.post("/api/auth/register", json={"email": "a@test.com", "password": "password123"})
    assert res.status_code == 200
    assert "fitmind_access" in res.cookies

def test_register_duplicate():
    client.post("/api/auth/register", json={"email": "b@test.com", "password": "password123"})
    res = client.post("/api/auth/register", json={"email": "b@test.com", "password": "password123"})
    assert res.status_code == 409

def test_login_success():
    client.post("/api/auth/register", json={"email": "c@test.com", "password": "password123"})
    client.cookies.clear()
    
    res = client.post("/api/auth/login", json={"email": "c@test.com", "password": "password123"})
    assert res.status_code == 200
    assert "fitmind_access" in res.cookies

def test_login_failure():
    res = client.post("/api/auth/login", json={"email": "c@test.com", "password": "wrong"})
    assert res.status_code == 400

def test_logout():
    client.post("/api/auth/register", json={"email": "d@test.com", "password": "password123"})
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert not res.cookies.get("fitmind_access")

def test_csrf_protection_missing_header():
    client.post("/api/auth/register", json={"email": "e@test.com", "password": "password123"})
    
    # Try POST without X-FitMind-CSRF
    res = client.post("/api/progress", json={"weight_kg": 80.0})
    assert res.status_code == 403
    assert "CSRF" in res.text

def test_csrf_protection_valid_header():
    client.post("/api/auth/register", json={"email": "f@test.com", "password": "password123"})
    
    res = client.post("/api/progress", json={"weight_kg": 80.0}, headers={"X-FitMind-CSRF": "1"})
    assert res.status_code == 200

def test_multi_user_isolation():
    # User A
    client.post("/api/auth/register", json={"email": "userA@test.com", "password": "password123"})
    client.put("/api/profile", json={
        "age": 30, "sex": "male", "height_cm": 180, "weight_kg": 80, "activity_level": "sedentary", "goal": "maintain"
    }, headers={"X-FitMind-CSRF": "1"})
    
    # Log progress for A
    res_a = client.post("/api/progress", json={"weight_kg": 80.0}, headers={"X-FitMind-CSRF": "1"})
    progress_id_a = res_a.json()["id"]

    client.cookies.clear()

    # User B
    client.post("/api/auth/register", json={"email": "userB@test.com", "password": "password123"})
    res_b = client.get("/api/profile")
    assert res_b.status_code == 404 # B shouldn't see A's profile

    # B tries to delete A's progress (IDOR attempt)
    del_res = client.delete(f"/api/progress/{progress_id_a}", headers={"X-FitMind-CSRF": "1"})
    assert del_res.status_code == 404 # Not found for B
