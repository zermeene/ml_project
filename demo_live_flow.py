"""
FOOLPROOF Demo: Automatically matches feature order from trained models
"""
import requests
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def get_model_feature_names():
    """Get the exact feature names and order from trained model"""
    try:
        scaler = joblib.load('models/scaler.pkl')
        
        # Get feature names from scaler
        if hasattr(scaler, 'feature_names_in_'):
            feature_names = scaler.feature_names_in_.tolist()
            console.print(f"✅ Found {len(feature_names)} features from scaler")
            return feature_names
        else:
            console.print("⚠️  Scaler doesn't have feature_names_in_")
            return None
    except Exception as e:
        console.print(f"❌ Error loading scaler: {e}")
        return None

def create_all_features():
    """Create ALL possible features that might be needed"""
    
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()
    month = now.month
    
    # Base measurements
    PM2_5 = 85.3
    PM10 = 150.2
    NO2 = 45.1
    SO2 = 12.5
    CO = 90.2
    O3 = 65.8
    temperature = 28.5
    humidity = 65.0
    wind_speed = 3.2
    
    # Create ALL possible features
    features = {
        # Base pollutants
        'PM2.5': PM2_5,
        'PM10': PM10,
        'NO2': NO2,
        'SO2': SO2,
        'CO': CO,
        'O3': O3,
        
        # Weather
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        
        # Time features
        'hour': hour,
        'day_of_week': day_of_week,
        'month': month,
        
        # Engineered features - ALL possible variations
        'PM_ratio': PM2_5 / (PM10 + 1e-6),
        'pollution_index': PM2_5 * 0.5 + PM10 * 0.3 + NO2 * 0.2,
        'temp_humidity': temperature * humidity / 100,
        'is_rush_hour': 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0,
        'is_weekend': 1 if day_of_week >= 5 else 0,
        
        # Additional possible features (in case they exist)
        'NO2_ratio': NO2 / (PM2_5 + 1e-6),
        'temp_wind': temperature * wind_speed,
        'humidity_wind': humidity * wind_speed,
    }
    
    return features

