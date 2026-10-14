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

## Quickstart & Installation

1. **Clone and Setup Virtual Environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt