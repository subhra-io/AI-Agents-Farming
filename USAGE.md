# AI-Based Farming Advisory Agent - Usage Guide

## Quick Start

### 1. Setup
```bash
# Clone or download the project
cd farming-advisory

# Create virtual environment
python3 -m venv farming_env
source farming_env/bin/activate  # On Windows: farming_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install OpenMP (macOS only)
brew install libomp
```

### 2. Basic Usage

#### Quick Recommendations
```bash
python main.py --lat 40.7128 --lon -74.0060 --quick
```

#### Comprehensive Analysis
```bash
python main.py --lat 28.6139 --lon 77.2090
```

#### Crop-Specific Advice
```bash
python main.py --lat 37.7749 --lon -122.4194 --crop wheat
```

#### Train ML Models
```bash
python main.py --train-models
```

### 3. API Server

Start the FastAPI server:
```bash
python api_server.py
```

Access the API documentation at: http://localhost:8000/docs

#### API Endpoints

**Quick Recommendations:**
```bash
curl -X POST "http://localhost:8000/recommendations/quick" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060}'
```

**Comprehensive Analysis:**
```bash
curl -X POST "http://localhost:8000/recommendations/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 28.6139, "longitude": 77.2090}'
```

**Crop-Specific Advice:**
```bash
curl -X POST "http://localhost:8000/advice/crop" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 37.7749, "longitude": -122.4194, "crop_name": "wheat"}'
```

### 4. Configuration

#### Weather API (Optional)
1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Copy `.env.example` to `.env`
3. Add your API key: `OPENWEATHER_API_KEY=your_key_here`

Without an API key, the system uses mock weather data for testing.

### 5. Available Crops

The system supports these crops:
- **Cereals:** Wheat, Rice, Corn (Maize), Barley
- **Legumes:** Soybean
- **Vegetables:** Tomato, Potato
- **Cash Crops:** Cotton, Sugarcane, Sunflower

### 6. Output Formats

#### Quick Mode
- Simple crop recommendations with grades
- Basic suitability information
- Key planting tips

#### Comprehensive Mode
- Detailed environmental analysis
- Scientific suitability scoring
- ML-based yield predictions
- Farmer-friendly explanations
- Actionable recommendations

#### JSON Output
Save results to file:
```bash
python main.py --lat 40.7128 --lon -74.0060 --output results.json
```

### 7. Understanding Results

#### Suitability Grades
- **A (0.8-1.0):** Excellent choice
- **B (0.7-0.8):** Very good option
- **C (0.6-0.7):** Good with proper care
- **D (0.4-0.6):** Challenging but possible
- **F (0.0-0.4):** Not recommended

#### Factors Considered
- **Temperature:** Current vs. optimal crop temperature
- **Soil:** pH, type, and fertility compatibility
- **Climate:** Geographic climate zone matching
- **Timing:** Seasonal planting windows
- **Water:** Precipitation and humidity requirements

### 8. Testing

Run the test suite:
```bash
python test_advisor.py
```

### 9. Troubleshooting

#### Common Issues

**XGBoost Installation (macOS):**
```bash
brew install libomp
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**API Key Issues:**
The system works without API keys using mock data. For real weather data, get a free OpenWeatherMap API key.

**Virtual Environment:**
Always activate the virtual environment before running:
```bash
source farming_env/bin/activate
```

### 10. Example Locations

Try these coordinates for testing:

| Location | Latitude | Longitude | Climate |
|----------|----------|-----------|---------|
| New York, USA | 40.7128 | -74.0060 | Temperate |
| New Delhi, India | 28.6139 | 77.2090 | Tropical/Temperate |
| São Paulo, Brazil | -23.5505 | -46.6333 | Tropical |
| Cairo, Egypt | 30.0444 | 31.2357 | Arid |
| London, UK | 51.5074 | -0.1278 | Temperate |

### 11. Future Enhancements

Planned features:
- NDVI satellite data integration
- Local LLM integration for explanations
- Android app connectivity
- Advanced ML models
- Real-time monitoring
- Historical yield data

### 12. Support

For issues or questions:
1. Check this usage guide
2. Run the test suite
3. Review error messages
4. Check API documentation at `/docs` when running the server