"""
Farmer-friendly explanation generator
"""
from typing import Dict, List, Any


class FarmerExplanationEngine:
    """Generates simple, farmer-friendly explanations of recommendations"""
    
    def __init__(self):
        self.grade_descriptions = {
            'A': 'Excellent choice',
            'B': 'Very good option',
            'C': 'Good with proper care',
            'D': 'Challenging but possible',
            'F': 'Not recommended'
        }
    
    def generate_crop_explanation(
        self, 
        crop_recommendation: Dict[str, Any],
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any]
    ) -> str:
        """Generate farmer-friendly explanation for crop recommendation"""
        
        crop_name = crop_recommendation['crop_name']
        crop_info = crop_recommendation['crop_info']
        scores = crop_recommendation['suitability_score']
        grade = scores['grade']
        
        explanation = f"**{crop_info['name']} - {self.grade_descriptions[grade]}**\n\n"
        
        # Overall assessment
        if scores['overall_score'] >= 0.8:
            explanation += "This crop is an excellent match for your location and current conditions. "
        elif scores['overall_score'] >= 0.6:
            explanation += "This crop should grow well in your area with proper management. "
        elif scores['overall_score'] >= 0.4:
            explanation += "This crop can be grown but may need extra attention and care. "
        else:
            explanation += "This crop is challenging for your current conditions. "
        
        # Temperature explanation
        current_temp = weather_data.get('temperature', 20)
        temp_range = crop_info.get('optimal_temperature', (20, 25))
        
        if scores['temperature'] >= 0.8:
            explanation += f"The current temperature ({current_temp}°C) is perfect for {crop_info['name']}. "
        elif scores['temperature'] >= 0.6:
            explanation += f"The temperature ({current_temp}°C) is acceptable, though {crop_info['name']} prefers {temp_range[0]}-{temp_range[1]}°C. "
        else:
            explanation += f"Temperature may be a challenge - {crop_info['name']} grows best at {temp_range[0]}-{temp_range[1]}°C. "
        
        # Soil explanation
        if scores['soil'] >= 0.7:
            explanation += "Your soil conditions are well-suited for this crop. "
        else:
            ph_range = crop_info.get('ph_range', (6.0, 7.0))
            explanation += f"Consider soil testing and amendments - this crop prefers pH {ph_range[0]}-{ph_range[1]}. "
        
        # Water requirements
        water_req = crop_info.get('water_requirement', 'moderate')
        humidity = weather_data.get('humidity', 50)
        
        if water_req == 'high':
            explanation += "This crop needs plenty of water - ensure good irrigation. "
            if humidity < 60:
                explanation += "Current humidity is low, so extra watering will be important. "
        elif water_req == 'low':
            explanation += "This crop is drought-tolerant and doesn't need much water. "
            if humidity > 70:
                explanation += "Make sure drainage is good to prevent root problems. "
        else:
            explanation += "Water needs are moderate - regular but not excessive irrigation. "
        
        # Timing advice
        if scores['timing'] < 0.8:
            planting_months = crop_info.get('planting_months', [])
            if planting_months:
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                optimal_months = [month_names[m-1] for m in planting_months]
                explanation += f"Best planting time: {', '.join(optimal_months)}. "
        
        # Growing season
        growing_season = crop_info.get('growing_season', 90)
        explanation += f"Harvest expected in about {growing_season} days. "
        
        return explanation
    
    def generate_yield_explanation(
        self, 
        yield_prediction: Dict[str, Any],
        crop_name: str
    ) -> str:
        """Generate explanation for yield prediction"""
        
        predicted_yield = yield_prediction['predicted_yield_kg_per_hectare']
        confidence = yield_prediction.get('confidence', 0.5)
        
        explanation = f"**Expected Yield: {predicted_yield:,.0f} kg per hectare**\n\n"
        
        if confidence >= 0.8:
            explanation += "This prediction is highly reliable based on your conditions. "
        elif confidence >= 0.6:
            explanation += "This is a good estimate, though actual results may vary. "
        else:
            explanation += "This is a rough estimate - actual yield may differ significantly. "
        
        # Yield category
        if predicted_yield >= 5000:
            explanation += "This is an excellent yield potential. "
        elif predicted_yield >= 3000:
            explanation += "This represents good productivity. "
        elif predicted_yield >= 1500:
            explanation += "This is a moderate yield expectation. "
        else:
            explanation += "Yield may be lower than average. "
        
        # Feature importance explanation
        if 'feature_importance' in yield_prediction:
            importance = yield_prediction['feature_importance']
            top_factors = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
            
            explanation += "Key factors affecting your yield: "
            factor_names = {
                'temperature': 'temperature',
                'humidity': 'humidity levels',
                'precipitation': 'rainfall',
                'ph': 'soil pH',
                'organic_matter': 'soil organic matter'
            }
            
            for factor, _ in top_factors:
                if factor in factor_names:
                    explanation += f"{factor_names[factor]}, "
            
            explanation = explanation.rstrip(', ') + ". "
        
        return explanation
    
    def generate_overall_summary(
        self, 
        recommendations: List[Dict[str, Any]],
        location_data: Dict[str, Any]
    ) -> str:
        """Generate overall farming advice summary"""
        
        if not recommendations:
            return "No suitable crops found for current conditions. Consider consulting local agricultural extension services."
        
        top_crop = recommendations[0]
        num_suitable = len([r for r in recommendations if r['suitability_score']['overall_score'] > 0.6])
        
        summary = f"**Farming Advice Summary**\n\n"
        summary += f"Location: {location_data.get('latitude', 0):.2f}, {location_data.get('longitude', 0):.2f}\n\n"
        
        if num_suitable >= 3:
            summary += f"Great news! You have {num_suitable} excellent crop options. "
        elif num_suitable >= 1:
            summary += f"You have {num_suitable} good crop options for your area. "
        else:
            summary += "Limited options available - consider soil improvement or different timing. "
        
        summary += f"**Top recommendation: {top_crop['crop_info']['name']}** "
        summary += f"(Grade: {top_crop['suitability_score']['grade']})\n\n"
        
        # General advice
        summary += "**General Tips:**\n"
        summary += "• Test your soil pH and nutrient levels before planting\n"
        summary += "• Monitor weather forecasts for optimal planting timing\n"
        summary += "• Consider crop rotation to maintain soil health\n"
        summary += "• Consult local agricultural extension for region-specific advice\n"
        
        return summary
    
    def generate_simple_recommendation(
        self, 
        crop_name: str, 
        grade: str, 
        key_points: List[str]
    ) -> str:
        """Generate very simple recommendation for basic users"""
        
        simple_explanation = f"{crop_name.title()} - {self.grade_descriptions.get(grade, 'Unknown')}\n"
        
        if grade in ['A', 'B']:
            simple_explanation += "✅ Good choice for your area\n"
        elif grade == 'C':
            simple_explanation += "⚠️ Possible with care\n"
        else:
            simple_explanation += "❌ Not recommended\n"
        
        if key_points:
            simple_explanation += "Key tips: " + "; ".join(key_points[:2])
        
        return simple_explanation