#!/usr/bin/env python3
"""
AI-Based Farming Advisory Agent - Main Entry Point
"""
import argparse
import json
import os
from dotenv import load_dotenv

from src.api.farming_advisor import FarmingAdvisor


def main():
    """Main entry point for the farming advisory system"""
    
    # Load environment variables
    load_dotenv()
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='AI-Based Farming Advisory Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --lat 40.7128 --lon -74.0060
  python main.py --lat 28.6139 --lon 77.2090 --quick
  python main.py --lat 37.7749 --lon -122.4194 --crop wheat
  python main.py --train-models
        """
    )
    
    parser.add_argument(
        '--lat', '--latitude', 
        type=float, 
        help='Latitude coordinate'
    )
    
    parser.add_argument(
        '--lon', '--longitude', 
        type=float, 
        help='Longitude coordinate'
    )
    
    parser.add_argument(
        '--crop', 
        type=str, 
        help='Get advice for specific crop'
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true', 
        help='Get quick recommendations only'
    )
    
    parser.add_argument(
        '--train-models', 
        action='store_true', 
        help='Train ML models with synthetic data'
    )
    
    parser.add_argument(
        '--ndvi', 
        action='store_true', 
        help='Get NDVI satellite vegetation analysis'
    )
    
    parser.add_argument(
        '--output', '-o', 
        type=str, 
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--api-key', 
        type=str, 
        help='OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    # Initialize the farming advisor
    api_key = args.api_key or os.getenv('OPENWEATHER_API_KEY')
    advisor = FarmingAdvisor(weather_api_key=api_key)
    
    # Handle model training
    if args.train_models:
        print("Training ML models...")
        advisor.train_ml_models()
        print("Model training completed!")
        return
    
    # Validate coordinates
    if args.lat is None or args.lon is None:
        print("Error: Both latitude and longitude are required")
        print("Use --help for usage information")
        return
    
    if not (-90 <= args.lat <= 90):
        print("Error: Latitude must be between -90 and 90")
        return
    
    if not (-180 <= args.lon <= 180):
        print("Error: Longitude must be between -180 and 180")
        return
    
    print(f"Analyzing farming conditions for location: {args.lat}, {args.lon}")
    print("=" * 60)
    
    try:
        # Get recommendations based on mode
        if args.ndvi:
            # NDVI satellite analysis
            print("Getting NDVI satellite analysis...")
            from src.core.ndvi_service import NDVIService
            ndvi_service = NDVIService()
            result = ndvi_service.get_ndvi_data(args.lat, args.lon)
            summary = ndvi_service.get_ndvi_summary(args.lat, args.lon)
            
            # Display NDVI results
            print(f"\n🛰️ NDVI Satellite Analysis for {args.lat}, {args.lon}")
            print("=" * 60)
            print(summary)
            
            ndvi_analysis = result['ndvi_analysis']
            print(f"\n📊 Detailed Analysis:")
            print(f"   Current NDVI: {ndvi_analysis['current_ndvi']:.3f}")
            print(f"   Average NDVI: {ndvi_analysis['average_ndvi']:.3f}")
            print(f"   Trend: {ndvi_analysis['trend']:+.3f}")
            print(f"   Risk Level: {ndvi_analysis['risk_level'].title()}")
            
            if result['alerts']:
                print(f"\n⚠️ Alerts:")
                for alert in result['alerts']:
                    print(f"   • {alert['message']}")
                    print(f"     Recommendation: {alert['recommendation']}")
            
            return
            
        elif args.crop:
            # Crop-specific analysis
            print(f"Getting advice for {args.crop}...")
            result = advisor.get_crop_specific_advice(args.crop, args.lat, args.lon)
            
        elif args.quick:
            # Quick recommendations
            print("Getting quick recommendations...")
            result = advisor.get_quick_recommendation(args.lat, args.lon)
            
        else:
            # Full comprehensive analysis
            print("Running comprehensive analysis...")
            result = advisor.get_recommendations(args.lat, args.lon)
        
        # Handle errors
        if 'error' in result:
            print(f"Analysis Error: {result['error']}")
            return
        
        # Display results
        display_results(result, args.quick, args.crop)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\nResults saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


def display_results(result: dict, quick_mode: bool = False, crop_specific: str = None):
    """Display results in a user-friendly format"""
    
    if crop_specific:
        display_crop_specific_results(result)
    elif quick_mode:
        display_quick_results(result)
    else:
        display_comprehensive_results(result)


def display_quick_results(result: dict):
    """Display quick recommendation results"""
    print(f"\nLocation: {result['location']}")
    
    # Handle both old and new metadata structure
    if 'metadata' in result:
        print(f"Analysis Time: {result['metadata']['timestamp']}")
    elif 'timestamp' in result:
        print(f"Analysis Time: {result['timestamp']}")
    
    print("\nTop Crop Recommendations:")
    print("-" * 40)
    
    for i, rec in enumerate(result['top_recommendations'], 1):
        print(f"{i}. {rec['crop']} (Grade: {rec['grade']}, Score: {rec['score']:.2f})")
        print(f"   {rec['simple_advice']}")
        print()


def display_crop_specific_results(result: dict):
    """Display crop-specific analysis results"""
    print(f"\nCrop: {result['crop_name']}")
    print(f"Location: {result['location']}")
    print(f"Analysis Time: {result['timestamp']}")
    print("\n" + "=" * 60)
    
    # Suitability analysis
    suitability = result['suitability_analysis']['suitability_score']
    print(f"Overall Suitability: {suitability['grade']} ({suitability['overall_score']:.2f})")
    print("\nScore Breakdown:")
    for factor, score in suitability.items():
        if factor not in ['overall_score', 'grade']:
            print(f"  {factor.title()}: {score:.2f}")
    
    # Yield prediction
    yield_pred = result['yield_prediction']
    print(f"\nExpected Yield: {yield_pred['predicted_yield_kg_per_hectare']:,.0f} kg/hectare")
    print(f"Confidence: {yield_pred['confidence']:.1%}")
    
    # Detailed explanations
    print("\n" + "=" * 60)
    print("DETAILED ANALYSIS")
    print("=" * 60)
    print(result['detailed_explanation'])
    print("\n" + "-" * 60)
    print(result['yield_explanation'])


def display_comprehensive_results(result: dict):
    """Display comprehensive analysis results"""
    
    # Header
    location = result['location']
    print(f"\nLocation: {location['latitude']:.4f}, {location['longitude']:.4f}")
    print(f"Analysis Time: {location['timestamp']}")
    print(f"Overall Confidence: {result['metadata']['confidence_level']:.1%}")
    print("\n" + "=" * 80)
    
    # Environmental conditions
    weather = result['environmental_conditions']['current_weather']
    soil = result['environmental_conditions']['soil_analysis']
    
    print("ENVIRONMENTAL CONDITIONS")
    print("=" * 80)
    print(f"Temperature: {weather['temperature']}°C")
    print(f"Humidity: {weather['humidity']}%")
    print(f"Weather: {weather['description']}")
    print(f"Soil Type: {soil['primary_soil_type']} ({soil['climate_zone']} zone)")
    print(f"Soil pH: {soil['ph_range'][0]:.1f}-{soil['ph_range'][1]:.1f}")
    print(f"Fertility: {soil['fertility_level']}")
    
    # NDVI Analysis (if available)
    if 'ndvi_analysis' in result['environmental_conditions']:
        ndvi = result['environmental_conditions']['ndvi_analysis']['ndvi_analysis']
        print(f"🛰️ Vegetation Health: {ndvi['health_status'].title()} (NDVI: {ndvi['current_ndvi']:.2f})")
        print(f"🚨 Risk Level: {ndvi['risk_level'].title()}")
    
    # Top crop recommendations
    crops = result['crop_recommendations']['rule_based']
    print(f"\n{'=' * 80}")
    print("TOP CROP RECOMMENDATIONS")
    print("=" * 80)
    
    for i, crop in enumerate(crops[:5], 1):
        name = crop['crop_info']['name']
        grade = crop['suitability_score']['grade']
        score = crop['suitability_score']['overall_score']
        
        print(f"{i}. {name} - Grade {grade} (Score: {score:.2f})")
        
        # Show yield prediction if available
        crop_name = crop['crop_name']
        if crop_name in result['crop_recommendations']['yield_predictions']:
            yield_pred = result['crop_recommendations']['yield_predictions'][crop_name]
            yield_val = yield_pred['predicted_yield_kg_per_hectare']
            print(f"   Expected Yield: {yield_val:,.0f} kg/hectare")
        
        print()
    
    # NDVI Summary (if available)
    if 'ndvi_summary' in result['explanations']:
        print("=" * 80)
        print("SATELLITE VEGETATION ANALYSIS")
        print("=" * 80)
        print(result['explanations']['ndvi_summary'])
    
    # Overall summary
    if result['explanations']['overall_summary']:
        print("\n" + "=" * 80)
        print("FARMING ADVICE SUMMARY")
        print("=" * 80)
        print(result['explanations']['overall_summary'])
    
    # Detailed explanations for top 3 crops
    explanations = result['explanations']['detailed_crop_explanations']
    if explanations:
        print("\n" + "=" * 80)
        print("DETAILED CROP ANALYSIS")
        print("=" * 80)
        
        for i, crop in enumerate(crops[:3], 1):
            crop_name = crop['crop_name']
            if crop_name in explanations:
                print(f"\n{i}. {explanations[crop_name]}")
                print("-" * 80)


if __name__ == "__main__":
    main()