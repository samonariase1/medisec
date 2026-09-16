import pytest
from core.database import db
from models.user import User
from models.event import Event
from models.incident import Incident
from sentinel.detector import analyze_event
from datetime import datetime, timezone
import uuid

@pytest.fixture
def sentinel_data(app):
    with app.app_context():
        user = User(id="S-USER-1", username="hacker", password_hash="hash", role="DOCTOR", department="ICU", is_active=True)
        db.session.add(user)
        db.session.commit()
        yield user

def create_mock_event(user_id, event_type, decision):
    return Event(
        id=str(uuid.uuid4()),
        type=event_type,
        user_id=user_id,
        action="TEST_ACTION",
        decision=decision,
        timestamp=datetime.now(timezone.utc),
        current_hash="pending"
    )

def test_sentinel_normal_behaviour(app, sentinel_data):
    """Normal access should not increase risk."""
    with app.app_context():
        evt = create_mock_event("S-USER-1", "RECORD_ACCESS", "ALLOW")
        incident = analyze_event(evt)
        assert incident is None # No risk added, no incident created

def test_sentinel_suspicious_escalation(app, sentinel_data):
    """Multiple denied accesses should escalate severity up to CRITICAL."""
    with app.app_context():
        # 1st Denial (+15 risk -> LOW)
        evt1 = create_mock_event("S-USER-1", "RECORD_ACCESS", "DENY")
        incident = analyze_event(evt1)
        assert incident.risk_score == 15
        assert incident.severity == "LOW"
        
        # 2nd Denial (+15 risk -> 30 -> MODERATE)
        evt2 = create_mock_event("S-USER-1", "RECORD_ACCESS", "DENY")
        incident = analyze_event(evt2)
        assert incident.risk_score == 30
        assert incident.severity == "MODERATE"
        
        # Break Glass Abuse (+30 risk -> 60 -> HIGH)
        evt3 = create_mock_event("S-USER-1", "BREAK_GLASS", "ALLOW")
        incident = analyze_event(evt3)
        assert incident.risk_score == 60
        assert incident.severity == "HIGH"
        
        # 3 more Denials (+45 risk -> 105 -> Capped at 100 -> CRITICAL)
        for _ in range(3):
            evt_spam = create_mock_event("S-USER-1", "PATIENT_ACCESS", "DENY")
            incident = analyze_event(evt_spam)
            
        assert incident.risk_score == 100
        assert incident.severity == "CRITICAL"