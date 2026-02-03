#!/usr/bin/env python3
"""
Demo script showcasing the AI-Based Farming Advisory Agent capabilities
"""
import time
from src.api.farming_advisor import FarmingAdvisor


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{title}")
    print("-" * len(title))


def demo_quick_recommendations():
    """Demo quick recommendations for multiple locations"""
    print_header("🌾 AI-BASED FARMING ADVISORY AGENT - DEMO")
    
    advisor = FarmingAdvisor()
    
    # Demo locations with different climates
    locations = [
        (40.7128, -74.0060, "New York, USA (Temperate)"),
        (28.6139, 77.2090, "New Delhi, India (Tropical/Temperate)"),
        (30.0444, 31.2357, "Cairo, Egypt (Arid)"),
        (-23.5505, -46.6333, "São Paulo, Brazil (Tropical)")
    ]
    
    print_section("🗺️  QUICK RECOMMENDATIONS FOR DIFFERENT CLIMATES")
    
    for lat, lon, location_name in locations:
        print(f"\n📍 {location_name}")
        print(f"   Coordinates: {lat}, {lon}")
        
        try:
            result = advisor.get_quick_recommendation(lat, lon)
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
                continue
            
            print("   🌱 Top 3 Recommendations:")
            for i, rec in enumerate(result['top_recommendations'][:3], 1):
                grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌"}
                emoji = grade_emoji.get(rec['grade'], "📊")
                print(f"      {i}. {emoji} {rec['crop']} (Grade: {rec['grade']})")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
        
        time.sleep(1)  # Small delay for demo effect


def demo_comprehensive_analysis():
    """Demo comprehensive analysis for one location"""
    print_section("🔬 COMPREHENSIVE ANALYSIS - MIDWEST USA FARMLAND")
    
    advisor = FarmingAdvisor()
    
    # Typical agricultural region - Midwest USA
    lat, lon = 40.0, -95.0
    location_name = "Midwest USA Agricultural Region"
    
    print(f"📍 Analyzing: {location_name}")
    print(f"   Coordinates: {lat}, {lon}")
    print("   🔄 Running comprehensive analysis...")
    
    try:
        result = advisor.get_recommendations(lat, lon, max_crops=5)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Environmental conditions
        weather = result['environmental_conditions']['current_weather']
        soil = result['environmental_conditions']['soil_analysis']
        
        print(f"\n🌡️  Environmental Conditions:")
        print(f"   Temperature: {weather['temperature']}°C")
        print(f"   Humidity: {weather['humidity']}%")
        print(f"   Weather: {weather['description']}")
        print(f"   Soil Type: {soil['primary_soil_type']} ({soil['climate_zone']} zone)")
        print(f"   Soil pH: {soil['ph_range'][0]:.1f}-{soil['ph_range'][1]:.1f}")
        print(f"   Fertility: {soil['fertility_level']}")
        
        # Top recommendations
        crops = result['crop_recommendations']['rule_based']
        yield_predictions = result['crop_recommendations']['yield_predictions']
        
        print(f"\n🏆 Top 5 Crop Recommendations:")
        for i, crop in enumerate(crops[:5], 1):
            name = crop['crop_info']['name']
            grade = crop['suitability_score']['grade']
            score = crop['suitability_score']['overall_score']
            
            grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌"}
            emoji = grade_emoji.get(grade, "📊")
            
            print(f"   {i}. {emoji} {name} - Grade {grade} (Score: {score:.2f})")
            
            # Show yield prediction if available
            crop_name = crop['crop_name']
            if crop_name in yield_predictions:
                yield_pred = yield_predictions[crop_name]
                yield_val = yield_pred['predicted_yield_kg_per_hectare']
                confidence = yield_pred['confidence']
                print(f"      💰 Expected Yield: {yield_val:,.0f} kg/hectare (Confidence: {confidence:.1%})")
        
        # Overall confidence
        confidence = result['metadata']['confidence_level']
        print(f"\n📊 Overall Analysis Confidence: {confidence:.1%}")
        
    except Exception as e:
        print(f"❌ Comprehensive analysis failed: {e}")


