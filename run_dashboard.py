#!/usr/bin/env python3
"""
Standalone Dashboard Runner
Direct test for HTML Dashboard connection
"""

import sys
import os

# Add JARVIS backend path
sys.path.append(os.path.dirname(__file__))

def main():
    """Run dashboard standalone"""
    try:
        from services.dashboard_service import DashboardService
        
        print("Starting JARVIS Dashboard...")
        dashboard = DashboardService()
        
        if not dashboard.app:
            print("ERROR: Flask not available")
            return False
        
        # Start dashboard
        if dashboard.start_dashboard():
            print(f"Dashboard running at: {dashboard.get_dashboard_url()}")
            print("Press Ctrl+C to stop")
            
            # Keep running
            try:
                import time
                while dashboard.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping dashboard...")
                dashboard.stop_dashboard()
        else:
            print("ERROR: Failed to start dashboard")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    main()
