from flask import Blueprint, render_template

# 1. Initialize the blueprint first!
frontend_bp = Blueprint('frontend', __name__)

# 2. Now you can use it as a decorator
@frontend_bp.route('/')
def landing_page():
    return render_template('landing/index.html')

@frontend_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
