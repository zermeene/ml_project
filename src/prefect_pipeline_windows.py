"""
Prefect workflow orchestration for Air Quality ML Pipeline
WINDOWS COMPATIBLE VERSION
"""

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
import logging
from datetime import datetime

from preprocessing import DataPreprocessor
from models import train_all_models
from config import PREFECT_FLOW_NAME, PREFECT_RETRIES, PREFECT_RETRY_DELAY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(
    name="data-ingestion",
    retries=PREFECT_RETRIES,
    retry_delay_seconds=PREFECT_RETRY_DELAY,
)
def ingest_data():
    """
    Task 1: Data Ingestion
    Load raw air quality data from source
    """
    logger.info("🔄 Starting data ingestion...")
    try:
        preprocessor = DataPreprocessor()
        df = preprocessor.load_data()
        logger.info(f"✅ Data ingestion completed: {len(df)} records loaded")
        return df
    except Exception as e:
        logger.error(f"❌ Data ingestion failed: {str(e)}")
        raise


@task(
    name="data-preprocessing",
    retries=PREFECT_RETRIES,
    retry_delay_seconds=PREFECT_RETRY_DELAY,
)
def preprocess_data(df):
    """
    Task 2: Data Preprocessing & Feature Engineering
    Clean data and create features
    """
    logger.info("🔄 Starting data preprocessing...")
    try:
        preprocessor = DataPreprocessor()

        # Handle missing values
        df = preprocessor.handle_missing_values(df)
        logger.info("✅ Missing values handled")

        # Create features
        df = preprocessor.create_features(df)
        logger.info("✅ Features created")

        return df
    except Exception as e:
        logger.error(f"❌ Data preprocessing failed: {str(e)}")
        raise


@task(
    name="prepare-datasets",
    retries=PREFECT_RETRIES,
    retry_delay_seconds=PREFECT_RETRY_DELAY,
)
def prepare_datasets(df):
    """
    Task 3: Prepare datasets for different ML tasks
    """
    logger.info("🔄 Preparing datasets for ML tasks...")
    try:
        preprocessor = DataPreprocessor()
        preprocessor.scaler = preprocessor.scaler  # Initialize scaler

        # Prepare classification data
        classification_data = preprocessor.prepare_classification_data(df)
        logger.info("✅ Classification dataset prepared")

        # Prepare regression data
        regression_data = preprocessor.prepare_regression_data(df)
        logger.info("✅ Regression dataset prepared")

        # Prepare clustering data
        clustering_data = preprocessor.prepare_clustering_data(df)
        logger.info("✅ Clustering dataset prepared")

        return {
            "classification": classification_data,
            "regression": regression_data,
            "clustering": clustering_data,
            "label_encoder": preprocessor.label_encoder,
        }
    except Exception as e:
        logger.error(f"❌ Dataset preparation failed: {str(e)}")
        raise


@task(
    name="train-models",
    retries=PREFECT_RETRIES,
    retry_delay_seconds=PREFECT_RETRY_DELAY,
)
def train_ml_models(data_dict):
    """
    Task 4: Train all ML models
    - Classification: AQI category prediction
    - Regression: PM2.5 prediction
    - Clustering: City grouping
    """
    logger.info("🔄 Starting model training...")
    try:
        results = train_all_models(data_dict)
        logger.info("✅ All models trained successfully")
        return results
    except Exception as e:
        logger.error(f"❌ Model training failed: {str(e)}")
        raise


