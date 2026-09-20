from flask import Blueprint, render_template

frontend_bp = Blueprint("frontend", __name__)

@frontend_bp.route("/", methods=["GET"])
def index():
    """
    Serves the primary Zero-Trust Clinical Infrastructure landing page
    to users and evaluation judges at the root URL.
    """
    return render_template("index.html")

@frontend_bp.route("/soc-dashboard", methods=["GET"])
def dashboard():
    """
    Serves the secure administrative Security Operations Center (SOC)
    dashboard interface to track real-time telemetry.
    """
    return render_template("dashboard.html")
