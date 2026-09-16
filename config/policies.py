"""
Prototype Policies for MediGuard.
In production, these would be loaded into memory from a secure configuration database.
"""
POLICIES = {
    "DOCTOR": {
        "permitted_actions": ["VIEW", "CREATE", "UPDATE"],
        "requires_assignment": True,
        "restricted_sensitivities": [] # Doctors can see all if assigned
    },
    "NURSE": {
        "permitted_actions": ["VIEW", "CREATE"],
        "requires_assignment": True,
        "restricted_sensitivities": ["RESTRICTED"] # Cannot see highly restricted psychiatric/sensitive notes
    },
    "RECORDS_OFFICER": {
        "permitted_actions": ["VIEW"],
        "requires_assignment": False, # Admin role, handles global demographics
        "allowed_patient_fields": ["id", "first_name", "last_name", "date_of_birth"], # Property-level auth
        "restricted_sensitivities": ["HIGH", "RESTRICTED"] # No clinical data access
    }
}