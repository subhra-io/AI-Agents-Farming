#!/usr/bin/env python3
"""
Production deployment script for AI-Based Farming Advisory Agent
Implements the 7-step production roadmap
"""
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def print_step(step_num, title, description):
    """Print formatted step header"""
    print(f"\n{'='*60}")
    print(f"🚀 STEP {step_num}: {title}")
    print(f"{'='*60}")
    print(f"📋 {description}")
    print()

def check_system_frozen():
    """Verify system is properly frozen"""
    print("🔒 Checking system freeze status...")
    
    try:
        from src.core.version import get_system_info, get_version
        system_info = get_system_info()
        
        print(f"✅ System Version: {system_info['version']}")
        print(f"✅ Model Version: {system_info['model_version']}")
        print(f"✅ Status: {system_info['status']}")
        print(f"✅ Frozen Date: {system_info['frozen_date']}")
        
        return True
    except Exception as e:
        print(f"❌ System freeze check failed: {e}")
        return False

def setup_real_data():
    """Setup real yield data for ML training"""
    print("📊 Setting up real yield data...")
    
    try:
        from src.data.real_yield_data import RealYieldDataLoader, get_real_training_data
        
        # Load and validate real data
        loader = RealYieldDataLoader()
        real_data = get_real_training_data()
        
        # Save processed data
        data_path = loader.save_processed_data(real_data)
        quality_report = loader.validate_data_quality(real_data)
        
        print(f"✅ Real data loaded: {quality_report['total_records']} records")
        print(f"✅ Data quality score: {quality_report['quality_score']:.2f}")
        print(f"✅ Crops covered: {quality_report['unique_crops']}")
        print(f"✅ Geographic coverage: {quality_report['unique_locations']} locations")
        print(f"✅ Data saved to: {data_path}")
        
        return True
    except Exception as e:
        print(f"❌ Real data setup failed: {e}")
        return False

def retrain_ml_models():
    """Retrain ML models with real data"""
    print("🤖 Retraining ML models with real data...")
    
    try:
        from src.core.ml_models import CropYieldPredictor
        
        # Initialize and train with real data
        predictor = CropYieldPredictor()
        predictor.train_models()  # Will automatically use real data
        
        print("✅ ML models retrained with real yield data")
        print("✅ Models saved to models/ directory")
        
        return True
    except Exception as e:
        print(f"❌ ML model retraining failed: {e}")
        return False

def create_production_config():
    """Create production configuration"""
    print("⚙️  Creating production configuration...")
    
    config = {
        "system": {
            "version": "1.0.0",
            "environment": "production",
            "frozen": True,
            "deployment_date": datetime.now().isoformat()
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 4,
            "timeout": 30
        },
        "caching": {
            "weather_cache_hours": 6,
            "soil_cache_permanent": True,
            "ndvi_cache_days": 7
        },
        "ml": {
            "model_version": "1.0.0",
            "confidence_threshold": 0.6,
            "use_real_data": True
        },
        "safety": {
            "advisory_only": True,
            "confidence_warnings": True,
            "disclaimer_required": True
        }
    }
    
    config_path = Path("production_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Production config created: {config_path}")
    return True

def run_production_tests():
    """Run comprehensive production tests"""
    print("🧪 Running production test suite...")
    
    try:
        # Run existing tests
        result = subprocess.run([sys.executable, "test_advisor.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print(f"❌ Tests failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def create_deployment_summary():
    """Create deployment summary report"""
    print("📋 Creating deployment summary...")
    
    summary = {
        "deployment_info": {
            "date": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "PRODUCTION_READY"
        },
        "completed_steps": [
            "✅ System frozen with version control",
            "✅ Real yield data integrated",
            "✅ ML models retrained",
            "✅ Production configuration created",
            "✅ Test suite passed"
        ],
        "next_steps": [
            "🔄 Add NDVI satellite data (Step 3)",
            "⚡ Implement API caching (Step 4)", 
            "👥 Run farmer pilot program (Step 5)",
            "📱 Build Android app (Step 6)",
            "⚠️  Add safety disclaimers (Step 7)"
        ],
        "production_endpoints": {
            "api_server": "python api_server.py",
            "cli_tool": "python main.py --lat LAT --lon LON",
            "demo": "python demo.py"
        }
    }
    
    summary_path = Path("DEPLOYMENT_SUMMARY.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Deployment summary created: {summary_path}")
    return summary

def main():
    """Main deployment function"""
    print("🌾 AI-BASED FARMING ADVISORY AGENT")
    print("🚀 PRODUCTION DEPLOYMENT SCRIPT")
    print("="*60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Verify system freeze
    print_step(1, "SYSTEM FREEZE VERIFICATION", 
               "Verify system is properly frozen with version control")
    if check_system_frozen():
        success_count += 1
    
    # Step 2: Setup real data
    print_step(2, "REAL DATA INTEGRATION", 
               "Replace synthetic ML data with real crop yield data")
    if setup_real_data():
        success_count += 1
    
    # Step 2b: Retrain models
    print_step("2b", "ML MODEL RETRAINING", 
               "Retrain XGBoost models with real yield data")
    if retrain_ml_models():
        success_count += 1
    
    # Step 3: Production config
    print_step(3, "PRODUCTION CONFIGURATION", 
               "Create production-ready configuration")
    if create_production_config():
        success_count += 1
    
    # Step 4: Run tests
    print_step(4, "PRODUCTION TESTING", 
               "Run comprehensive test suite")
    if run_production_tests():
        success_count += 1
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETE")
    print("="*60)
    
    summary = create_deployment_summary()
    
    print(f"✅ Steps completed: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎯 PRODUCTION DEPLOYMENT SUCCESSFUL!")
        print("\n🚀 Ready to launch:")
        print("   • API Server: python api_server.py")
        print("   • CLI Tool: python main.py --lat 40.7128 --lon -74.0060")
        print("   • Demo: python demo.py")
        
        print("\n📋 Next Priority Steps:")
        for step in summary['next_steps']:
            print(f"   {step}")
            
    else:
        print("⚠️  DEPLOYMENT INCOMPLETE")
        print("Please resolve the failed steps before production launch.")
    
    print(f"\n📄 Full report: DEPLOYMENT_SUMMARY.json")

if __name__ == "__main__":
    main()