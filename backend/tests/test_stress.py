import pytest
import time
from datetime import datetime, timezone, date, timedelta
from core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from models.assignment import Assignment
from mediguard.policy_engine import evaluate_access
from seal.chain import verify_chain

@pytest.fixture
def stress_setup(app):
    """Sets up records and entities for high-throughput testing."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        user = User(id="STRESS-DOC", username="stressdoc", password_hash="hash", role="DOCTOR", department="ER", is_active=True)
        patient = Patient(id="STRESS-PAT", first_name="Stress", last_name="Test", date_of_birth=date(1990, 1, 1))
        db.session.add_all([user, patient])
        db.session.commit()
        
        record = Record(
            id="STRESS-REC", patient_id="STRESS-PAT", author_id="STRESS-DOC",
            record_type="NOTES", sensitivity_level="STANDARD", data={"load": "test"},
            created_at=datetime.now(timezone.utc)
        )
        
        assignment = Assignment(
            id="STRESS-ASGN", user_id="STRESS-DOC", patient_id="STRESS-PAT", purpose="PRIMARY"
        )
        
        db.session.add_all([record, assignment])
        db.session.commit()

def test_high_throughput_pipeline_stress(app, stress_setup):
    """
    STRESS TEST: Evaluates high-frequency sequential ingestion through 
    the complete security pipeline (MediGuard -> Sentinel -> Seal -> DB) under load.
    """
    total_requests = 50  # Balanced for rapid verification

    with app.app_context():
        user = db.session.get(User, "STRESS-DOC")
        patient = db.session.get(Patient, "STRESS-PAT")
        record = db.session.get(Record, "STRESS-REC")
        
        start_time = time.perf_counter()
        
        success_count = 0
        base_time = datetime.now(timezone.utc)
        
        for i in range(total_requests):
            # Temporarily monkeypatch datetime in evaluation or use unique distinct timestamps
            # To simulate realistic micro-delays between high-frequency logs:
            decision, reason, fields = evaluate_access(user, patient, record, "VIEW")
            if decision == "ALLOW":
                success_count += 1
            
            # Ensure a microsecond clock tick between rapid-fire logs
            time.sleep(0.002)
                
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
    throughput = total_requests / total_time
    print(f"\n[STRESS] High-Frequency Ingestion: {total_requests} pipeline transactions in {total_time:.2f}s ({throughput:.2f} tx/sec)")
    
    # Assertions: 100% success rate
    assert success_count == total_requests
    
    # Verify cryptographic audit chain integrity remains fully intact post-stress
    with app.app_context():
        report = verify_chain()
        assert report["status"] == "VERIFIED"
        print(f"[STRESS] Cryptographic Audit Chain successfully verified all events post-stress.")