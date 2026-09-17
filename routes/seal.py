from flask import Blueprint, jsonify
from backend.core.auth import login_required
from seal.chain import verify_chain

seal_bp = Blueprint("seal", __name__)

@seal_bp.route("/api/seal/verify", methods=["GET"])
@login_required
def run_verification(user):
    """
    Triggers a full cryptographic audit of the system.
    """
    if user.role not in ["SECURITY_ADMIN", "RECORDS_OFFICER", "DOCTOR"]: # Adjust for your needs
        return jsonify({"error": "Unauthorized to perform audit"}), 403
        
    report = verify_chain()
    return jsonify(report), 200
