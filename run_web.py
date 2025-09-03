#!/usr/bin/env python3
"""
Rations Web Dashboard - Main Entry Point
Run this file to start the Flask web application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.web_app import app
from config import Config

if __name__ == "__main__":
    print("Starting Rations Web Dashboard...")
    print(f"Environment: {Config.FLASK_ENV}")
    print(f"Debug Mode: {Config.FLASK_ENV == 'development'}")
    print("=" * 50)
    
    app.run(
        debug=Config.FLASK_ENV == 'development',
        host='0.0.0.0',
        port=5000
    )
