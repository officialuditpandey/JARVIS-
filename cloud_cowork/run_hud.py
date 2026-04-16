#!/usr/bin/env python3
"""
Simple Cloud Cowork HUD Launcher
Modern JARVIS interface with floating HUD design
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def launch_hud():
    """Launch the Cloud Cowork HUD"""
    print("🚀 Launching Cloud Cowork HUD...")
    print("🎨 Modern HUD Interface Loading...")
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Launch the HUD using app.py directly
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'app.py'
        ], capture_output=True, text=True, cwd=script_dir)
        
        if result.returncode == 0:
            print("✅ Cloud Cowork HUD launched successfully!")
            print("🌐 HUD should be available at: http://localhost:3000")
            print("💡 Press Ctrl+C to stop the HUD")
            
            # Wait a moment and try to open browser
            import time
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:3000')
                print("🌐 Opening HUD in default browser...")
            except Exception as e:
                print(f"⚠️ Could not open browser: {e}")
        else:
            print(f"❌ HUD launch failed: {result.stderr}")
            
    except KeyboardInterrupt:
        print("\n🛑 HUD launch cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error launching HUD: {e}")

if __name__ == "__main__":
    launch_hud()