def demo_crop_specific_advice():
    """Demo crop-specific advice"""
    print_section("🌾 CROP-SPECIFIC ADVICE - WHEAT IN KANSAS")
    
    advisor = FarmingAdvisor()
    
    # Kansas wheat belt
    lat, lon = 38.5, -98.0
    crop_name = "wheat"
    
    print(f"📍 Location: Kansas Wheat Belt ({lat}, {lon})")
    print(f"🌾 Analyzing: {crop_name.title()}")
    
    try:
        result = advisor.get_crop_specific_advice(crop_name, lat, lon)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Suitability analysis
        suitability = result['suitability_analysis']['suitability_score']
        grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌"}
        emoji = grade_emoji.get(suitability['grade'], "📊")
        
        print(f"\n{emoji} Overall Suitability: Grade {suitability['grade']} ({suitability['overall_score']:.2f})")
        
        print(f"\n📊 Detailed Scores:")
        score_labels = {
            'temperature': '🌡️  Temperature',
            'soil': '🌱 Soil',
            'climate': '🌍 Climate',
            'timing': '📅 Timing',
            'water': '💧 Water'
        }
        
        for factor, score in suitability.items():
            if factor not in ['overall_score', 'grade'] and factor in score_labels:
                bar_length = int(score * 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                print(f"   {score_labels[factor]}: {bar} {score:.2f}")
        
        # Yield prediction
        yield_pred = result['yield_prediction']
        print(f"\n💰 Expected Yield: {yield_pred['predicted_yield_kg_per_hectare']:,.0f} kg/hectare")
        print(f"   Confidence: {yield_pred['confidence']:.1%}")
        print(f"   Model: {yield_pred['model_used']}")
        
    except Exception as e:
        print(f"❌ Crop-specific analysis failed: {e}")


def demo_ml_capabilities():
    """Demo ML model training and capabilities"""
    print_section("🤖 MACHINE LEARNING CAPABILITIES")
    
    advisor = FarmingAdvisor()
    
    print("🔄 Training ML models with synthetic data...")
    print("   (This demonstrates the XGBoost integration)")
    
    try:
        advisor.train_ml_models()
        print("✅ ML models trained successfully!")
        
        print("\n🧠 ML Model Features:")
        print("   • XGBoost regression for yield prediction")
        print("   • XGBoost classification for crop recommendation")
        print("   • Feature importance analysis")
        print("   • Confidence scoring")
        print("   • Synthetic training data generation")
        
    except Exception as e:
        print(f"❌ ML training failed: {e}")


def demo_api_info():
    """Show API information"""
    print_section("🌐 API SERVER CAPABILITIES")
    
    print("The system includes a FastAPI server with these endpoints:")
    print("   • POST /recommendations/quick - Quick crop recommendations")
    print("   • POST /recommendations/comprehensive - Full analysis")
    print("   • POST /advice/crop - Crop-specific advice")
    print("   • GET /crops/available - List available crops")
    print("   • GET /weather/{lat}/{lon} - Weather data")
    print("   • GET /soil/{lat}/{lon} - Soil analysis")
    
    print("\n🚀 To start the API server:")
    print("   python api_server.py")
    print("   Then visit: http://localhost:8000/docs")


def main():
    """Run the complete demo"""
    try:
        demo_quick_recommendations()
        time.sleep(2)
        
        demo_comprehensive_analysis()
        time.sleep(2)
        
        demo_crop_specific_advice()
        time.sleep(2)
        
        demo_ml_capabilities()
        time.sleep(1)
        
        demo_api_info()
        
        print_header("🎉 DEMO COMPLETED")
        print("The AI-Based Farming Advisory Agent is ready for use!")
        print("\nNext steps:")
        print("• Try: python main.py --lat YOUR_LAT --lon YOUR_LON")
        print("• Start API: python api_server.py")
        print("• Read: USAGE.md for detailed instructions")
        print("• Enhance: Add real weather API keys in .env file")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()