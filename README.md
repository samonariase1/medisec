# MediSec: Secure Medical Records Management & Provenance Engine

MediSec is a high-performance, cryptographically verifiable medical records management platform built for robust clinical environments. It implements a strict **fail-closed security model** reinforced by three core defensive engines.

---

## Architecture & Core Engines

1. **MediGuard (Context-Aware Authorization Engine)**
   - Protects against BOLA (Broken Object Level Authorization) and IDOR vulnerabilities.
   - Enforces role-based permissions, record sensitivity clearance, and active patient-clinician assignment windows.

2. **Sentinel (Behavioural Threat Detection Engine)**
   - Tracks operational velocity and privilege escalations in $O(1)$ time.
   - Automatically flags suspicious behavior, logs security incidents, and dynamically escalates risk metrics.

3. **Seal (Cryptographic Record Provenance Engine)**
   - Implements blockchain-inspired SHA-256 event hashing with strict canonical JSON serialization (`previous_hash` chaining).
   - Guarantees tamper detection: modifying any historical event invalidates all downstream cryptographic links.

---

## Current Phase 1 Scope

The current deployment focuses on production readiness for the MediSec prototype:

- Render-compatible Flask deployment
- Gunicorn application serving
- Managed PostgreSQL configuration
- Local SQLite development support
- Environment-variable configuration
- Restricted CORS configuration
- Database-aware health checks
- Initial database table creation
- Secure production session settings

The following features are planned for later phases and should not currently be described as fully implemented:

- Complete SHA-256 payload-based hash chaining in Seal
- Automated hash-chain verification
- O(1) Redis-backed Sentinel velocity tracking
- Automated risk response policies
- JWT or OAuth2 browser-extension authentication
- Offline IndexedDB or SQLite synchronization
- Full Flask-Migrate production migration history
- Complete HIPAA compliance certification

MediSec is a security-focused prototype and is not a substitute for a certified HIPAA-compliant healthcare production system.

---

## Quickstart & Installation

1. **Clone and Setup Virtual Environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
