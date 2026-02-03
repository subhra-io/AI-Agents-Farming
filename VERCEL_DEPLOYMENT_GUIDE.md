# Vercel Deployment Guide

## AI-Based Farming Advisory Agent - Production Deployment

This guide walks you through deploying the farming advisory system to Vercel for production use.

## 🚀 Quick Deployment

### Prerequisites
- Node.js installed (for Vercel CLI)
- Git repository (optional but recommended)
- OpenWeatherMap API key

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Run Deployment Script
```bash
python deploy_vercel.py
```

The script will:
- ✅ Check Vercel CLI installation
- ✅ Validate all required files
- ✅ Create deployment configuration
- 🚀 Deploy to Vercel

### Step 3: Configure Environment Variables
After deployment, set your API key in Vercel dashboard:

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add: `OPENWEATHER_API_KEY` = `your_api_key_here`
4. Redeploy if needed

## 📁 Deployment Structure

```
├── api/
│   └── index.py          # Serverless FastAPI entry point
├── static/
│   ├── index.html        # Web UI
│   ├── style.css         # Styles
│   └── app.js           # Frontend logic
├── src/                  # Core application code
├── vercel.json          # Vercel configuration
└── requirements.txt     # Python dependencies
```

## 🌐 API Endpoints (Production)

Base URL: `https://your-app.vercel.app`

### Core Endpoints
- `GET /` - Web UI
- `GET /api/status` - System status and data sources
- `POST /api/recommendations/quick` - Quick crop recommendations
- `POST /api/recommendations/comprehensive` - Full analysis
- `GET /api/location/{lat}/{lon}` - Location name lookup
- `GET /api/ndvi/{lat}/{lon}` - NDVI satellite analysis

### Example API Usage
```javascript
// Quick recommendations
const response = await fetch('https://your-app.vercel.app/api/recommendations/quick', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        latitude: 20.2961,
        longitude: 85.8245
    })
});
```

## 🏛️ Odisha-Optimized Features

The system is specifically optimized for Odisha, India:

### Pre-configured Locations
- **Bhubaneswar**: 20.2961, 85.8245
- **Cuttack**: 20.4625, 85.8828
- **Puri**: 19.8135, 85.8312
- **Berhampur**: 19.3149, 84.7941
- **Sambalpur**: 21.4669, 83.9812

### Agricultural Districts
- **Mayurbhanj**: 21.9288, 86.7378
- **Keonjhar**: 21.6297, 85.5804
- **Balasore**: 21.4942, 86.9336
- **Kendrapara**: 20.5014, 86.4222

### Coastal Zones
- **Paradip**: 20.3102, 86.6094
- **Gopalpur**: 19.2588, 84.9030

## 🔧 Configuration Options

### Environment Variables
```bash
OPENWEATHER_API_KEY=your_api_key_here
```

### Vercel Settings
- **Runtime**: Python 3.9+
- **Max Duration**: 30 seconds
- **Memory**: 1024 MB (default)
- **Regions**: Auto (global CDN)

## 📊 Performance Targets

- **Response Time**: <2 seconds
- **Cache Hit Rate**: >80%
- **Uptime**: 99.9%
- **Real Data Coverage**: 86% (with API key)

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify key in Vercel dashboard
   - Check OpenWeatherMap account status
   - Redeploy after setting variables

2. **Slow Response Times**
   - Check cache performance at `/api/cache/stats`
   - Monitor at `/api/status`

3. **Import Errors**
   - Ensure all dependencies in `requirements.txt`
   - Check Python path configuration

### Debug Endpoints
- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/cache/stats` - Cache performance

## 🌾 Usage Examples

### For Farmers in Odisha
1. Visit your deployed URL
2. Click "🏛️ Odisha Locations" for quick coordinates
3. Select your district/city
4. Choose analysis type:
   - **Quick**: Fast crop recommendations
   - **Comprehensive**: Full analysis with ML predictions
   - **NDVI**: Satellite vegetation monitoring

### For Developers
```python
import requests

# API base URL
base_url = "https://your-app.vercel.app/api"

# Get recommendations for Bhubaneswar
response = requests.post(f"{base_url}/recommendations/comprehensive", 
    json={"latitude": 20.2961, "longitude": 85.8245}
)

recommendations = response.json()
```

## 📈 Monitoring

### Key Metrics to Monitor
- Response times via `X-Process-Time` header
- Cache hit rates at `/api/cache/stats`
- API status at `/api/status`
- Error rates in Vercel dashboard

### Performance Optimization
- Cache TTL policies automatically configured
- Intelligent caching for weather (6h), soil (permanent), NDVI (7d)
- Automatic cleanup of expired cache entries

## 🔄 Updates and Maintenance

### Redeployment
```bash
# Make changes to code
git add .
git commit -m "Update farming advisor"

# Redeploy
vercel --prod
```

### Environment Updates
- Update variables in Vercel dashboard
- No redeployment needed for env var changes

## 📞 Support

For issues or questions:
1. Check `/api/status` for system health
2. Review Vercel function logs
3. Test individual endpoints
4. Check environment variable configuration

---

**Production Ready**: ✅ This system is optimized for Odisha agriculture with real weather data, location services, and ML-based recommendations.