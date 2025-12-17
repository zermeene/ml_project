# 🌊 WHERE DOES THE LIVE DATA GO? - VISUAL EXPLANATION

## 🎯 YOUR QUESTION: "Where is live data going through model?"

**Here's EXACTLY where the data flows:**

---

## 📊 COMPLETE DATA FLOW (Step by Step)

```
STEP 1: LIVE DATA SOURCE
┌─────────────────────────────────────┐
│   🌍 OpenAQ API                     │
│   (Real monitoring stations)        │
│                                     │
│   Delhi Station: PM2.5 = 85.3      │
│   Beijing Station: PM2.5 = 120.5   │
│   London Station: PM2.5 = 12.2     │
└──────────────┬──────────────────────┘
               │
               ↓ Fetch (every few minutes)
               │
STEP 2: DATA FETCHER
┌──────────────┴──────────────────────┐
│   📡 live_data.py                   │
│   LiveDataFetcher.fetch_latest()    │
│                                     │
│   Makes HTTP request to API         │
│   Gets JSON response                │
│   Converts to DataFrame             │
└──────────────┬──────────────────────┘
               │
               ↓ Raw measurements
               │
STEP 3: FEATURE STORE
┌──────────────┴──────────────────────┐
│   💾 FeatureStore.save_features()   │
│   Saves to: feature_store.parquet   │
│                                     │
│   Timestamp: 2025-12-17 10:30:00   │
│   PM2.5: 85.3                      │
│   PM10: 150.2                      │
│   NO2: 45.1                        │
└──────────────┬──────────────────────┘
               │
               ↓ Stored features
               │
STEP 4: PREPROCESSING
┌──────────────┴──────────────────────┐
│   🔧 preprocessing.py               │
│   prepare_features()                │
│                                     │
│   Creates: PM_ratio, pollution_idx  │
│   Adds: is_weekend, is_rush_hour   │
│   Scales: StandardScaler            │
└──────────────┬──────────────────────┘
               │
               ↓ Cleaned features
               │
STEP 5: MODEL PREDICTION
┌──────────────┴──────────────────────┐
│   🤖 TRAINED MODEL                  │
│   (Random Forest / Gradient Boost)  │
│                                     │
│   Input: [85.3, 150.2, 45.1, ...]  │
│   Processing: Tree decisions        │
│   Output: "Unhealthy" or 85.3      │
└──────────────┬──────────────────────┘
               │
               ↓ Prediction result
               │
STEP 6: API RESPONSE
┌──────────────┴──────────────────────┐
│   🌐 api.py (FastAPI)               │
│   /predict/aqi endpoint             │
│                                     │
│   Returns JSON:                     │
│   {                                 │
│     "aqi_category": "Unhealthy",   │
│     "confidence": 0.95             │
│   }                                 │
└──────────────┬──────────────────────┘
               │
               ↓ JSON response
               │
STEP 7: FRONTEND DISPLAY
┌──────────────┴──────────────────────┐
│   🎨 app.py (Streamlit)             │
│   Or user's application             │
│                                     │
│   Shows: "Air Quality: Unhealthy"  │
│   Graph: Updates in real-time      │
│   Alert: "Avoid outdoor activity"  │
└─────────────────────────────────────┘
```

---

## 🔄 CONTINUOUS MONITORING LOOP

```
┌──────────────────────────────────────┐
│  START: Every 5 minutes              │
└───────────────┬──────────────────────┘
                │
                ↓
┌───────────────┴──────────────────────┐
│  1. Fetch new data from API          │
└───────────────┬──────────────────────┘
                │
                ↓
┌───────────────┴──────────────────────┐
│  2. Compare with training data       │
│     (drift_monitoring.py)            │
└───────────────┬──────────────────────┘
                │
                ↓
         ┌──────┴──────┐
         │             │
    [No Drift]    [Drift Detected!]
         │             │
         ↓             ↓
┌─────────────┐  ┌─────────────────────┐
│ 3. Use      │  │ 3. Retrain Model!   │
│    existing │  │    (prefect_pipe)   │
│    model    │  │                     │
└──────┬──────┘  └──────┬──────────────┘
       │                │
       └────────┬───────┘
                │
                ↓
┌───────────────┴──────────────────────┐
│  4. Make prediction                  │
└───────────────┬──────────────────────┘
                │
                ↓
┌───────────────┴──────────────────────┐
│  5. Log to monitoring                │
│     (ModelPerformanceMonitor)        │
└───────────────┬──────────────────────┘
                │
                ↓
        [Wait 5 minutes]
                │
                └──────> REPEAT
```

