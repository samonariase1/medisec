from flask import Blueprint, jsonify
from backend.core.auth import login_required
from models.patient import Patient
from models.record import Record
from backend.core.database import db
from mediguard.policy_engine import evaluate_access

records_bp = Blueprint("records", __name__)

@records_bp.route("/api/patients/<patient_id>/records/<record_id>", methods=["GET"])
@login_required
def get_record(user, patient_id, record_id):
    patient = db.session.get(Patient, patient_id)
    record = db.session.get(Record, record_id)
    
    if not patient or not record:
        return jsonify({"error": "Not found"}), 404
        
    if record.patient_id != patient.id:
        return jsonify({"error": "Record does not belong to specified patient"}), 400

    decision, reason, allowed_fields = evaluate_access(user, patient, record, "VIEW")

    if decision != "ALLOW":
        return jsonify({"error": "Unauthorized", "reason": reason}), 403

    response_data = {k: getattr(record, k) for k in allowed_fields if hasattr(record, k)}
    return jsonify(response_data), 200
