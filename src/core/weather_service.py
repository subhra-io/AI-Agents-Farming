"""
Weather data service using free public APIs with high-performance caching
"""
import requests
from typing import Dict, Any, Optional
import os
from datetime import datetime, timedelta
from ..core.cache_service import cache_weather, get_cached_weather


class WeatherService:
    """Fetches weather data from OpenWeatherMap API (free tier)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather conditions with caching (6-hour TTL)"""
        
        # Check cache first
        cached_data = get_cached_weather(lat, lon)
        if cached_data:
            return cached_data
        
        if not self.api_key:
            weather_data = self._mock_current_weather(lat, lon)
            cache_weather(lat, lon, weather_data)
            return weather_data
            
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'precipitation': data.get('rain', {}).get('1h', 0),
                'weather_condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'timestamp': datetime.now().isoformat(),
                'cached': False,
                'source': 'openweathermap_api'
            }
            
            # Cache the result
            cache_weather(lat, lon, weather_data)
            return weather_data
            
        except Exception as e:
            print(f"Weather API error: {e}")
            if "401" in str(e) or "Invalid API key" in str(e):
                print("❌ Invalid OpenWeatherMap API key. Using mock data.")
                print("💡 Get a free API key at: https://openweathermap.org/api")
            weather_data = self._mock_current_weather(lat, lon)
            cache_weather(lat, lon, weather_data)
            return weather_data
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> Dict[str, Any]:
        """Fetch weather forecast"""
        if not self.api_key:
            return self._mock_forecast(lat, lon, days)
            
        url = f"{self.base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast_data.append({
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'precipitation': item.get('rain', {}).get('3h', 0),
                    'weather_condition': item['weather'][0]['main']
                })
            
            return {
                'forecast': forecast_data,
                'location': data['city']['name'],
                'country': data['city']['country']
            }
        except Exception as e:
            print(f"Forecast API error: {e}")
            return self._mock_forecast(lat, lon, days)
    
    def _mock_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Mock weather data for testing without API key"""
        return {
            'temperature': 22.5,
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 3.2,
            'precipitation': 0,
            'weather_condition': 'Clear',
            'description': 'clear sky',
            'timestamp': datetime.now().isoformat(),
            'cached': False,
            'source': 'mock_data'
        }
    
    def _mock_forecast(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Mock forecast data for testing"""
        forecast_data = []
        base_temp = 22.5
        
        for i in range(days * 8):
            forecast_data.append({
                'datetime': (datetime.now() + timedelta(hours=i*3)).strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': base_temp + (i % 10 - 5),
                'humidity': 60 + (i % 20),
                'precipitation': 0 if i % 4 else 2.5,
                'weather_condition': 'Clear' if i % 3 else 'Clouds'
            })
        
        return {
            'forecast': forecast_data,
            'location': f'Location_{lat}_{lon}',
            'country': 'Unknown'
        }