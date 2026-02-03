"""
Crop characteristics and requirements database
"""
from typing import Dict, List, Any


class CropDatabase:
    """Database of crop characteristics and growing requirements"""
    
    CROPS = {
        'wheat': {
            'name': 'Wheat',
            'category': 'cereal',
            'temperature_range': (10, 25),  # Celsius
            'optimal_temperature': (15, 20),
            'rainfall_requirement': (300, 800),  # mm annually
            'ph_range': (6.0, 7.5),
            'soil_types': ['mollisol', 'alfisol', 'inceptisol'],
            'growing_season': 120,  # days
            'planting_months': [9, 10, 11, 3, 4],  # Sept-Nov, Mar-Apr
            'yield_potential': (2000, 8000),  # kg/hectare
            'water_requirement': 'moderate',
            'climate_zones': ['temperate', 'arid']
        },
        'rice': {
            'name': 'Rice',
            'category': 'cereal',
            'temperature_range': (20, 35),
            'optimal_temperature': (25, 30),
            'rainfall_requirement': (1000, 2000),
            'ph_range': (5.5, 7.0),
            'soil_types': ['alfisol', 'inceptisol', 'vertisol'],
            'growing_season': 90,
            'planting_months': [5, 6, 7, 11, 12],
            'yield_potential': (3000, 10000),
            'water_requirement': 'high',
            'climate_zones': ['tropical', 'temperate']
        },
        'corn': {
            'name': 'Corn (Maize)',
            'category': 'cereal',
            'temperature_range': (15, 35),
            'optimal_temperature': (20, 30),
            'rainfall_requirement': (500, 1200),
            'ph_range': (6.0, 7.0),
            'soil_types': ['mollisol', 'alfisol', 'ultisol'],
            'growing_season': 100,
            'planting_months': [3, 4, 5, 6],
            'yield_potential': (4000, 12000),
            'water_requirement': 'moderate',
            'climate_zones': ['tropical', 'temperate']
        },
        'soybean': {
            'name': 'Soybean',
            'category': 'legume',
            'temperature_range': (20, 30),
            'optimal_temperature': (22, 28),
            'rainfall_requirement': (450, 700),
            'ph_range': (6.0, 7.0),
            'soil_types': ['mollisol', 'alfisol'],
            'growing_season': 95,
            'planting_months': [4, 5, 6],
            'yield_potential': (1500, 4500),
            'water_requirement': 'moderate',
            'climate_zones': ['temperate']
        },
        'cotton': {
            'name': 'Cotton',
            'category': 'fiber',
            'temperature_range': (18, 35),
            'optimal_temperature': (23, 32),
            'rainfall_requirement': (500, 1000),
            'ph_range': (5.8, 8.0),
            'soil_types': ['mollisol', 'alfisol', 'vertisol'],
            'growing_season': 160,
            'planting_months': [3, 4, 5],
            'yield_potential': (800, 2500),
            'water_requirement': 'moderate',
            'climate_zones': ['tropical', 'temperate', 'arid']
        },
        'tomato': {
            'name': 'Tomato',
            'category': 'vegetable',
            'temperature_range': (18, 29),
            'optimal_temperature': (21, 26),
            'rainfall_requirement': (400, 800),
            'ph_range': (6.0, 7.0),
            'soil_types': ['mollisol', 'alfisol', 'inceptisol'],
            'growing_season': 75,
            'planting_months': [2, 3, 4, 8, 9],
            'yield_potential': (20000, 80000),
            'water_requirement': 'moderate',
            'climate_zones': ['tropical', 'temperate']
        },
        'potato': {
            'name': 'Potato',
            'category': 'tuber',
            'temperature_range': (15, 25),
            'optimal_temperature': (18, 22),
            'rainfall_requirement': (400, 600),
            'ph_range': (5.0, 6.5),
            'soil_types': ['mollisol', 'alfisol', 'inceptisol'],
            'growing_season': 90,
            'planting_months': [1, 2, 3, 10, 11],
            'yield_potential': (15000, 50000),
            'water_requirement': 'moderate',
            'climate_zones': ['temperate']
        },
        'sugarcane': {
            'name': 'Sugarcane',
            'category': 'cash_crop',
            'temperature_range': (20, 35),
            'optimal_temperature': (26, 32),
            'rainfall_requirement': (1000, 1500),
            'ph_range': (6.0, 7.5),
            'soil_types': ['mollisol', 'alfisol', 'vertisol'],
            'growing_season': 300,
            'planting_months': [2, 3, 4, 10, 11],
            'yield_potential': (60000, 120000),
            'water_requirement': 'high',
            'climate_zones': ['tropical']
        },
        'barley': {
            'name': 'Barley',
            'category': 'cereal',
            'temperature_range': (8, 22),
            'optimal_temperature': (12, 18),
            'rainfall_requirement': (300, 650),
            'ph_range': (6.0, 7.5),
            'soil_types': ['mollisol', 'alfisol', 'aridisol'],
            'growing_season': 90,
            'planting_months': [9, 10, 11, 2, 3],
            'yield_potential': (1500, 6000),
            'water_requirement': 'low',
            'climate_zones': ['temperate', 'arid']
        },
        'sunflower': {
            'name': 'Sunflower',
            'category': 'oilseed',
            'temperature_range': (18, 28),
            'optimal_temperature': (20, 25),
            'rainfall_requirement': (400, 700),
            'ph_range': (6.0, 7.5),
            'soil_types': ['mollisol', 'alfisol', 'vertisol'],
            'growing_season': 85,
            'planting_months': [3, 4, 5, 6],
            'yield_potential': (1000, 3500),
            'water_requirement': 'moderate',
            'climate_zones': ['temperate', 'arid']
        }
    }
    
    @classmethod
    def get_crop_info(cls, crop_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific crop"""
        return cls.CROPS.get(crop_name.lower(), {})
    
    @classmethod
    def get_all_crops(cls) -> List[str]:
        """Get list of all available crops"""
        return list(cls.CROPS.keys())
    
    @classmethod
    def get_crops_by_category(cls, category: str) -> List[str]:
        """Get crops filtered by category"""
        return [
            crop for crop, info in cls.CROPS.items()
            if info.get('category') == category
        ]
    
    @classmethod
    def get_crops_by_climate(cls, climate_zone: str) -> List[str]:
        """Get crops suitable for a specific climate zone"""
        return [
            crop for crop, info in cls.CROPS.items()
            if climate_zone in info.get('climate_zones', [])
        ]