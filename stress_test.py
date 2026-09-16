import requests
import time
import threading

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "dr_smith"
PASSWORD = "password123"

def simulate_data_scraping():
    print(f"--- Initiating Sentinel Stress Test ---")
    
    session = requests.Session()
    login_data = {"username": USERNAME, "password": PASSWORD}
    
    print("[*] Attempting to authenticate...")
    login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"[!] Login failed. HTTP {login_response.status_code}")
        return
        
    print("[+] Authentication successful.")
    
    # 1. Extract the VIP session cookies to pass directly into our threads
    auth_cookies = session.cookies.get_dict()
    if not auth_cookies:
        print("[!] Warning: No cookies were received from the server.")
        
    print("[*] Launching rapid scraping attack (Requesting 50 records in 2 seconds)...")
    
    def fetch_record(patient_id):
        url = f"{BASE_URL}/api/patients/PAT-{patient_id:05d}" 
        
        # 2. Inject the cookies directly into a fresh request
        response = requests.get(url, cookies=auth_cookies)
        
        if response.status_code == 200:
            print(f"[SUCCESS] Downloaded PAT-{patient_id:05d}")
        elif response.status_code == 429:
            print(f"[BLOCKED] Sentinel Velocity Triggered (429) on PAT-{patient_id:05d}")
        elif response.status_code == 403:
            print(f"[BLOCKED] MediGuard Access Denied (403) on PAT-{patient_id:05d}")
        else:
            # 3. Print the EXACT server error message so we aren't guessing
            print(f"[ERROR] HTTP {response.status_code} on PAT-{patient_id:05d} | Reason: {response.text.strip()}")

   # Fire 500 rapid requests across the entire database
    threads = []
    for i in range(1, 501):
        t = threading.Thread(target=fetch_record, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(0.05)

    for t in threads:
        t.join()
        
    print("--- Stress Test Complete ---")

if __name__ == "__main__":
    simulate_data_scraping()