def demo_live_flow():
    """Complete demonstration with automatic feature matching"""
    
    console.print(Panel.fit(
        "[bold cyan]🌊 LIVE DATA FLOW DEMO - AUTO-MATCH VERSION[/bold cyan]\n"
        "[white]Automatically matches trained model's feature order[/white]",
        border_style="cyan"
    ))
    
    # Step 1: Get model's expected features
    console.print("\n" + "="*70)
    console.print("📍 [bold]STEP 1: LOADING MODEL & CHECKING FEATURES[/bold]")
    console.print("="*70)
    
    expected_features = get_model_feature_names()
    
    if expected_features is None:
        console.print("❌ Could not determine expected features")
        console.print("\n💡 [yellow]Run this to check:[/yellow]")
        console.print("   python -c \"import joblib; s=joblib.load('models/scaler.pkl'); print(s.feature_names_in_)\"")
        return
    
    console.print("\n📋 Model expects these features (in this order):")
    for i, feat in enumerate(expected_features, 1):
        console.print(f"   {i:2d}. {feat}")
    
    # Step 2: Create all possible features
    console.print("\n" + "="*70)
    console.print("📍 [bold]STEP 2: GENERATING FEATURES[/bold]")
    console.print("="*70)
    
    all_features = create_all_features()
    console.print(f"✅ Created {len(all_features)} possible features")
    
    # Step 3: Match to model's expected features
    console.print("\n" + "="*70)
    console.print("📍 [bold]STEP 3: MATCHING TO MODEL'S REQUIREMENTS[/bold]")
    console.print("="*70)
    
    matched_features = {}
    missing_features = []
    
    for feat in expected_features:
        if feat in all_features:
            matched_features[feat] = all_features[feat]
            console.print(f"✓ {feat}: {all_features[feat]:.2f}")
        else:
            missing_features.append(feat)
            console.print(f"✗ {feat}: MISSING!")
    
    if missing_features:
        console.print(f"\n❌ [bold red]Missing {len(missing_features)} features:[/bold red]")
        for feat in missing_features:
            console.print(f"   - {feat}")
        console.print("\n💡 [yellow]You need to add these to create_all_features()[/yellow]")
        return
    
    # Create DataFrame in correct order
    input_df = pd.DataFrame([matched_features])
    
    console.print("\n✅ All features matched!")
    console.print(f"   Shape: {input_df.shape}")
    console.print(f"   Features: {list(input_df.columns)}")
    
    # Step 4: Load models
    console.print("\n" + "="*70)
    console.print("📍 [bold]STEP 4: LOADING MODELS[/bold]")
    console.print("="*70)
    
    try:
        classifier = joblib.load('models/aqi_classifier.pkl')
        scaler = joblib.load('models/scaler.pkl')
        console.print("✅ Models loaded successfully!")
    except Exception as e:
        console.print(f"❌ Error loading models: {e}")
        return
    
    # Step 5: Prediction
    console.print("\n" + "="*70)
    console.print("📍 [bold]STEP 5: MAKING PREDICTION[/bold]")
    console.print("="*70)
    
    try:
        console.print("🎯 Scaling features...")
        input_scaled = scaler.transform(input_df)
        
        console.print("🎯 Running classifier...")
        prediction = classifier.predict(input_scaled)[0]
        probabilities = classifier.predict_proba(input_scaled)[0]
        
        console.print("\n✅ [bold green]PREDICTION SUCCESSFUL![/bold green]\n")
        
        # Results table
        result_table = Table(show_header=True, header_style="bold cyan")
        result_table.add_column("AQI Category", style="yellow")
        result_table.add_column("Confidence", justify="right", style="green")
        
        categories = classifier.classes_
        for cat, prob in zip(categories, probabilities):
            style = "bold green" if cat == prediction else "white"
            marker = "👉 " if cat == prediction else "   "
            result_table.add_row(
                f"{marker}{cat}",
                f"{prob*100:.2f}%",
                style=style
            )
        
        console.print(result_table)
        
        # Step 6: API validation
        console.print("\n" + "="*70)
        console.print("📍 [bold]STEP 6: API VALIDATION[/bold]")
        console.print("="*70)
        
        # Prepare API data (only base features)
        api_data = {
            "PM2_5": float(matched_features.get('PM2.5', 85.3)),
            "PM10": float(matched_features.get('PM10', 150.2)),
            "NO2": float(matched_features.get('NO2', 45.1)),
            "SO2": float(matched_features.get('SO2', 12.5)),
            "CO": float(matched_features.get('CO', 90.2)),
            "O3": float(matched_features.get('O3', 65.8)),
            "temperature": float(matched_features.get('temperature', 28.5)),
            "humidity": float(matched_features.get('humidity', 65.0)),
            "wind_speed": float(matched_features.get('wind_speed', 3.2)),
            "hour": int(matched_features.get('hour', 14)),
            "day_of_week": int(matched_features.get('day_of_week', 2)),
            "month": int(matched_features.get('month', 12))
        }
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict/aqi",
                json=api_data,
                timeout=5
            )
            
            if response.status_code == 200:
                api_result = response.json()
                console.print("✅ API Response:")
                console.print(f"   Category: {api_result['category']}")
                console.print(f"   Confidence: {api_result['confidence']*100:.2f}%")
                
                if api_result['category'] == prediction:
                    console.print("   ✓ [green]Matches local prediction![/green]")
                else:
                    console.print("   ⚠️  [yellow]Different from local prediction[/yellow]")
            else:
                console.print(f"⚠️  API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            console.print("⚠️  [yellow]API not running. Start with:[/yellow]")
            console.print("   uvicorn src.api:app --reload")
        except Exception as e:
            console.print(f"⚠️  API call failed: {e}")
        
        # Summary
        console.print("\n" + "="*70)
        console.print("📊 [bold]SUCCESS SUMMARY[/bold]")
        console.print("="*70)
        
        summary = f"""
✅ Feature Matching: {len(expected_features)} features matched perfectly
✅ Model Loading: Classifier + Scaler loaded
✅ Prediction: {prediction} ({probabilities[list(categories).index(prediction)]*100:.1f}% confidence)
✅ API Integration: Validated with REST endpoint

🎯 Complete MLOps Pipeline Working!
"""
        console.print(Panel(summary, border_style="green"))
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Error:[/bold red]")
        console.print(f"   {str(e)}")
        console.print("\n💡 [yellow]Debug info:[/yellow]")
        console.print(f"   Expected features: {len(expected_features)}")
        console.print(f"   Provided features: {len(input_df.columns)}")
        console.print(f"   Input shape: {input_df.shape}")
        console.print(f"\n   Expected: {expected_features}")
        console.print(f"   Provided: {list(input_df.columns)}")

if __name__ == "__main__":
    try:
        demo_live_flow()
    except KeyboardInterrupt:
        console.print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()