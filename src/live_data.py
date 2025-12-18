"""
Fixed Live Data Fetcher - OpenAQ v3 API
Works with latest OpenAQ API structure
"""
import requests
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveDataFetcher:
    """Fetch live air quality data from OpenAQ API"""
    
    def __init__(self):
        # Try multiple API versions
        self.apis = [
            {
                'name': 'OpenAQ v3',
                'base_url': 'https://api.openaq.org/v3',
                'method': self._fetch_v3
            },
            {
                'name': 'OpenAQ v2 (legacy)',
                'base_url': 'https://api.openaq.org/v2',
                'method': self._fetch_v2
            }
        ]
        
    def _fetch_v3(self, city):
        """Fetch from OpenAQ v3 API"""
        try:
            # v3 endpoint for latest measurements
            url = f"https://api.openaq.org/v3/locations"
            
            params = {
                'city': city,
                'limit': 10,
                'order_by': 'lastUpdated',
                'sort_order': 'desc'
            }
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Air-Quality-MLOps/1.0'
            }
            
            logger.info(f"Trying OpenAQ v3 API for {city}...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            logger.info(f"v3 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # v3 has different structure
                if 'results' in data and len(data['results']) > 0:
                    locations = data['results']
                    logger.info(f"✅ v3: Found {len(locations)} locations")
                    
                    # Get latest measurements from first location
                    location = locations[0]
                    
                    if 'parameters' in location:
                        measurements = []
                        for param in location['parameters']:
                            measurements.append({
                                'parameter': param.get('parameter', 'unknown'),
                                'value': param.get('lastValue', 0),
                                'unit': param.get('unit', 'μg/m³'),
                                'lastUpdated': param.get('lastUpdated', 'unknown')
                            })
                        
                        if measurements:
                            logger.info(f"✅ v3: Got {len(measurements)} measurements")
                            return pd.DataFrame(measurements)
                    
            logger.warning(f"v3 returned status {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"v3 API error: {e}")
            return None
    
    def _fetch_v2(self, city):
        """Fetch from OpenAQ v2 API (legacy)"""
        try:
            url = "https://api.openaq.org/v2/latest"
            
            params = {
                'city': city,
                'limit': 10
            }
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Air-Quality-MLOps/1.0'
            }
            
            logger.info(f"Trying OpenAQ v2 API for {city}...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            logger.info(f"v2 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    results = data['results']
                    logger.info(f"✅ v2: Found {len(results)} results")
                    
                    measurements = []
                    for result in results:
                        if 'measurements' in result:
                            for m in result['measurements']:
                                measurements.append({
                                    'parameter': m.get('parameter', 'unknown'),
                                    'value': m.get('value', 0),
                                    'unit': m.get('unit', 'μg/m³'),
                                    'lastUpdated': m.get('lastUpdated', 'unknown')
                                })
                    
                    if measurements:
                        logger.info(f"✅ v2: Got {len(measurements)} measurements")
                        return pd.DataFrame(measurements)
            
            return None
            
        except Exception as e:
            logger.error(f"v2 API error: {e}")
            return None
    
    def fetch(self, city='Delhi'):
        """
        Fetch live data, trying multiple API versions
        Falls back to synthetic data if all fail
        """
        logger.info(f"Fetching data for {city}...")
        
        # Try each API version
        for api in self.apis:
            logger.info(f"Attempting {api['name']}...")
            data = api['method'](city)
            
            if data is not None and not data.empty:
                logger.info(f"✅ Success using {api['name']}!")
                return data, api['name']
        
        # All APIs failed, use synthetic data
        logger.warning("All APIs failed. Using synthetic data...")
        return self._generate_synthetic_data(city), "Synthetic"
    
    def _generate_synthetic_data(self, city='Delhi'):
        """Generate realistic synthetic data"""
        import numpy as np
        
        # Base values vary by city
        city_profiles = {
            'Delhi': {'pm25': 85, 'pm10': 150, 'no2': 45, 'so2': 12, 'co': 90, 'o3': 65},
            'Beijing': {'pm25': 75, 'pm10': 130, 'no2': 50, 'so2': 15, 'co': 85, 'o3': 60},
            'London': {'pm25': 15, 'pm10': 30, 'no2': 35, 'so2': 5, 'co': 20, 'o3': 45},
            'Default': {'pm25': 50, 'pm10': 90, 'no2': 30, 'so2': 10, 'co': 60, 'o3': 55}
        }
        
        profile = city_profiles.get(city, city_profiles['Default'])
        
        # Add some random variation
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        
        measurements = []
        for param, base_value in profile.items():
            variation = np.random.normal(0, base_value * 0.1)
            value = max(0, base_value + variation)
            
            measurements.append({
                'parameter': param,
                'value': round(value, 1),
                'unit': 'μg/m³',
                'lastUpdated': datetime.now().isoformat()
            })
        
        return pd.DataFrame(measurements)


class FeatureStore:
    """Simple feature store for air quality data"""
    
    def __init__(self, store_path='data/feature_store.parquet'):
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_features(self, features, group_name='measurements'):
        """Save features to store with timestamp"""
        features['timestamp'] = datetime.now()
        features['feature_group'] = group_name
        
        # Append to existing store or create new
        if self.store_path.exists():
            existing = pd.read_parquet(self.store_path)
            combined = pd.concat([existing, features], ignore_index=True)
            combined.to_parquet(self.store_path, index=False)
        else:
            features.to_parquet(self.store_path, index=False)
        
        logger.info(f"Saved {len(features)} features to store")
        return True
    
    def get_latest(self, group_name='measurements', n=10):
        """Get latest n feature sets"""
        if not self.store_path.exists():
            logger.warning("Feature store is empty")
            return None
        
        df = pd.read_parquet(self.store_path)
        df = df[df['feature_group'] == group_name]
        df = df.sort_values('timestamp', ascending=False)
        return df.head(n)


def test_live_fetcher():
    """Test the live data fetcher"""
    print("="*60)
    print("TESTING LIVE DATA FETCHER")
    print("="*60)
    
    fetcher = LiveDataFetcher()
    
    # Test with Delhi
    data, source = fetcher.fetch('Delhi')
    
    print(f"\n✅ Data Source: {source}")
    print(f"✅ Shape: {data.shape}")
    print("\n📊 Data Preview:")
    print(data.to_string(index=False))
    
    # Test feature store
    print("\n" + "="*60)
    print("TESTING FEATURE STORE")
    print("="*60)
    
    store = FeatureStore()
    
    # Save features
    success = store.save_features(data, 'test_measurements')
    print(f"\n✅ Features saved: {success}")
    
    # Retrieve latest
    latest = store.get_latest('test_measurements', n=1)
    if latest is not None:
        print(f"\n✅ Retrieved {len(latest)} feature sets")
        print("\n📊 Latest Features:")
        print(latest[['parameter', 'value', 'unit', 'timestamp']].to_string(index=False))


if __name__ == "__main__":
    test_live_fetcher()