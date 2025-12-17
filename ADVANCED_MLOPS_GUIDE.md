# 🚀 ADVANCED MLOPS FEATURES GUIDE

## 🎯 Complete MLOps Pipeline with Production Features

This project now includes **ADVANCED MLOps features** discussed in class:

✅ **Live Time Series Data** - Real-time API integration  
✅ **Feature Storage** - Centralized feature management  
✅ **Model Registry** - MLflow versioning & tracking  
✅ **Data Drift Monitoring** - Automatic distribution shift detection  
✅ **Model Monitoring** - Performance tracking in production  
✅ **CI/CD Pipeline** - Automated deployment  
✅ **Automatic Testing** - Comprehensive test suite  

---

## 📋 TABLE OF CONTENTS

1. [Live Data Integration](#1-live-data-integration)
2. [Feature Storage](#2-feature-storage)
3. [Model Registry](#3-model-registry)
4. [Data Drift Monitoring](#4-data-drift-monitoring)
5. [Model Monitoring](#5-model-monitoring)
6. [Complete Workflow](#6-complete-workflow)
7. [IEEE Report Guide](#7-ieee-report-guide)

---

## 1. LIVE DATA INTEGRATION

### What It Does
Fetches **real-time air quality data** from OpenAQ API (live measurements from 100+ cities worldwide).

### File: `src/live_data.py`

### Usage

```python
from src.live_data import LiveDataFetcher

# Initialize fetcher
fetcher = LiveDataFetcher()

# Fetch latest data for a city
df = fetcher.fetch_latest_measurements("Delhi", limit=100)

# Fetch time series data
ts_data = fetcher.fetch_time_series("Beijing", parameter="pm25", days=7)

# Fetch multiple cities
cities = ["Delhi", "Beijing", "London"]
multi_city_data = fetcher.get_multiple_cities(cities)
```

### Terminal Commands

```powershell
# Test live data fetching
cd src
python live_data.py
```

**Output:**
```
==============================================================
TESTING LIVE DATA FETCHER
==============================================================

✅ Fetched 50 measurements
Parameters available: ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']

Sample data:
  city    country  parameter  value  ...
  Delhi   IN       pm25       85.3   ...
```

### What You Get
- **Real-time measurements** from actual monitoring stations
- **Time series data** for trend analysis
- **Multiple cities** for comparative studies
- **Automatic transformation** to model format

---

## 2. FEATURE STORAGE

### What It Does
Centralized storage for features with versioning and time-travel queries.

### File: `src/live_data.py` (FeatureStore class)

### Usage

```python
from src.live_data import FeatureStore

# Initialize store
store = FeatureStore()

# Save features
store.save_features(df, feature_group="live_measurements")

# Load latest features
latest = store.get_latest_features("live_measurements", n=100)

# Load all features
all_features = store.load_features()
```

### Storage Format
- **Format:** Apache Parquet (efficient, compressed)
- **Location:** `data/feature_store.parquet`
- **Metadata:** Created timestamp, feature group

### Benefits
1. **Consistency:** Same features in training and serving
2. **Versioning:** Track feature evolution over time
3. **Efficiency:** Fast reads with columnar storage
4. **Time-travel:** Access historical features

---

## 3. MODEL REGISTRY

### What It Does
**MLflow-based** model versioning, tracking, and lifecycle management.

### File: `src/model_registry.py`

### Usage

```python
from src.model_registry import ModelRegistry, register_all_models

# Initialize registry
registry = ModelRegistry()

# Register a model
registry.log_model(
    model=trained_model,
    model_name="aqi_classifier",
    metrics={"accuracy": 0.95, "f1": 0.94},
    params={"n_estimators": 100, "max_depth": 10},
    tags={"version": "v1.0", "author": "Bingbang"}
)

# Load model
model = registry.load_model("aqi_classifier", version=2)

# Promote model to production
registry.promote_model("aqi_classifier", version=2, stage="Production")

# Compare model versions
comparison = registry.compare_models("aqi_classifier", limit=5)
```

### Terminal Commands

```powershell
# Register all trained models
cd src
python model_registry.py
```

**Output:**
```
==============================================================
REGISTERING MODELS WITH MLFLOW
==============================================================

✅ AQI Classifier registered
   - Accuracy: 1.0000
   - F1 Score: 1.0000

✅ PM2.5 Regressor registered
   - R² Score: 0.9240
   - RMSE: 9.10
```

### MLflow UI

```powershell
# Start MLflow UI
mlflow ui
```

Open: **http://localhost:5000**

**Features:**
- View all experiment runs
- Compare model metrics
- Download model artifacts
- Track parameters and hyperparameters
- Visualize metrics over time

### Model Lifecycle

```
Development → Staging → Production → Archived
```

1. **Development:** Model training and experimentation
2. **Staging:** Testing and validation
3. **Production:** Serving live predictions
4. **Archived:** Deprecated models

---

## 4. DATA DRIFT MONITORING

### What It Does
Automatically detects when **production data distribution** differs from training data.

### File: `src/drift_monitoring.py`

### Usage

```python
from src.drift_monitoring import DataDriftDetector

# Initialize with reference (training) data
detector = DataDriftDetector(reference_data=training_df, threshold=0.05)

# Detect drift in current (production) data
report = detector.detect_drift(
    current_data=production_df,
    numeric_features=['PM2.5', 'PM10', 'NO2', 'temperature'],
    categorical_features=['day_of_week']
)

# Check results
if report['summary']['overall_drift']:
    print(f"⚠️ DRIFT DETECTED!")
    print(f"Drifted features: {report['drifted_features']}")
else:
    print(f"✅ No drift detected")

# Save report
detector.save_report(report)

# Calculate statistics drift
stats_comparison = detector.calculate_statistics_drift(
    production_df, 
    numeric_features=['PM2.5', 'PM10']
)
```

### Statistical Tests

**1. Kolmogorov-Smirnov Test** (Numerical features)
- Tests if two distributions are the same
- P-value < 0.05 → Drift detected

**2. Chi-Square Test** (Categorical features)
- Tests goodness-of-fit
- P-value < 0.05 → Drift detected

### Terminal Commands

```powershell
# Test drift detector
cd src
python drift_monitoring.py
```

**Output:**
```
==============================================================
TESTING DATA DRIFT DETECTION
==============================================================

📊 Drift Report:
   Drifted features: ['PM2.5']
   Drift percentage: 33.33%

⚠️  DRIFT DETECTED!
   - PM2.5: p-value = 0.001 (DRIFT)
   - PM10: p-value = 0.234 (OK)
   - temperature: p-value = 0.456 (OK)
```

### When to Retrain

**Trigger retraining if:**
- Drift detected in >20% of features
- Critical features (PM2.5, PM10) show drift
- Model performance drops >5%

---

## 5. MODEL MONITORING

### What It Does
Tracks **model performance** in production (predictions, errors, metrics).

### File: `src/drift_monitoring.py` (ModelPerformanceMonitor class)

### Usage

```python
from src.drift_monitoring import ModelPerformanceMonitor

# Initialize monitor
monitor = ModelPerformanceMonitor()

# Log predictions
monitor.log_prediction(
    prediction=45.3,
    actual=47.1,  # if available
    metadata={"city": "Delhi", "hour": 14}
)

# Calculate metrics over recent predictions
metrics = monitor.calculate_metrics(window_size=100)
print(f"MAE: {metrics['mae']:.2f}")
print(f"RMSE: {metrics['rmse']:.2f}")

# Save logs
monitor.save_logs()
```

### Monitoring Dashboard

The Streamlit frontend (`app.py`) includes monitoring visualization:
- Real-time prediction tracking
- Error distribution plots
- Performance over time
- Alert thresholds

---

## 6. COMPLETE WORKFLOW

### 🎯 End-to-End Pipeline

```
1. LIVE DATA → 2. FEATURE STORE → 3. TRAINING → 
4. MODEL REGISTRY → 5. DEPLOYMENT → 6. MONITORING → 
7. DRIFT DETECTION → [Retrain if needed]
```

### Step-by-Step Commands

#### **Step 1: Fetch Live Data**

```powershell
cd src
python live_data.py
```

#### **Step 2: Train Models with Prefect**

```powershell
python prefect_pipeline.py
```

#### **Step 3: Register Models**

```powershell
python model_registry.py
```

#### **Step 4: Start API Server**

```powershell
# Terminal 1
uvicorn api:app --reload
```

#### **Step 5: Start Frontend**

```powershell
# Terminal 2
cd ..
streamlit run app.py
```

#### **Step 6: Monitor Performance**

```python
# In your application
from src.drift_monitoring import ModelPerformanceMonitor

monitor = ModelPerformanceMonitor()
# Log each prediction
monitor.log_prediction(prediction, actual)
```

#### **Step 7: Check for Drift**

```python
from src.drift_monitoring import DataDriftDetector

detector = DataDriftDetector(training_data)
report = detector.detect_drift(production_data, numeric_features)

if report['summary']['overall_drift']:
    # Trigger retraining
    print("⚠️ Retraining needed!")
```

---

## 7. IEEE REPORT GUIDE

### Using the Template

**File:** `IEEE_RESEARCH_PAPER.md`

### Sections to Complete

1. **Abstract** - Update with your results
2. **Introduction** - Add your motivation
3. **Related Work** - Cite relevant papers
4. **Methodology** - Describe your approach
5. **Results** - Fill in your metrics
6. **Discussion** - Analyze findings
7. **Conclusion** - Summarize contributions

### Tables to Fill

- **TABLE I:** Your classification results
- **TABLE II:** Your regression results
- **TABLE IV:** Your drift detection results
- **TABLE V:** Your API performance

### Figures to Create

- **FIG. 1:** Feature importance chart
- **FIG. 2:** Monitoring dashboard screenshot
- Architecture diagrams (draw using draw.io or similar)

### References Format

```
[1] A. Author, "Title of Paper," Journal Name, vol. X, no. Y, pp. Z-W, Year.
[2] B. Author et al., "Another Paper," Conf. Name, City, Country, Year.
```

---

## 8. ADVANCED FEATURES SUMMARY

### What Makes This Project Advanced

| Feature | Basic Project | **This Project** |
|---------|---------------|------------------|
| Data Source | Static CSV | **Live API** ✅ |
| Features | Hardcoded | **Feature Store** ✅ |
| Models | Pickle files | **MLflow Registry** ✅ |
| Monitoring | None | **Drift Detection** ✅ |
| Deployment | Manual | **CI/CD** ✅ |
| Testing | Basic | **Comprehensive** ✅ |
| Documentation | README | **IEEE Paper** ✅ |

---

## 9. DEMO CHECKLIST

### For Your Video Demonstration

#### **Part 1: Live Data** (2 min)
```powershell
cd src
python live_data.py
# Show real-time data fetching
```

#### **Part 2: Feature Store** (1 min)
```python
# Show feature storage and retrieval
store.save_features(df)
loaded = store.get_latest_features()
```

#### **Part 3: Model Training** (2 min)
```powershell
python prefect_pipeline.py
# Show training progress
```

#### **Part 4: Model Registry** (2 min)
```powershell
python model_registry.py
mlflow ui
# Show MLflow UI
```

#### **Part 5: Drift Monitoring** (2 min)
```powershell
python drift_monitoring.py
# Show drift detection
```

#### **Part 6: API & Frontend** (3 min)
```powershell
uvicorn api:app --reload
streamlit run app.py
# Demo predictions
```

---

## 10. TROUBLESHOOTING

### Issue: MLflow Database Error
```powershell
# Reset MLflow
rm mlflow.db
python src/model_registry.py
```

### Issue: Feature Store Not Found
```powershell
# Create directory
mkdir -p data
# Will auto-create on first save
```

### Issue: Live Data API Timeout
```python
# Increase timeout in live_data.py
response = requests.get(url, timeout=30)  # Increase from 10
```

---

## 11. PRODUCTION DEPLOYMENT

### Using Docker

```powershell
# Build image
docker build -t air-quality-mlops:advanced .

# Run with all features
docker-compose up --build
```

### Environment Variables

```bash
# .env file
OPENAQ_API_KEY=your_key_here
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
DRIFT_THRESHOLD=0.05
MONITORING_WINDOW=100
```

---

## 12. NEXT-LEVEL ENHANCEMENTS

Want to go even further?

1. **Prometheus + Grafana** - Advanced monitoring dashboards
2. **Kubernetes** - Distributed deployment
3. **Apache Kafka** - Real-time data streaming
4. **DVC** - Data version control
5. **SHAP** - Model explainability
6. **A/B Testing** - Compare model versions in production

---

## 🎊 YOU NOW HAVE A PROFESSIONAL-GRADE MLOPS SYSTEM!

**This project demonstrates:**
✅ Live data integration  
✅ Feature engineering & storage  
✅ Model versioning & registry  
✅ Drift monitoring  
✅ Performance tracking  
✅ CI/CD automation  
✅ Production deployment  
✅ IEEE-format documentation  

**Ready for industry! Ready for your demo! SLAAYYY!** 🚀✨

---

**Questions? Check:**
- `COMPLETE_WORKFLOW.md` - Full workflow
- `IEEE_RESEARCH_PAPER.md` - Research paper template
- Source code comments - Detailed explanations
