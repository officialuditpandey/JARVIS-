#!/usr/bin/env python3
"""
JARVIS Cloud Cowork - Main Launcher
Launches native desktop GUI with local Ollama integration
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Main launcher function"""
    print("=== JARVIS Cloud Cowork - Desktop HUD ===")
    print("Launching native Windows overlay with local Ollama...")
    print("==========================================")
    
    try:
        # Import and launch desktop GUI
        from desktop_gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"Failed to import desktop GUI: {e}")
        print("Please ensure PyQt6 is installed:")
        print("pip install PyQt6")
        return 1
        
    except Exception as e:
        print(f"Failed to launch JARVIS Desktop: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
