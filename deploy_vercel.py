#!/usr/bin/env python3
"""
Vercel Deployment Script for AI-Based Farming Advisory Agent
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not installed")
        return False

def install_vercel_cli():
    """Install Vercel CLI"""
    print("📦 Installing Vercel CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        print("✅ Vercel CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Vercel CLI")
        print("Please install manually: npm install -g vercel")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first")
        return False

def validate_deployment_files():
    """Validate that all required files exist"""
    required_files = [
        'vercel.json',
        'api/index.py',
        'requirements.txt',
        'static/index.html',
        'static/style.css',
        'static/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required deployment files found")
    return True

def check_environment_variables():
    """Check if environment variables are set"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("⚠️ OpenWeatherMap API key not set in environment")
        print("   You'll need to set it in Vercel dashboard after deployment")
        return False
    else:
        print(f"✅ OpenWeatherMap API key configured: {api_key[:8]}...")
        return True

def create_deployment_summary():
    """Create deployment summary"""
    summary = {
        "deployment_type": "vercel_serverless",
        "api_structure": {
            "entry_point": "api/index.py",
            "static_files": "static/",
            "endpoints": [
                "/api/recommendations/quick",
                "/api/recommendations/comprehensive", 
                "/api/location/{lat}/{lon}",
                "/api/ndvi/{lat}/{lon}",
                "/api/status",
                "/api/health"
            ]
        },
        "environment_variables": {
            "OPENWEATHER_API_KEY": "Required - set in Vercel dashboard"
        },
        "features": [
            "Real weather data integration",
            "Location name lookup",
            "NDVI satellite analysis",
            "ML-based crop recommendations",
            "Odisha-optimized coordinates",
            "Performance caching (<2s response)"
        ],
        "deployment_date": "2026-02-03",
        "production_ready": True
    }
    
    with open('DEPLOYMENT_SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Deployment summary created: DEPLOYMENT_SUMMARY.json")

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Starting Vercel deployment...")
    
    try:
        # Run vercel deployment
        result = subprocess.run(['vercel', '--prod'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print("\n📋 Deployment Output:")
            print(result.stdout)
            
            # Extract deployment URL
            lines = result.stdout.split('\n')
            for line in lines:
                if 'https://' in line and 'vercel.app' in line:
                    deployment_url = line.strip()
                    print(f"\n🌐 Your app is live at: {deployment_url}")
                    print(f"📊 API Status: {deployment_url}/api/status")
                    print(f"📖 API Docs: {deployment_url}/api/docs")
                    break
            
            return True
        else:
            print("❌ Deployment failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment error: {e}")
        return False

def main():
    """Main deployment function"""
    print("🌾 AI-Based Farming Advisory Agent - Vercel Deployment")
    print("=" * 60)
    
    # Step 1: Check Vercel CLI
    if not check_vercel_cli():
        if not install_vercel_cli():
            sys.exit(1)
    
    # Step 2: Validate files
    if not validate_deployment_files():
        sys.exit(1)
    
    # Step 3: Check environment
    env_ok = check_environment_variables()
    
    # Step 4: Create deployment summary
    create_deployment_summary()
    
    # Step 5: Deploy
    print("\n" + "=" * 60)
    print("Ready to deploy! This will:")
    print("1. Deploy your FastAPI backend to Vercel serverless functions")
    print("2. Serve your web UI from Vercel's CDN")
    print("3. Configure API endpoints with /api prefix")
    
    if not env_ok:
        print("\n⚠️ Remember to set OPENWEATHER_API_KEY in Vercel dashboard after deployment")
    
    confirm = input("\nProceed with deployment? (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        if deploy_to_vercel():
            print("\n🎉 Deployment completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Set environment variables in Vercel dashboard if needed")
            print("2. Test the API endpoints")
            print("3. Share your farming advisor with users!")
        else:
            print("\n❌ Deployment failed. Check the errors above.")
            sys.exit(1)
    else:
        print("Deployment cancelled.")

if __name__ == "__main__":
    main()