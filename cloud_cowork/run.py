#!/usr/bin/env python3
"""
Cloud Cowork - JARVIS Autonomous Agent System
Main entry point for the Reflex dashboard
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

import reflex as rx

# Import the app configuration
from cloud_cowork import app

if __name__ == "__main__":
    print("Starting Cloud Cowork - JARVIS Autonomous Agent System...")
    print("Dashboard will be available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    # Initialize and run the Reflex app
    app.run()