@task(
    name="evaluate-models",
    retries=PREFECT_RETRIES,
    retry_delay_seconds=PREFECT_RETRY_DELAY,
)
def evaluate_models(results):
    """
    Task 5: Evaluate and validate model performance
    """
    logger.info("🔄 Evaluating models...")
    try:
        # Get metrics
        classification_accuracy = results["classification"]["accuracy"]
        regression_r2 = results["regression"]["r2"]
        clustering_silhouette = results["clustering"]["silhouette_score"]

        # Performance summary
        summary = {
            "classification": {
                "accuracy": classification_accuracy,
                "status": "PASS" if classification_accuracy > 0.70 else "FAIL",
            },
            "regression": {
                "r2_score": regression_r2,
                "rmse": results["regression"]["rmse"],
                "mae": results["regression"]["mae"],
                "status": "PASS" if regression_r2 > 0.65 else "FAIL",
            },
            "clustering": {
                "silhouette_score": clustering_silhouette,
                "status": "PASS" if clustering_silhouette > 0.45 else "FAIL",
            },
            "overall_status": (
                "SUCCESS"
                if all(
                    [
                        classification_accuracy > 0.70,
                        regression_r2 > 0.65,
                        clustering_silhouette > 0.45,
                    ]
                )
                else "WARNING"
            ),
        }

        logger.info("✅ Model evaluation completed")
        return summary
    except Exception as e:
        logger.error(f"❌ Model evaluation failed: {str(e)}")
        raise


@task(name="generate-report")
def generate_report(summary):
    """
    Task 6: Generate pipeline execution report
    """
    logger.info("🔄 Generating execution report...")
    try:
        report = f"""
        
======================================================================
AIR QUALITY ML PIPELINE - EXECUTION REPORT
======================================================================
Pipeline: {PREFECT_FLOW_NAME}
Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Overall Status: {summary['overall_status']}
======================================================================

MODEL PERFORMANCE SUMMARY
======================================================================

1. AQI CLASSIFICATION (Random Forest)
   - Accuracy: {summary['classification']['accuracy']:.4f}
   - Status: {summary['classification']['status']}

2. PM2.5 REGRESSION (Gradient Boosting)
   - R2 Score: {summary['regression']['r2_score']:.4f}
   - RMSE: {summary['regression']['rmse']:.4f}
   - MAE: {summary['regression']['mae']:.4f}
   - Status: {summary['regression']['status']}

3. CITY CLUSTERING (K-Means)
   - Silhouette Score: {summary['clustering']['silhouette_score']:.4f}
   - Status: {summary['clustering']['status']}

======================================================================
PIPELINE COMPLETED SUCCESSFULLY!
======================================================================
        """

        print(report)
        logger.info("✅ Report generated")

        # Save report to file with UTF-8 encoding (Windows compatible)
        try:
            with open("pipeline_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            logger.info("✅ Report saved to pipeline_report.txt")
        except Exception as e:
            logger.warning(f"⚠️  Could not save report file: {str(e)}")

        return report
    except Exception as e:
        logger.error(f"❌ Report generation failed: {str(e)}")
        raise


@flow(
    name=PREFECT_FLOW_NAME,
    task_runner=ConcurrentTaskRunner(),
    description="End-to-end ML pipeline for air quality prediction",
)
def air_quality_ml_pipeline():
    """
    Main Prefect Flow: Air Quality ML Pipeline

    This flow orchestrates the complete ML workflow:
    1. Data Ingestion
    2. Data Preprocessing
    3. Dataset Preparation
    4. Model Training
    5. Model Evaluation
    6. Report Generation
    """
    logger.info("🚀 Starting Air Quality ML Pipeline...")

    try:
        # Step 1: Ingest data
        raw_data = ingest_data()

        # Step 2: Preprocess data
        processed_data = preprocess_data(raw_data)

        # Step 3: Prepare datasets
        datasets = prepare_datasets(processed_data)

        # Step 4: Train models
        training_results = train_ml_models(datasets)

        # Step 5: Evaluate models
        evaluation_summary = evaluate_models(training_results)

        # Step 6: Generate report
        final_report = generate_report(evaluation_summary)

        logger.info("✅ Pipeline completed successfully!")

        return {
            "status": "SUCCESS",
            "summary": evaluation_summary,
            "report": final_report,
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🌍 AIR QUALITY ML PIPELINE - PREFECT ORCHESTRATION")
    print("=" * 70 + "\n")

    # Run the flow
    result = air_quality_ml_pipeline()

    print("\n" + "=" * 70)
    print(f"FINAL STATUS: {result['status']}")
    print("=" * 70 + "\n")
