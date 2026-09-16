document.getElementById('verifyBtn').addEventListener('click', async () => {
  const statusText = document.getElementById('status-text');
  statusText.textContent = "Verifying session with MediSec API...";

  try {
    // Replace with your local or production backend endpoint
    const response = await fetch('http://127.0.0.1:5000/api/v1/verify-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': 'Bearer <token_from_storage>'
      },
      body: JSON.stringify({ timestamp: new Date().toISOString() })
    });

    if (response.ok) {
      statusText.textContent = "Secure: Access verified & logged.";
      statusText.style.color = "#16a34a";
    } else {
      statusText.textContent = "Warning: Session flagged!";
      statusText.style.color = "#dc2626";
    }
  } catch (error) {
    statusText.textContent = "Error connecting to backend.";
    statusText.style.color = "#dc2626";
    console.error("MediSec API error:", error);
  }
});