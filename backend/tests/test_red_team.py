import pytest
from core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from models.event import Event
from seal.chain import seal_event, verify_chain
from datetime import datetime, timezone, date

@pytest.fixture
def red_team_env(app):
    with app.app_context():
        # Clean state
        db.drop_all()
        db.create_all()
        
        # Create an attacker (Doctor A) and a victim patient (Patient B)
        attacker = User(id="ATTACKER", username="dr_evil", password_hash="hash", role="DOCTOR", department="SURGERY", is_active=True)
        victim_patient = Patient(id="VICTIM-P", first_name="John", last_name="Doe", date_of_birth=date(1985, 5, 5))
        
        db.session.add_all([attacker, victim_patient])
        db.session.commit()
        
        secret_record = Record(
            id="SECRET-R", patient_id="VICTIM-P", author_id="ATTACKER", 
            record_type="PSYCH", sensitivity_level="RESTRICTED", 
            data={"secret": "Confidential medical history"}, created_at=datetime.now(timezone.utc)
        )
        db.session.add(secret_record)
        db.session.commit()

def test_attack_bola_idor_unassigned_record(client, red_team_env):
    """
    ATTACK 1: BOLA / IDOR Horizontal Privilege Escalation.
    Attacker tries to view a patient record they have no clinical assignment to.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "ATTACKER"
        
    response = client.get("/api/patients/VICTIM-P/records/SECRET-R")
    
    # Must fail securely with 403 Forbidden
    assert response.status_code == 403
    assert "No active clinical assignment" in response.json["reason"]

def test_attack_audit_log_forgery(app, red_team_env):
    """
    ATTACK 2: Audit Log Corruption & Direct DB Tampering.
    Attacker gets direct access to the database and changes an event reason.
    Seal must immediately flag this as a tamper attempt.
    """
    with app.app_context():
        # Create a legitimate sealed event
        evt = Event(
            id="LEGIT-EVT", type="LOGIN", user_id="ATTACKER", action="AUTH",
            decision="ALLOW", reason="Standard login", timestamp=datetime.now(timezone.utc), current_hash="pending"
        )
        seal_event(evt)
        db.session.add(evt)
        db.session.commit()
        
        # THE ATTACK: Modify the event in the database directly
        compromised = db.session.get(Event, "LEGIT-EVT")
        compromised.reason = "Attacker injected fake reason"
        db.session.commit()
        
        # Verify chain integrity
        report = verify_chain()
        assert report["status"] == "TAMPER_DETECTED"
        assert report["failed_event_id"] == "LEGIT-EVT"

def test_attack_unauthorized_break_glass(client, app, red_team_env):
    """
    ATTACK 3: Administrative Escalation via Break-Glass.
    An unauthorized role tries to invoke emergency override.
    """
    with app.app_context():
        attacker = db.session.get(User, "ATTACKER")
        attacker.role = "GUEST"
        db.session.commit()
        
    with client.session_transaction() as sess:
        sess["user_id"] = "ATTACKER"
        
    response = client.post("/api/break-glass", json={
        "patient_id": "VICTIM-P",
        "reason": "Attempting unauthorized emergency bypass."
    })
    
    assert response.status_code == 403
    assert "Role not authorized" in response.json["error"]