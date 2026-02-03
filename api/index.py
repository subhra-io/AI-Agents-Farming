#!/usr/bin/env python3
"""
Vercel-compatible FastAPI backend for the Farming Advisory Agent
Ultra-lightweight version - completely self-contained
"""
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from datetime import datetime
import time

# Initialize FastAPI app
app = FastAPI(
    title="AI-Based Farming Advisory API",
    description="Intelligent farming recommendations for Odisha, India",
    version="1.0.0-lightweight",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment
api_key = os.getenv('OPENWEATHER_API_KEY', '6e0d1f88ed58eff296b5ca0b3c7aa7fb')

# Add performance timing middleware
@app.middleware("http")
async def add_performance_timing(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Pydantic models
class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")

# Odisha crop database (embedded)
ODISHA_CROPS = {
    "rice": {
        "name": "Rice",
        "suitability_score": 0.95,
        "yield_prediction": "4.5-5.5 tons/hectare",
        "season": "Kharif (June-November)",
        "water_requirement": "High (1200-1500mm)",
        "best_practices": [
            "Use high-yielding varieties like Swarna, MTU-1010",
            "Ensure proper drainage during monsoon",
            "Apply balanced fertilizers (NPK 120:60:40 kg/ha)"
        ],
        "risk_factors": ["Cyclones", "Flooding"]
    },
    "maize": {
        "name": "Maize",
        "suitability_score": 0.85,
        "yield_prediction": "6-8 tons/hectare",
        "season": "Kharif/Rabi",
        "water_requirement": "Medium (600-800mm)",
        "best_practices": [
            "Plant during pre-monsoon (April-May)",
            "Use hybrid varieties for better yield",
            "Maintain 60cm row spacing"
        ],
        "risk_factors": ["Drought", "Pest attacks"]
    },
    "groundnut": {
        "name": "Groundnut",
        "suitability_score": 0.80,
        "yield_prediction": "2-3 tons/hectare",
        "season": "Kharif",
        "water_requirement": "Medium (500-700mm)",
        "best_practices": [
            "Sow during June-July",
            "Use certified seeds",
            "Apply gypsum at flowering stage"
        ],
        "risk_factors": ["Leaf spot", "Pod rot"]
    },
    "sugarcane": {
        "name": "Sugarcane",
        "suitability_score": 0.75,
        "yield_prediction": "80-100 tons/hectare",
        "season": "Annual",
        "water_requirement": "High (1500-2000mm)",
        "best_practices": [
            "Plant during February-March",
            "Ensure adequate irrigation",
            "Apply organic manure"
        ],
        "risk_factors": ["Red rot", "Drought"]
    }
}

# Odisha location mapping
ODISHA_LOCATIONS = {
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "name": "Bhubaneswar, Odisha, India"},
    "cuttack": {"lat": 20.4625, "lon": 85.8828, "name": "Cuttack, Odisha, India"},
    "puri": {"lat": 19.8135, "lon": 85.8312, "name": "Puri, Odisha, India"},
    "berhampur": {"lat": 19.3149, "lon": 84.7941, "name": "Berhampur, Odisha, India"},
    "sambalpur": {"lat": 21.4669, "lon": 83.9812, "name": "Sambalpur, Odisha, India"}
}

def is_in_odisha(lat: float, lon: float) -> bool:
    """Check if coordinates are in Odisha region"""
    return (19.0 <= lat <= 22.5) and (81.0 <= lon <= 87.5)

def get_location_name(lat: float, lon: float) -> str:
    """Get location name from coordinates"""
    if not is_in_odisha(lat, lon):
        return f"Location ({lat:.2f}, {lon:.2f})"
    
    # Check if close to known cities
    for city, info in ODISHA_LOCATIONS.items():
        if abs(lat - info["lat"]) < 0.2 and abs(lon - info["lon"]) < 0.2:
            return info["name"]
    
    return f"Odisha, India ({lat:.2f}, {lon:.2f})"

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse({
        "message": "🌾 AI-Based Farming Advisory API for Odisha",
        "status": "deployed_successfully",
        "version": "1.0.0-lightweight",
        "api_docs": "/api/docs",
        "endpoints": {
            "quick_recommendations": "/api/recommendations/quick",
            "comprehensive_analysis": "/api/recommendations/comprehensive",
            "location_lookup": "/api/location/{lat}/{lon}",
            "api_status": "/api/status"
        }
    })

@app.get("/api")
async def api_info():
    """API information"""
    return {
        "message": "AI-Based Farming Advisory API",
        "version": "1.0.0-lightweight",
        "deployment": "vercel_serverless",
        "status": "operational",
        "optimized_for": "Odisha, India",
        "endpoints": {
            "quick_recommendations": "/api/recommendations/quick",
            "comprehensive_analysis": "/api/recommendations/comprehensive",
            "location_lookup": "/api/location/{lat}/{lon}",
            "api_status": "/api/status",
            "health_check": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "farming-advisory-api", 
        "deployment": "vercel",
        "timestamp": datetime.now().isoformat(),
        "region": "odisha_optimized"
    }

@app.get("/api/status")
async def get_api_status():
    """Get API status"""
    return {
        'system_status': 'operational',
        'deployment': 'vercel_serverless_lightweight',
        'version': '1.0.0-lightweight',
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
            },
            'location': {
                'status': 'active',
                'message': 'Odisha location mapping active',
                'cities_mapped': len(ODISHA_LOCATIONS)
            }
        },
        'features': [
            'Odisha-optimized crop recommendations',
            'Rule-based agricultural intelligence',
            'Location-aware suggestions',
            'Fast response times (<1s)'
        ],
        'production_ready': True
    }

