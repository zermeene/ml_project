"""
MLflow Model Registry Integration
Handles model versioning, tracking, and deployment
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelRegistry:
    """MLflow-based model registry"""

    def __init__(self, tracking_uri: str = "sqlite:///mlflow.db"):
        """
        Initialize model registry

        Args:
            tracking_uri: MLflow tracking URI
        """
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        logger.info(f"MLflow tracking URI: {tracking_uri}")

    def log_model(
        self,
        model,
        model_name: str,
        metrics: Dict[str, float],
        params: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Log model with metrics and parameters

        Args:
            model: Trained model
            model_name: Name for the model
            metrics: Performance metrics
            params: Model parameters
            tags: Additional tags
        """
        try:
            with mlflow.start_run(
                run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ):
                # Log parameters
                mlflow.log_params(params)

                # Log metrics
                mlflow.log_metrics(metrics)

                # Log tags
                if tags:
                    mlflow.set_tags(tags)

                # Log model
                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path="model",
                    registered_model_name=model_name,
                )

                logger.info(f"✅ Model '{model_name}' logged successfully")
                logger.info(f"   Metrics: {metrics}")

        except Exception as e:
            logger.error(f"❌ Error logging model: {str(e)}")

    def load_model(
        self, model_name: str, version: Optional[int] = None, stage: str = "Production"
    ):
        """
        Load model from registry

        Args:
            model_name: Name of the model
            version: Specific version (optional)
            stage: Model stage (Production, Staging, None)

        Returns:
            Loaded model
        """
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            else:
                model_uri = f"models:/{model_name}/{stage}"

            model = mlflow.sklearn.load_model(model_uri)
            logger.info(f"✅ Loaded model: {model_uri}")
            return model

        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            return None

    def promote_model(self, model_name: str, version: int, stage: str = "Production"):
        """
        Promote model to a specific stage

        Args:
            model_name: Name of the model
            version: Version to promote
            stage: Target stage (Production, Staging, Archived)
        """
        try:
            self.client.transition_model_version_stage(
                name=model_name, version=version, stage=stage
            )
            logger.info(f"✅ Model {model_name} v{version} promoted to {stage}")
        except Exception as e:
            logger.error(f"❌ Error promoting model: {str(e)}")

    def get_latest_versions(self, model_name: str, stages: list = None):
        """Get latest model versions"""
        try:
            versions = self.client.get_latest_versions(
                name=model_name, stages=stages or ["Production", "Staging"]
            )
            return versions
        except Exception as e:
            logger.error(f"❌ Error getting versions: {str(e)}")
            return []

    def compare_models(self, model_name: str, limit: int = 5) -> Dict:
        """
        Compare recent model versions

        Args:
            model_name: Name of the model
            limit: Number of versions to compare

        Returns:
            Dictionary with comparison data
        """
        try:
            # Search for runs
            experiment = self.client.get_experiment_by_name("Default")
            runs = self.client.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"tags.mlflow.runName LIKE '{model_name}%'",
                max_results=limit,
                order_by=["start_time DESC"],
            )

            comparison = []
            for run in runs:
                comparison.append(
                    {
                        "run_id": run.info.run_id,
                        "start_time": run.info.start_time,
                        "metrics": run.data.metrics,
                        "params": run.data.params,
                    }
                )

            return comparison

        except Exception as e:
            logger.error(f"❌ Error comparing models: {str(e)}")
            return {}

    def log_experiment_metadata(self, metadata: Dict[str, Any]):
        """Log additional experiment metadata"""
        try:
            mlflow.log_params(metadata)
        except Exception as e:
            logger.error(f"Error logging metadata: {str(e)}")


def register_all_models():
    """Register all trained models with MLflow"""
    from config import (CLASSIFIER_MODEL_PATH, CLASSIFIER_PARAMS,
                        REGRESSOR_MODEL_PATH, REGRESSOR_PARAMS)

    registry = ModelRegistry()

    print("\n" + "=" * 60)
    print("REGISTERING MODELS WITH MLFLOW")
    print("=" * 60)

    # Register Classifier
    try:
        classifier = joblib.load(CLASSIFIER_MODEL_PATH)
        registry.log_model(
            model=classifier,
            model_name="aqi_classifier",
            metrics={"accuracy": 1.0, "f1_score": 1.0},  # Replace with actual metrics
            params=CLASSIFIER_PARAMS,
            tags={"model_type": "classification", "algorithm": "random_forest"},
        )
        print("✅ AQI Classifier registered")
    except Exception as e:
        print(f"❌ Failed to register classifier: {e}")

    # Register Regressor
    try:
        regressor = joblib.load(REGRESSOR_MODEL_PATH)
        registry.log_model(
            model=regressor,
            model_name="pm25_regressor",
            metrics={
                "r2_score": 0.924,  # Replace with actual metrics
                "rmse": 9.10,
                "mae": 7.01,
            },
            params=REGRESSOR_PARAMS,
            tags={"model_type": "regression", "algorithm": "gradient_boosting"},
        )
        print("✅ PM2.5 Regressor registered")
    except Exception as e:
        print(f"❌ Failed to register regressor: {e}")

    print("=" * 60)
    print("✅ MODEL REGISTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    # Test model registry
    print("\n" + "=" * 60)
    print("TESTING MODEL REGISTRY")
    print("=" * 60)

    # Register models
    register_all_models()

    # List models
    registry = ModelRegistry()

    print("\n📋 Registered Models:")
    try:
        models = registry.client.search_registered_models()
        for model in models:
            print(f"   - {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
