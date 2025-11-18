#!/usr/bin/env python3
"""
CalorieApp Testnet - XRPL Wallet & Token Management Application

Main entry point for the application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from core.app import CalorieAppTestnet

if __name__ == "__main__":
    app = CalorieAppTestnet()
    app.run()
