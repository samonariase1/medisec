import random
from faker import Faker
from argon2 import PasswordHasher
from app import create_app
from backend.core.database import db
from models.user import User
from models.patient import Patient

fake = Faker('en_NG')
ph = PasswordHasher()

def seed_database(num_doctors=10, num_patients=500):
    app = create_app()
    with app.app_context():
        print("Clearing old data...")
        db.drop_all()
        db.create_all()

        print(f"Generating {num_doctors} Doctors (Users)...")
        doctors = []
        hashed_pw = ph.hash("password123")
        departments = ["Cardiology", "Neurology", "Pediatrics", "Emergency", "Internal Medicine"]
        wards = ["Ward A", "Ward B", "ICU", "Outpatient", "Ward C"]

        for i in range(num_doctors):
            doc_id = f"DOC-{i+1:03d}"
            doc = User(
                id=doc_id,
                username=f"dr_{fake.last_name().lower()}_{i+1}",
                role="Doctor",
                department=random.choice(departments),
                ward=random.choice(wards),
                password_hash=hashed_pw,
                is_active=True
            )
            db.session.add(doc)
            doctors.append(doc)
        
        # Primary test user for the live competition demo
        demo_doc = User(
            id="DOC-999",
            username="dr_smith",
            role="Doctor",
            department="Emergency",
            ward="ICU",
            password_hash=hashed_pw,
            is_active=True
        )
        db.session.add(demo_doc)
        doctors.append(demo_doc)
        db.session.commit()

        print(f"Generating {num_patients} Patients...")

        for i in range(num_patients):
            # Force the first 100 patients to belong to dr_smith (DOC-999)
            if i < 100:
                assigned_doc_id = "DOC-999"
            else:
                assigned_doc = random.choice(doctors)
                assigned_doc_id = assigned_doc.id
                
            pat_id = f"PAT-{i+1:05d}"
            
            patient = Patient(
                id=pat_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=2, maximum_age=85),
                assigned_doctor_id=assigned_doc_id
            )
            db.session.add(patient)
            
            if (i + 1) % 100 == 0:
                print(f"{i + 1} patients generated...")
                db.session.commit()

        db.session.commit()
        print("Database expansive import complete! Ready for Sentinel stress testing.")

if __name__ == "__main__":
    seed_database()
