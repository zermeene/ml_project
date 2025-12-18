"""
Configuration file for Air Quality MLOps Pipeline
"""

import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
MODEL_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Data configuration
DATA_FILE = DATA_DIR / "air_quality_data.csv"

# Model file paths
CLASSIFIER_MODEL_PATH = MODEL_DIR / "aqi_classifier.pkl"
REGRESSOR_MODEL_PATH = MODEL_DIR / "pm25_regressor.pkl"
CLUSTERING_MODEL_PATH = MODEL_DIR / "city_clustering.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# Feature columns
POLLUTANT_FEATURES = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
WEATHER_FEATURES = ["temperature", "humidity", "wind_speed"]
TEMPORAL_FEATURES = ["hour", "day_of_week", "month"]
ALL_FEATURES = POLLUTANT_FEATURES + WEATHER_FEATURES + TEMPORAL_FEATURES

# Target columns
CLASSIFICATION_TARGET = "AQI_Category"
REGRESSION_TARGET = "PM2.5"

# Model hyperparameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_CLUSTERS = 3

# Classifier params
CLASSIFIER_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "random_state": RANDOM_STATE,
}

# Regressor params
REGRESSOR_PARAMS = {
    "n_estimators": 100,
    "learning_rate": 0.1,
    "max_depth": 5,
    "random_state": RANDOM_STATE,
}

# API configuration
API_TITLE = "Air Quality Intelligence API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
🌍 Air Quality Monitoring & Intelligence System

This API provides real-time predictions for:
- Air Quality Index (AQI) category classification
- PM2.5 concentration prediction
- City pollution pattern analysis
"""

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Prefect configuration
PREFECT_FLOW_NAME = "air-quality-ml-pipeline"
PREFECT_RETRIES = 2
PREFECT_RETRY_DELAY = 60  # seconds

# Performance thresholds
MIN_CLASSIFIER_ACCURACY = 0.70
MIN_REGRESSOR_R2 = 0.65
MIN_CLUSTERING_SILHOUETTE = 0.45
