from core.database import db

class Incident(db.Model):
    """Sentinel: Behavioural threat alerts."""
    __tablename__ = "incidents"
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    risk_score = db.Column(db.Integer, nullable=False)
    severity = db.Column(db.String(20), nullable=False) # LOW, MODERATE, HIGH, CRITICAL
    status = db.Column(db.String(20), default="OPEN")
    timestamp = db.Column(db.DateTime, nullable=False)