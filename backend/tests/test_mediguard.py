import pytest
from core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from models.assignment import Assignment
from datetime import datetime, date, timezone

@pytest.fixture
def mediguard_data(app):
    """Seeds the database with users, patients, records, and assignments for auth testing."""
    with app.app_context():
        doc = User(id="DOC1", username="doc1", password_hash="hash", role="DOCTOR", department="ICU", is_active=True)
        nurse = User(id="NURSE1", username="nurse1", password_hash="hash", role="NURSE", department="ICU", is_active=True)
        
        patient1 = Patient(id="P1", first_name="John", last_name="Doe", date_of_birth=date(1980, 1, 1))
        patient2 = Patient(id="P2", first_name="Jane", last_name="Smith", date_of_birth=date(1990, 1, 1))
        
        # 1. Commit the parents first to satisfy strict Foreign Key constraints
        db.session.add_all([doc, nurse, patient1, patient2])
        db.session.commit()
        
        # Standard record for P1
        record1 = Record(id="R1", patient_id="P1", author_id="DOC1", record_type="NOTES", sensitivity_level="STANDARD", data={"note": "Stable"}, created_at=datetime.now(timezone.utc))
        # Restricted record for P1
        record2 = Record(id="R2", patient_id="P1", author_id="DOC1", record_type="PSYCH", sensitivity_level="RESTRICTED", data={"note": "Sensitive"}, created_at=datetime.now(timezone.utc))
        
        # Assign doc to P1 only. Nurse to P1 only.
        assign1 = Assignment(id="A1", user_id="DOC1", patient_id="P1", purpose="PRIMARY")
        assign2 = Assignment(id="A2", user_id="NURSE1", patient_id="P1", purpose="PRIMARY")

        # 2. Commit the children second
        db.session.add_all([record1, record2, assign1, assign2])
        db.session.commit()

def login_as(client, user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

def test_assigned_doctor_access(client, mediguard_data):
    login_as(client, "DOC1")
    response = client.get("/api/patients/P1/records/R1")
    assert response.status_code == 200
    assert response.json["data"]["note"] == "Stable"

def test_unassigned_doctor_denied(client, mediguard_data):
    login_as(client, "DOC1")
    # DOC1 is not assigned to P2
    response = client.get("/api/patients/P2")
    assert response.status_code == 403
    assert "No active clinical assignment" in response.json["reason"]

def test_nurse_restricted_record_denied(client, mediguard_data):
    login_as(client, "NURSE1")
    # Nurse is assigned to P1, but R2 is RESTRICTED sensitivity
    response = client.get("/api/patients/P1/records/R2")
    assert response.status_code == 403
    assert "Insufficient clearance" in response.json["reason"]

def test_record_patient_mismatch_bola(client, mediguard_data):
    login_as(client, "DOC1")
    # R1 belongs to P1. Requesting it under P2 should fail BOLA check instantly.
    response = client.get("/api/patients/P2/records/R1")
    assert response.status_code == 400
    assert "does not belong to specified patient" in response.json["error"]