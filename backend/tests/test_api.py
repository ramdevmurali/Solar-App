import pytest
from app import create_app
import numpy as np

class MockModel:
    def predict(self, X):
        # Always return a fixed value for testing
        return np.array([42.0])

def test_predict_valid(monkeypatch):
    app = create_app(model_override=MockModel())
    client = app.test_client()
    # Example valid input
    payload = {
        "temperature_2m": 20.0,
        "precipitation": 0.0,
        "weather_code": 1,
        "cloudcover_low": 10.0,
        "cloudcover_mid": 20.0,
        "cloudcover_high": 30.0,
        "wind_speed_10m": 5.0,
        "timestamp": "2023-10-27T14:00:00"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "predicted_solar_generation_mw" in data
    assert data["predicted_solar_generation_mw"] == 42.0

def test_predict_missing_data():
    app = create_app(model_override=MockModel())
    client = app.test_client()
    # Missing required fields
    payload = {"temperature_2m": 20.0}
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data 