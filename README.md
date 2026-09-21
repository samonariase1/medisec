# MediSec: Secure Medical Records Management & Provenance Engine

MediSec is a high-performance, cryptographically verifiable medical records management platform built for robust clinical environments. It implements a strict **fail-closed security model** reinforced by three core defensive engines.

---

## Architecture & Core Engines

1. **MediGuard (Context-Aware Authorization Engine)**
   - Protects against BOLA (Broken Object Level Authorization) and IDOR vulnerabilities.
   - Enforces role-based permissions, record sensitivity clearance, and active patient-clinician assignment windows.

2. **Sentinel (Behavioural Threat Detection Engine)**
   - Tracks operational velocity and privilege escalations in O(1) time.
   - Automatically flags suspicious behavior, logs security incidents, and dynamically escalates risk metrics.

3. **Seal (Cryptographic Record Provenance Engine)**
   - Implements blockchain-inspired SHA-256 event hashing with strict canonical JSON serialization (`previous_hash` chaining).
   - Guarantees tamper detection: modifying any historical event invalidates all downstream cryptographic links.

---

## Current Phase 1 Scope

The current deployment focuses on production readiness for the MediSec prototype:

- **Production Cloud Deployment:** Stable web application hosting running live on Render.
- **Reliable Data Persistence:** Backed by a managed **Render PostgreSQL** production database cluster.
- **Ecosystem Environment Synchronization:** Built-in platform checks that automatically bridge `/tmp` allocations for staging and isolated absolute pathing locally.
- **RESTful Gateway Protection:** Restricts cross-origin requests to explicitly validated extension origins via secure CORS policies.
- **Robust Infrastructure Monitoring:** Core database-aware `/health` status validation pings that monitor runtime dependencies.
- **Session Lifecycle Controls:** Rigid 30-minute idle expiration windows to reinforce data protection boundaries.

---

## Future Roadmap (Phases 2–4)

The following advanced security and architecture features are slated for upcoming integration milestones:

- Complete SHA-256 record payload-inclusive block chaining inside the Seal engine.
- Automated validation workers that continuously parse history graphs to flag broken cryptographic links.
- Caching layers (Redis) to move Sentinel tracking into pure inline, constant-time sliding windows.
- Automated risk-handling libraries (`risk_handler.py`) to execute dynamic rate-limiting alerts during threshold breaches.
- OAuth2 / JWT Bearer token authentication handshakes between the background browser client and Flask API.
- Bidirectional offline queues utilizing browser IndexedDB storage for low-connectivity clinical settings.
- Formalized HIPAA structural governance certification and complete data-at-rest cryptographic wrappers.

*Disclaimer: MediSec is currently a security-focused prototype designed for proof-of-concept evaluation and is not a substitute for an enterprise-certified medical records platform.*

---

## Quickstart & Local Installation

### 1. Clone the Repository & Initialize Environment
```bash
# Clone your repository
git clone <your-repository-url>
cd medisec

# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Project Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the Development Server Locally
```bash
# Flask will auto-create a local 'instance/app.db' SQLite file automatically
python backend/app.py
```
The local server will boot up at `http://127.0.0`. You can test your system status locally or via your production URL at `https://onrender.com`.

---

# Browser Extension Setup

MediSec is a secure browser extension designed to protect and enhance your web browsing experience.

## 🚀 How to Install (Developer Mode)

Since this extension is loaded locally, follow these steps to install it in your browser:

### For Google Chrome / Microsoft Edge / Brave:
1. **Download the code:** Click the green **Code** button at the top right of this repository page and select **Download ZIP**. 
2. **Extract the ZIP:** Extract the downloaded file somewhere permanent on your computer.
3. **Open Extensions Page:** Open your browser and navigate to:
   * Chrome: `chrome://extensions`
   * Edge: `edge://extensions`
4. **Enable Developer Mode:** Toggle the **Developer mode** switch in the top-right corner of the page.
5. **Load the Extension:** Click the **Load unpacked** button in the top-left corner.
6. **Select Folder:** Select the folder containing your extracted files (the folder where `manifest.json` is located).

---

## ⌨️ Keyboard Shortcuts

To make navigating MediSec faster, you can initialize actions using shortcuts:
* **Open Extension Popup:** Click the extension icon in your toolbar.
* **Customize Shortcuts:** Go to `chrome://extensions/shortcuts` in your browser to bind custom keys for MediSec actions.

## 📁 File Structure

* `manifest.json` - Configuration and permissions for the extension.
* `background.js` - Handles background tasks and persistent processes.
* `content.js` - Interacts directly with web pages.
* `popup.html` & `popup.js` - The user interface and logic when you click the extension icon.
