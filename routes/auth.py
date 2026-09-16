from flask import Blueprint, request, jsonify, session
from core.auth import verify_password, is_rate_limited
from core.database import db
from models.user import User
from models.event import Event
from core.events import dispatch_security_event
import uuid
from datetime import datetime, timezone

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Too many attempts. Try again later."}), 429

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.is_active or not verify_password(user.password_hash, password):
        # Even failed logins could be logged to Sentinel in a full implementation
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user.id
    session.permanent = True

    evt = Event(
        id=str(uuid.uuid4()), type="LOGIN", user_id=user.id, action="AUTHENTICATE",
        decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal"
    )
    dispatch_security_event(evt) # PIPELINE ROUTING

    return jsonify({"message": "Authentication successful"}), 200

@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    user_id = session.get("user_id")
    if user_id:
        evt = Event(
            id=str(uuid.uuid4()), type="LOGOUT", user_id=user_id, action="AUTHENTICATE",
            decision="ALLOW", timestamp=datetime.now(timezone.utc), current_hash="pending_seal"
        )
        dispatch_security_event(evt) # PIPELINE ROUTING
    
    session.clear()
    return jsonify({"message": "Logged out securely"}), 200