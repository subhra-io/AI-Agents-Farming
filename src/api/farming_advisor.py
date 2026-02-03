"""
Main Farming Advisory API - Orchestrates all components
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from ..core.weather_service import WeatherService
from ..core.soil_inference import SoilInference
from ..core.crop_rules import CropSuitabilityEngine
from ..core.ml_models import CropYieldPredictor
from ..core.ndvi_service import NDVIService
from ..core.location_service import LocationService
from ..core.version import get_system_info, get_version
from ..utils.explanations import FarmerExplanationEngine


class FarmingAdvisor:
    """Main farming advisory system that coordinates all components"""
    
    def __init__(self, weather_api_key: Optional[str] = None):
        self.weather_service = WeatherService(weather_api_key)
        self.soil_inference = SoilInference()
        self.crop_engine = CropSuitabilityEngine()
        self.ml_predictor = CropYieldPredictor()
        self.ndvi_service = NDVIService()
        self.location_service = LocationService()
        self.explanation_engine = FarmerExplanationEngine()
    
    def get_recommendations(
        self, 
        latitude: float, 
        longitude: float,
        detailed_explanations: bool = True,
        max_crops: int = 5
    ) -> Dict[str, Any]:
        """
        Get comprehensive farming recommendations for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            detailed_explanations: Whether to include detailed farmer-friendly explanations
            max_crops: Maximum number of crop recommendations to return
            
        Returns:
            Complete farming advisory report
        """
        
        # Prepare location data with place name
        location_info = self.location_service.get_location_name(latitude, longitude)
        location_data = {
            'latitude': latitude,
            'longitude': longitude,
            'place_name': location_info.get('display_name', f"{latitude:.2f}, {longitude:.2f}"),
            'city': location_info.get('city'),
            'state': location_info.get('state'),
            'country': location_info.get('country'),
            'coordinates': f"{latitude:.4f}, {longitude:.4f}",
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Fetch weather data
            print("Fetching weather data...")
            current_weather = self.weather_service.get_current_weather(latitude, longitude)
            weather_forecast = self.weather_service.get_forecast(latitude, longitude)
            
            # Step 2: Infer soil characteristics
            print("Analyzing soil conditions...")
            soil_data = self.soil_inference.infer_soil_type(latitude, longitude)
            
            # Step 2b: Get NDVI satellite data for risk assessment
            print("Fetching satellite vegetation data...")
            ndvi_data = self.ndvi_service.get_ndvi_data(latitude, longitude)
            
            # Step 3: Apply crop suitability rules
            print("Evaluating crop suitability...")
            suitable_crops = self.crop_engine.evaluate_crop_suitability(
                current_weather, soil_data, location_data
            )
            
            # Limit to top crops
            suitable_crops = suitable_crops[:max_crops]
            
            # Step 4: ML-based predictions
            print("Running ML predictions...")
            ml_crop_predictions = self.ml_predictor.predict_best_crops(
                current_weather, soil_data, location_data, max_crops
            )
            
            # Step 5: Generate yield predictions for top crops
            yield_predictions = {}
            for crop in suitable_crops[:3]:  # Top 3 crops
                crop_name = crop['crop_name']
                yield_pred = self.ml_predictor.predict_yield(
                    crop_name, current_weather, soil_data, location_data
                )
                yield_predictions[crop_name] = yield_pred
            
            # Step 6: Generate explanations
            explanations = {}
            if detailed_explanations:
                print("Generating explanations...")
                for crop in suitable_crops:
                    explanations[crop['crop_name']] = self.explanation_engine.generate_crop_explanation(
                        crop, current_weather, soil_data
                    )
                
                # Overall summary
                overall_summary = self.explanation_engine.generate_overall_summary(
                    suitable_crops, location_data
                )
            else:
                overall_summary = "Recommendations generated successfully."
            
            # Step 7: Compile comprehensive report with NDVI integration
            report = {
                'system_info': get_system_info(),
                'location': location_data,
                'environmental_conditions': {
                    'current_weather': current_weather,
                    'weather_forecast': weather_forecast,
                    'soil_analysis': soil_data,
                    'ndvi_analysis': ndvi_data
                },
                'crop_recommendations': {
                    'rule_based': suitable_crops,
                    'ml_based': ml_crop_predictions,
                    'yield_predictions': yield_predictions
                },
                'explanations': {
                    'detailed_crop_explanations': explanations,
                    'overall_summary': overall_summary,
                    'ndvi_summary': self.ndvi_service.get_ndvi_summary(latitude, longitude)
                },
                'metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'system_version': get_version(),
                    'confidence_level': self._calculate_overall_confidence_with_ndvi(
                        suitable_crops, soil_data, ndvi_data
                    ),
                    'confidence_category': self._get_confidence_category(
                        self._calculate_overall_confidence_with_ndvi(suitable_crops, soil_data, ndvi_data)
                    ),
                    'data_sources': [
                        'OpenWeatherMap API',
                        'Geographic soil inference',
                        'Scientific crop database',
                        'XGBoost ML models',
                        'Sentinel-2 NDVI satellite data'
                    ],
                    'frozen_system': True,
                    'production_ready': True,
                    'ndvi_enabled': True
                }
            }
            
            return report
            
        except Exception as e:
            return {
                'error': f"Analysis failed: {str(e)}",
                'location': location_data,
                'system_info': get_system_info(),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'system_version': get_version()
                }
            }
    
    def get_quick_recommendation(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """Get simplified, quick recommendation"""
        
        try:
            # Get location name
            location_info = self.location_service.get_location_name(latitude, longitude)
            
            # Get basic data
            weather = self.weather_service.get_current_weather(latitude, longitude)
            soil = self.soil_inference.infer_soil_type(latitude, longitude)
            location = {
                'latitude': latitude, 
                'longitude': longitude,
                'place_name': location_info.get('display_name', f"{latitude:.2f}, {longitude:.2f}"),
                'city': location_info.get('city'),
                'state': location_info.get('state'),
                'country': location_info.get('country')
            }
            
            # Get top 3 crops
            crops = self.crop_engine.evaluate_crop_suitability(weather, soil, location)[:3]
            
            # Simple recommendations
            recommendations = []
            for crop in crops:
                recommendations.append({
                    'crop': crop['crop_info']['name'],
                    'grade': crop['suitability_score']['grade'],
                    'score': crop['suitability_score']['overall_score'],
                    'simple_advice': self.explanation_engine.generate_simple_recommendation(
                        crop['crop_info']['name'],
                        crop['suitability_score']['grade'],
                        crop.get('recommendations', [])[:2]
                    )
                })
            
            return {
                'system_info': get_system_info(),
                'location': location_info.get('display_name', f"{latitude:.2f}, {longitude:.2f}"),
                'location_details': {
                    'coordinates': f"{latitude:.4f}, {longitude:.4f}",
                    'city': location_info.get('city'),
                    'state': location_info.get('state'),
                    'country': location_info.get('country')
                },
                'top_recommendations': recommendations,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'system_version': get_version(),
                    'confidence_category': 'medium',
                    'frozen_system': True
                }
            }
            
        except Exception as e:
            return {
                'error': f"Quick analysis failed: {str(e)}",
                'system_info': get_system_info(),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'system_version': get_version()
                }
            }
    
    def train_ml_models(self):
        """Train the ML models with synthetic data"""
        print("Training ML models...")
        self.ml_predictor.train_models()
        print("ML model training completed.")
    
    def get_crop_specific_advice(
        self, 
        crop_name: str,
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """Get specific advice for a particular crop"""
        
        try:
            # Get environmental data
            weather = self.weather_service.get_current_weather(latitude, longitude)
            soil = self.soil_inference.infer_soil_type(latitude, longitude)
            location = {'latitude': latitude, 'longitude': longitude}
            
            # Get crop-specific analysis
            all_crops = self.crop_engine.evaluate_crop_suitability(weather, soil, location)
            
            # Find the specific crop
            crop_analysis = None
            for crop in all_crops:
                if crop['crop_name'].lower() == crop_name.lower():
                    crop_analysis = crop
                    break
            
            if not crop_analysis:
                return {
                    'error': f"Crop '{crop_name}' not found in database",
                    'available_crops': [c['crop_name'] for c in all_crops[:5]]
                }
            
            # Get yield prediction
            yield_pred = self.ml_predictor.predict_yield(
                crop_name, weather, soil, location
            )
            
            # Generate detailed explanation
            explanation = self.explanation_engine.generate_crop_explanation(
                crop_analysis, weather, soil
            )
            
            yield_explanation = self.explanation_engine.generate_yield_explanation(
                yield_pred, crop_name
            )
            
            return {
                'system_info': get_system_info(),
                'crop_name': crop_name,
                'location': f"{latitude:.2f}, {longitude:.2f}",
                'suitability_analysis': crop_analysis,
                'yield_prediction': yield_pred,
                'detailed_explanation': explanation,
                'yield_explanation': yield_explanation,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'system_version': get_version(),
                    'frozen_system': True
                }
            }
            
        except Exception as e:
            return {
                'error': f"Crop analysis failed: {str(e)}",
                'system_info': get_system_info(),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'system_version': get_version()
                }
            }
    
    def _calculate_overall_confidence(
        self, 
        suitable_crops: List[Dict[str, Any]], 
        soil_data: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence in recommendations"""
        
        if not suitable_crops:
            return 0.1
        
        # Base confidence on soil inference confidence
        soil_confidence = soil_data.get('confidence', 0.7)
        
        # Average crop suitability scores
        avg_crop_score = sum(
            crop['suitability_score']['overall_score'] 
            for crop in suitable_crops
        ) / len(suitable_crops)
        
        # Combine factors
        overall_confidence = (soil_confidence * 0.4) + (avg_crop_score * 0.6)
        
        return min(overall_confidence, 0.95)  # Cap at 95%
    
    def _calculate_overall_confidence_with_ndvi(
        self, 
        suitable_crops: List[Dict[str, Any]], 
        soil_data: Dict[str, Any],
        ndvi_data: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence including NDVI adjustment"""
        
        # Base confidence calculation
        base_confidence = self._calculate_overall_confidence(suitable_crops, soil_data)
        
        # Apply NDVI confidence adjustment
        ndvi_adjustment = ndvi_data.get('confidence_adjustment', 1.0)
        
        # Final confidence with NDVI
        final_confidence = base_confidence * ndvi_adjustment
        
        return min(final_confidence, 0.95)  # Cap at 95%
    
    def _get_confidence_category(self, confidence: float) -> str:
        """Convert confidence score to category"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        else:
            return 'low'