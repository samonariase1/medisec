from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from functools import wraps
from flask import session, request, jsonify
from models.user import User
from core.database import db  # <--- THIS WAS MISSING
import time

ph = PasswordHasher()

# Simple In-Memory Rate Limiter (Prototype scale)
RATE_LIMITS = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

def is_rate_limited(ip):
    now = time.time()
    if ip not in RATE_LIMITS:
        RATE_LIMITS[ip] = []
    RATE_LIMITS[ip] = [t for t in RATE_LIMITS[ip] if now - t < WINDOW_SECONDS]
    
    if len(RATE_LIMITS[ip]) >= MAX_ATTEMPTS:
        return True
    
    RATE_LIMITS[ip].append(now)
    return False

def hash_password(password):
    return ph.hash(password)

def verify_password(hashed, password):
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False

def login_required(f):
    """
    Security: Ensures the request has a valid session and the account is active.
    Passes the trusted database User object to the route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Modern SQLAlchemy 2.0 session get syntax
        user = db.session.get(User, session["user_id"])
        
        if not user or not user.is_active:
            session.clear()
            return jsonify({"error": "Account inactive or unauthorized"}), 401
            
        return f(user, *args, **kwargs)
    return decorated_function