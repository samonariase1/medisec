from config.policies import POLICIES
from models.assignment import Assignment
from models.event import Event
from backend.core.events import dispatch_security_event
import uuid
from datetime import datetime, timezone

def evaluate_access(user, patient, record, action):
    decision = "DENY"
    reason = "Default fail-closed"
    allowed_fields = []

    try:
        role_policy = POLICIES.get(user.role)
        if not role_policy:
            raise ValueError("Role not recognized")

        if action not in role_policy.get("permitted_actions", []):
            raise ValueError(f"Action {action} not permitted for role")

        if record and record.sensitivity_level in role_policy.get("restricted_sensitivities", []):
            raise ValueError("Insufficient clearance for record sensitivity")

        if role_policy.get("requires_assignment"):
            assignment = Assignment.query.filter_by(user_id=user.id, patient_id=patient.id).first()
            if not assignment:
                raise ValueError("No active clinical assignment to patient")
            if assignment.valid_until and assignment.valid_until < datetime.now(timezone.utc):
                raise ValueError("Clinical assignment has expired")

        if record:
            allowed_fields = role_policy.get("allowed_record_fields", ["id", "patient_id", "author_id", "record_type", "data", "created_at"])
        elif patient:
            allowed_fields = role_policy.get("allowed_patient_fields", ["id", "first_name", "last_name", "date_of_birth"])

        decision = "ALLOW"
        reason = "Policy conditions met"

    except ValueError as ve:
        # Security rules naturally drop here, setting the exact denial reason
        decision = "DENY"
        reason = str(ve)
    except Exception as e:
        # True database/system errors drop here and fail closed safely
        decision = "DENY"
        reason = "Authorization engine evaluation error"
    
    # GUARANTEED EXECUTION: Every decision (ALLOW or DENY) is now properly logged
    evt = Event(
        id=str(uuid.uuid4()),
        type="RECORD_ACCESS" if record else "PATIENT_ACCESS",
        user_id=user.id, patient_id=patient.id if patient else None,
        record_id=record.id if record else None, action=action, decision=decision,
        reason=reason, timestamp=datetime.now(timezone.utc), current_hash="pending_seal"
    )
    dispatch_security_event(evt) # PIPELINE ROUTING

    return decision, reason, allowed_fields
