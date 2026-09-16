def test_frontend_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MediSec Security Dashboard" in response.data