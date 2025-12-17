"""
Live Data Fetcher for Air Quality Monitoring
Fetches real-time air quality data from OpenAQ API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveDataFetcher:
    """Fetch real-time air quality data from OpenAQ API"""
    
    def __init__(self):
        self.base_url = "https://api.openaq.org/v2"
        self.headers = {"Accept": "application/json"}
    
    def fetch_latest_measurements(self, city: str = "Delhi", limit: int = 100) -> pd.DataFrame:
        """
        Fetch latest air quality measurements for a city
        
        Args:
            city: City name
            limit: Number of measurements to fetch
            
        Returns:
            DataFrame with air quality measurements
        """
        try:
            logger.info(f"Fetching data for {city}...")
            
            # Fetch latest measurements
            url = f"{self.base_url}/latest"
            params = {
                "city": city,
                "limit": limit
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    logger.warning(f"No data found for {city}")
                    return pd.DataFrame()
                
                # Parse measurements
                measurements = []
                for result in results:
                    for measurement in result.get('measurements', []):
                        measurements.append({
                            'city': result.get('city'),
                            'country': result.get('country'),
                            'location': result.get('location'),
                            'parameter': measurement.get('parameter'),
                            'value': measurement.get('value'),
                            'unit': measurement.get('unit'),
                            'timestamp': measurement.get('lastUpdated'),
                            'latitude': result.get('coordinates', {}).get('latitude'),
                            'longitude': result.get('coordinates', {}).get('longitude')
                        })
                
                df = pd.DataFrame(measurements)
                logger.info(f"Fetched {len(df)} measurements")
                return df
                
            else:
                logger.error(f"API error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def fetch_time_series(self, city: str, parameter: str = "pm25", 
                         days: int = 7) -> pd.DataFrame:
        """
        Fetch time series data for specific parameter
        
        Args:
            city: City name
            parameter: Pollutant parameter (pm25, pm10, etc.)
            days: Number of days of historical data
            
        Returns:
            DataFrame with time series data
        """
        try:
            logger.info(f"Fetching {days} days of {parameter} data for {city}...")
            
            date_to = datetime.now()
            date_from = date_to - timedelta(days=days)
            
            url = f"{self.base_url}/measurements"
            params = {
                "city": city,
                "parameter": parameter,
                "date_from": date_from.strftime("%Y-%m-%d"),
                "date_to": date_to.strftime("%Y-%m-%d"),
                "limit": 10000
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                measurements = []
                for result in results:
                    measurements.append({
                        'timestamp': result.get('date', {}).get('utc'),
                        'value': result.get('value'),
                        'parameter': result.get('parameter'),
                        'city': result.get('city'),
                        'location': result.get('location')
                    })
                
                df = pd.DataFrame(measurements)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                logger.info(f"Fetched {len(df)} time series points")
                return df
            else:
                logger.error(f"API error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching time series: {str(e)}")
            return pd.DataFrame()
    
    def get_multiple_cities(self, cities: List[str]) -> pd.DataFrame:
        """Fetch data for multiple cities"""
        all_data = []
        
        for city in cities:
            df = self.fetch_latest_measurements(city)
            if not df.empty:
                all_data.append(df)
            time.sleep(1)  # Rate limiting
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def transform_to_model_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform API data to model input format
        
        Args:
            df: Raw API data
            
        Returns:
            DataFrame ready for model prediction
        """
        # Pivot to get one row per location
        pivot_df = df.pivot_table(
            index=['city', 'location', 'timestamp'],
            columns='parameter',
            values='value',
            aggfunc='mean'
        ).reset_index()
        
        # Add time features
        pivot_df['timestamp'] = pd.to_datetime(pivot_df['timestamp'])
        pivot_df['hour'] = pivot_df['timestamp'].dt.hour
        pivot_df['day_of_week'] = pivot_df['timestamp'].dt.dayofweek
        pivot_df['month'] = pivot_df['timestamp'].dt.month
        
        return pivot_df


class FeatureStore:
    """Simple feature store implementation"""
    
    def __init__(self, storage_path: str = "data/feature_store.parquet"):
        self.storage_path = storage_path
        self.features = None
    
    def save_features(self, df: pd.DataFrame, feature_group: str):
        """Save features to store"""
        try:
            df['feature_group'] = feature_group
            df['created_at'] = datetime.now()
            
            # Append to existing or create new
            try:
                existing = pd.read_parquet(self.storage_path)
                combined = pd.concat([existing, df], ignore_index=True)
                combined.to_parquet(self.storage_path, index=False)
            except FileNotFoundError:
                df.to_parquet(self.storage_path, index=False)
            
            logger.info(f"Saved {len(df)} features to store")
        except Exception as e:
            logger.error(f"Error saving features: {str(e)}")
    
    def load_features(self, feature_group: Optional[str] = None) -> pd.DataFrame:
        """Load features from store"""
        try:
            df = pd.read_parquet(self.storage_path)
            
            if feature_group:
                df = df[df['feature_group'] == feature_group]
            
            return df
        except Exception as e:
            logger.error(f"Error loading features: {str(e)}")
            return pd.DataFrame()
    
    def get_latest_features(self, feature_group: str, n: int = 100) -> pd.DataFrame:
        """Get most recent features"""
        df = self.load_features(feature_group)
        if not df.empty:
            df = df.sort_values('created_at', ascending=False).head(n)
        return df


if __name__ == "__main__":
    # Test the fetcher
    fetcher = LiveDataFetcher()
    
    # Fetch latest data
    print("\n" + "="*60)
    print("TESTING LIVE DATA FETCHER")
    print("="*60)
    
    df = fetcher.fetch_latest_measurements("Delhi", limit=50)
    if not df.empty:
        print(f"\n✅ Fetched {len(df)} measurements")
        print(f"\nParameters available: {df['parameter'].unique()}")
        print(f"\nSample data:")
        print(df.head())
    
    # Test feature store
    print("\n" + "="*60)
    print("TESTING FEATURE STORE")
    print("="*60)
    
    store = FeatureStore()
    if not df.empty:
        store.save_features(df, "live_measurements")
        print("✅ Features saved to store")
        
        loaded = store.get_latest_features("live_measurements", n=10)
        print(f"✅ Loaded {len(loaded)} features from store")
