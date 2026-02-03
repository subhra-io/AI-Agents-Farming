#!/usr/bin/env python3
"""
Test script for the new location feature
"""
import requests
import json
from src.core.location_service import LocationService
from src.api.farming_advisor import FarmingAdvisor


def test_location_service():
    """Test the location service directly"""
    print("🧪 Testing Location Service...")
    
    location_service = LocationService()
    
    # Test Indian locations
    test_locations = [
        (28.6139, 77.2090, "Delhi"),
        (19.0760, 72.8777, "Mumbai"),
        (12.9716, 77.5946, "Bangalore"),
        (22.5726, 88.3639, "Kolkata"),
        (30.9, 75.8, "Punjab")
    ]
    
    for lat, lon, expected_region in test_locations:
        location_data = location_service.get_location_name(lat, lon)
        print(f"  📍 {lat}, {lon} → {location_data.get('display_name', 'Unknown')}")
        print(f"     City: {location_data.get('city', 'N/A')}")
        print(f"     State: {location_data.get('state', 'N/A')}")
        print(f"     Country: {location_data.get('country', 'N/A')}")
        print(f"     Cached: {location_data.get('cached', False)}")
        print()


def test_api_endpoints():
    """Test the API endpoints"""
    print("🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test location endpoint
    try:
        response = requests.get(f"{base_url}/location/28.6139/77.2090", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Location API: {data['location_name']}")
        else:
            print(f"  ❌ Location API failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Location API error: {e}")
    
    # Test quick recommendation with location
    try:
        response = requests.post(
            f"{base_url}/recommendations/quick",
            json={"latitude": 30.9, "longitude": 75.8},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Quick Recommendation: {data.get('location', 'N/A')}")
            if 'location_details' in data:
                details = data['location_details']
                print(f"     City: {details.get('city', 'N/A')}")
                print(f"     State: {details.get('state', 'N/A')}")
        else:
            print(f"  ❌ Quick Recommendation failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Quick Recommendation error: {e}")


def test_farming_advisor():
    """Test the farming advisor with location integration"""
    print("🌾 Testing Farming Advisor Integration...")
    
    advisor = FarmingAdvisor()
    
    # Test quick recommendation
    result = advisor.get_quick_recommendation(28.6139, 77.2090)
    
    if 'error' not in result:
        print(f"  ✅ Quick Analysis: {result.get('location', 'N/A')}")
        if 'location_details' in result:
            details = result['location_details']
            print(f"     📍 {details.get('city', 'N/A')}, {details.get('state', 'N/A')}, {details.get('country', 'N/A')}")
        print(f"     🌾 {len(result.get('top_recommendations', []))} crop recommendations")
    else:
        print(f"  ❌ Quick Analysis failed: {result['error']}")


if __name__ == "__main__":
    print("🚀 Testing Location Feature Integration\n")
    
    # Test location service
    test_location_service()
    
    # Test farming advisor
    test_farming_advisor()
    
    # Test API endpoints (requires server to be running)
    test_api_endpoints()
    
    print("✅ Location feature testing completed!")