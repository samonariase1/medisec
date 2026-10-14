from flask import Blueprint, jsonify
from core.auth import login_required
from models.incident import Incident

sentinel_bp = Blueprint("sentinel", __name__)

@sentinel_bp.route("/api/incidents", methods=["GET"])
@login_required
def get_incidents(user):
    """
    Security Dashboard Endpoint.
    In production, this would be locked to 'SECURITY_ADMIN' roles.
    """
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    
    data = [
        {
            "incident_id": i.id,
            "user_id": i.user_id,
            "risk_score": i.risk_score,
            "severity": i.severity,
            "status": i.status,
            "last_updated": i.timestamp.isoformat()
        } for i in incidents
    ]
    
    return jsonify(data), 200