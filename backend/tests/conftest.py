import pytest
from app.main import app
from app.auth import get_current_user
from fastapi import Request

def mock_get_current_user(request: Request):
    # Skip CSRF check and return a hardcoded user_id=1 for all old tests
    return 1

@pytest.fixture(autouse=True)
def override_dependency(request):
    from app.database import init_db, get_connection
    init_db()
    conn = get_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test@test.com', '!', 'now')")
        conn.commit()
    finally:
        conn.close()
    
    if "test_phase14_auth_multiuser" in request.node.nodeid or "test_isolation_bug" in request.node.nodeid:
        yield
        return
        
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides = {}
