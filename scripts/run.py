#!/usr/bin/env python3
"""
CalorieApp Launcher

Simple launcher script for the CalorieApp application.
This script ensures proper environment setup before launching the app.
"""

import sys
import os
import logging

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import kivy
        import kivymd
        import xrpl
        import cryptography
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup the application environment"""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Configure Kivy settings
    os.environ['KIVY_WINDOW_POSITION'] = 'custom'
    os.environ['KIVY_WINDOW_LEFT'] = '100'
    os.environ['KIVY_WINDOW_TOP'] = '100'

def main():
    """Main launcher function"""
    print("🚀 Starting CalorieApp...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Import and run the main application
    try:
        from src.core.app import CalorieAppTestnet
        app = CalorieAppTestnet()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()