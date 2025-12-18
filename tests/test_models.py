"""
Unit tests for ML models
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import (MIN_CLASSIFIER_ACCURACY, MIN_CLUSTERING_SILHOUETTE,
                    MIN_REGRESSOR_R2)
from models import AQIClassifier, CityClustering, PM25Regressor
from preprocessing import DataPreprocessor


class TestMLModels:
    """Test suite for ML models"""

    @pytest.fixture(scope="class")
    def sample_data(self):
        """Generate sample data for testing"""
        preprocessor = DataPreprocessor()
        df = preprocessor.load_data()
        df = preprocessor.handle_missing_values(df)
        df = preprocessor.create_features(df)
        return df

    @pytest.fixture(scope="class")
    def prepared_data(self, sample_data):
        """Prepare datasets for testing"""
        preprocessor = DataPreprocessor()
        return {
            "classification": preprocessor.prepare_classification_data(sample_data),
            "regression": preprocessor.prepare_regression_data(sample_data),
            "clustering": preprocessor.prepare_clustering_data(sample_data),
            "label_encoder": preprocessor.label_encoder,
        }

    def test_classifier_training(self, prepared_data):
        """Test classifier can be trained"""
        classifier = AQIClassifier()
        X_train, X_test, y_train, y_test = prepared_data["classification"]

        # Train
        classifier.train(X_train, y_train)

        # Check model exists
        assert classifier.model is not None
        assert classifier.feature_importance is not None

    def test_classifier_performance(self, prepared_data):
        """Test classifier meets minimum performance threshold"""
        classifier = AQIClassifier()
        X_train, X_test, y_train, y_test = prepared_data["classification"]

        # Train and evaluate
        classifier.train(X_train, y_train)
        results = classifier.evaluate(X_test, y_test, prepared_data["label_encoder"])

        # Check performance
        assert (
            results["accuracy"] >= MIN_CLASSIFIER_ACCURACY
        ), f"Classifier accuracy {results['accuracy']:.4f} below threshold {MIN_CLASSIFIER_ACCURACY}"

    def test_classifier_predictions(self, prepared_data):
        """Test classifier makes valid predictions"""
        classifier = AQIClassifier()
        X_train, X_test, y_train, y_test = prepared_data["classification"]

        classifier.train(X_train, y_train)
        predictions = classifier.model.predict(X_test)

        # Check predictions are valid
        assert len(predictions) == len(y_test)
        assert all(pred >= 0 for pred in predictions)

    def test_regressor_training(self, prepared_data):
        """Test regressor can be trained"""
        regressor = PM25Regressor()
        X_train, X_test, y_train, y_test = prepared_data["regression"]

        # Train
        regressor.train(X_train, y_train)

        # Check model exists
        assert regressor.model is not None
        assert regressor.feature_importance is not None

    def test_regressor_performance(self, prepared_data):
        """Test regressor meets minimum performance threshold"""
        regressor = PM25Regressor()
        X_train, X_test, y_train, y_test = prepared_data["regression"]

        # Train and evaluate
        regressor.train(X_train, y_train)
        results = regressor.evaluate(X_test, y_test)

        # Check performance
        assert (
            results["r2"] >= MIN_REGRESSOR_R2
        ), f"Regressor R² {results['r2']:.4f} below threshold {MIN_REGRESSOR_R2}"
        assert results["rmse"] > 0
        assert results["mae"] > 0

    def test_regressor_predictions(self, prepared_data):
        """Test regressor makes valid predictions"""
        regressor = PM25Regressor()
        X_train, X_test, y_train, y_test = prepared_data["regression"]

        regressor.train(X_train, y_train)
        predictions = regressor.model.predict(X_test)

        # Check predictions are valid
        assert len(predictions) == len(y_test)
        assert all(not np.isnan(pred) for pred in predictions)

    def test_clustering_training(self, prepared_data):
        """Test clustering can be trained"""
        clustering = CityClustering()
        X_cluster, cities = prepared_data["clustering"]

        # Train
        clustering.train(X_cluster, cities)

        # Check model exists
        assert clustering.model is not None
        assert clustering.labels is not None
        assert len(clustering.labels) == len(cities)

    def test_clustering_performance(self, prepared_data):
        """Test clustering meets minimum performance threshold"""
        clustering = CityClustering()
        X_cluster, cities = prepared_data["clustering"]

        # Train and evaluate
        clustering.train(X_cluster, cities)
        results = clustering.evaluate(X_cluster)

        # Check performance
        assert (
            results["silhouette_score"] >= MIN_CLUSTERING_SILHOUETTE
        ), f"Clustering silhouette {results['silhouette_score']:.4f} below threshold {MIN_CLUSTERING_SILHOUETTE}"

    def test_model_persistence(self, prepared_data, tmp_path):
        """Test models can be saved and loaded"""
        import joblib

        # Train classifier
        classifier = AQIClassifier()
        X_train, X_test, y_train, y_test = prepared_data["classification"]
        classifier.train(X_train, y_train)

        # Save
        model_path = tmp_path / "test_classifier.pkl"
        joblib.dump(classifier.model, model_path)

        # Load
        loaded_model = joblib.load(model_path)

        # Compare predictions
        original_pred = classifier.model.predict(X_test)
        loaded_pred = loaded_model.predict(X_test)

        assert np.array_equal(original_pred, loaded_pred)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
