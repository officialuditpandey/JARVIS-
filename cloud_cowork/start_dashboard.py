#!/usr/bin/env python3
"""
Cloud Cowork - JARVIS Autonomous Agent System
Reflex dashboard starter
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

import reflex as rx

async def main():
    """Launch the Cloud Cowork dashboard"""
    print("Starting Cloud Cowork - JARVIS Autonomous Agent System...")
    print("Dashboard will be available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    # Import the app configuration
    from cloud_cowork import app
    
    # Run the app
    await rx.run_in_thread(app)

if __name__ == "__main__":
    asyncio.run(main())
