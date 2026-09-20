from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import db


health_bp = Blueprint("health", __name__)


def _health_response():
    """
    Check application and database readiness.

    Returns HTTP 200 only when the database connection is working.
    Returns HTTP 503 when the application is running but the database
    is unavailable.
    """
    try:
        db.session.execute(text("SELECT 1"))
        db.session.remove()

        return jsonify(
            {
                "status": "healthy",
                "service": "MediSec",
                "database": "healthy",
            }
        ), 200

    except SQLAlchemyError:
        db.session.rollback()
        db.session.remove()

        return jsonify(
            {
                "status": "unhealthy",
                "service": "MediSec",
                "database": "unavailable",
            }
        ), 503


@health_bp.route("/health", methods=["GET"])
@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return _health_response()
