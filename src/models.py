"""
Machine Learning models for Air Quality prediction
"""

import logging
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, mean_absolute_error,
                             mean_squared_error, r2_score, silhouette_score)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (CLASSIFIER_MODEL_PATH, CLASSIFIER_PARAMS,
                    CLUSTERING_MODEL_PATH, MODEL_DIR, N_CLUSTERS,
                    REGRESSOR_MODEL_PATH, REGRESSOR_PARAMS)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AQIClassifier:
    """Air Quality Index category classifier"""

    def __init__(self):
        self.model = RandomForestClassifier(**CLASSIFIER_PARAMS)
        self.feature_importance = None

    def train(self, X_train, y_train):
        """Train the classifier"""
        logger.info("Training AQI classifier...")
        self.model.fit(X_train, y_train)
        self.feature_importance = self.model.feature_importances_
        logger.info("Classifier training completed")

    def evaluate(self, X_test, y_test, label_encoder):
        """Evaluate classifier performance"""
        logger.info("Evaluating classifier...")
        y_pred = self.model.predict(X_test)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, target_names=label_encoder.classes_
        )

        logger.info(f"Classifier Accuracy: {accuracy:.4f}")
        print("\n" + "=" * 50)
        print("CLASSIFICATION REPORT")
        print("=" * 50)
        print(report)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        self._plot_confusion_matrix(cm, label_encoder.classes_)

        return {
            "accuracy": accuracy,
            "classification_report": report,
            "confusion_matrix": cm,
        }

    def _plot_confusion_matrix(self, cm, classes):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=classes,
            yticklabels=classes,
        )
        plt.title("Confusion Matrix - AQI Classifier")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.tight_layout()
        plt.savefig(MODEL_DIR / "confusion_matrix.png", dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Confusion matrix saved to {MODEL_DIR / 'confusion_matrix.png'}")

    def save(self):
        """Save trained model"""
        joblib.dump(self.model, CLASSIFIER_MODEL_PATH)
        logger.info(f"Classifier saved to {CLASSIFIER_MODEL_PATH}")

    @staticmethod
    def load():
        """Load trained model"""
        return joblib.load(CLASSIFIER_MODEL_PATH)


class PM25Regressor:
    """PM2.5 concentration regressor"""

    def __init__(self):
        self.model = GradientBoostingRegressor(**REGRESSOR_PARAMS)
        self.feature_importance = None

    def train(self, X_train, y_train):
        """Train the regressor"""
        logger.info("Training PM2.5 regressor...")
        self.model.fit(X_train, y_train)
        self.feature_importance = self.model.feature_importances_
        logger.info("Regressor training completed")

    def evaluate(self, X_test, y_test):
        """Evaluate regressor performance"""
        logger.info("Evaluating regressor...")
        y_pred = self.model.predict(X_test)

        # Metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        logger.info(f"Regressor RMSE: {rmse:.4f}")
        logger.info(f"Regressor MAE: {mae:.4f}")
        logger.info(f"Regressor R²: {r2:.4f}")

        # Prediction plot
        self._plot_predictions(y_test, y_pred)

        return {"rmse": rmse, "mae": mae, "r2": r2}

    def _plot_predictions(self, y_test, y_pred):
        """Plot actual vs predicted"""
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5, s=20)
        plt.plot(
            [y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()],
            "r--",
            lw=2,
            label="Perfect Prediction",
        )
        plt.xlabel("Actual PM2.5")
        plt.ylabel("Predicted PM2.5")
        plt.title("PM2.5 Predictions: Actual vs Predicted")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            MODEL_DIR / "regression_predictions.png", dpi=300, bbox_inches="tight"
        )
        plt.close()
        logger.info(
            f"Prediction plot saved to {MODEL_DIR / 'regression_predictions.png'}"
        )

    def save(self):
        """Save trained model"""
        joblib.dump(self.model, REGRESSOR_MODEL_PATH)
        logger.info(f"Regressor saved to {REGRESSOR_MODEL_PATH}")

    @staticmethod
    def load():
        """Load trained model"""
        return joblib.load(REGRESSOR_MODEL_PATH)


class CityClustering:
    """City pollution pattern clustering"""

    def __init__(self):
        self.model = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
        self.labels = None
        self.cities = None

    def train(self, X, cities):
        """Train clustering model"""
        logger.info("Training city clustering...")
        self.labels = self.model.fit_predict(X)
        self.cities = cities
        logger.info("Clustering completed")

    def evaluate(self, X):
        """Evaluate clustering performance"""
        logger.info("Evaluating clustering...")
        silhouette = silhouette_score(X, self.labels)

        logger.info(f"Silhouette Score: {silhouette:.4f}")

        # Show cluster assignments
        print("\n" + "=" * 50)
        print("CITY CLUSTER ASSIGNMENTS")
        print("=" * 50)
        for cluster_id in range(N_CLUSTERS):
            cluster_cities = [
                city
                for city, label in zip(self.cities, self.labels)
                if label == cluster_id
            ]
            print(f"\nCluster {cluster_id}: {', '.join(cluster_cities)}")

        return {
            "silhouette_score": silhouette,
            "cluster_assignments": dict(zip(self.cities, self.labels)),
        }

    def save(self):
        """Save trained model"""
        joblib.dump(self.model, CLUSTERING_MODEL_PATH)
        logger.info(f"Clustering model saved to {CLUSTERING_MODEL_PATH}")

    @staticmethod
    def load():
        """Load trained model"""
        return joblib.load(CLUSTERING_MODEL_PATH)


def train_all_models(data_dict):
    """Train all ML models"""
    results = {}

    # 1. Train Classifier
    print("\n" + "=" * 60)
    print("TASK 1: AQI CLASSIFICATION")
    print("=" * 60)
    classifier = AQIClassifier()
    X_train_cls, X_test_cls, y_train_cls, y_test_cls = data_dict["classification"]
    classifier.train(X_train_cls, y_train_cls)
    results["classification"] = classifier.evaluate(
        X_test_cls, y_test_cls, data_dict["label_encoder"]
    )
    classifier.save()

    # 2. Train Regressor
    print("\n" + "=" * 60)
    print("TASK 2: PM2.5 REGRESSION")
    print("=" * 60)
    regressor = PM25Regressor()
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = data_dict["regression"]
    regressor.train(X_train_reg, y_train_reg)
    results["regression"] = regressor.evaluate(X_test_reg, y_test_reg)
    regressor.save()

    # 3. Train Clustering
    print("\n" + "=" * 60)
    print("TASK 3: CITY CLUSTERING")
    print("=" * 60)
    clustering = CityClustering()
    X_cluster, cities = data_dict["clustering"]
    clustering.train(X_cluster, cities)
    results["clustering"] = clustering.evaluate(X_cluster)
    clustering.save()

    return results


if __name__ == "__main__":
    from preprocessing import DataPreprocessor

    # Preprocess data
    preprocessor = DataPreprocessor()
    data = preprocessor.preprocess_pipeline()

    # Train all models
    results = train_all_models(data)

    print("\n" + "=" * 60)
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Classification Accuracy: {results['classification']['accuracy']:.4f}")
    print(f"Regression R²: {results['regression']['r2']:.4f}")
    print(f"Clustering Silhouette: {results['clustering']['silhouette_score']:.4f}")
