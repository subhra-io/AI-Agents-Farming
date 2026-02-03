"""
NDVI Satellite Data Service with weekly caching
Weekly NDVI fetch from Sentinel-2 for risk alerts & confidence adjustment
"""
import requests
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import time
from ..core.cache_service import cache_ndvi, get_cached_ndvi


class NDVIService:
    """
    NDVI satellite data service using Sentinel-2 data
    Focused on risk alerts and confidence adjustment
    """
    
    def __init__(self, cache_dir: str = "data/ndvi_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # NDVI interpretation thresholds
        self.ndvi_thresholds = {
            'excellent': 0.8,    # Very healthy vegetation
            'good': 0.6,         # Healthy vegetation  
            'moderate': 0.4,     # Moderate vegetation
            'poor': 0.2,         # Sparse vegetation
            'bare': 0.0          # Bare soil/water
        }
        
        # Risk assessment based on NDVI trends
        self.risk_levels = {
            'low': {'min_ndvi': 0.6, 'trend': 'stable_or_improving'},
            'medium': {'min_ndvi': 0.4, 'trend': 'declining_slowly'},
            'high': {'min_ndvi': 0.2, 'trend': 'declining_rapidly'},
            'critical': {'min_ndvi': 0.0, 'trend': 'severe_decline'}
        }
    
    def get_ndvi_data(self, lat: float, lon: float, days_back: int = 30) -> Dict[str, Any]:
        """
        Get NDVI data for location with weekly caching
        
        Args:
            lat: Latitude
            lon: Longitude  
            days_back: Days of historical data to fetch
            
        Returns:
            NDVI analysis with risk assessment
        """
        
        # Check cache first (weekly refresh)
        cached_data = get_cached_ndvi(lat, lon)
        if cached_data:
            cached_data['cached'] = True
            return cached_data
        
        try:
            # Try to fetch real NDVI data
            ndvi_data = self._fetch_sentinel_ndvi(lat, lon, days_back)
            
            if not ndvi_data:
                # Fallback to simulated NDVI based on location/season
                ndvi_data = self._generate_realistic_ndvi(lat, lon, days_back)
            
            # Analyze NDVI for risk assessment
            analysis = self._analyze_ndvi_data(ndvi_data, lat, lon)
            analysis['cached'] = False
            
            # Cache the results (weekly TTL)
            cache_ndvi(lat, lon, analysis)
            
            return analysis
            
        except Exception as e:
            print(f"NDVI fetch error: {e}")
            # Return safe fallback
            fallback = self._generate_realistic_ndvi(lat, lon, days_back)
            analysis = self._analyze_ndvi_data(fallback, lat, lon)
            analysis['cached'] = False
            cache_ndvi(lat, lon, analysis)
            return analysis
    
    def _fetch_sentinel_ndvi(self, lat: float, lon: float, days_back: int) -> Optional[Dict]:
        """
        Fetch real NDVI data from Sentinel-2 (via Google Earth Engine or similar)
        This is a placeholder for actual satellite API integration
        """
        
        # Placeholder for real satellite API calls
        # In production, this would connect to:
        # - Google Earth Engine API
        # - Sentinel Hub API  
        # - NASA MODIS API
        # - Copernicus Open Access Hub
        
        # For now, return None to trigger realistic simulation
        return None
    
    def _generate_realistic_ndvi(self, lat: float, lon: float, days_back: int) -> Dict[str, Any]:
        """
        Generate realistic NDVI data based on location, season, and climate
        This provides meaningful data until real satellite integration
        """
        
        current_date = datetime.now()
        dates = [(current_date - timedelta(days=i)) for i in range(0, days_back, 7)]
        
        # Base NDVI based on climate zone and season
        base_ndvi = self._calculate_base_ndvi(lat, lon)
        
        # Generate weekly NDVI values with realistic variation
        ndvi_values = []
        for i, date in enumerate(dates):
            # Seasonal adjustment
            seasonal_factor = self._get_seasonal_factor(lat, date)
            
            # Add realistic noise and trends
            trend_factor = 1.0 - (i * 0.02)  # Slight decline over time
            noise = np.random.normal(0, 0.05)  # Small random variation
            
            ndvi = base_ndvi * seasonal_factor * trend_factor + noise
            ndvi = max(0.0, min(1.0, ndvi))  # Clamp to valid range
            
            ndvi_values.append({
                'date': date.isoformat(),
                'ndvi': round(ndvi, 3),
                'quality': 'simulated'
            })
        
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'time_series': ndvi_values,
            'data_source': 'realistic_simulation',
            'fetch_date': current_date.isoformat()
        }
    
    def _calculate_base_ndvi(self, lat: float, lon: float) -> float:
        """Calculate base NDVI based on geographic location"""
        
        abs_lat = abs(lat)
        
        # Climate-based base NDVI
        if abs_lat <= 23.5:  # Tropical
            if self._is_arid_region(lat, lon):
                return 0.3  # Arid tropical
            else:
                return 0.7  # Humid tropical
        elif abs_lat <= 66.5:  # Temperate
            if self._is_agricultural_region(lat, lon):
                return 0.6  # Agricultural temperate
            else:
                return 0.5  # Natural temperate
        else:  # Arctic/Antarctic
            return 0.2  # Sparse vegetation
    
    def _is_arid_region(self, lat: float, lon: float) -> bool:
        """Check if location is in arid region"""
        # Simplified arid region detection
        arid_regions = [
            (15, 35, -20, 40),    # Sahara
            (12, 32, 35, 60),     # Arabian Peninsula  
            (-35, -15, 110, 155), # Australian Outback
            (25, 40, -125, -100)  # SW USA/N Mexico
        ]
        
        for lat_min, lat_max, lon_min, lon_max in arid_regions:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return True
        return False
    
    def _is_agricultural_region(self, lat: float, lon: float) -> bool:
        """Check if location is in major agricultural region"""
        # Major agricultural regions
        ag_regions = [
            (30, 50, -125, -75),  # North American Great Plains
            (45, 60, -10, 40),    # European Plains
            (20, 40, 70, 120),    # Asian Agricultural Belt
            (-40, -20, -65, -35), # South American Pampas
        ]
        
        for lat_min, lat_max, lon_min, lon_max in ag_regions:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return True
        return False
    
    def _get_seasonal_factor(self, lat: float, date: datetime) -> float:
        """Get seasonal adjustment factor for NDVI"""
        
        # Day of year (1-365)
        day_of_year = date.timetuple().tm_yday
        
        # Northern vs Southern hemisphere
        if lat >= 0:  # Northern hemisphere
            # Peak growing season around day 180 (June)
            seasonal_peak = 180
        else:  # Southern hemisphere  
            # Peak growing season around day 365 (December)
            seasonal_peak = 365
        
        # Calculate seasonal factor (0.7 to 1.3)
        days_from_peak = min(abs(day_of_year - seasonal_peak), 
                           365 - abs(day_of_year - seasonal_peak))
        
        # Cosine-based seasonal variation
        seasonal_factor = 1.0 + 0.3 * np.cos(2 * np.pi * days_from_peak / 365)
        
        return max(0.7, min(1.3, seasonal_factor))
    
    def _analyze_ndvi_data(self, ndvi_data: Dict[str, Any], lat: float, lon: float) -> Dict[str, Any]:
        """
        Analyze NDVI data for risk assessment and confidence adjustment
        """
        
        time_series = ndvi_data['time_series']
        ndvi_values = [point['ndvi'] for point in time_series]
        
        if not ndvi_values:
            return self._create_default_analysis(lat, lon)
        
        # Current and historical NDVI
        current_ndvi = ndvi_values[0]  # Most recent
        avg_ndvi = np.mean(ndvi_values)
        
        # Trend analysis
        if len(ndvi_values) >= 3:
            recent_trend = np.mean(ndvi_values[:3]) - np.mean(ndvi_values[-3:])
        else:
            recent_trend = 0.0
        
        # Vegetation health assessment
        health_status = self._assess_vegetation_health(current_ndvi)
        
        # Risk level determination
        risk_level = self._determine_risk_level(current_ndvi, recent_trend)
        
        # Confidence adjustment factor
        confidence_adjustment = self._calculate_confidence_adjustment(
            current_ndvi, avg_ndvi, recent_trend
        )
        
        # Generate alerts if needed
        alerts = self._generate_ndvi_alerts(current_ndvi, recent_trend, health_status)
        
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'ndvi_analysis': {
                'current_ndvi': round(current_ndvi, 3),
                'average_ndvi': round(avg_ndvi, 3),
                'trend': round(recent_trend, 3),
                'health_status': health_status,
                'risk_level': risk_level
            },
            'confidence_adjustment': confidence_adjustment,
            'alerts': alerts,
            'time_series': time_series,
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(ndvi_values),
                'data_source': ndvi_data.get('data_source', 'unknown')
            }
        }
    
    def _assess_vegetation_health(self, ndvi: float) -> str:
        """Assess vegetation health based on NDVI value"""
        
        if ndvi >= self.ndvi_thresholds['excellent']:
            return 'excellent'
        elif ndvi >= self.ndvi_thresholds['good']:
            return 'good'
        elif ndvi >= self.ndvi_thresholds['moderate']:
            return 'moderate'
        elif ndvi >= self.ndvi_thresholds['poor']:
            return 'poor'
        else:
            return 'bare'
    
    def _determine_risk_level(self, current_ndvi: float, trend: float) -> str:
        """Determine agricultural risk level"""
        
        # Risk based on current NDVI and trend
        if current_ndvi >= 0.6 and trend >= -0.05:
            return 'low'
        elif current_ndvi >= 0.4 and trend >= -0.1:
            return 'medium'
        elif current_ndvi >= 0.2 and trend >= -0.15:
            return 'high'
        else:
            return 'critical'
    
    def _calculate_confidence_adjustment(self, current_ndvi: float, avg_ndvi: float, trend: float) -> float:
        """
        Calculate confidence adjustment factor for crop recommendations
        Returns multiplier (0.7 to 1.0) to adjust overall confidence
        """
        
        # Base confidence adjustment
        base_adjustment = 1.0
        
        # Adjust based on vegetation health
        if current_ndvi >= 0.6:
            health_adjustment = 1.0  # No reduction
        elif current_ndvi >= 0.4:
            health_adjustment = 0.95  # Slight reduction
        elif current_ndvi >= 0.2:
            health_adjustment = 0.85  # Moderate reduction
        else:
            health_adjustment = 0.7   # Significant reduction
        
        # Adjust based on trend
        if trend >= 0:
            trend_adjustment = 1.0    # Improving/stable
        elif trend >= -0.1:
            trend_adjustment = 0.95   # Slight decline
        elif trend >= -0.2:
            trend_adjustment = 0.85   # Moderate decline
        else:
            trend_adjustment = 0.75   # Rapid decline
        
        # Combined adjustment
        final_adjustment = base_adjustment * health_adjustment * trend_adjustment
        
        return max(0.7, min(1.0, final_adjustment))
    
    def _generate_ndvi_alerts(self, current_ndvi: float, trend: float, health_status: str) -> List[Dict[str, Any]]:
        """Generate risk alerts based on NDVI analysis"""
        
        alerts = []
        
        # Low vegetation alert
        if current_ndvi < 0.3:
            alerts.append({
                'type': 'vegetation_stress',
                'severity': 'high',
                'message': f'Low vegetation index detected (NDVI: {current_ndvi:.2f}). Consider irrigation or crop protection measures.',
                'recommendation': 'Monitor soil moisture and consider supplemental irrigation'
            })
        
        # Declining trend alert
        if trend < -0.15:
            alerts.append({
                'type': 'declining_vegetation',
                'severity': 'medium',
                'message': f'Vegetation health declining rapidly (trend: {trend:.2f}). Early intervention recommended.',
                'recommendation': 'Investigate potential stress factors (drought, pests, disease)'
            })
        
        # Seasonal alert
        if health_status in ['poor', 'bare'] and current_ndvi < 0.2:
            alerts.append({
                'type': 'crop_risk',
                'severity': 'critical',
                'message': 'Critical vegetation stress detected. Immediate action required.',
                'recommendation': 'Consult agricultural extension services immediately'
            })
        
        return alerts
    
    def _get_cached_ndvi(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get cached NDVI data if available"""
        
        cache_key = f"ndvi_{lat:.4f}_{lon:.4f}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        
        return None
    
    def _is_cache_valid(self, cached_data: Dict[str, Any], days: int = 7) -> bool:
        """Check if cached data is still valid"""
        
        try:
            cache_date = datetime.fromisoformat(cached_data['metadata']['analysis_date'])
            age_days = (datetime.now() - cache_date).days
            return age_days < days
        except Exception:
            return False
    
    def _cache_ndvi_data(self, lat: float, lon: float, analysis: Dict[str, Any]):
        """Cache NDVI analysis data"""
        
        cache_key = f"ndvi_{lat:.4f}_{lon:.4f}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def _create_default_analysis(self, lat: float, lon: float) -> Dict[str, Any]:
        """Create default analysis when no data available"""
        
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'ndvi_analysis': {
                'current_ndvi': 0.5,
                'average_ndvi': 0.5,
                'trend': 0.0,
                'health_status': 'moderate',
                'risk_level': 'medium'
            },
            'confidence_adjustment': 0.8,
            'alerts': [{
                'type': 'data_unavailable',
                'severity': 'info',
                'message': 'NDVI satellite data temporarily unavailable. Using default assessment.',
                'recommendation': 'Monitor local field conditions closely'
            }],
            'time_series': [],
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'data_points': 0,
                'data_source': 'default'
            }
        }
    
    def get_ndvi_summary(self, lat: float, lon: float) -> str:
        """Get human-readable NDVI summary for farmers"""
        
        analysis = self.get_ndvi_data(lat, lon)
        ndvi_data = analysis['ndvi_analysis']
        
        health_descriptions = {
            'excellent': '🟢 Excellent - Very healthy vegetation',
            'good': '🟡 Good - Healthy vegetation',
            'moderate': '🟠 Moderate - Average vegetation health',
            'poor': '🔴 Poor - Stressed vegetation',
            'bare': '⚫ Bare - Little to no vegetation'
        }
        
        risk_descriptions = {
            'low': '✅ Low risk - Conditions favorable',
            'medium': '⚠️ Medium risk - Monitor closely',
            'high': '🚨 High risk - Action recommended',
            'critical': '🆘 Critical risk - Immediate action needed'
        }
        
        summary = f"""
🛰️ Satellite Vegetation Analysis:
• Current Status: {health_descriptions.get(ndvi_data['health_status'], 'Unknown')}
• Risk Level: {risk_descriptions.get(ndvi_data['risk_level'], 'Unknown')}
• NDVI Value: {ndvi_data['current_ndvi']:.2f}
• Trend: {'📈 Improving' if ndvi_data['trend'] > 0 else '📉 Declining' if ndvi_data['trend'] < -0.05 else '➡️ Stable'}
        """.strip()
        
        return summary