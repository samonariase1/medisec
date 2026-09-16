def test_health_endpoint(client):
    """Ensure the API is responsive."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

def test_global_error_handler(client):
    """Security: Ensure non-existent routes return generic JSON, not HTML stack traces."""
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert "error" in response.json
    assert response.json["error"] == "Not Found"