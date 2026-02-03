#!/usr/bin/env python3
"""
Vercel-compatible Flask backend for the Farming Advisory Agent
Ultra-minimal version using Flask instead of FastAPI
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API key from environment
api_key = os.getenv('OPENWEATHER_API_KEY', '6e0d1f88ed58eff296b5ca0b3c7aa7fb')

# Odisha crop database (embedded)
ODISHA_CROPS = {
    "rice": {
        "name": "Rice",
        "suitability_score": 0.95,
        "yield_prediction": "4.5-5.5 tons/hectare",
        "season": "Kharif (June-November)",
        "best_practices": [
            "Use high-yielding varieties like Swarna, MTU-1010",
            "Ensure proper drainage during monsoon",
            "Apply balanced fertilizers (NPK 120:60:40 kg/ha)"
        ]
    },
    "maize": {
        "name": "Maize", 
        "suitability_score": 0.85,
        "yield_prediction": "6-8 tons/hectare",
        "season": "Kharif/Rabi",
        "best_practices": [
            "Plant during pre-monsoon (April-May)",
            "Use hybrid varieties for better yield",
            "Maintain 60cm row spacing"
        ]
    },
    "groundnut": {
        "name": "Groundnut",
        "suitability_score": 0.80,
        "yield_prediction": "2-3 tons/hectare", 
        "season": "Kharif",
        "best_practices": [
            "Sow during June-July",
            "Use certified seeds",
            "Apply gypsum at flowering stage"
        ]
    }
}

def is_in_odisha(lat, lon):
    """Check if coordinates are in Odisha region"""
    return (19.0 <= lat <= 22.5) and (81.0 <= lon <= 87.5)

def get_location_name(lat, lon):
    """Get location name from coordinates"""
    if not is_in_odisha(lat, lon):
        return f"Location ({lat:.2f}, {lon:.2f})"
    
    # Check major cities
    if abs(lat - 20.2961) < 0.2 and abs(lon - 85.8245) < 0.2:
        return "Bhubaneswar, Odisha, India"
    elif abs(lat - 20.4625) < 0.2 and abs(lon - 85.8828) < 0.2:
        return "Cuttack, Odisha, India"
    elif abs(lat - 19.8135) < 0.2 and abs(lon - 85.8312) < 0.2:
        return "Puri, Odisha, India"
    else:
        return f"Odisha, India ({lat:.2f}, {lon:.2f})"

# Routes
@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "🌾 AI-Based Farming Advisory API for Odisha",
        "status": "deployed_successfully",
        "version": "1.0.0-flask",
        "api_docs": "Available endpoints listed below",
        "endpoints": {
            "quick_recommendations": "/api/recommendations/quick",
            "comprehensive_analysis": "/api/recommendations/comprehensive", 
            "location_lookup": "/api/location/<lat>/<lon>",
            "api_status": "/api/status",
            "health_check": "/api/health"
        }
    })

@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        "message": "AI-Based Farming Advisory API",
        "version": "1.0.0-flask",
        "deployment": "vercel_serverless_flask",
        "status": "operational",
        "optimized_for": "Odisha, India",
        "endpoints": {
            "quick_recommendations": "/api/recommendations/quick",
            "comprehensive_analysis": "/api/recommendations/comprehensive",
            "location_lookup": "/api/location/<lat>/<lon>",
            "api_status": "/api/status",
            "health_check": "/api/health"
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "farming-advisory-api",
        "deployment": "vercel_flask",
        "timestamp": datetime.now().isoformat(),
        "region": "odisha_optimized"
    })

@app.route('/api/status')
def get_api_status():
    """Get API status"""
    return jsonify({
        'system_status': 'operational',
        'deployment': 'vercel_serverless_flask',
        'version': '1.0.0-flask',
        'optimized_for': 'Odisha, India',
        'data_sources': {
            'weather': {
                'status': 'configured' if api_key else 'mock',
                'message': 'OpenWeatherMap API configured' if api_key else 'Using mock weather data',
                'api_key_configured': bool(api_key)
            },
            'crop_data': {
                'status': 'active',
                'message': 'Rule-based crop recommendations for Odisha',
                'crops_available': len(ODISHA_CROPS)
            }
        },
        'features': [
            'Odisha-optimized crop recommendations',
            'Rule-based agricultural intelligence',
            'Location-aware suggestions',
            'Fast response times'
        ],
        'production_ready': True
    })

@app.route('/api/recommendations/quick', methods=['POST'])
def get_quick_recommendations():
    """Get quick crop recommendations"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({"error": "Missing latitude or longitude"}), 400
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        location_name = get_location_name(lat, lon)
        
        if is_in_odisha(lat, lon):
            # Odisha-specific recommendations
            recommendations = [
                {
                    "crop": "Rice",
                    "suitability_score": 0.95,
                    "confidence": 0.9,
                    "reason": "Primary crop of Odisha, ideal for monsoon climate",
                    "season": "Kharif (June-November)",
                    "yield_prediction": "4.5-5.5 tons/hectare"
                },
                {
                    "crop": "Maize",
                    "suitability_score": 0.85,
                    "confidence": 0.8,
                    "reason": "Excellent alternative crop, drought tolerant",
                    "season": "Kharif/Rabi",
                    "yield_prediction": "6-8 tons/hectare"
                },
                {
                    "crop": "Groundnut",
                    "suitability_score": 0.80,
                    "confidence": 0.75,
                    "reason": "Good cash crop for Odisha soil conditions",
                    "season": "Kharif",
                    "yield_prediction": "2-3 tons/hectare"
                }
            ]
        else:
            # General recommendations
            recommendations = [
                {
                    "crop": "Wheat",
                    "suitability_score": 0.7,
                    "confidence": 0.6,
                    "reason": "General recommendation (system optimized for Odisha)",
                    "season": "Rabi (November-April)",
                    "yield_prediction": "3-4 tons/hectare"
                }
            ]
        
        return jsonify({
            "location": f"{lat:.4f}, {lon:.4f}",
            "location_name": location_name,
            "region": "Odisha, India" if is_in_odisha(lat, lon) else "Outside Odisha",
            "recommendations": recommendations,
            "analysis_type": "rule_based_quick",
            "timestamp": datetime.now().isoformat(),
            "note": "Optimized for Odisha agriculture"
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/recommendations/comprehensive', methods=['POST'])
def get_comprehensive_recommendations():
    """Get comprehensive farming analysis"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({"error": "Missing latitude or longitude"}), 400
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        location_name = get_location_name(lat, lon)
        
        if is_in_odisha(lat, lon):
            # Comprehensive Odisha recommendations
            recommendations = []
            for crop_key, crop_data in ODISHA_CROPS.items():
                rec = {
                    "crop": crop_data["name"],
                    "suitability_score": crop_data["suitability_score"],
                    "confidence": 0.85,
                    "yield_prediction": crop_data["yield_prediction"],
                    "season": crop_data["season"],
                    "best_practices": crop_data["best_practices"],
                    "detailed_advice": f"For {crop_data['name']} cultivation in Odisha: Expected yield is {crop_data['yield_prediction']}. Best season is {crop_data['season']}."
                }
                recommendations.append(rec)
            
            weather_summary = {
                "climate_type": "Tropical monsoon",
                "average_rainfall": "1400-1600mm annually",
                "temperature_range": "20-35°C",
                "humidity": "High (70-85%)",
                "growing_seasons": ["Kharif (June-Nov)", "Rabi (Dec-May)", "Summer (Mar-Jun)"]
            }
        else:
            # Limited recommendations for non-Odisha
            recommendations = [
                {
                    "crop": "Wheat",
                    "suitability_score": 0.7,
                    "confidence": 0.6,
                    "yield_prediction": "3-4 tons/hectare",
                    "season": "Rabi (November-April)",
                    "note": "System optimized for Odisha region"
                }
            ]
            
            weather_summary = {
                "note": "Weather analysis optimized for Odisha region"
            }
        
        return jsonify({
            "location": f"{lat:.4f}, {lon:.4f}",
            "location_name": location_name,
            "region": "Odisha, India" if is_in_odisha(lat, lon) else "Outside Odisha",
            "recommendations": recommendations,
            "weather_summary": weather_summary,
            "analysis_type": "comprehensive_rule_based",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat(),
            "system_note": "Rule-based analysis optimized for Odisha agriculture"
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/location/<float:latitude>/<float:longitude>')
def get_location_info(latitude, longitude):
    """Get location information"""
    try:
        location_name = get_location_name(latitude, longitude)
        is_odisha_region = is_in_odisha(latitude, longitude)
        
        # Determine city if in Odisha
        city = "Unknown"
        if is_odisha_region:
            if abs(latitude - 20.2961) < 0.2 and abs(longitude - 85.8245) < 0.2:
                city = "Bhubaneswar"
            elif abs(latitude - 20.4625) < 0.2 and abs(longitude - 85.8828) < 0.2:
                city = "Cuttack"
            elif abs(latitude - 19.8135) < 0.2 and abs(longitude - 85.8312) < 0.2:
                city = "Puri"
            else:
                city = "Odisha"
        
        return jsonify({
            'coordinates': f"{latitude:.4f}, {longitude:.4f}",
            'location_name': location_name,
            'details': {
                'city': city,
                'state': 'Odisha' if is_odisha_region else 'Unknown',
                'country': 'India' if is_odisha_region else 'Unknown',
                'formatted_address': location_name,
                'confidence': 0.9 if is_odisha_region else 0.5,
                'source': 'odisha_location_mapping'
            },
            'agricultural_zone': 'Odisha Agricultural Zone' if is_odisha_region else 'Outside Coverage Area',
            'system_optimized': is_odisha_region
        })
        
    except Exception as e:
        return jsonify({"error": f"Location lookup failed: {str(e)}"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# For Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)