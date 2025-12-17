"""
Unit tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
    
    def test_aqi_prediction_valid_input(self):
        """Test AQI prediction with valid input"""
        payload = {
            "PM2_5": 55.3,
            "PM10": 102.5,
            "NO2": 45.2,
            "SO2": 12.8,
            "CO": 85.3,
            "O3": 65.4,
            "temperature": 25.5,
            "humidity": 65.0,
            "wind_speed": 3.2,
            "hour": 14,
            "day_of_week": 2,
            "month": 6
        }
        
        response = client.post("/predict/aqi", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "aqi_category" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert data["confidence"] >= 0 and data["confidence"] <= 1
    
    def test_aqi_prediction_invalid_input(self):
        """Test AQI prediction with invalid input"""
        payload = {
            "PM2_5": -10,  # Invalid negative value
            "PM10": 102.5,
            "NO2": 45.2,
            "SO2": 12.8,
            "CO": 85.3,
            "O3": 65.4,
            "temperature": 25.5,
            "humidity": 65.0,
            "wind_speed": 3.2,
            "hour": 14,
            "day_of_week": 2,
            "month": 6
        }
        
        response = client.post("/predict/aqi", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_pm25_prediction_valid_input(self):
        """Test PM2.5 prediction with valid input"""
        payload = {
            "NO2": 45.2,
            "SO2": 12.8,
            "CO": 85.3,
            "O3": 65.4,
            "temperature": 25.5,
            "humidity": 65.0,
            "wind_speed": 3.2,
            "hour": 14,
            "day_of_week": 2,
            "month": 6
        }
        
        response = client.post("/predict/pm25", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_pm25" in data
        assert "unit" in data
        assert data["predicted_pm25"] >= 0
    
    def test_batch_prediction(self):
        """Test batch prediction endpoint"""
        payload = [
            {
                "PM2_5": 55.3,
                "PM10": 102.5,
                "NO2": 45.2,
                "SO2": 12.8,
                "CO": 85.3,
                "O3": 65.4,
                "temperature": 25.5,
                "humidity": 65.0,
                "wind_speed": 3.2,
                "hour": 14,
                "day_of_week": 2,
                "month": 6
            },
            {
                "PM2_5": 25.0,
                "PM10": 50.0,
                "NO2": 20.0,
                "SO2": 5.0,
                "CO": 30.0,
                "O3": 80.0,
                "temperature": 20.0,
                "humidity": 50.0,
                "wind_speed": 5.0,
                "hour": 10,
                "day_of_week": 0,
                "month": 3
            }
        ]
        
        response = client.post("/predict/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "count" in data
        assert data["count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
