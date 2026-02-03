#!/usr/bin/env python3
"""
Simple launcher for the AI Farming Advisor Web UI
"""
import subprocess
import sys
import webbrowser
import time
import threading


def open_browser_delayed():
    """Open browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8000')
        print("🌐 Web UI opened in browser: http://localhost:8000")
    except:
        pass


def main():
    print("🌾 Starting AI Farming Advisor Web UI...")
    print("🚀 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()