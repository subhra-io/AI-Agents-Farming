"""
Scientific crop suitability rules and filtering logic
"""
from typing import Dict, List, Any, Tuple
from datetime import datetime
from ..data.crop_database import CropDatabase


class CropSuitabilityEngine:
    """Applies scientific rules to determine crop suitability"""
    
    def __init__(self):
        self.crop_db = CropDatabase()
    
    def evaluate_crop_suitability(
        self, 
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate suitability of all crops based on environmental conditions
        """
        suitable_crops = []
        current_month = datetime.now().month
        
        for crop_name in self.crop_db.get_all_crops():
            crop_info = self.crop_db.get_crop_info(crop_name)
            suitability_score = self._calculate_suitability_score(
                crop_info, weather_data, soil_data, location_data, current_month
            )
            
            if suitability_score['overall_score'] > 0.3:  # Minimum threshold
                suitable_crops.append({
                    'crop_name': crop_name,
                    'crop_info': crop_info,
                    'suitability_score': suitability_score,
                    'recommendations': self._generate_crop_recommendations(
                        crop_info, suitability_score
                    )
                })
        
        # Sort by suitability score
        suitable_crops.sort(
            key=lambda x: x['suitability_score']['overall_score'], 
            reverse=True
        )
        
        return suitable_crops
    
    def _calculate_suitability_score(
        self,
        crop_info: Dict[str, Any],
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any],
        current_month: int
    ) -> Dict[str, Any]:
        """Calculate comprehensive suitability score for a crop"""
        
        scores = {}
        
        # Temperature suitability (0-1)
        scores['temperature'] = self._score_temperature_suitability(
            crop_info, weather_data
        )
        
        # Soil suitability (0-1)
        scores['soil'] = self._score_soil_suitability(
            crop_info, soil_data
        )
        
        # Climate zone suitability (0-1)
        scores['climate'] = self._score_climate_suitability(
            crop_info, soil_data.get('climate_zone')
        )
        
        # Seasonal timing (0-1)
        scores['timing'] = self._score_seasonal_timing(
            crop_info, current_month
        )
        
        # Water availability (0-1)
        scores['water'] = self._score_water_suitability(
            crop_info, weather_data
        )
        
        # Calculate weighted overall score
        weights = {
            'temperature': 0.25,
            'soil': 0.20,
            'climate': 0.20,
            'timing': 0.15,
            'water': 0.20
        }
        
        overall_score = sum(
            scores[factor] * weight 
            for factor, weight in weights.items()
        )
        
        scores['overall_score'] = overall_score
        scores['grade'] = self._get_suitability_grade(overall_score)
        
        return scores
    
    def _score_temperature_suitability(
        self, 
        crop_info: Dict[str, Any], 
        weather_data: Dict[str, Any]
    ) -> float:
        """Score temperature suitability (0-1)"""
        current_temp = weather_data.get('temperature', 20)
        temp_range = crop_info.get('temperature_range', (0, 50))
        optimal_range = crop_info.get('optimal_temperature', temp_range)
        
        min_temp, max_temp = temp_range
        opt_min, opt_max = optimal_range
        
        if current_temp < min_temp or current_temp > max_temp:
            return 0.0
        elif opt_min <= current_temp <= opt_max:
            return 1.0
        else:
            # Linear decay outside optimal range
            if current_temp < opt_min:
                return (current_temp - min_temp) / (opt_min - min_temp)
            else:
                return (max_temp - current_temp) / (max_temp - opt_max)
    
    def _score_soil_suitability(
        self, 
        crop_info: Dict[str, Any], 
        soil_data: Dict[str, Any]
    ) -> float:
        """Score soil suitability (0-1)"""
        score = 0.0
        
        # Soil type compatibility
        crop_soil_types = crop_info.get('soil_types', [])
        soil_type = soil_data.get('primary_soil_type', '')
        
        if soil_type in crop_soil_types:
            score += 0.5
        elif any(soil in soil_type for soil in crop_soil_types):
            score += 0.3
        
        # pH compatibility
        crop_ph_range = crop_info.get('ph_range', (0, 14))
        soil_ph_range = soil_data.get('ph_range', (7, 7))
        
        # Ensure both are tuples for consistent handling
        if not isinstance(crop_ph_range, (tuple, list)):
            crop_ph_range = (crop_ph_range, crop_ph_range)
        if not isinstance(soil_ph_range, (tuple, list)):
            soil_ph_range = (soil_ph_range, soil_ph_range)
        
        # Convert to tuples if they're lists
        if isinstance(crop_ph_range, list):
            crop_ph_range = tuple(crop_ph_range)
        if isinstance(soil_ph_range, list):
            soil_ph_range = tuple(soil_ph_range)
        
        # Calculate average pH from soil range
        soil_ph = sum(soil_ph_range) / 2
        crop_ph_min, crop_ph_max = crop_ph_range
        
        if crop_ph_min <= soil_ph <= crop_ph_max:
            score += 0.5
        else:
            # Partial score for near-optimal pH
            ph_distance = min(
                abs(soil_ph - crop_ph_min),
                abs(soil_ph - crop_ph_max)
            )
            if ph_distance <= 1.0:
                score += 0.5 * (1 - ph_distance)
        
        return min(score, 1.0)
    
    def _score_climate_suitability(
        self, 
        crop_info: Dict[str, Any], 
        climate_zone: str
    ) -> float:
        """Score climate zone suitability (0-1)"""
        crop_climates = crop_info.get('climate_zones', [])
        
        if climate_zone in crop_climates:
            return 1.0
        elif len(crop_climates) == 0:
            return 0.5  # No specific climate requirement
        else:
            return 0.2  # Possible but not ideal
    
    def _score_seasonal_timing(
        self, 
        crop_info: Dict[str, Any], 
        current_month: int
    ) -> float:
        """Score seasonal planting timing (0-1)"""
        planting_months = crop_info.get('planting_months', [])
        
        if not planting_months:
            return 0.5  # No specific timing requirement
        
        if current_month in planting_months:
            return 1.0
        
        # Check if within 1 month of planting season
        for month in planting_months:
            if abs(current_month - month) <= 1 or abs(current_month - month) >= 11:
                return 0.7
        
        return 0.3  # Wrong season but still possible
    
    def _score_water_suitability(
        self, 
        crop_info: Dict[str, Any], 
        weather_data: Dict[str, Any]
    ) -> float:
        """Score water availability suitability (0-1)"""
        water_requirement = crop_info.get('water_requirement', 'moderate')
        current_humidity = weather_data.get('humidity', 50)
        precipitation = weather_data.get('precipitation', 0)
        
        # Simple heuristic based on humidity and recent precipitation
        water_availability = (current_humidity / 100) * 0.7 + min(precipitation / 10, 1) * 0.3
        
        if water_requirement == 'low':
            return 1.0 if water_availability >= 0.3 else water_availability / 0.3
        elif water_requirement == 'moderate':
            return 1.0 if 0.4 <= water_availability <= 0.8 else max(0, 1 - abs(water_availability - 0.6) * 2)
        elif water_requirement == 'high':
            return water_availability if water_availability >= 0.6 else water_availability / 0.6
        
        return 0.5
    
    def _get_suitability_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        elif score >= 0.4:
            return 'D'
        else:
            return 'F'
    
    def _generate_crop_recommendations(
        self, 
        crop_info: Dict[str, Any], 
        suitability_score: Dict[str, Any]
    ) -> List[str]:
        """Generate specific recommendations for crop cultivation"""
        recommendations = []
        
        # Temperature recommendations
        if suitability_score['temperature'] < 0.7:
            temp_range = crop_info.get('optimal_temperature', (20, 25))
            recommendations.append(
                f"Consider temperature management. Optimal range: {temp_range[0]}-{temp_range[1]}°C"
            )
        
        # Soil recommendations
        if suitability_score['soil'] < 0.7:
            ph_range = crop_info.get('ph_range', (6.0, 7.0))
            recommendations.append(
                f"Soil amendment may be needed. Target pH: {ph_range[0]}-{ph_range[1]}"
            )
        
        # Water management
        water_req = crop_info.get('water_requirement', 'moderate')
        if suitability_score['water'] < 0.7:
            if water_req == 'high':
                recommendations.append("Ensure adequate irrigation system for high water needs")
            elif water_req == 'low':
                recommendations.append("Good drainage essential to prevent waterlogging")
        
        # Timing recommendations
        if suitability_score['timing'] < 0.8:
            planting_months = crop_info.get('planting_months', [])
            if planting_months:
                month_names = [
                    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]
                optimal_months = [month_names[m-1] for m in planting_months]
                recommendations.append(
                    f"Optimal planting months: {', '.join(optimal_months)}"
                )
        
        return recommendations