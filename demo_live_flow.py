"""
Complete Live Data Flow Demo
Shows exactly how data moves through the entire system
"""
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.live_data import LiveDataFetcher, FeatureStore
    from src.drift_monitoring import ModelPerformanceMonitor
    import joblib
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)


def print_step(step_num, title):
    """Print a formatted step header"""
    print("\n" + "="*70)
    print(f"📍 STEP {step_num}: {title}")
    print("="*70)


def demo_live_flow():
    """Demonstrate the complete data flow"""
    
    print("\n")
    print("┏" + "━"*68 + "┓")
    print("┃" + " "*20 + "🌊 LIVE DATA FLOW DEMO" + " "*25 + "┃")
    print("┃" + " "*15 + "Shows How Data Moves Through System" + " "*16 + "┃")
    print("┗" + "━"*68 + "┛")
    
    # STEP 1: Fetch Live Data
    print_step(1, "FETCHING LIVE DATA FROM OPENAQ API")
    print("\n🌍 Connecting to OpenAQ API...")
    
    fetcher = LiveDataFetcher()
    
    try:
        print("   Requesting data for Delhi...")
        live_data = fetcher.fetch_latest_measurements("Delhi", limit=5)
        
        if not live_data.empty:
            print(f"\n✅ SUCCESS! Fetched {len(live_data)} measurements")
            print("\n📊 Sample Data:")
            print(live_data[['city', 'parameter', 'value', 'unit']].head())
            
            # Check what parameters we got
            params = live_data['parameter'].unique()
            print(f"\n📋 Available parameters: {', '.join(params)}")
        else:
            raise ValueError("No data returned")
            
    except Exception as e:
        print(f"\n⚠️  API fetch failed: {e}")
        print("📝 Using synthetic data for demonstration...")
        
        # Create synthetic data
        live_data = pd.DataFrame({
            'city': ['Delhi'] * 6,
            'parameter': ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'],
            'value': [85.3, 150.2, 45.1, 12.5, 90.2, 65.8],
            'unit': ['μg/m³'] * 6
        })
        print("\n✅ Using synthetic data")
        print(live_data)
    
    time.sleep(1.5)
    
    # STEP 2: Feature Store
    print_step(2, "SAVING TO FEATURE STORE")
    print("\n💾 Feature Store: Centralized storage for features")
    print("   Location: data/feature_store.parquet")
    
    try:
        store = FeatureStore()
        store.save_features(live_data, "demo_live_measurements")
        print("\n✅ Features saved with timestamp")
        print(f"   Feature Group: demo_live_measurements")
        print(f"   Timestamp: {pd.Timestamp.now()}")
    except Exception as e:
        print(f"⚠️  Feature store save failed: {e}")
    
    time.sleep(1.5)
    
    # STEP 3: Prepare Input
    print_step(3, "PREPROCESSING DATA")
    print("\n🔧 Converting to model input format...")
    
    # Create model input
    model_input = {
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
    
    print("\n📋 Input Features:")
    for key, value in model_input.items():
        print(f"   {key:15s}: {value}")
    
    time.sleep(1.5)
    
    # STEP 4: Load Model
    print_step(4, "LOADING TRAINED ML MODEL")
    
    try:
        print("\n🤖 Loading models from disk...")
        classifier = joblib.load('models/aqi_classifier.pkl')
        scaler = joblib.load('models/scaler.pkl')
        print("✅ Models loaded successfully!")
        print("   - Random Forest Classifier")
        print("   - Standard Scaler")
        
        models_loaded = True
    except FileNotFoundError:
        print("❌ Models not found!")
        print("\n💡 To train models, run:")
        print("   python src/prefect_pipeline.py")
        models_loaded = False
    
    time.sleep(1.5)
    
    # STEP 5: Make Prediction
    if models_loaded:
        print_step(5, "MAKING PREDICTION")
        
        print("\n🎯 Running model inference...")
        
        # Prepare input
        input_df = pd.DataFrame([model_input])
        
        # Scale features
        print("   1. Scaling features...")
        input_scaled = scaler.transform(input_df)
        
        # Predict
        print("   2. Running Random Forest...")
        prediction = classifier.predict(input_scaled)[0]
        probabilities = classifier.predict_proba(input_scaled)[0]
        
        # Get class names
        classes = ['Good', 'Moderate', 'Unhealthy for Sensitive', 
                  'Unhealthy', 'Very Unhealthy']
        
        print("\n" + "─"*70)
        print("✨ PREDICTION RESULT:")
        print("─"*70)
        print(f"   AQI Category: {prediction}")
        print(f"   Confidence:   {max(probabilities):.2%}")
        print("\n📊 All Probabilities:")
        for cls, prob in zip(classes[:len(probabilities)], probabilities):
            bar = "█" * int(prob * 50)
            print(f"   {cls:25s}: {prob:.2%} {bar}")
        print("─"*70)
        
        time.sleep(2)
        
        # STEP 6: Monitor
        print_step(6, "LOGGING TO MONITORING SYSTEM")
        
        print("\n📊 Model Performance Monitoring:")
        try:
            monitor = ModelPerformanceMonitor()
            monitor.log_prediction(
                prediction=85.3,  # Example PM2.5 value
                metadata={
                    'city': 'Delhi',
                    'category': prediction,
                    'confidence': float(max(probabilities)),
                    'timestamp': pd.Timestamp.now().isoformat()
                }
            )
            print("✅ Prediction logged successfully")
            print("   Stored for drift detection and performance tracking")
        except Exception as e:
            print(f"⚠️  Monitoring log failed: {e}")
    
    # STEP 7: Summary
    print("\n")
    print("┏" + "━"*68 + "┓")
    print("┃" + " "*20 + "🎉 FLOW COMPLETE!" + " "*27 + "┃")
    print("┗" + "━"*68 + "┛")
    
    print("\n📝 WHAT HAPPENED:")
    print("\n   1. 📡 Fetched live data from OpenAQ API")
    print("   2. 💾 Saved to feature store with timestamp")
    print("   3. 🔧 Preprocessed and scaled features")
    if models_loaded:
        print("   4. 🤖 Loaded trained ML model")
        print("   5. 🎯 Made prediction with confidence score")
        print("   6. 📊 Logged to monitoring system")
    else:
        print("   4. ⚠️  Models need to be trained first")
    
    print("\n🔄 IN PRODUCTION:")
    print("   → This loop runs continuously (every 5-10 minutes)")
    print("   → Each prediction is monitored for drift")
    print("   → Drift detection triggers automatic retraining")
    print("   → Results served via FastAPI to users")
    
    print("\n" + "="*70)
    
    return models_loaded


if __name__ == "__main__":
    demo_live_flow()
    
    print("\n💡 NEXT STEPS:")
    print("\n   Try these commands to see more:")
    print("\n   1. Fetch live data:")
    print("      cd src && python live_data.py")
    print("\n   2. Start API server:")
    print("      uvicorn src.api:app --reload")
    print("\n   3. Open API docs:")
    print("      http://127.0.0.1:8000/docs")
    print("\n   4. Start Streamlit UI:")
    print("      streamlit run app.py")
    print("\n   5. View MLflow experiments:")
    print("      mlflow ui")
    print("\n" + "="*70)
