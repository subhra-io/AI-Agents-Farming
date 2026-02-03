#!/usr/bin/env python3
"""
Setup and installation script for the AI-Based Farming Advisory Agent
"""
import os
import subprocess
import sys


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True


def create_directories():
    """Create necessary directories"""
    directories = ["models", "data", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")


def setup_environment():
    """Setup environment file"""
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        try:
            with open('.env.example', 'r') as template:
                content = template.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ Created .env file")
            print("⚠️  Please edit .env file and add your API keys")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    else:
        print("📄 .env file already exists")


def test_installation():
    """Test the installation"""
    print("\nTesting installation...")
    try:
        from src.api.farming_advisor import FarmingAdvisor
        advisor = FarmingAdvisor()
        
        # Quick test
        result = advisor.get_quick_recommendation(40.7128, -74.0060)
        if 'top_recommendations' in result:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed - no recommendations returned")
            return False
            
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🌾 AI-Based Farming Advisory Agent Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed at requirements installation")
        return
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys (optional)")
        print("2. Run: python main.py --lat 40.7128 --lon -74.0060")
        print("3. Or run: python test_advisor.py")
        print("4. For API server: python api_server.py")
    else:
        print("\n❌ Setup completed with errors")
        print("Please check the error messages above")


if __name__ == "__main__":
    main()