"""
Location service for reverse geocoding (coordinates to place names)
"""
import requests
from typing import Dict, Any, Optional
import time
from ..core.cache_service import cache_location, get_cached_location


class LocationService:
    """Service to convert coordinates to readable place names"""
    
    def __init__(self):
        # Using free geocoding services
        self.services = [
            {
                'name': 'nominatim',
                'url': 'https://nominatim.openstreetmap.org/reverse',
                'rate_limit': 1.0  # 1 second between requests
            }
        ]
        self.last_request_time = 0
    
    def get_location_name(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get readable location name from coordinates with caching
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with location information
        """
        
        # Check cache first (permanent storage for locations)
        cached_location = get_cached_location(latitude, longitude)
        if cached_location:
            cached_location['cached'] = True
            return cached_location
        
        # Try to get location from geocoding service
        location_data = self._reverse_geocode(latitude, longitude)
        
        # Cache the result permanently
        if location_data:
            cache_location(latitude, longitude, location_data)
        
        location_data['cached'] = False
        return location_data
    
    def _reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Perform reverse geocoding using free services"""
        
        # Rate limiting for free services
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0:
            time.sleep(1.0 - time_since_last)
        
        try:
            # Use Nominatim (OpenStreetMap) - free and reliable
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1,
                'zoom': 10,
                'accept-language': 'en'
            }
            
            headers = {
                'User-Agent': 'AI-Farming-Advisor/1.0 (Educational Project)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_nominatim_response(data, latitude, longitude)
            else:
                return self._fallback_location(latitude, longitude)
                
        except Exception as e:
            print(f"Geocoding error: {e}")
            return self._fallback_location(latitude, longitude)
    
    def _parse_nominatim_response(self, data: Dict[str, Any], lat: float, lon: float) -> Dict[str, Any]:
        """Parse Nominatim API response"""
        
        address = data.get('address', {})
        
        # Extract location components
        city = (address.get('city') or 
                address.get('town') or 
                address.get('village') or 
                address.get('hamlet') or
                address.get('municipality'))
        
        state = (address.get('state') or 
                address.get('province') or
                address.get('region'))
        
        country = address.get('country')
        
        # Build display name
        display_parts = []
        if city:
            display_parts.append(city)
        if state and state != city:
            display_parts.append(state)
        if country:
            display_parts.append(country)
        
        display_name = ', '.join(display_parts) if display_parts else data.get('display_name', f"{lat:.2f}, {lon:.2f}")
        
        return {
            'display_name': display_name,
            'city': city,
            'state': state,
            'country': country,
            'formatted_address': data.get('display_name', ''),
            'coordinates': f"{lat:.4f}, {lon:.4f}",
            'source': 'nominatim',
            'confidence': 0.9 if city else 0.7
        }
    
    def _fallback_location(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fallback location info when geocoding fails"""
        
        # Basic geographic region detection
        region = self._detect_region(latitude, longitude)
        
        return {
            'display_name': f"{region} ({latitude:.2f}, {longitude:.2f})",
            'city': None,
            'state': None,
            'country': None,
            'formatted_address': f"Coordinates: {latitude:.4f}, {longitude:.4f}",
            'coordinates': f"{latitude:.4f}, {longitude:.4f}",
            'source': 'fallback',
            'confidence': 0.3,
            'region': region
        }
    
    def _detect_region(self, latitude: float, longitude: float) -> str:
        """Detect basic geographic region from coordinates"""
        
        # Simple region detection based on coordinates
        if 6.0 <= latitude <= 37.0 and 68.0 <= longitude <= 97.0:
            return "India"
        elif 25.0 <= latitude <= 49.0 and -125.0 <= longitude <= -66.0:
            return "United States"
        elif -35.0 <= latitude <= -10.0 and 113.0 <= longitude <= 154.0:
            return "Australia"
        elif 35.0 <= latitude <= 71.0 and -10.0 <= longitude <= 40.0:
            return "Europe"
        elif -35.0 <= latitude <= 5.0 and -75.0 <= longitude <= -35.0:
            return "South America"
        elif -35.0 <= latitude <= 37.0 and -20.0 <= longitude <= 52.0:
            return "Africa"
        elif 10.0 <= latitude <= 55.0 and 95.0 <= longitude <= 145.0:
            return "East Asia"
        elif -23.5 <= latitude <= 23.5:
            return "Tropical Region"
        elif latitude > 66.5:
            return "Arctic Region"
        elif latitude < -66.5:
            return "Antarctic Region"
        else:
            return "Unknown Region"
    
    def get_location_summary(self, latitude: float, longitude: float) -> str:
        """Get a concise location summary for display"""
        
        location_data = self.get_location_name(latitude, longitude)
        
        if location_data.get('city') and location_data.get('state'):
            return f"{location_data['city']}, {location_data['state']}"
        elif location_data.get('city'):
            return location_data['city']
        elif location_data.get('state'):
            return location_data['state']
        else:
            return location_data.get('display_name', f"{latitude:.2f}, {longitude:.2f}")