"""
Version and system information for the Farming Advisory Agent
"""
from datetime import datetime

# System version
VERSION = "1.0.0"
BUILD_DATE = "2026-02-02"
MODEL_VERSION = "1.0.0"

# System metadata
SYSTEM_INFO = {
    "version": VERSION,
    "model_version": MODEL_VERSION,
    "build_date": BUILD_DATE,
    "frozen_date": datetime.now().isoformat(),
    "status": "FROZEN_PRODUCTION",
    "supported_crops": [
        "wheat", "rice", "corn", "soybean", "cotton", 
        "tomato", "potato", "sugarcane", "barley", "sunflower"
    ],
    "analysis_factors": [
        "temperature", "soil", "climate", "timing", "water"
    ],
    "confidence_levels": {
        "high": ">= 0.8",
        "medium": "0.6 - 0.8", 
        "low": "< 0.6"
    }
}

def get_system_info():
    """Get complete system information"""
    return SYSTEM_INFO.copy()

def get_version():
    """Get system version"""
    return VERSION

def get_model_version():
    """Get ML model version"""
    return MODEL_VERSION