import pytest
from core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from seal.chain import verify_chain
from datetime import datetime, timezone, date

@pytest.fixture
def integration_setup(app):
    """Sets up a clean environment for a full pipeline test."""
    app.config["PROPAGATE_EXCEPTIONS"] = True 
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        doc = User(id="INT-DOC", username="intdoc", password_hash="hash", role="DOCTOR", department="ER", is_active=True)
        p1 = Patient(id="INT-P1", first_name="Int", last_name="Patient", date_of_birth=date(1980, 1, 1))
        db.session.add_all([doc, p1])
        db.session.commit()
        
        rec = Record(id="INT-R1", patient_id="INT-P1", author_id="INT-DOC", record_type="NOTES", sensitivity_level="STANDARD", data={"note": "Test"}, created_at=datetime.now(timezone.utc))
        db.session.add(rec)
        db.session.commit()
        yield doc

def test_full_security_pipeline(client, integration_setup):
    """
    Tests the ultimate competition thesis:
    Request -> MediGuard (DENY) -> Sentinel (Escalate Risk) -> Seal (Cryptographic Hash)
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "INT-DOC"
        
    # 1. Trigger MediGuard Deny (Doctor has no assignment to INT-P1)
    response = client.get("/api/patients/INT-P1/records/INT-R1")
    assert response.status_code == 403
    
    # 2. Verify Sentinel Caught It
    incidents_response = client.get("/api/incidents")
    incidents = incidents_response.json
    assert len(incidents) > 0
    assert incidents[0]["risk_score"] > 0
    
    # 3. Verify Seal Successfully Chained It
    report = verify_chain()
    assert report["status"] == "VERIFIED"
    assert report.get("failed_event_id") is None