"""
Data Drift Monitoring
Detects distribution shifts in production data
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataDriftDetector:
    """Detect data drift using statistical tests"""

    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        """
        Initialize drift detector

        Args:
            reference_data: Training/baseline data
            threshold: P-value threshold for drift detection
        """
        self.reference_data = reference_data
        self.threshold = threshold
        self.drift_reports = []

    def kolmogorov_smirnov_test(
        self, feature: str, current_data: pd.DataFrame
    ) -> Tuple[float, bool]:
        """
        KS test for continuous features

        Args:
            feature: Feature name
            current_data: Current/production data

        Returns:
            (p_value, is_drift)
        """
        try:
            ref_values = self.reference_data[feature].dropna()
            curr_values = current_data[feature].dropna()

            if len(ref_values) == 0 or len(curr_values) == 0:
                return 1.0, False

            statistic, p_value = stats.ks_2samp(ref_values, curr_values)
            is_drift = p_value < self.threshold

            return p_value, is_drift

        except Exception as e:
            logger.error(f"KS test error for {feature}: {str(e)}")
            return 1.0, False

    def chi_square_test(
        self, feature: str, current_data: pd.DataFrame
    ) -> Tuple[float, bool]:
        """
        Chi-square test for categorical features

        Args:
            feature: Feature name
            current_data: Current/production data

        Returns:
            (p_value, is_drift)
        """
        try:
            ref_counts = self.reference_data[feature].value_counts()
            curr_counts = current_data[feature].value_counts()

            # Align categories
            all_categories = set(ref_counts.index) | set(curr_counts.index)
            ref_freq = [ref_counts.get(cat, 0) for cat in all_categories]
            curr_freq = [curr_counts.get(cat, 0) for cat in all_categories]

            statistic, p_value = stats.chisquare(curr_freq, ref_freq)
            is_drift = p_value < self.threshold

            return p_value, is_drift

        except Exception as e:
            logger.error(f"Chi-square test error for {feature}: {str(e)}")
            return 1.0, False

    def detect_drift(
        self,
        current_data: pd.DataFrame,
        numeric_features: List[str],
        categorical_features: List[str] = None,
    ) -> Dict:
        """
        Detect drift across all features

        Args:
            current_data: Current/production data
            numeric_features: List of numeric feature names
            categorical_features: List of categorical feature names

        Returns:
            Drift report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(numeric_features)
            + (len(categorical_features) if categorical_features else 0),
            "drifted_features": [],
            "drift_scores": {},
            "summary": {},
        }

        # Test numeric features
        for feature in numeric_features:
            if (
                feature in current_data.columns
                and feature in self.reference_data.columns
            ):
                p_value, is_drift = self.kolmogorov_smirnov_test(feature, current_data)

                report["drift_scores"][feature] = {
                    "p_value": float(p_value),
                    "is_drift": bool(is_drift),
                    "test": "ks_test",
                }

                if is_drift:
                    report["drifted_features"].append(feature)

        # Test categorical features
        if categorical_features:
            for feature in categorical_features:
                if (
                    feature in current_data.columns
                    and feature in self.reference_data.columns
                ):
                    p_value, is_drift = self.chi_square_test(feature, current_data)

                    report["drift_scores"][feature] = {
                        "p_value": float(p_value),
                        "is_drift": bool(is_drift),
                        "test": "chi_square",
                    }

                    if is_drift:
                        report["drifted_features"].append(feature)

        # Summary
        report["summary"] = {
            "num_drifted": len(report["drifted_features"]),
            "drift_percentage": (
                len(report["drifted_features"]) / report["total_features"]
            )
            * 100,
            "overall_drift": len(report["drifted_features"]) > 0,
        }

        self.drift_reports.append(report)

        logger.info(
            f"Drift Detection: {report['summary']['num_drifted']}/{report['total_features']} features drifted"
        )

        return report

    def calculate_statistics_drift(
        self, current_data: pd.DataFrame, numeric_features: List[str]
    ) -> Dict:
        """
        Compare statistical properties (mean, std, etc.)

        Args:
            current_data: Current data
            numeric_features: Numeric features to compare

        Returns:
            Statistics comparison
        """
        comparison = {}

        for feature in numeric_features:
            if (
                feature in current_data.columns
                and feature in self.reference_data.columns
            ):
                ref_stats = {
                    "mean": float(self.reference_data[feature].mean()),
                    "std": float(self.reference_data[feature].std()),
                    "min": float(self.reference_data[feature].min()),
                    "max": float(self.reference_data[feature].max()),
                }

                curr_stats = {
                    "mean": float(current_data[feature].mean()),
                    "std": float(current_data[feature].std()),
                    "min": float(current_data[feature].min()),
                    "max": float(current_data[feature].max()),
                }

                # Calculate percentage changes
                mean_change = (
                    (curr_stats["mean"] - ref_stats["mean"]) / ref_stats["mean"]
                ) * 100
                std_change = (
                    (curr_stats["std"] - ref_stats["std"]) / ref_stats["std"]
                ) * 100

                comparison[feature] = {
                    "reference": ref_stats,
                    "current": curr_stats,
                    "mean_change_pct": float(mean_change),
                    "std_change_pct": float(std_change),
                }

        return comparison

    def save_report(self, report: Dict, filepath: str = "logs/drift_reports.json"):
        """Save drift report to file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Load existing reports
            try:
                with open(filepath, "r") as f:
                    reports = json.load(f)
            except FileNotFoundError:
                reports = []

            # Append new report
            reports.append(report)

            # Save
            with open(filepath, "w") as f:
                json.dump(reports, f, indent=2)

            logger.info(f"Drift report saved to {filepath}")

        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")

    def get_drift_history(
        self, filepath: str = "logs/drift_reports.json"
    ) -> List[Dict]:
        """Load drift history"""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
            return []


class ModelPerformanceMonitor:
    """Monitor model performance in production"""

    def __init__(self):
        self.performance_log = []

    def log_prediction(
        self, prediction: float, actual: float = None, metadata: Dict = None
    ):
        """
        Log a prediction for monitoring

        Args:
            prediction: Model prediction
            actual: Actual value (if available)
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prediction": float(prediction),
            "actual": float(actual) if actual is not None else None,
            "metadata": metadata or {},
        }

        if actual is not None:
            log_entry["error"] = abs(prediction - actual)
            log_entry["squared_error"] = (prediction - actual) ** 2

        self.performance_log.append(log_entry)

    def calculate_metrics(self, window_size: int = 100) -> Dict:
        """
        Calculate performance metrics over recent predictions

        Args:
            window_size: Number of recent predictions to consider

        Returns:
            Performance metrics
        """
        recent_logs = self.performance_log[-window_size:]

        # Filter logs with actuals
        with_actuals = [log for log in recent_logs if log["actual"] is not None]

        if not with_actuals:
            return {"message": "No actual values available"}

        errors = [log["error"] for log in with_actuals]
        squared_errors = [log["squared_error"] for log in with_actuals]

        metrics = {
            "mae": np.mean(errors),
            "rmse": np.sqrt(np.mean(squared_errors)),
            "max_error": np.max(errors),
            "sample_size": len(with_actuals),
        }

        return metrics

    def save_logs(self, filepath: str = "logs/performance_logs.json"):
        """Save performance logs"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(self.performance_log, f, indent=2)
            logger.info(f"Performance logs saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving logs: {str(e)}")


if __name__ == "__main__":
    # Test drift detector
    print("\n" + "=" * 60)
    print("TESTING DATA DRIFT DETECTION")
    print("=" * 60)

    # Create sample data
    np.random.seed(42)
    reference = pd.DataFrame(
        {
            "PM2.5": np.random.normal(50, 10, 1000),
            "PM10": np.random.normal(100, 20, 1000),
            "temperature": np.random.normal(25, 5, 1000),
        }
    )

    # Simulate drift
    current = pd.DataFrame(
        {
            "PM2.5": np.random.normal(70, 15, 500),  # Drifted
            "PM10": np.random.normal(100, 20, 500),  # No drift
            "temperature": np.random.normal(25, 5, 500),  # No drift
        }
    )

    detector = DataDriftDetector(reference)
    report = detector.detect_drift(current, ["PM2.5", "PM10", "temperature"])

    print(f"\n📊 Drift Report:")
    print(f"   Drifted features: {report['drifted_features']}")
    print(f"   Drift percentage: {report['summary']['drift_percentage']:.2f}%")

    if report["summary"]["overall_drift"]:
        print(f"\n⚠️  DRIFT DETECTED!")
    else:
        print(f"\n✅ No significant drift detected")
