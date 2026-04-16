#!/usr/bin/env python3
"""
Cloud Cowork HUD Launcher
Modern JARVIS interface with floating HUD design
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    required_packages = [
        'cv2', 'numpy', 'Pillow', 'requests',
        'aiohttp', 'pycaw', 'screen_brightness_control',
        'pywhatkit', 'pyautogui', 'keyboard', 'ollama',
        'google-generativeai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        for package in missing_packages:
            print(f"  pip install {package}")
        return False
    
    print("✅ All dependencies available")
    return True

def launch_hud():
    """Launch the Cloud Cowork HUD"""
    print("🚀 Launching Cloud Cowork HUD...")
    print("🎨 Modern HUD Interface Loading...")
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Launch the HUD
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

def main():
    """Main function"""
    print("=" * 50)
    print("🎯 Cloud Cowork HUD Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return 1
    
    # Launch HUD
    launch_hud()

if __name__ == "__main__":
    main()
