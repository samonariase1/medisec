from backend.core.database import db
from sentinel.detector import analyze_event
from seal.chain import seal_event

def dispatch_security_event(event):
    """
    The Central Security Pipeline.
    Every event must pass through Sentinel and Seal before final persistence.
    """
    # 1. Behavioural Threat Analysis (Sentinel)
    analyze_event(event)
    
    # 2. Cryptographic Provenance (Seal)
    sealed_event = seal_event(event)
    
    # 3. Final Persistence
    db.session.add(sealed_event)
    db.session.commit()
    
    return sealed_event
