from flask import Blueprint, request, jsonify
from backend.core.auth import login_required
from backend.core.database import db
from models.patient import Patient
from models.assignment import Assignment
from models.event import Event
from core.events import dispatch_security_event
import uuid
from datetime import datetime, timedelta, timezone

break_glass_bp = Blueprint("break_glass", __name__)
ALLOWED_ROLES = ["DOCTOR", "NURSE"]

@break_glass_bp.route("/api/break-glass", methods=["POST"])
@login_required
def declare_emergency(user):
    if user.role not in ALLOWED_ROLES:
        return jsonify({"error": "Role not authorized for emergency override"}), 403

    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    reason = data.get("reason", "").strip()

    if not patient_id or len(reason) < 10:
        return jsonify({"error": "Patient ID and a detailed reason (min 10 chars) are required"}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    existing = Assignment.query.filter_by(user_id=user.id, patient_id=patient.id).first()
    now = datetime.now(timezone.utc)
    
    if existing and (not existing.valid_until or existing.valid_until > now):
        return jsonify({"message": "Active assignment already exists"}), 200

    expiry = now + timedelta(hours=2)
    temp_assignment = Assignment(
        id=str(uuid.uuid4()), user_id=user.id, patient_id=patient.id,
        purpose=f"EMERGENCY_OVERRIDE: {reason}", valid_until=expiry
    )
    db.session.add(temp_assignment)
    db.session.commit() # Commit assignment first to prevent FK errors

    evt = Event(
        id=str(uuid.uuid4()), type="BREAK_GLASS", user_id=user.id, patient_id=patient.id,
        action="EMERGENCY_OVERRIDE", decision="ALLOW", reason=reason,
        timestamp=now, current_hash="pending_seal"
    )
    dispatch_security_event(evt) # PIPELINE ROUTING

    return jsonify({"message": "Emergency access granted.", "valid_until": expiry.isoformat()}), 201
