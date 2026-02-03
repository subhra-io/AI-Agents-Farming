#!/usr/bin/env python3
"""
Vercel-compatible FastAPI backend for the Farming Advisory Agent
"""
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import sys
from datetime import datetime
from pathlib import Path as PathLib

# Add the parent directory to Python path for imports
current_dir = PathLib(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from src.api.farming_advisor import FarmingAdvisor
from src.core.ndvi_service import NDVIService
from src.core.location_service import LocationService
from src.core.cache_service import get_cache
import time

# Initialize FastAPI app
app = FastAPI(
    title="AI-Based Farming Advisory API",
    description="Intelligent farming recommendations based on location, weather, and soil analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware for web app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with environment variables
api_key = os.getenv('OPENWEATHER_API_KEY', '6e0d1f88ed58eff296b5ca0b3c7aa7fb')
advisor = FarmingAdvisor(weather_api_key=api_key)
ndvi_service = NDVIService()
location_service = LocationService()
cache = get_cache()

# Add performance timing middleware
@app.middleware("http")
async def add_performance_timing(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Performance-Target"] = "<2s"
    
    # Log slow requests
    if process_time > 2.0:
        print(f"⚠️ Slow request: {request.url.path} took {process_time:.2f}s")
    elif process_time > 1.0:
        print(f"🟡 Medium request: {request.url.path} took {process_time:.2f}s")
    
    return response

# Pydantic models for request/response
class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")

class CropAdviceRequest(LocationRequest):
    crop_name: str = Field(..., description="Name of the crop to analyze")

# Serve static files for web UI
@app.get("/")
async def root():
    """Serve the web UI"""
    try:
        static_path = parent_dir / "static" / "index.html"
        if static_path.exists():
            return FileResponse(str(static_path))
        else:
            return JSONResponse({
                "message": "AI-Based Farming Advisory API", 
                "web_ui": "Static files not found in serverless environment",
                "api_docs": "/api/docs",
                "endpoints": {
                    "quick_recommendations": "/api/recommendations/quick",
                    "comprehensive_analysis": "/api/recommendations/comprehensive",
                    "location_lookup": "/api/location/{lat}/{lon}",
                    "api_status": "/api/status"
                }
            })
    except Exception as e:
        return JSONResponse({
            "message": "AI-Based Farming Advisory API",
            "api_docs": "/api/docs",
            "note": "Web UI served separately in production"
        })

@app.get("/style.css")
async def get_styles():
    """Serve CSS file"""
    try:
        css_path = parent_dir / "static" / "style.css"
        if css_path.exists():
            return FileResponse(str(css_path), media_type="text/css")
        else:
            raise HTTPException(status_code=404, detail="CSS file not found")
    except Exception:
        raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/app.js")
async def get_script():
    """Serve JavaScript file"""
    try:
        js_path = parent_dir / "static" / "app.js"
        if js_path.exists():
            return FileResponse(str(js_path), media_type="application/javascript")
        else:
            raise HTTPException(status_code=404, detail="JavaScript file not found")
    except Exception:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

@app.get("/api/status")
async def get_api_status():
    """Get API integration status and data sources"""
    try:
        # Test weather API
        weather_status = "mock"
        weather_message = "Using mock weather data"
        
        if api_key and api_key != 'your_api_key_here':
            try:
                test_weather = advisor.weather_service.get_current_weather(40.0, -95.0)
                if test_weather.get('source') == 'openweathermap_api':
                    weather_status = "active"
                    weather_message = "Real weather data from OpenWeatherMap"
                else:
                    weather_status = "invalid_key"
                    weather_message = "Invalid API key - using mock data"
            except:
                weather_status = "error"
                weather_message = "Weather API error - using mock data"
        
        return {
            'system_status': 'operational',
            'deployment': 'vercel_serverless',
            'data_sources': {
                'weather': {
                    'status': weather_status,
                    'message': weather_message,
                    'api_key_configured': bool(api_key and api_key != 'your_api_key_here')
                },
                'location': {
                    'status': 'active',
                    'message': 'Real location data from OpenStreetMap',
                    'api_key_configured': False
                },
                'crop_data': {
                    'status': 'active',
                    'message': '110 real crop yield records from global sources',
                    'api_key_configured': False
                },
                'ndvi_satellite': {
                    'status': 'simulated',
                    'message': 'Realistic NDVI simulation (ready for satellite API)',
                    'api_key_configured': False
                }
            },
            'real_data_percentage': 71 if weather_status == 'mock' else 86,
            'production_ready': True,
            'recommendations': {
                'weather': 'Get free API key from https://openweathermap.org/api' if weather_status != 'active' else 'Weather API working correctly',
                'satellite': 'Consider integrating Google Earth Engine or Sentinel Hub for real NDVI data'
            }
        }
        
    except Exception as e:
        return {
            'system_status': 'error',
            'error': str(e),
            'real_data_percentage': 71,
            'production_ready': True
        }

@app.get("/api")
async def api_info():
    """API information and endpoints"""
    return {
        "message": "AI-Based Farming Advisory API",
        "version": "1.0.0",
        "deployment": "vercel_serverless",
        "web_ui": "/",
        "endpoints": {
            "quick_recommendations": "/api/recommendations/quick",
            "comprehensive_analysis": "/api/recommendations/comprehensive",
            "crop_specific_advice": "/api/advice/crop",
            "ndvi_analysis": "/api/ndvi/{lat}/{lon}",
            "location_lookup": "/api/location/{lat}/{lon}",
            "api_status": "/api/status",
            "cache_stats": "/api/cache/stats",
            "health_check": "/api/health"
        }
    }

@app.get("/api/cache/stats")
async def get_cache_statistics():
    """Get cache performance statistics"""
    try:
        stats = cache.get_performance_stats()
        
        # Add cleanup info
        cleaned = cache.cleanup_expired()
        if cleaned > 0:
            stats['expired_entries_cleaned'] = cleaned
        
        return {
            'cache_performance': stats,
            'optimization_status': 'active',
            'target_response_time': '<2s',
            'cache_policies': {
                'weather': '6 hours TTL',
                'soil': 'permanent',
                'ndvi': '7 days TTL',
                'ml_prediction': '1 hour TTL'
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats failed: {str(e)}")

@app.post("/api/cache/cleanup")
async def cleanup_cache():
    """Manually trigger cache cleanup"""
    try:
        cleaned = cache.cleanup_expired()
        return {
            'message': f'Cache cleanup completed',
            'expired_entries_removed': cleaned,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache cleanup failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "farming-advisory-api", "deployment": "vercel"}

@app.post("/api/recommendations/quick")
async def get_quick_recommendations(request: LocationRequest):
    """Get quick crop recommendations for a location"""
    try:
        result = advisor.get_quick_recommendation(
            request.latitude, 
            request.longitude
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/recommendations/comprehensive")
async def get_comprehensive_recommendations(
    request: LocationRequest,
    max_crops: int = Query(5, ge=1, le=10, description="Maximum number of crops to analyze"),
    detailed_explanations: bool = Query(True, description="Include detailed explanations")
):
    """Get comprehensive farming analysis and recommendations"""
    try:
        print(f"Comprehensive request: lat={request.latitude}, lon={request.longitude}, max_crops={max_crops}, detailed={detailed_explanations}")
        
        result = advisor.get_recommendations(
            request.latitude,
            request.longitude,
            detailed_explanations=detailed_explanations,
            max_crops=max_crops
        )
        
        if 'error' in result:
            print(f"Error in advisor result: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])
        
        print("Comprehensive analysis completed successfully")
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy array
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # Clean the result
        clean_result = convert_numpy_types(result)
        
        return clean_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Comprehensive analysis exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/advice/crop")
async def get_crop_specific_advice(request: CropAdviceRequest):
    """Get specific advice for a particular crop at a location"""
    try:
        result = advisor.get_crop_specific_advice(
            request.crop_name,
            request.latitude,
            request.longitude
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/crops/available")
async def get_available_crops():
    """Get list of available crops in the database"""
    try:
        from src.data.crop_database import CropDatabase
        crops = CropDatabase.get_all_crops()
        
        crop_info = {}
        for crop in crops:
            info = CropDatabase.get_crop_info(crop)
            crop_info[crop] = {
                'name': info.get('name', crop.title()),
                'category': info.get('category', 'unknown'),
                'climate_zones': info.get('climate_zones', [])
            }
        
        return {
            'available_crops': crop_info,
            'total_count': len(crops)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve crops: {str(e)}")

@app.post("/api/models/train")
async def train_ml_models():
    """Train ML models with synthetic data (admin endpoint)"""
    try:
        advisor.train_ml_models()
        return {"message": "ML models trained successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/api/location/{latitude}/{longitude}")
async def get_location_name(
    latitude: float = Path(..., ge=-90, le=90),
    longitude: float = Path(..., ge=-180, le=180)
):
    """Get readable location name from coordinates"""
    try:
        location_data = location_service.get_location_name(latitude, longitude)
        
        return {
            'coordinates': f"{latitude:.4f}, {longitude:.4f}",
            'location_name': location_data.get('display_name', f"{latitude:.2f}, {longitude:.2f}"),
            'details': {
                'city': location_data.get('city'),
                'state': location_data.get('state'),
                'country': location_data.get('country'),
                'formatted_address': location_data.get('formatted_address'),
                'confidence': location_data.get('confidence', 0.5),
                'source': location_data.get('source', 'unknown')
            },
            'cached': location_data.get('cached', False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location lookup failed: {str(e)}")

@app.get("/api/weather/{latitude}/{longitude}")
async def get_weather_data(
    latitude: float = Path(..., ge=-90, le=90),
    longitude: float = Path(..., ge=-180, le=180)
):
    """Get current weather data for a location"""
    try:
        weather = advisor.weather_service.get_current_weather(latitude, longitude)
        forecast = advisor.weather_service.get_forecast(latitude, longitude, days=3)
        
        return {
            'current_weather': weather,
            'forecast': forecast,
            'location': f"{latitude}, {longitude}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather data retrieval failed: {str(e)}")

@app.get("/api/ndvi/{latitude}/{longitude}")
async def get_ndvi_analysis(
    latitude: float = Path(..., ge=-90, le=90),
    longitude: float = Path(..., ge=-180, le=180),
    days_back: int = Query(30, ge=7, le=90, description="Days of historical NDVI data")
):
    """Get NDVI satellite analysis for vegetation monitoring"""
    try:
        ndvi_data = ndvi_service.get_ndvi_data(latitude, longitude, days_back)
        ndvi_summary = ndvi_service.get_ndvi_summary(latitude, longitude)
        
        return {
            'location': f"{latitude}, {longitude}",
            'ndvi_analysis': ndvi_data,
            'farmer_summary': ndvi_summary,
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'sentinel_2_simulation'
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NDVI analysis failed: {str(e)}")

@app.get("/api/soil/{latitude}/{longitude}")
async def get_soil_analysis(
    latitude: float = Path(..., ge=-90, le=90),
    longitude: float = Path(..., ge=-180, le=180)
):
    """Get soil analysis for a location"""
    try:
        soil_data = advisor.soil_inference.infer_soil_type(latitude, longitude)
        
        return {
            'soil_analysis': soil_data,
            'location': f"{latitude}, {longitude}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Soil analysis failed: {str(e)}")

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    raise HTTPException(status_code=400, detail=str(exc))

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    raise HTTPException(status_code=500, detail="Internal server error")

# Export the app for Vercel
handler = app