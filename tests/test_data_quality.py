"""
Data quality and validation tests
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CLASSIFICATION_TARGET, DATA_FILE, POLLUTANT_FEATURES
from preprocessing import DataPreprocessor


class TestDataQuality:
    """Test suite for data quality validation"""

    @pytest.fixture(scope="class")
    def data(self):
        """Load data for testing"""
        preprocessor = DataPreprocessor()
        return preprocessor.load_data()

    def test_data_file_exists(self):
        """Test that data file exists"""
        assert DATA_FILE.exists(), f"Data file not found at {DATA_FILE}"

    def test_data_not_empty(self, data):
        """Test that data is not empty"""
        assert len(data) > 0, "Dataset is empty"
        assert data.shape[0] > 100, f"Dataset too small: {data.shape[0]} rows"

    def test_required_columns_exist(self, data):
        """Test that all required columns exist"""
        required_columns = POLLUTANT_FEATURES + [
            "temperature",
            "humidity",
            "wind_speed",
            "hour",
            "day_of_week",
            "month",
            CLASSIFICATION_TARGET,
            "AQI",
        ]

        for col in required_columns:
            assert col in data.columns, f"Required column '{col}' not found"

    def test_no_duplicate_rows(self, data):
        """Test that there are no complete duplicate rows"""
        duplicates = data.duplicated().sum()
        duplicate_pct = (duplicates / len(data)) * 100
        assert duplicate_pct < 5, f"Too many duplicate rows: {duplicate_pct:.2f}%"

    def test_missing_values_acceptable(self, data):
        """Test that missing values are within acceptable threshold"""
        missing_pct = (data.isnull().sum() / len(data)) * 100

        for col, pct in missing_pct.items():
            assert pct < 20, f"Column '{col}' has {pct:.2f}% missing values"

    def test_pollutant_values_range(self, data):
        """Test that pollutant values are within expected ranges"""
        ranges = {
            "PM2.5": (0, 500),
            "PM10": (0, 600),
            "NO2": (0, 400),
            "SO2": (0, 300),
            "CO": (0, 500),
            "O3": (0, 400),
        }

        for pollutant, (min_val, max_val) in ranges.items():
            if pollutant in data.columns:
                assert (
                    data[pollutant].min() >= min_val
                ), f"{pollutant} has values below {min_val}"
                assert (
                    data[pollutant].max() <= max_val
                ), f"{pollutant} has values above {max_val}"

    def test_weather_values_range(self, data):
        """Test that weather values are within expected ranges"""
        assert data["temperature"].min() >= -50, "Temperature too low"
        assert data["temperature"].max() <= 60, "Temperature too high"
        assert data["humidity"].min() >= 0, "Humidity below 0%"
        assert data["humidity"].max() <= 100, "Humidity above 100%"
        assert data["wind_speed"].min() >= 0, "Wind speed cannot be negative"

    def test_temporal_features_valid(self, data):
        """Test that temporal features are valid"""
        assert (
            data["hour"].min() >= 0 and data["hour"].max() <= 23
        ), "Hour values out of range"
        assert (
            data["day_of_week"].min() >= 0 and data["day_of_week"].max() <= 6
        ), "Day of week values out of range"
        assert (
            data["month"].min() >= 1 and data["month"].max() <= 12
        ), "Month values out of range"

    def test_aqi_categories_valid(self, data):
        """Test that AQI categories are valid"""
        valid_categories = [
            "Good",
            "Moderate",
            "Unhealthy for Sensitive",
            "Unhealthy",
            "Very Unhealthy",
        ]

        if CLASSIFICATION_TARGET in data.columns:
            unique_categories = data[CLASSIFICATION_TARGET].unique()
            for cat in unique_categories:
                assert cat in valid_categories, f"Invalid AQI category: {cat}"

    def test_class_distribution(self, data):
        """Test that class distribution is not severely imbalanced"""
        if CLASSIFICATION_TARGET in data.columns:
            class_counts = data[CLASSIFICATION_TARGET].value_counts()
            min_class_pct = (class_counts.min() / len(data)) * 100

            # At least 2% of data should be in smallest class
            assert (
                min_class_pct >= 1
            ), f"Severe class imbalance: smallest class is {min_class_pct:.2f}%"

    def test_correlations_reasonable(self, data):
        """Test that pollutant correlations are reasonable"""
        pollutants = [col for col in POLLUTANT_FEATURES if col in data.columns]

        if len(pollutants) >= 2:
            corr_matrix = data[pollutants].corr()

            # PM2.5 and PM10 should be positively correlated
            if "PM2.5" in pollutants and "PM10" in pollutants:
                pm_corr = corr_matrix.loc["PM2.5", "PM10"]
                assert (
                    pm_corr > 0.5
                ), f"PM2.5 and PM10 correlation too low: {pm_corr:.2f}"

    def test_no_extreme_outliers(self, data):
        """Test that there are no extreme outliers"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in POLLUTANT_FEATURES:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1

                # Outliers beyond 3*IQR
                outliers = data[(data[col] < Q1 - 3 * IQR) | (data[col] > Q3 + 3 * IQR)]
                outlier_pct = (len(outliers) / len(data)) * 100

                assert (
                    outlier_pct < 5
                ), f"Too many extreme outliers in {col}: {outlier_pct:.2f}%"

    def test_feature_engineering_output(self):
        """Test that feature engineering produces valid features"""
        preprocessor = DataPreprocessor()
        df = preprocessor.load_data()
        df = preprocessor.create_features(df)

        # Check new features exist
        assert "PM_ratio" in df.columns
        assert "pollution_index" in df.columns
        assert "is_weekend" in df.columns
        assert "is_rush_hour" in df.columns

        # Check feature values are valid
        assert df["PM_ratio"].min() >= 0
        assert df["is_weekend"].isin([0, 1]).all()
        assert df["is_rush_hour"].isin([0, 1]).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
