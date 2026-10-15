import click
from flask.cli import with_appcontext
from datetime import datetime, timezone, date
from backend.core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from models.assignment import Assignment

def register_commands(app):
    """Registers custom Flask CLI commands."""
    
    @app.cli.command("seed-data")
    @with_appcontext
    def seed_data():
        """Populates the database with realistic hospital records and test profiles."""
        print("[SEED] Initializing database seeding...")
        
        # 1. Clear existing data or reset tables if desired (optional)
        # db.drop_all()
        db.create_all()
        
        # 2. Create Hospital Staff (Users)
        users_data = [
            {"id": "DOC-001", "username": "dr_adeleke", "role": "DOCTOR", "department": "ER"},
            {"id": "DOC-002", "username": "dr_okafor", "role": "DOCTOR", "department": "SURGERY"},
            {"id": "NURSE-01", "username": "nurse_sarah", "role": "NURSE", "department": "ER"},
            {"id": "ADMIN-01", "username": "admin_compliance", "role": "ADMIN", "department": "COMPLIANCE"}
        ]
        
        for u in users_data:
            if not db.session.get(User, u["id"]):
                user = User(
                    id=u["id"],
                    username=u["username"],
                    role=u["role"],
                    department=u["department"],
                    is_active=True
                )
                user.set_password("Password123!")
                db.session.add(user)
        
        # 3. Create Synthetic Patients
        patients_data = [
            {"id": "PAT-101", "first_name": "Oluwaseun", "last_name": "Bello", "dob": date(1985, 4, 12)},
            {"id": "PAT-102", "first_name": "Amina", "last_name": "Garba", "dob": date(1992, 8, 23)},
            {"id": "PAT-103", "first_name": "Chinedu", "last_name": "Okafor", "dob": date(1978, 11, 5)}
        ]
        
        for p in patients_data:
            if not db.session.get(Patient, p["id"]):
                patient = Patient(
                    id=p["id"],
                    first_name=p["first_name"],
                    last_name=p["last_name"],
                    date_of_birth=p["dob"]
                )
                db.session.add(patient)
        
        db.session.commit()
        
        # 4. Create Clinical Records & Assignments
        records_data = [
            {"id": "REC-501", "patient_id": "PAT-101", "author_id": "DOC-001", "type": "EMERGENCY_NOTES", "sensitivity": "STANDARD", "note": "Patient presented with acute appendicitis. Stabilized in ER."},
            {"id": "REC-502", "patient_id": "PAT-102", "author_id": "DOC-002", "type": "SURGICAL_LOG", "sensitivity": "RESTRICTED", "note": "Post-operative orthopedic review. Healing progressing normally."},
        ]
        
        for r in records_data:
            if not db.session.get(Record, r["id"]):
                record = Record(
                    id=r["id"],
                    patient_id=r["patient_id"],
                    author_id=r["author_id"],
                    record_type=r["type"],
                    sensitivity_level=r["sensitivity"],
                    data={"clinical_summary": r["note"]},
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(record)
                
        # 5. Assign Doctor 001 to Patient 101 so MediGuard allows authorized access
        if not db.session.get(Assignment, "ASGN-01"):
            assignment = Assignment(
                id="ASGN-01",
                user_id="DOC-001",
                patient_id="PAT-101",
                purpose="PRIMARY_CARE"
            )
            db.session.add(assignment)
            
        db.session.commit()
        print("[SEED] Database successfully seeded with realistic hospital entities!")
