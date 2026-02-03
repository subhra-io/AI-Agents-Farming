"""
Soil type inference using geographical heuristics with permanent caching
"""
from typing import Dict, Any, Tuple
import math
from ..core.cache_service import cache_soil, get_cached_soil


class SoilInference:
    """Infers soil characteristics based on geographic location"""
    
    # Simplified soil type mapping based on climate zones and geography
    SOIL_REGIONS = {
        'tropical': {
            'lat_range': (-23.5, 23.5),
            'soil_types': ['laterite', 'oxisol', 'ultisol'],
            'characteristics': {
                'ph': (5.5, 6.5),
                'organic_matter': (2, 4),
                'drainage': 'moderate',
                'fertility': 'medium'
            }
        },
        'temperate': {
            'lat_range': (23.5, 66.5),
            'soil_types': ['mollisol', 'alfisol', 'inceptisol'],
            'characteristics': {
                'ph': (6.0, 7.5),
                'organic_matter': (3, 6),
                'drainage': 'good',
                'fertility': 'high'
            }
        },
        'arid': {
            'lat_range': (15, 35),
            'soil_types': ['aridisol', 'entisol'],
            'characteristics': {
                'ph': (7.0, 8.5),
                'organic_matter': (0.5, 2),
                'drainage': 'excellent',
                'fertility': 'low'
            }
        },
        'arctic': {
            'lat_range': (66.5, 90),
            'soil_types': ['gelisol', 'spodosol'],
            'characteristics': {
                'ph': (4.5, 6.0),
                'organic_matter': (5, 15),
                'drainage': 'poor',
                'fertility': 'low'
            }
        }
    }
    
    def __init__(self):
        pass
    
    def infer_soil_type(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Infer soil type and characteristics based on coordinates with permanent caching
        """
        
        # Check cache first (permanent storage)
        cached_data = get_cached_soil(lat, lon)
        if cached_data:
            cached_data['cached'] = True
            return cached_data
        
        # Determine climate zone
        climate_zone = self._get_climate_zone(lat, lon)
        
        # Get base soil characteristics
        soil_info = self.SOIL_REGIONS.get(climate_zone, self.SOIL_REGIONS['temperate'])
        
        # Apply geographic modifiers
        modified_characteristics = self._apply_geographic_modifiers(
            lat, lon, soil_info['characteristics'].copy()
        )
        
        # Select most likely soil type
        primary_soil_type = self._select_primary_soil_type(lat, lon, soil_info['soil_types'])
        
        result = {
            'primary_soil_type': primary_soil_type,
            'climate_zone': climate_zone,
            'ph_range': modified_characteristics['ph'],
            'organic_matter_percent': modified_characteristics['organic_matter'],
            'drainage': modified_characteristics['drainage'],
            'fertility_level': modified_characteristics['fertility'],
            'confidence': self._calculate_confidence(lat, lon),
            'cached': False
        }
        
        # Cache permanently
        cache_soil(lat, lon, result)
        
        return result
    
    def _get_climate_zone(self, lat: float, lon: float) -> str:
        """Determine climate zone based on latitude"""
        abs_lat = abs(lat)
        
        # Check for arid regions (simplified - based on known desert locations)
        if self._is_arid_region(lat, lon):
            return 'arid'
        
        if abs_lat <= 23.5:
            return 'tropical'
        elif abs_lat <= 66.5:
            return 'temperate'
        else:
            return 'arctic'
    
    def _is_arid_region(self, lat: float, lon: float) -> bool:
        """Check if location is in known arid regions"""
        # Simplified arid region detection
        arid_regions = [
            # Sahara
            (15, 35, -20, 40),
            # Arabian Peninsula
            (12, 32, 35, 60),
            # Australian Outback
            (-35, -15, 110, 155),
            # Southwestern US/Northern Mexico
            (25, 40, -125, -100)
        ]
        
        for lat_min, lat_max, lon_min, lon_max in arid_regions:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return True
        return False
    
    def _apply_geographic_modifiers(self, lat: float, lon: float, characteristics: Dict) -> Dict:
        """Apply location-specific modifiers to soil characteristics"""
        
        # Coastal modifier (within ~100km of major water bodies)
        if self._is_coastal(lat, lon):
            # Coastal soils tend to be more saline and sandy
            if isinstance(characteristics['ph'], tuple):
                ph_min, ph_max = characteristics['ph']
                characteristics['ph'] = (ph_min + 0.2, ph_max + 0.3)
        
        # Elevation modifier (simplified)
        elevation_factor = self._estimate_elevation_factor(lat, lon)
        if elevation_factor > 0.5:  # High elevation
            # Higher elevation typically means better drainage, lower temperatures
            characteristics['drainage'] = 'excellent'
            if isinstance(characteristics['organic_matter'], tuple):
                om_min, om_max = characteristics['organic_matter']
                characteristics['organic_matter'] = (om_min * 0.8, om_max * 0.9)
        
        return characteristics
    
    def _is_coastal(self, lat: float, lon: float) -> bool:
        """Simplified coastal detection"""
        # This is a very basic heuristic - in production, use actual coastline data
        return abs(lon) > 100 or abs(lat) < 10
    
    def _estimate_elevation_factor(self, lat: float, lon: float) -> float:
        """Estimate relative elevation (0-1 scale)"""
        # Simplified elevation estimation based on known mountain ranges
        mountain_regions = [
            # Himalayas
            (25, 40, 70, 100),
            # Andes
            (-55, 15, -80, -60),
            # Rocky Mountains
            (30, 50, -125, -100),
            # Alps
            (45, 48, 5, 15)
        ]
        
        for lat_min, lat_max, lon_min, lon_max in mountain_regions:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return 0.8
        
        return 0.2  # Default to low elevation
    
    def _select_primary_soil_type(self, lat: float, lon: float, soil_types: list) -> str:
        """Select the most likely soil type from the climate zone options"""
        # Simple selection based on additional geographic factors
        if len(soil_types) == 1:
            return soil_types[0]
        
        # Use longitude and other factors for selection
        selection_index = int(abs(lon) / 60) % len(soil_types)
        return soil_types[selection_index]
    
    def _calculate_confidence(self, lat: float, lon: float) -> float:
        """Calculate confidence score for soil inference"""
        # Higher confidence for well-known agricultural regions
        # Lower confidence for extreme latitudes or remote areas
        
        abs_lat = abs(lat)
        
        if abs_lat > 70:  # Arctic regions
            return 0.6
        elif abs_lat < 5:  # Equatorial regions
            return 0.7
        elif 25 <= abs_lat <= 50:  # Major agricultural zones
            return 0.85
        else:
            return 0.75