@app.post("/api/recommendations/quick")
async def get_quick_recommendations(request: LocationRequest):
    """Get quick crop recommendations"""
    try:
        lat, lon = request.latitude, request.longitude
        location_name = get_location_name(lat, lon)
        
        if is_in_odisha(lat, lon):
            # Odisha-specific recommendations
            recommendations = [
                {
                    "crop": ODISHA_CROPS["rice"]["name"],
                    "suitability_score": ODISHA_CROPS["rice"]["suitability_score"],
                    "confidence": 0.9,
                    "reason": "Primary crop of Odisha, ideal for monsoon climate",
                    "season": ODISHA_CROPS["rice"]["season"],
                    "yield_prediction": ODISHA_CROPS["rice"]["yield_prediction"]
                },
                {
                    "crop": ODISHA_CROPS["maize"]["name"],
                    "suitability_score": ODISHA_CROPS["maize"]["suitability_score"],
                    "confidence": 0.8,
                    "reason": "Excellent alternative crop, drought tolerant",
                    "season": ODISHA_CROPS["maize"]["season"],
                    "yield_prediction": ODISHA_CROPS["maize"]["yield_prediction"]
                },
                {
                    "crop": ODISHA_CROPS["groundnut"]["name"],
                    "suitability_score": ODISHA_CROPS["groundnut"]["suitability_score"],
                    "confidence": 0.75,
                    "reason": "Good cash crop for Odisha soil conditions",
                    "season": ODISHA_CROPS["groundnut"]["season"],
                    "yield_prediction": ODISHA_CROPS["groundnut"]["yield_prediction"]
                }
            ]
        else:
            # General recommendations for non-Odisha regions
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
        
        return {
            "location": f"{lat:.4f}, {lon:.4f}",
            "location_name": location_name,
            "region": "Odisha, India" if is_in_odisha(lat, lon) else "Outside Odisha",
            "recommendations": recommendations,
            "analysis_type": "rule_based_quick",
            "timestamp": datetime.now().isoformat(),
            "note": "Optimized for Odisha agriculture"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/recommendations/comprehensive")
async def get_comprehensive_recommendations(
    request: LocationRequest,
    max_crops: int = Query(5, ge=1, le=10, description="Maximum number of crops"),
    detailed_explanations: bool = Query(True, description="Include detailed explanations")
):
    """Get comprehensive farming analysis"""
    try:
        lat, lon = request.latitude, request.longitude
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
                    "water_requirement": crop_data["water_requirement"],
                    "risk_factors": crop_data["risk_factors"]
                }
                
                if detailed_explanations:
                    rec["best_practices"] = crop_data["best_practices"]
                    rec["detailed_advice"] = f"For {crop_data['name']} cultivation in Odisha: " + \
                                           f"Expected yield is {crop_data['yield_prediction']}. " + \
                                           f"Best season is {crop_data['season']}."
                
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
        
        return {
            "location": f"{lat:.4f}, {lon:.4f}",
            "location_name": location_name,
            "region": "Odisha, India" if is_in_odisha(lat, lon) else "Outside Odisha",
            "recommendations": recommendations[:max_crops],
            "weather_summary": weather_summary,
            "analysis_type": "comprehensive_rule_based",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat(),
            "system_note": "Rule-based analysis optimized for Odisha agriculture"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/location/{latitude}/{longitude}")
async def get_location_info(
    latitude: float = Path(..., ge=-90, le=90),
    longitude: float = Path(..., ge=-180, le=180)
):
    """Get location information"""
    try:
        location_name = get_location_name(latitude, longitude)
        is_odisha_region = is_in_odisha(latitude, longitude)
        
        # Determine city if in Odisha
        city = "Unknown"
        if is_odisha_region:
            for city_key, city_info in ODISHA_LOCATIONS.items():
                if abs(latitude - city_info["lat"]) < 0.2 and abs(longitude - city_info["lon"]) < 0.2:
                    city = city_key.title()
                    break
            if city == "Unknown":
                city = "Odisha"
        
        return {
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
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location lookup failed: {str(e)}")

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Please try again later"}
    )

# Export the app for Vercel
handler = app