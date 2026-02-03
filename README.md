# AI-Based Farming Advisory Agent

An intelligent farming advisory system that provides crop recommendations and yield predictions based on location, weather data, soil characteristics, and satellite imagery.

## 🌐 **Web Interface Available!**

**New**: Simple, farmer-friendly web interface for easy access to AI farming recommendations.

```bash
# Start the web UI
python start_web_ui.py

# Access at: http://localhost:8000
```

## Features

- **🌐 Web Interface**: Clean, responsive UI for farmers
- **Location-based Analysis**: Input latitude/longitude for precise recommendations
- **Real-time Weather Integration**: Fetches current and forecast weather data
- **Soil Inference**: Geographic heuristics for soil type determination
- **Crop Suitability**: Scientific rule-based crop filtering
- **ML Predictions**: XGBoost-based crop and yield prediction
- **Satellite Integration**: NDVI vegetation indices for risk assessment
- **Farmer-friendly Explanations**: Simple language recommendations
- **High Performance**: Sub-second response times with intelligent caching

## Project Structure

```
farming-advisory/
├── src/
│   ├── core/
│   │   ├── weather_service.py      # Weather data fetching
│   │   ├── soil_inference.py       # Soil type inference
│   │   ├── crop_rules.py          # Crop suitability rules
│   │   └── ml_models.py           # ML prediction models
│   ├── data/
│   │   ├── crop_database.py       # Crop characteristics
│   │   └── soil_data.py           # Soil type mappings
│   ├── api/
│   │   └── farming_advisor.py     # Main advisory logic
│   └── utils/
│       └── explanations.py        # Farmer-friendly explanations
├── models/                        # Trained ML models
├── requirements.txt
└── main.py                       # Entry point
```

## Quick Start

### Web Interface (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web UI
python start_web_ui.py

# Open browser to: http://localhost:8000
```

### Command Line Interface
```bash
# Quick recommendations
python main.py --lat 40.7128 --lon -74.0060 --quick

# Comprehensive analysis
python main.py --lat 28.6139 --lon 77.2090

# Crop-specific advice
python main.py --lat 37.7749 --lon -122.4194 --crop wheat

# NDVI satellite analysis
python main.py --lat 40.0 --lon -95.0 --ndvi
```

### API Server
```bash
# Start API server
python api_server.py

# Access API docs: http://localhost:8000/docs
```

## Interfaces

### 🌐 Web UI
- **Farmer-friendly interface**: Clean, responsive design
- **GPS location detection**: One-click coordinate input
- **Three analysis types**: Quick, Comprehensive, NDVI
- **Interactive results**: Rich visualizations and explanations
- **Mobile-optimized**: Works on all devices

### 💻 Command Line
- **Quick analysis**: `--quick` for fast recommendations
- **Comprehensive**: Full analysis with explanations
- **Crop-specific**: `--crop wheat` for targeted advice
- **NDVI analysis**: `--ndvi` for satellite vegetation data

### 🔌 REST API
- **POST /recommendations/quick**: Fast crop recommendations
- **POST /recommendations/comprehensive**: Detailed analysis
- **GET /ndvi/{lat}/{lon}**: Satellite vegetation analysis
- **GET /cache/stats**: Performance monitoring