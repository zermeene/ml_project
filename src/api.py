"""
FastAPI application for Air Quality Intelligence System
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import joblib
import numpy as np
import logging
from datetime import datetime

import sys
from pathlib import Path
# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    CLASSIFIER_MODEL_PATH, REGRESSOR_MODEL_PATH, 
    CLUSTERING_MODEL_PATH, SCALER_PATH
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Global model storage
models = {}


class AirQualityInput(BaseModel):
    """Input schema for air quality prediction"""
    PM2_5: float = Field(..., ge=0, le=500, description="PM2.5 concentration (μg/m³)")
    PM10: float = Field(..., ge=0, le=600, description="PM10 concentration (μg/m³)")
    NO2: float = Field(..., ge=0, le=400, description="NO2 concentration (μg/m³)")
    SO2: float = Field(..., ge=0, le=300, description="SO2 concentration (μg/m³)")
    CO: float = Field(..., ge=0, le=500, description="CO concentration (mg/m³)")
    O3: float = Field(..., ge=0, le=400, description="O3 concentration (μg/m³)")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Humidity (%)")
    wind_speed: float = Field(..., ge=0, le=50, description="Wind speed (m/s)")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    
    class Config:
        schema_extra = {
            "example": {
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
        }


class PM25PredictionInput(BaseModel):
    """Input schema for PM2.5 regression prediction"""
    NO2: float = Field(..., ge=0, le=400)
    SO2: float = Field(..., ge=0, le=300)
    CO: float = Field(..., ge=0, le=500)
    O3: float = Field(..., ge=0, le=400)
    temperature: float = Field(..., ge=-50, le=60)
    humidity: float = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0, le=50)
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    month: int = Field(..., ge=1, le=12)
    
    class Config:
        schema_extra = {
            "example": {
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
        }


class ClassificationResponse(BaseModel):
    """Response schema for AQI classification"""
    aqi_category: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str


class RegressionResponse(BaseModel):
    """Response schema for PM2.5 prediction"""
    predicted_pm25: float
    unit: str = "μg/m³"
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    models_loaded: Dict[str, bool]
    timestamp: str


@app.on_event("startup")
async def load_models():
    """Load all models on startup"""
    try:
        logger.info("Loading models...")
        models['classifier'] = joblib.load(CLASSIFIER_MODEL_PATH)
        models['regressor'] = joblib.load(REGRESSOR_MODEL_PATH)
        models['clustering'] = joblib.load(CLUSTERING_MODEL_PATH)
        models['scaler'] = joblib.load(SCALER_PATH)
        logger.info("✅ All models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "🌍 Air Quality Intelligence API",
        "version": API_VERSION,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict_aqi": "/predict/aqi",
            "predict_pm25": "/predict/pm25"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    models_status = {
        "classifier": "classifier" in models,
        "regressor": "regressor" in models,
        "clustering": "clustering" in models,
        "scaler": "scaler" in models
    }
    
    return {
        "status": "healthy" if all(models_status.values()) else "unhealthy",
        "models_loaded": models_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict/aqi", response_model=ClassificationResponse, tags=["Predictions"])
async def predict_aqi_category(data: AirQualityInput):
    """
    Predict Air Quality Index (AQI) category
    
    Returns one of: Good, Moderate, Unhealthy for Sensitive, Unhealthy, Very Unhealthy
    """
    try:
        # Prepare features
        features = np.array([[
            data.PM2_5, data.PM10, data.NO2, data.SO2, data.CO, data.O3,
            data.temperature, data.humidity, data.wind_speed,
            data.hour, data.day_of_week, data.month,
            data.PM10 / (data.PM2_5 + 1),  # PM_ratio
            (data.PM2_5 + data.PM10 + data.NO2) / 3,  # pollution_index
            1 if data.day_of_week >= 5 else 0,  # is_weekend
            1 if data.hour in [7, 8, 9, 17, 18, 19] else 0,  # is_rush_hour
            data.temperature * data.humidity  # temp_humidity
        ]])
        
        # Scale features
        features_scaled = models['scaler'].transform(features)
        
        # Predict
        prediction = models['classifier'].predict(features_scaled)[0]
        probabilities = models['classifier'].predict_proba(features_scaled)[0]
        
        # Map to class names
        class_names = ['Good', 'Moderate', 'Unhealthy', 'Unhealthy for Sensitive', 'Very Unhealthy']
        predicted_class = class_names[prediction]
        
        # Create probability dict
        prob_dict = {class_names[i]: float(prob) for i, prob in enumerate(probabilities)}
        
        return {
            "aqi_category": predicted_class,
            "confidence": float(probabilities[prediction]),
            "probabilities": prob_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/pm25", response_model=RegressionResponse, tags=["Predictions"])
async def predict_pm25_concentration(data: PM25PredictionInput):
    """
    Predict PM2.5 concentration (μg/m³)
    
    Returns the predicted PM2.5 value based on weather and other pollutants
    """
    try:
        # Prepare features
        features = np.array([[
            data.NO2, data.SO2, data.CO, data.O3,
            data.temperature, data.humidity, data.wind_speed,
            data.hour, data.day_of_week, data.month,
            1 if data.day_of_week >= 5 else 0,  # is_weekend
            1 if data.hour in [7, 8, 9, 17, 18, 19] else 0,  # is_rush_hour
            data.temperature * data.humidity  # temp_humidity
        ]])
        
        # Predict
        prediction = models['regressor'].predict(features)[0]
        
        return {
            "predicted_pm25": float(max(0, prediction)),  # Ensure non-negative
            "unit": "μg/m³",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Predictions"])
async def predict_batch(data: List[AirQualityInput]):
    """
    Batch prediction for multiple air quality measurements
    """
    try:
        results = []
        for item in data:
            # Use the existing prediction function
            result = await predict_aqi_category(item)
            results.append(result)
        
        return {
            "predictions": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
