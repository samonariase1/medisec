import hashlib
import json

def canonicalize_event(event_dict):
    """
    Security: Deterministic serialization.
    Ensures the exact same bytes are produced every time, regardless of OS or memory.
    """
    # Remove the current_hash itself, as it cannot be part of the data being hashed
    if "current_hash" in event_dict:
        del event_dict["current_hash"]
        
    # Convert SQLAlchemy object dictionary to strict JSON
    # sort_keys=True ensures consistent order. separators remove all whitespace.
    canonical_string = json.dumps(
        event_dict,
        sort_keys=True,
        separators=(',', ':'),
        default=str # Handles datetime objects by casting to ISO strings
    )
    
    return canonical_string

def generate_hash(canonical_string):
    """Generate SHA-256 hash of the canonical string."""
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()