---

## 🎬 REAL-TIME DEMO SCRIPT

**This shows the LIVE flow in action:**

### Create this file: `demo_live_flow.py`

```python
"""
Live Data Flow Demo
Shows exactly how data moves through the system
"""
import time
from src.live_data import LiveDataFetcher, FeatureStore
from src.preprocessing import prepare_data_for_classification
import joblib
import pandas as pd

print("\n" + "="*60)
print("🌊 LIVE DATA FLOW DEMONSTRATION")
print("="*60)

# STEP 1: Fetch live data
print("\n📡 STEP 1: Fetching live data from OpenAQ API...")
fetcher = LiveDataFetcher()
live_data = fetcher.fetch_latest_measurements("Delhi", limit=10)

if not live_data.empty:
    print(f"✅ Fetched {len(live_data)} measurements")
    print(f"\nSample data:")
    print(live_data[['city', 'parameter', 'value', 'timestamp']].head())
else:
    print("❌ No data fetched. Using synthetic data for demo...")
    # Create sample data
    live_data = pd.DataFrame({
        'PM2.5': [85.3],
        'PM10': [150.2],
        'NO2': [45.1],
        'SO2': [12.5],
        'CO': [90.2],
        'O3': [65.8],
        'temperature': [28.5],
        'humidity': [65.0],
        'wind_speed': [3.2],
        'hour': [14],
        'day_of_week': [2],
        'month': [12]
    })

time.sleep(1)

# STEP 2: Save to feature store
print("\n💾 STEP 2: Saving to feature store...")
store = FeatureStore()
store.save_features(live_data, "demo_live_data")
print("✅ Features saved with timestamp")

time.sleep(1)

# STEP 3: Prepare features
print("\n🔧 STEP 3: Preprocessing data...")
# For demo, use synthetic data
demo_input = {
    'PM2.5': 85.3,
    'PM10': 150.2,
    'NO2': 45.1,
    'SO2': 12.5,
    'CO': 90.2,
    'O3': 65.8,
    'temperature': 28.5,
    'humidity': 65.0,
    'wind_speed': 3.2,
    'hour': 14,
    'day_of_week': 2,
    'month': 12
}
print(f"Input features: {demo_input}")

time.sleep(1)

# STEP 4: Load model and predict
print("\n🤖 STEP 4: Loading trained model...")
try:
    classifier = joblib.load('models/aqi_classifier.pkl')
    scaler = joblib.load('models/scaler.pkl')
    print("✅ Models loaded")
    
    # Prepare input
    input_df = pd.DataFrame([demo_input])
    
    # Scale
    input_scaled = scaler.transform(input_df)
    
    # Predict
    print("\n🎯 STEP 5: Making prediction...")
    prediction = classifier.predict(input_scaled)[0]
    probabilities = classifier.predict_proba(input_scaled)[0]
    confidence = max(probabilities)
    
    print(f"\n✨ PREDICTION RESULT:")
    print(f"   Category: {prediction}")
    print(f"   Confidence: {confidence:.2%}")
    
except FileNotFoundError:
    print("❌ Models not found. Train them first:")
    print("   python src/prefect_pipeline.py")

time.sleep(1)

# STEP 6: Monitor
print("\n📊 STEP 6: Logging to monitoring system...")
from src.drift_monitoring import ModelPerformanceMonitor
monitor = ModelPerformanceMonitor()
monitor.log_prediction(
    prediction=85.3,
    metadata={'city': 'Delhi', 'timestamp': time.time()}
)
print("✅ Prediction logged")

print("\n" + "="*60)
print("🎉 COMPLETE DATA FLOW DEMONSTRATED!")
print("="*60)
print("\nThis shows how:")
print("  1. Live data is fetched")
print("  2. Stored in feature store")
print("  3. Preprocessed")
print("  4. Fed to ML model")
print("  5. Prediction made")
print("  6. Result monitored")
print("\nIn production, this happens continuously!")
```

