from flask import Blueprint, render_template

@frontend_bp.route('/')
def landing_page():
    return render_template('landing/index.html') # Or wherever your landing page is located

@frontend_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
