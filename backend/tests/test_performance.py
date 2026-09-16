import pytest
import time
from datetime import datetime, timezone, date
from mediguard.policy_engine import evaluate_access
from seal.hashing import canonicalize_event, generate_hash
from seal.chain import verify_chain
from core.database import db
from models.user import User
from models.patient import Patient
from models.record import Record
from models.assignment import Assignment

@pytest.fixture
def perf_context(app):
    with app.app_context():
        user = User(id="P-DOC", username="pdoc", password_hash="hash", role="DOCTOR", department="ICU", is_active=True)
        patient = Patient(id="P-PAT", first_name="Perf", last_name="Test", date_of_birth=date(1980, 1, 1))
        
        db.session.add_all([user, patient])
        db.session.commit()
        
        record = Record(
            id="P-REC", 
            patient_id="P-PAT", 
            author_id="P-DOC", 
            record_type="NOTES", 
            sensitivity_level="STANDARD", 
            data={"vitals": "normal"},
            created_at=datetime.now(timezone.utc)
        )
        assignment = Assignment(id="P-ASGN", user_id="P-DOC", patient_id="P-PAT", purpose="PRIMARY")
        
        db.session.add_all([record, assignment])
        db.session.commit()

def test_policy_engine_throughput(app, perf_context):
    """Measures the execution speed of MediGuard's authorization engine."""
    iterations = 100 
    
    with app.app_context():
        start_time = time.perf_counter()
        for _ in range(iterations):
            # Fetch fresh instances on each iteration to prevent DetachedInstanceError after commits
            user = db.session.get(User, "P-DOC")
            patient = db.session.get(Patient, "P-PAT")
            record = db.session.get(Record, "P-REC")
            
            evaluate_access(user, patient, record, "VIEW")
        end_time = time.perf_counter()
        
    total_time_ms = (end_time - start_time) * 1000
    avg_latency_ms = total_time_ms / iterations
    
    print(f"\n[PERF] MediGuard Policy Engine: {iterations} evaluations in {total_time_ms:.2f}ms (Avg: {avg_latency_ms:.4f}ms/req)")
    
    assert avg_latency_ms < 25.0

def test_cryptographic_hashing_throughput():
    """Measures the speed of Seal's canonicalization and SHA-256 hashing."""
    iterations = 1000
    sample_event = {
        "id": "EVT-PERF-1",
        "type": "RECORD_ACCESS",
        "user_id": "P-DOC",
        "patient_id": "P-PAT",
        "record_id": "P-REC",
        "action": "VIEW",
        "decision": "ALLOW",
        "reason": "Policy conditions met",
        "timestamp": "2026-09-10T12:00:00",
        "previous_hash": "GENESIS"
    }
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        canonical_str = canonicalize_event(sample_event)
        generate_hash(canonical_str)
    end_time = time.perf_counter()
    
    total_time_ms = (end_time - start_time) * 1000
    avg_latency_ms = total_time_ms / iterations
    
    print(f"\n[PERF] Seal Cryptographic Hashing: {iterations} hashes in {total_time_ms:.2f}ms (Avg: {avg_latency_ms:.4f}ms/hash)")
    
    assert avg_latency_ms < 0.5