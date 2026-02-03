#!/usr/bin/env python3
"""
Demo script for the AI Farming Advisor Web UI
Starts the server and opens the web interface
"""
import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path


def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirements: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting AI Farming Advisor Web Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌐 Web UI will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print()
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected - consider using one")
    
    print("=" * 60)
    
    try:
        # Start the server
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")


def open_browser():
    """Open the web browser to the UI"""
    time.sleep(2)  # Give server time to start
    try:
        webbrowser.open('http://localhost:8000')
        print("🌐 Opening web browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please manually open: http://localhost:8000")


def show_demo_info():
    """Show demo information"""
    print("🌾 AI FARMING ADVISOR - WEB UI DEMO")
    print("=" * 60)
    print()
    print("🎯 What you'll see:")
    print("   • Clean, farmer-friendly web interface")
    print("   • Location input with GPS detection")
    print("   • Three analysis types: Quick, Comprehensive, NDVI")
    print("   • Real-time crop recommendations")
    print("   • Interactive results with detailed explanations")
    print("   • Mobile-responsive design")
    print()
    print("📱 Features:")
    print("   • GPS location detection")
    print("   • Sub-second response times")
    print("   • Satellite vegetation analysis")
    print("   • Farmer-friendly explanations")
    print("   • Grade-based crop scoring (A-F)")
    print("   • Yield predictions with confidence")
    print()
    print("🧪 Try these sample locations:")
    print("   • Iowa, USA: 42.0, -93.5 (Corn Belt)")
    print("   • Punjab, India: 30.9, 75.8 (Wheat Region)")
    print("   • São Paulo, Brazil: -23.5, -46.6 (Soybean)")
    print("   • California, USA: 36.8, -119.8 (Diverse Agriculture)")
    print()


def main():
    """Main demo function"""
    show_demo_info()
    
    if not check_requirements():
        return
    
    # Check if static files exist
    static_dir = Path("static")
    if not static_dir.exists() or not (static_dir / "index.html").exists():
        print("❌ Static files not found. Please ensure static/ directory exists with web UI files.")
        return
    
    print("✅ Web UI files found")
    print()
    
    try:
        # Start server (this will block)
        start_server()
        
    except KeyboardInterrupt:
        print("\n👋 Demo ended. Thank you for trying the AI Farming Advisor!")


if __name__ == "__main__":
    main()