from app import create_app
from core.database import db
from models.user import User
from argon2 import PasswordHasher
import os

app = create_app()
ph = PasswordHasher()

print(f"[DEBUG] Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    db.create_all()
    secure_hash = ph.hash("securepassword123")
    
    # Query by username instead of ID to be 100% safe
    user = User.query.filter_by(username="dr_smith").first()
    
    if user:
        user.password_hash = secure_hash
        print("[DEBUG] Updated existing user password.")
    else:
        doc = User(
            id="DOC-001",
            username="dr_smith",
            role="DOCTOR",
            department="ER",
            is_active=True,
            password_hash=secure_hash
        )
        db.session.add(doc)
        print("[DEBUG] Created new user dr_smith.")
        
    db.session.commit()
    print("SUCCESS: dr_smith is ready with a valid Argon2 hash in the correct database!")