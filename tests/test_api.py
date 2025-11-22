"""
Basic API Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "GSWS" in response.json()["message"]

def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_services" in data

def test_predictions():
    """Test predictions endpoint"""
    response = client.post("/api/v1/predict", json={"prediction_horizon_days": 7})
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "total_predictions" in data

def test_analytics():
    """Test analytics endpoint"""
    from datetime import datetime, timedelta
    response = client.post("/api/v1/analytics", json={
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat()
    })
    assert response.status_code == 200
    data = response.json()
    assert "total_services" in data
    assert "root_cause_analysis" in data

