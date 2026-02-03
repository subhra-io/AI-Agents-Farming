#!/usr/bin/env python3
"""
Test script for the Farming Advisory Agent
"""
from src.api.farming_advisor import FarmingAdvisor


def test_basic_functionality():
    """Test basic functionality without API keys"""
    
    print("Testing AI-Based Farming Advisory Agent")
    print("=" * 50)
    
    # Initialize advisor (will use mock data without API key)
    advisor = FarmingAdvisor()
    
    # Test locations
    test_locations = [
        (40.7128, -74.0060, "New York, USA"),
        (28.6139, 77.2090, "New Delhi, India"),
        (37.7749, -122.4194, "San Francisco, USA"),
        (-23.5505, -46.6333, "São Paulo, Brazil")
    ]
    
    for lat, lon, location_name in test_locations:
        print(f"\nTesting location: {location_name}")
        print(f"Coordinates: {lat}, {lon}")
        print("-" * 30)
        
        try:
            # Get quick recommendations
            result = advisor.get_quick_recommendation(lat, lon)
            
            if 'error' in result:
                print(f"Error: {result['error']}")
                continue
            
            print("Top 3 Crop Recommendations:")
            for i, rec in enumerate(result['top_recommendations'], 1):
                print(f"{i}. {rec['crop']} (Grade: {rec['grade']})")
            
        except Exception as e:
            print(f"Test failed for {location_name}: {e}")
    
    print("\n" + "=" * 50)
    print("Basic functionality test completed!")


def test_comprehensive_analysis():
    """Test comprehensive analysis for one location"""
    
    print("\nTesting Comprehensive Analysis")
    print("=" * 50)
    
    advisor = FarmingAdvisor()
    
    # Test with a typical agricultural region
    lat, lon = 40.0, -95.0  # Midwest USA
    
    try:
        result = advisor.get_recommendations(lat, lon, max_crops=3)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"Location: {lat}, {lon}")
        print(f"Confidence: {result['metadata']['confidence_level']:.1%}")
        
        # Show environmental conditions
        weather = result['environmental_conditions']['current_weather']
        soil = result['environmental_conditions']['soil_analysis']
        
        print(f"\nEnvironmental Conditions:")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Soil Type: {soil['primary_soil_type']}")
        print(f"Climate Zone: {soil['climate_zone']}")
        
        # Show top recommendations
        crops = result['crop_recommendations']['rule_based']
        print(f"\nTop Recommendations:")
        for i, crop in enumerate(crops, 1):
            name = crop['crop_info']['name']
            grade = crop['suitability_score']['grade']
            print(f"{i}. {name} - Grade {grade}")
        
        print("\nComprehensive analysis test completed!")
        
    except Exception as e:
        print(f"Comprehensive test failed: {e}")


def test_ml_training():
    """Test ML model training"""
    
    print("\nTesting ML Model Training")
    print("=" * 50)
    
    try:
        advisor = FarmingAdvisor()
        advisor.train_ml_models()
        print("ML model training test completed!")
        
    except Exception as e:
        print(f"ML training test failed: {e}")


if __name__ == "__main__":
    test_basic_functionality()
    test_comprehensive_analysis()
    test_ml_training()