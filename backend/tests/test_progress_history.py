import pytest
import os
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.main import app
from app.database import get_connection, CREATE_PROGRESS_TABLE, CREATE_PROFILE_TABLE

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Use the test db environment variable or a temp file
    db_path = "test_progress.db"
    os.environ["FITMIND_DB_PATH"] = db_path
    
    # Initialize DB
    from app.database import init_db
    init_db(db_path)
    conn = get_connection(db_path)
    conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test', '!', 'now')")
    conn.commit()
    conn.close()
    
    yield
    
    # Teardown
    for suffix in ["", "-wal", "-shm"]:
        p = db_path + suffix
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

def test_add_progress_entry():
    response = client.post("/api/progress", json={"weight_kg": 90.5})
    assert response.status_code == 200
    data = response.json()
    assert data["weight_kg"] == 90.5
    assert "recorded_at" in data

def test_add_progress_entry_invalid_weight():
    response = client.post("/api/progress", json={"weight_kg": 10.0})
    assert response.status_code == 422
    
    response = client.post("/api/progress", json={"weight_kg": 600.0})
    assert response.status_code == 422

def test_progress_summary_insufficient_data():
    client.post("/api/progress", json={"weight_kg": 90.5})
    client.post("/api/progress", json={"weight_kg": 90.0})
    
    response = client.get("/api/progress/summary")
    data = response.json()
    assert data["entries_count"] == 2
    assert data["trend"] == "insufficient_data"
    assert data["total_change_kg"] == -0.5

def test_progress_summary_losing_trend():
    now = datetime.now(timezone.utc)
    client.post("/api/progress", json={"weight_kg": 95.0, "recorded_at": (now - timedelta(weeks=3)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 94.0, "recorded_at": (now - timedelta(weeks=2)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 93.0, "recorded_at": (now - timedelta(weeks=1)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 92.0, "recorded_at": now.isoformat()})
    
    response = client.get("/api/progress/summary")
    data = response.json()
    assert data["entries_count"] == 4
    assert data["trend"] == "losing"
    assert data["starting_weight"] == 95.0
    assert data["current_weight"] == 92.0
    assert data["total_change_kg"] == -3.0

def test_progress_summary_gaining_trend():
    now = datetime.now(timezone.utc)
    client.post("/api/progress", json={"weight_kg": 70.0, "recorded_at": (now - timedelta(weeks=3)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 71.0, "recorded_at": (now - timedelta(weeks=2)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 72.0, "recorded_at": (now - timedelta(weeks=1)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 73.0, "recorded_at": now.isoformat()})
    
    response = client.get("/api/progress/summary")
    data = response.json()
    assert data["entries_count"] == 4
    assert data["trend"] == "gaining"
    assert data["total_change_kg"] == 3.0

def test_progress_summary_stable_trend():
    now = datetime.now(timezone.utc)
    client.post("/api/progress", json={"weight_kg": 70.0, "recorded_at": (now - timedelta(weeks=3)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 70.1, "recorded_at": (now - timedelta(weeks=2)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 69.9, "recorded_at": (now - timedelta(weeks=1)).isoformat()})
    client.post("/api/progress", json={"weight_kg": 70.0, "recorded_at": now.isoformat()})
    
    response = client.get("/api/progress/summary")
    data = response.json()
    assert data["entries_count"] == 4
    assert data["trend"] == "stable"

def test_delete_progress_entry():
    response = client.post("/api/progress", json={"weight_kg": 90.5})
    entry_id = response.json()["id"]
    
    delete_response = client.delete(f"/api/progress/{entry_id}")
    assert delete_response.status_code == 200
    
    history_response = client.get("/api/progress")
    assert len(history_response.json()["entries"]) == 0

def test_add_progress_entry_future_date_rejected():
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/progress", json={"weight_kg": 90.0, "recorded_at": future_date})
    assert response.status_code == 400
    assert "Cannot record future dates" in response.json()["detail"]
