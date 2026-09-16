import pytest
from core.database import db
from models.user import User
from models.patient import Patient
from models.assignment import Assignment
from models.event import Event
from datetime import date

@pytest.fixture
def bg_data(app):
    """Seeds the database specifically for Break-Glass testing."""
    with app.app_context():
        doc = User(id="BG-DOC", username="bgdoc", password_hash="hash", role="DOCTOR", department="ER", is_active=True)
        clerk = User(id="BG-CLERK", username="bgclerk", password_hash="hash", role="RECORDS_OFFICER", department="ADMIN", is_active=True)
        patient = Patient(id="BG-P1", first_name="Emergency", last_name="Patient", date_of_birth=date(1990, 1, 1))
        
        db.session.add_all([doc, clerk, patient])
        db.session.commit()

def login_as(client, user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

def test_break_glass_success(client, app, bg_data):
    login_as(client, "BG-DOC")
    response = client.post("/api/break-glass", json={
        "patient_id": "BG-P1",
        "reason": "Patient unresponsive in ER, immediate medical history needed."
    })
    assert response.status_code == 201
    assert "valid_until" in response.json
    
    # Verify the temporary assignment was actually created
    with app.app_context():
        assignment = Assignment.query.filter_by(user_id="BG-DOC", patient_id="BG-P1").first()
        assert assignment is not None
        assert "EMERGENCY_OVERRIDE" in assignment.purpose
        
        # Verify the security event was logged
        event = Event.query.filter_by(type="BREAK_GLASS").first()
        assert event is not None

def test_break_glass_unauthorized_role(client, bg_data):
    # Records Officers should never be able to break glass
    login_as(client, "BG-CLERK")
    response = client.post("/api/break-glass", json={
        "patient_id": "BG-P1",
        "reason": "I need to check their address for billing."
    })
    assert response.status_code == 403

def test_break_glass_insufficient_reason(client, bg_data):
    login_as(client, "BG-DOC")
    # Reason must be at least 10 characters
    response = client.post("/api/break-glass", json={
        "patient_id": "BG-P1",
        "reason": "short" 
    })
    assert response.status_code == 400
    assert "detailed reason" in response.json["error"]