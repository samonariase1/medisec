from backend.core.database import db

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    
    # NEW: Links the patient to a specific doctor for MediGuard checks
    assigned_doctor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)