"""
Demo script to test the Air Quality ML system
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("🏥 TESTING HEALTH CHECK")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_aqi_prediction():
    """Test AQI category prediction"""
    print("\n" + "="*60)
    print("🌫️  TESTING AQI PREDICTION")
    print("="*60)
    
    # Sample data - High pollution scenario
    data = {
        "PM2_5": 85.3,
        "PM10": 152.5,
        "NO2": 65.2,
        "SO2": 22.8,
        "CO": 125.3,
        "O3": 45.4,
        "temperature": 28.5,
        "humidity": 75.0,
        "wind_speed": 2.1,
        "hour": 17,  # Rush hour
        "day_of_week": 2,  # Wednesday
        "month": 7  # July (summer)
    }
    
    print(f"\nInput Data:")
    print(f"  PM2.5: {data['PM2_5']} μg/m³")
    print(f"  PM10: {data['PM10']} μg/m³")
    print(f"  NO2: {data['NO2']} μg/m³")
    print(f"  Temperature: {data['temperature']}°C")
    print(f"  Time: {data['hour']}:00 (Rush hour)")
    
    response = requests.post(f"{BASE_URL}/predict/aqi", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Prediction Result:")
        print(f"  Category: {result['aqi_category']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"\n  All Probabilities:")
        for category, prob in result['probabilities'].items():
            print(f"    {category}: {prob:.2%}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_pm25_prediction():
    """Test PM2.5 regression prediction"""
    print("\n" + "="*60)
    print("📊 TESTING PM2.5 PREDICTION")
    print("="*60)
    
    # Sample data - Predicting PM2.5 from other factors
    data = {
        "NO2": 45.2,
        "SO2": 12.8,
        "CO": 85.3,
        "O3": 65.4,
        "temperature": 25.5,
        "humidity": 65.0,
        "wind_speed": 3.2,
        "hour": 14,
        "day_of_week": 2,
        "month": 6
    }
    
    print(f"\nInput Data:")
    print(f"  NO2: {data['NO2']} μg/m³")
    print(f"  Wind Speed: {data['wind_speed']} m/s")
    print(f"  Temperature: {data['temperature']}°C")
    print(f"  Humidity: {data['humidity']}%")
    
    response = requests.post(f"{BASE_URL}/predict/pm25", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Prediction Result:")
        print(f"  Predicted PM2.5: {result['predicted_pm25']:.2f} {result['unit']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_batch_prediction():
    """Test batch prediction"""
    print("\n" + "="*60)
    print("📦 TESTING BATCH PREDICTION")
    print("="*60)
    
    # Multiple scenarios
    batch_data = [
        {  # Good air quality
            "PM2_5": 10.0,
            "PM10": 20.0,
            "NO2": 15.0,
            "SO2": 5.0,
            "CO": 20.0,
            "O3": 90.0,
            "temperature": 22.0,
            "humidity": 50.0,
            "wind_speed": 8.0,
            "hour": 10,
            "day_of_week": 6,  # Sunday
            "month": 3
        },
        {  # Moderate pollution
            "PM2_5": 35.0,
            "PM10": 65.0,
            "NO2": 35.0,
            "SO2": 15.0,
            "CO": 50.0,
            "O3": 70.0,
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 4.0,
            "hour": 8,
            "day_of_week": 1,
            "month": 6
        }
    ]
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=batch_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Batch Prediction Results:")
        print(f"  Total Predictions: {result['count']}")
        for i, pred in enumerate(result['predictions'], 1):
            print(f"\n  Sample {i}:")
            print(f"    Category: {pred['aqi_category']}")
            print(f"    Confidence: {pred['confidence']:.2%}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def main():
    """Run all demo tests"""
    print("\n" + "="*70)
    print("🌍 AIR QUALITY INTELLIGENCE SYSTEM - DEMO")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  uvicorn src.api:app --reload")
    print("\nOr using Docker:")
    print("  docker-compose up")
    print("\n" + "="*70)
    
    try:
        # Run all tests
        tests = [
            ("Health Check", test_health),
            ("AQI Prediction", test_aqi_prediction),
            ("PM2.5 Prediction", test_pm25_prediction),
            ("Batch Prediction", test_batch_prediction)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
            except requests.exceptions.ConnectionError:
                print(f"\n❌ Connection Error: API server not running!")
                print("\nPlease start the API server first:")
                print("  uvicorn src.api:app --reload")
                return
            except Exception as e:
                print(f"\n❌ Error in {test_name}: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*70)
        print("📊 DEMO RESULTS SUMMARY")
        print("="*70)
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        total_passed = sum(1 for _, success in results if success)
        print(f"\nTotal: {total_passed}/{len(results)} tests passed")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")

if __name__ == "__main__":
    main()
