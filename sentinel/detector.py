from core.database import db
from models.incident import Incident
from sentinel.risk import RISK_WEIGHTS, classify_severity
from datetime import datetime, timezone
import uuid

def analyze_event(event):
    """
    Core Sentinel Detection Engine.
    Processes a single event and updates the user's ongoing risk profile.
    """
    if not event.user_id:
        return None
        
    # Construct a state key, e.g., "RECORD_ACCESS_DENY"
    action_key = f"{event.type}_{event.decision}".upper()
    risk_increase = RISK_WEIGHTS.get(action_key, 0)
    
    if risk_increase == 0:
        return None # Normal behaviour, no state change required
        
    # Find the user's open incident, or create a new one
    incident = Incident.query.filter_by(user_id=event.user_id, status="OPEN").first()
    
    if not incident:
        incident = Incident(
            id=str(uuid.uuid4()),
            user_id=event.user_id,
            risk_score=0,
            severity="LOW",
            status="OPEN",
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(incident)
        
    # Apply incremental risk and cap at 100
    incident.risk_score = min(incident.risk_score + risk_increase, 100)
    incident.severity = classify_severity(incident.risk_score)
    incident.timestamp = datetime.now(timezone.utc)
    
    db.session.commit()
    return incident