"""
Sentinel Risk Model
These prototype weights determine how suspicious behaviour escalates risk.
"""

RISK_WEIGHTS = {
    # High Risk Indicators
    "BREAK_GLASS_ALLOW": 30,         # Inherently risky, requires scrutiny
    "RECORD_ACCESS_DENY": 15,        # Probing unauthorized records
    "PATIENT_ACCESS_DENY": 15,       # Probing unauthorized patients
    "AUTHENTICATE_DENY": 10,         # Failed logins
    
    # Normal Behaviour (No risk)
    "LOGIN_ALLOW": 0,
    "LOGOUT_ALLOW": 0,
    "RECORD_ACCESS_ALLOW": 0,
    "PATIENT_ACCESS_ALLOW": 0,
}

def classify_severity(score):
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    else:
        return "CRITICAL"