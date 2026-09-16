import random
import time
import requests
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://127.0.0.1:5000/api/v1/soc"

# Realistic hospital nodes and threat vectors for simulation
ENDPOINTS = [
    "CLINIC_NODE_NORTH_01", "CLINIC_NODE_EAST_04", "ER_TRAUMA_BAY_02",
    "ICU_MONITOR_WR_05", "PEDIATRIC_WING_08", "SURGICAL_SUITE_12",
    "UNKNOWN_IP_192.168.4.12", "EXTERNAL_GATEWAY_99"
]

ACTIONS = [
    "EMR_RECORD_ACCESS", "TOKEN_VERIFICATION", "BREAK_GLASS_OVERRIDE",
    "PAYLOAD_INJECTION_ATTEMPT", "SESSION_HANDSHAKE", "UNAUTHORIZED_ENUMERATION"
]

STATUSES = [
    ("SUCCESS", "success"),
    ("WARNING", "warning"),
    ("BLOCKED_CRITICAL", "danger")
]

def simulate_telemetry_burst():
    """Generates a batch of randomized, realistic security and access events."""
    endpoint = random.choice(ENDPOINTS)
    action = random.choice(ACTIONS)
    status_label, badge = random.choice(STATUSES)
    
    # Payload structure matching your Flask ingestion expectations
    payload = {
        "endpoint": endpoint,
        "action": action,
        "status": status_label,
        "badge": badge,
        "hash": f"0x{random.randint(10000000, 99999999):x}{random.randint(10000000, 99999999):x}"
    }
    
    try:
        # Assuming you have a telemetry ingestion route, or we target the audit log logger
        response = requests.post(f"{API_URL}/ingest-telemetry", json=payload, timeout=2)
        return response.status_code == 200
    except Exception as e:
        # Fallback if connection fails
        return False

def run_stress_test(total_events=5000, concurrency=20):
    print(f"[*] Starting MediSec Stress Test: Injecting {total_events} events with {concurrency} threads...")
    start_time = time.time()
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(simulate_telemetry_burst) for _ in range(total_events)]
        for future in futures:
            if future.result():
                success_count += 1
                
    duration = time.time() - start_time
    print(f"[+] Stress test complete!")
    print(f"    - Total Events Sent: {total_events}")
    print(f"    - Successful Ingests: {success_count}")
    print(f"    - Time Taken: {duration:.2f} seconds")
    print(f"    - Velocity: {total_events / duration:.2f} events/sec")

if __name__ == "__main__":
    run_stress_test(total_events=500, concurrency=50)