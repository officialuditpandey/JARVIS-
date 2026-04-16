#!/usr/bin/env python3
"""
JARVIS Dashboard Launcher
Simple script to open the Cloud Cowork dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Cloud Cowork dashboard"""
    print("JARVIS: Opening Cloud Cowork dashboard, sir...")
    
    # Change to the cloud_cowork directory
    dashboard_path = os.path.join(os.path.dirname(__file__), "cloud_cowork")
    
    try:
        # Launch the dashboard
        subprocess.run([
            sys.executable, "start_dashboard.py"
        ], cwd=dashboard_path, check=True)
        
        print("JARVIS: Dashboard launched successfully!")
        print("JARVIS: You can access it at http://localhost:3000")
        
    except subprocess.CalledProcessError as e:
        print(f"JARVIS: Error launching dashboard: {e}")
        return False
    except FileNotFoundError:
        print("JARVIS: Cloud Cowork system not found. Please ensure it's installed.")
        return False
    
    return True

if __name__ == "__main__":
    main()
