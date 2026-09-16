import pytest
from core.database import db
from core.auth import hash_password, RATE_LIMITS
from models.user import User
import time

@pytest.fixture
def test_user(app):
    """Creates a seeded user for testing."""
    with app.app_context():
        user = User(
            id="U-TEST-01",
            username="doctor_who",
            password_hash=hash_password("secure_password_123"),
            role="DOCTOR",
            department="CARDIOLOGY",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        yield user

def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "username": "doctor_who",
        "password": "secure_password_123"
    })
    assert response.status_code == 200
    assert "session" in response.headers.get("Set-Cookie", "")

def test_login_failure_wrong_password(client, test_user):
    response = client.post("/api/auth/login", json={
        "username": "doctor_who",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert response.json["error"] == "Invalid credentials"

def test_login_failure_inactive_account(client, app):
    # Create an inactive account specifically for this test
    with app.app_context():
        inactive_user = User(
            id="U-TEST-02",
            username="inactive_doc",
            password_hash=hash_password("secure_password_123"),
            role="DOCTOR",
            department="CARDIOLOGY",
            is_active=False
        )
        db.session.add(inactive_user)
        db.session.commit()

    response = client.post("/api/auth/login", json={
        "username": "inactive_doc",
        "password": "secure_password_123"
    })
    assert response.status_code == 401

    response = client.post("/api/auth/login", json={
        "username": "doctor_who",
        "password": "secure_password_123"
    })
    assert response.status_code == 401

def test_rate_limiting(client, test_user):
    # Clear the rate limit dictionary before test
    RATE_LIMITS.clear()
    
    # Hit it 5 times (Max attempts)
    for _ in range(5):
        client.post("/api/auth/login", json={"username": "wrong", "password": "x"})
        
    # The 6th attempt should trigger 429 Too Many Requests
    response = client.post("/api/auth/login", json={"username": "wrong", "password": "x"})
    assert response.status_code == 429
    assert "Too many attempts" in response.json["error"]

def test_logout(client, test_user):
    # Login first
    client.post("/api/auth/login", json={
        "username": "doctor_who",
        "password": "secure_password_123"
    })
    
    # Then logout
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    # Flask session clearance typically writes an empty cookie or expires it
    cookie = response.headers.get("Set-Cookie", "")
    assert "session=;" in cookie or "Expires" in cookie