# AI-Based Farming Advisory Agent - Project Structure

## 📁 Complete Project Layout

```
farming-advisory/
├── 📄 README.md                    # Project overview and introduction
├── 📄 USAGE.md                     # Detailed usage instructions
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 setup.py                     # Installation and setup script
├── 📄 main.py                      # Main CLI entry point
├── 📄 api_server.py                # FastAPI web server
├── 📄 test_advisor.py              # Test suite
├── 📄 demo.py                      # Interactive demo script
├── 📁 farming_env/                 # Python virtual environment
├── 📁 models/                      # Trained ML models storage
│   ├── crop_model.pkl              # XGBoost crop classification model
│   ├── yield_model.pkl             # XGBoost yield prediction model
│   ├── scaler.pkl                  # Feature scaling model
│   └── label_encoder.pkl           # Crop label encoder
└── 📁 src/                         # Source code modules
    ├── __init__.py
    ├── 📁 api/                     # Main API orchestration
    │   ├── __init__.py
    │   └── farming_advisor.py      # Main FarmingAdvisor class
    ├── 📁 core/                    # Core analysis engines
    │   ├── __init__.py
    │   ├── weather_service.py      # Weather data fetching
    │   ├── soil_inference.py       # Geographic soil analysis
    │   ├── crop_rules.py           # Scientific crop suitability
    │   └── ml_models.py            # XGBoost ML predictions
    ├── 📁 data/                    # Data and databases
    │   ├── __init__.py
    │   └── crop_database.py        # Crop characteristics database
    └── 📁 utils/                   # Utility functions
        ├── __init__.py
        └── explanations.py         # Farmer-friendly explanations
```

## 🏗️ Architecture Overview

### Core Components

#### 1. **Main Entry Points**
- `main.py` - Command-line interface
- `api_server.py` - REST API server
- `demo.py` - Interactive demonstration

#### 2. **API Layer** (`src/api/`)
- `FarmingAdvisor` - Main orchestration class
- Coordinates all analysis components
- Provides unified interface for recommendations

#### 3. **Core Analysis Engines** (`src/core/`)

**Weather Service** (`weather_service.py`)
- Integrates with OpenWeatherMap API
- Provides mock data for testing
- Fetches current conditions and forecasts

**Soil Inference** (`soil_inference.py`)
- Geographic heuristics for soil type
- Climate zone determination
- pH and fertility estimation

**Crop Rules Engine** (`crop_rules.py`)
- Scientific crop suitability scoring
- Multi-factor analysis (temperature, soil, timing, water)
- Grade-based recommendation system

**ML Models** (`ml_models.py`)
- XGBoost yield prediction
- XGBoost crop classification
- Feature engineering and scaling
- Model training and persistence

#### 4. **Data Layer** (`src/data/`)

**Crop Database** (`crop_database.py`)
- Comprehensive crop characteristics
- Growing requirements and constraints
- Yield potential ranges

#### 5. **Utilities** (`src/utils/`)

**Explanation Engine** (`explanations.py`)
- Farmer-friendly language generation
- Technical to plain language translation
- Actionable recommendations

## 🔄 Data Flow

```
1. Input (Lat/Lon) → Weather Service → Current/Forecast Data
                   ↓
2. Input (Lat/Lon) → Soil Inference → Soil Characteristics
                   ↓
3. Weather + Soil → Crop Rules Engine → Suitability Scores
                   ↓
4. Environmental Data → ML Models → Yield Predictions
                   ↓
5. All Data → Explanation Engine → Farmer-friendly Text
                   ↓
6. Combined Results → JSON Output / CLI Display / API Response
```

## 🧩 Component Interactions

### FarmingAdvisor (Main Orchestrator)
```python
# Coordinates all components
weather_data = weather_service.get_current_weather(lat, lon)
soil_data = soil_inference.infer_soil_type(lat, lon)
crop_scores = crop_engine.evaluate_crop_suitability(weather, soil, location)
yield_pred = ml_predictor.predict_yield(crop, weather, soil, location)
explanations = explanation_engine.generate_explanations(...)
```

### Analysis Pipeline
1. **Environmental Assessment**
   - Weather conditions (temperature, humidity, precipitation)
   - Soil characteristics (type, pH, fertility)
   - Geographic factors (climate zone, elevation)

2. **Crop Evaluation**
   - Rule-based suitability scoring
   - ML-based predictions
   - Seasonal timing analysis

3. **Output Generation**
   - Scientific scores and grades
   - Yield predictions with confidence
   - Farmer-friendly explanations

## 📊 Data Models

### Weather Data Structure
```python
{
    'temperature': float,      # Celsius
    'humidity': int,          # Percentage
    'precipitation': float,   # mm
    'weather_condition': str, # Clear, Clouds, Rain, etc.
    'wind_speed': float      # m/s
}
```

### Soil Data Structure
```python
{
    'primary_soil_type': str,     # mollisol, alfisol, etc.
    'climate_zone': str,          # tropical, temperate, arid
    'ph_range': tuple,            # (min_ph, max_ph)
    'organic_matter_percent': tuple, # (min_om, max_om)
    'fertility_level': str,       # low, medium, high
    'confidence': float          # 0.0 to 1.0
}
```

### Crop Recommendation Structure
```python
{
    'crop_name': str,
    'crop_info': dict,           # From crop database
    'suitability_score': {
        'overall_score': float,   # 0.0 to 1.0
        'grade': str,            # A, B, C, D, F
        'temperature': float,     # Individual factor scores
        'soil': float,
        'climate': float,
        'timing': float,
        'water': float
    },
    'recommendations': list      # Actionable advice
}
```

## 🔧 Configuration

### Environment Variables
```bash
OPENWEATHER_API_KEY=your_key_here  # Optional - uses mock data if not set
```

### Model Configuration
- Models stored in `models/` directory
- Automatic training with synthetic data
- Configurable hyperparameters in `ml_models.py`

### Crop Database
- Easily extensible in `crop_database.py`
- Add new crops with characteristics
- Modify growing requirements

## 🚀 Deployment Options

### 1. Command Line Tool
```bash
python main.py --lat 40.7128 --lon -74.0060
```

### 2. REST API Server
```bash
python api_server.py
# Access at http://localhost:8000
```

### 3. Python Library
```python
from src.api.farming_advisor import FarmingAdvisor
advisor = FarmingAdvisor()
result = advisor.get_recommendations(lat, lon)
```

## 🔮 Future Enhancements

### Planned Architecture Extensions

1. **Satellite Data Integration**
   - NDVI vegetation indices
   - Real-time crop monitoring
   - Historical yield correlation

2. **Advanced ML Pipeline**
   - Deep learning models
   - Time series forecasting
   - Multi-modal data fusion

3. **Real-time Monitoring**
   - IoT sensor integration
   - Continuous recommendations
   - Alert systems

4. **Mobile Integration**
   - Android app connectivity
   - Offline capabilities
   - GPS-based recommendations

5. **Local LLM Integration**
   - Enhanced explanations
   - Natural language queries
   - Conversational interface

## 📝 Development Guidelines

### Adding New Crops
1. Update `crop_database.py` with crop characteristics
2. Test with existing analysis pipeline
3. Verify ML model compatibility

### Adding New Analysis Factors
1. Extend scoring functions in `crop_rules.py`
2. Update ML feature engineering
3. Modify explanation templates

### API Extensions
1. Add new endpoints in `api_server.py`
2. Update Pydantic models
3. Document in OpenAPI schema

This architecture provides a solid foundation for an intelligent farming advisory system with clear separation of concerns, extensible design, and production-ready capabilities.