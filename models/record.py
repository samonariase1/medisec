from core.database import db

class Record(db.Model):
    __tablename__ = "records"
    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String(36), db.ForeignKey("patients.id"), nullable=False, index=True)
    author_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    sensitivity_level = db.Column(db.String(20), nullable=False) # e.g., STANDARD, HIGH, RESTRICTED
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)