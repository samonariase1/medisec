from core.database import db

class Assignment(db.Model):
    """Links a User to a Patient for authorized clinical context."""
    __tablename__ = "assignments"
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    patient_id = db.Column(db.String(36), db.ForeignKey("patients.id"), nullable=False, index=True)
    purpose = db.Column(db.String(100), nullable=False)
    valid_until = db.Column(db.DateTime, nullable=True)