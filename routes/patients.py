from flask import Blueprint, jsonify
from backend.core.auth import login_required
from models.patient import Patient
from backend.core.database import db
from mediguard.policy_engine import evaluate_access

patients_bp = Blueprint("patients", __name__)

@patients_bp.route("/api/patients/<patient_id>", methods=["GET"])
@login_required
def get_patient(user, patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    decision, reason, allowed_fields = evaluate_access(user, patient, None, "VIEW")

    if decision != "ALLOW":
        return jsonify({"error": "Unauthorized", "reason": reason}), 403

    response_data = {k: getattr(patient, k) for k in allowed_fields if hasattr(patient, k)}
    return jsonify(response_data), 200
