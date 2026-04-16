#!/usr/bin/env python3
"""
Simple Cloud Cowork Dashboard Launcher
Handles npm dependencies and launches the dashboard
"""

import subprocess
import sys
import os
import time

def install_frontend_deps():
    """Install frontend dependencies if needed"""
    web_dir = os.path.join(os.path.dirname(__file__), ".web")
    package_json = os.path.join(web_dir, "package.json")
    
    if not os.path.exists(package_json):
        print("Creating frontend package configuration...")
        os.makedirs(web_dir, exist_ok=True)
        
        # Create a minimal package.json
        package_content = {
            "name": "cloud-cowork-frontend",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            }
        }
        
        import json
        with open(package_json, "w") as f:
            json.dump(package_content, f, indent=2)
    
    # Install dependencies
    try:
        print("Installing frontend dependencies...")
        result = subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            cwd=web_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("Frontend dependencies installed successfully")
            return True
        else:
            print(f"npm install warning: {result.stderr}")
            return True  # Continue anyway
    except subprocess.TimeoutExpired:
        print("npm install timed out, continuing anyway...")
        return True
    except Exception as e:
        print(f"npm install error: {e}")
        return True  # Continue anyway

def launch_dashboard():
    """Launch the Cloud Cowork dashboard"""
    print("Starting Cloud Cowork - JARVIS Autonomous Agent System...")
    print("Dashboard will be available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    # Install frontend dependencies
    install_frontend_deps()
    
    # Import and run the app
    try:
        import asyncio
        import reflex as rx
        
        # Import the app configuration
        from cloud_cowork import app
        
        # Run the app
        asyncio.run(rx.run_in_thread(app))
        
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("You can try running: python -m reflex run")

if __name__ == "__main__":
    launch_dashboard()