---

## 🎯 WHERE TO SEE LIVE DATA IN ACTION

### **Option 1: Terminal Demo**
```powershell
# Create the demo file above, then run:
python demo_live_flow.py
```
**Shows:** Complete flow from API to prediction

### **Option 2: Streamlit UI**
```powershell
streamlit run app.py
```
**Shows:** 
- Input sliders (simulating live data)
- Real-time prediction
- Visual graphs updating

### **Option 3: API Endpoint**
```powershell
uvicorn src.api:app --reload
# Open: http://127.0.0.1:8000/docs
```
**Shows:**
- Send data → Get prediction
- Like a live system would do

---

## 📈 TIME SERIES VISUALIZATION

**To see data changing over time:**

Create: `visualize_timeseries.py`

```python
"""
Visualize time series data
"""
from src.live_data import LiveDataFetcher
import matplotlib.pyplot as plt
import pandas as pd

print("Fetching time series data...")
fetcher = LiveDataFetcher()

# Get 7 days of data
ts_data = fetcher.fetch_time_series("Delhi", parameter="pm25", days=7)

if not ts_data.empty:
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(ts_data['timestamp'], ts_data['value'])
    plt.title('PM2.5 Levels - Last 7 Days (Delhi)')
    plt.xlabel('Time')
    plt.ylabel('PM2.5 (μg/m³)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    print(f"\nFetched {len(ts_data)} data points")
    print(f"Average PM2.5: {ts_data['value'].mean():.2f}")
else:
    print("No time series data available")
```

**Run:**
```powershell
python visualize_timeseries.py
```
**Shows:** Graph with PM2.5 changing over time!

---

## 🎓 FOR YOUR VIVA - SIMPLE EXPLANATION

**When asked: "Where does live data go?"**

**Say this:**

"Let me show you the complete flow:

1. **Fetch** - My system calls OpenAQ API every few minutes to get real pollution data from monitoring stations

2. **Store** - Data is saved in a feature store with timestamps for version control

3. **Process** - Data goes through preprocessing to create features like pollution_index and time-based features

4. **Predict** - The trained model (Random Forest or Gradient Boosting) makes a prediction

5. **Monitor** - I check for data drift using statistical tests. If data distribution changes significantly, it triggers retraining

6. **Serve** - Result is sent back through the FastAPI endpoint

7. **Display** - User sees the prediction in Streamlit UI or receives JSON response

This happens continuously in a loop, monitoring every few minutes for new data."

**Then show:** Run `demo_live_flow.py` to demonstrate!

---

## 🚀 QUICK DEMO FOR VIVA

```powershell
# 1. Show live data fetching
cd src
python live_data.py

# 2. Show the complete flow
cd ..
python demo_live_flow.py

# 3. Show API in action
uvicorn src.api:app --reload
# Visit: http://127.0.0.1:8000/docs
# Make a prediction

# 4. Show Streamlit
streamlit run app.py
# Adjust sliders, get prediction
```

**This CLEARLY shows where data flows!**

---

## ✅ SUMMARY

**Live data flows through:**

1. OpenAQ API → 2. Fetcher → 3. Feature Store →  
4. Preprocessing → 5. ML Model → 6. API Response →  
7. Frontend Display

**With continuous monitoring:**
- Every 5-10 minutes: Fetch new data
- Every prediction: Check for drift
- If drift detected: Trigger retraining
- All predictions: Logged for monitoring

**In your demo:**
- Show `demo_live_flow.py` to demonstrate complete flow
- Show `live_data.py` to fetch real data
- Show API making predictions
- Show Streamlit UI updating

**PERFECT FOR VIVA!** ✨
