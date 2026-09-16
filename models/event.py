from backend.core.database import db

class Event(db.Model):
    """Seal + Sentinel: Cryptographic log of security-significant events."""
    __tablename__ = "events"
    id = db.Column(db.String(36), primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    patient_id = db.Column(db.String(36), db.ForeignKey("patients.id"), nullable=True)
    record_id = db.Column(db.String(36), db.ForeignKey("records.id"), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    decision = db.Column(db.String(20), nullable=False) # ALLOW, DENY, BREAK_GLASS
    reason = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    previous_hash = db.Column(db.String(64), nullable=True) # For Seal chaining
    current_hash = db.Column(db.String(64), nullable=False)