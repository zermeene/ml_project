"""
Data preprocessing and feature engineering for air quality data
"""

import logging
import sys
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ALL_FEATURES,
    CLASSIFICATION_TARGET,
    DATA_FILE,
    RANDOM_STATE,
    REGRESSION_TARGET,
    SCALER_PATH,
    TEST_SIZE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handle all data preprocessing and feature engineering"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

    def load_data(self) -> pd.DataFrame:
        """Load air quality dataset"""
        logger.info(f"Loading data from {DATA_FILE}")
        df = pd.read_csv(DATA_FILE)
        logger.info(f"Loaded {len(df)} records")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in dataset"""
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

        # Fill categorical with mode
        categorical_columns = df.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode()[0])

        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create additional features"""
        # Pollution ratio features
        df["PM_ratio"] = df["PM10"] / (df["PM2.5"] + 1)  # Avoid division by zero
        df["pollution_index"] = (df["PM2.5"] + df["PM10"] + df["NO2"]) / 3

        # Temporal features
        df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
        df["is_rush_hour"] = df["hour"].apply(
            lambda x: 1 if x in [7, 8, 9, 17, 18, 19] else 0
        )

        # Weather interaction
        df["temp_humidity"] = df["temperature"] * df["humidity"]

        return df

    def prepare_classification_data(self, df: pd.DataFrame) -> Tuple:
        """Prepare data for AQI category classification"""
        logger.info("Preparing classification data...")

        # Encode target
        y = self.label_encoder.fit_transform(df[CLASSIFICATION_TARGET])

        # Select features
        X = df[
            ALL_FEATURES
            + [
                "PM_ratio",
                "pollution_index",
                "is_weekend",
                "is_rush_hour",
                "temp_humidity",
            ]
        ]

        # Handle any remaining NaN
        X = X.fillna(X.median())

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Save scaler
        joblib.dump(self.scaler, SCALER_PATH)
        logger.info(f"Scaler saved to {SCALER_PATH}")

        return X_train_scaled, X_test_scaled, y_train, y_test

    def prepare_regression_data(self, df: pd.DataFrame) -> Tuple:
        """Prepare data for PM2.5 regression"""
        logger.info("Preparing regression data...")

        # Target
        y = df[REGRESSION_TARGET]

        # Features (excluding PM2.5 and PM10 from features for PM2.5 prediction)
        feature_cols = [f for f in ALL_FEATURES if f not in ["PM2.5", "PM10"]]
        feature_cols += ["is_weekend", "is_rush_hour", "temp_humidity"]

        X = df[feature_cols]
        X = X.fillna(X.median())

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )

        return X_train, X_test, y_train, y_test

    def prepare_clustering_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for city clustering"""
        logger.info("Preparing clustering data...")

        # Aggregate by city
        city_stats = df.groupby("city")[ALL_FEATURES].mean()

        # Normalize
        scaler = StandardScaler()
        city_stats_scaled = scaler.fit_transform(city_stats)

        return city_stats_scaled, city_stats.index.tolist()

    def preprocess_pipeline(self) -> dict:
        """Complete preprocessing pipeline"""
        # Load data
        df = self.load_data()

        # Handle missing values
        df = self.handle_missing_values(df)

        # Create features
        df = self.create_features(df)

        # Prepare all datasets
        classification_data = self.prepare_classification_data(df)
        regression_data = self.prepare_regression_data(df)
        clustering_data = self.prepare_clustering_data(df)

        return {
            "classification": classification_data,
            "regression": regression_data,
            "clustering": clustering_data,
            "label_encoder": self.label_encoder,
        }


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    data = preprocessor.preprocess_pipeline()

    print("\n✅ Data preprocessing completed!")
    print(f"Classification data: {data['classification'][0].shape}")
    print(f"Regression data: {data['regression'][0].shape}")
    print(f"Clustering data: {data['clustering'][0].shape}")
    print(f"Classes: {preprocessor.label_encoder.classes_}")
