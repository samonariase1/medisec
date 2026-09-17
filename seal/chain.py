from backend.core.database import db
from models.event import Event
from seal.hashing import canonicalize_event, generate_hash

def _extract_event_data(event):
    """
    Helper to ensure strict determinism. 
    Forces the timestamp into a precise string format (including microseconds) 
    to survive SQLite's database round-trip and maintain chronological order under high throughput.
    """
    ts_str = None
    if event.timestamp:
        # Include microseconds (%f) to guarantee unique ordering in rapid-fire loops
        ts_str = event.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        
    return {
        "id": event.id,
        "type": event.type,
        "user_id": event.user_id,
        "patient_id": event.patient_id,
        "record_id": event.record_id,
        "action": event.action,
        "decision": event.decision,
        "reason": event.reason,
        "timestamp": ts_str,
        "previous_hash": event.previous_hash
    }

def seal_event(event):
    """Links the event to the cryptographic chain and computes its final hash."""
    last_event = Event.query.filter(Event.current_hash != "pending_seal")\
                            .order_by(Event.timestamp.desc(), Event.id.desc()).first()
    
    if last_event:
        event.previous_hash = last_event.current_hash
    else:
        event.previous_hash = "GENESIS"

    # Use the deterministic extractor
    event_dict = _extract_event_data(event)
    canonical_str = canonicalize_event(event_dict)
    event.current_hash = generate_hash(canonical_str)
    
    return event

def verify_chain():
    """
    Traverses the entire event chain, re-hashing each event and verifying 
    that the stored cryptographic hashes match and the previous_hash links are unbroken.
    """
    # Sort deterministically by timestamp and event ID to handle identical timestamps safely
    events = Event.query.order_by(Event.timestamp.asc(), Event.id.asc()).all()
    
    if not events:
        return {"status": "VERIFIED", "message": "Chain is empty."}
        
    expected_previous = "GENESIS"
    
    for event in events:
        # 1. Verify previous hash link
        if event.previous_hash != expected_previous:
            return {
                "status": "CHAIN_BROKEN",
                "failed_event_id": event.id,
                "reason": f"Expected previous_hash {expected_previous}, found {event.previous_hash}"
            }
            
        # 2. Re-compute hash from canonical form
        canonical_str = canonicalize_event(_extract_event_data(event))
        computed_hash = generate_hash(canonical_str)
        
        if event.current_hash != computed_hash:
            return {
                "status": "TAMPER_DETECTED",
                "failed_event_id": event.id,
                "reason": "Cryptographic hash mismatch (Data tampering detected)"
            }
            
        expected_previous = event.current_hash
        
    return {"status": "VERIFIED", "message": f"Successfully verified {len(events)} events in chain."}
