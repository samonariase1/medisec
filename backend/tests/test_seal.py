import pytest
from core.database import db
from models.event import Event
from models.user import User
from seal.chain import seal_event, verify_chain
from datetime import datetime, timezone
import uuid

@pytest.fixture
def seal_setup(app):
    """Ensures a clean event table and creates the required foreign keys."""
    with app.app_context():
        # Clear out old events
        Event.query.delete()
        
        # Create a dummy user to satisfy the Foreign Key constraint
        if not User.query.filter_by(id="U1").first():
            dummy_user = User(
                id="U1", username="seal_tester", password_hash="hash", 
                role="DOCTOR", department="IT", is_active=True
            )
            db.session.add(dummy_user)
            
        db.session.commit()
        yield

def test_seal_genesis_and_chain(app, seal_setup):
    with app.app_context():
        # Create Event 1 (Genesis)
        evt1 = Event(
            id="EVT-1", type="LOGIN", user_id="U1", action="AUTH", 
            decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal"
        )
        seal_event(evt1)
        db.session.add(evt1)
        db.session.commit()
        
        assert evt1.previous_hash == "GENESIS"
        assert evt1.current_hash != "pending_seal"
        
        # Create Event 2 (Chained)
        evt2 = Event(
            id="EVT-2", type="RECORD_ACCESS", user_id="U1", action="VIEW", 
            decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal"
        )
        seal_event(evt2)
        db.session.add(evt2)
        db.session.commit()
        
        assert evt2.previous_hash == evt1.current_hash
        
        # Verify the chain is mathematically intact
        report = verify_chain()
        assert report["status"] == "VERIFIED"

def test_tamper_detection(app, seal_setup):
    with app.app_context():
        # Create a valid chain of 2 events
        evt1 = Event(id="EVT-1", type="LOGIN", user_id="U1", action="AUTH", decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal")
        seal_event(evt1)
        db.session.add(evt1)
        
        evt2 = Event(id="EVT-2", type="RECORD_ACCESS", user_id="U1", action="VIEW", decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal")
        seal_event(evt2)
        db.session.add(evt2)
        db.session.commit()
        
        # THE ATTACK: A malicious admin alters the database directly to hide what action they took
        malicious_alteration = db.session.get(Event, "EVT-2")
        malicious_alteration.action = "EXPORT"  # Changed from VIEW
        db.session.commit()
        
        # The Audit
        report = verify_chain()
        assert report["status"] == "TAMPER_DETECTED"
        assert report["failed_event_id"] == "EVT-2"