#!/usr/bin/env python3
"""
JARVIS Vision Eye Upgrade Demo
Demonstrates the new vision capabilities
"""

import sys
import os

# Add JARVIS backend path
sys.path.append(os.path.dirname(__file__))

def demo_vision_system():
    """Demo the Vision Eye Upgrade"""
    print("🤖 JARVIS Vision Eye Upgrade Demo")
    print("="*50)
    
    try:
        # Import the vision plugin
        from plugins.vision_plugin import VisionPlugin
        
        print("1. Initializing Vision Plugin...")
        vision_plugin = VisionPlugin()
        
        if vision_plugin.initialize():
            print("✅ Vision Plugin initialized successfully")
        else:
            print("❌ Vision Plugin initialization failed")
            return
        
        print("\n2. Testing command patterns...")
        test_commands = [
            "JARVIS, what do you see?",
            "scan the room",
            "describe what you see",
            "vision analysis"
        ]
        
        for cmd in test_commands:
            if vision_plugin.handles_command(cmd):
                print(f"✅ Recognizes: '{cmd}'")
            else:
                print(f"❌ Doesn't recognize: '{cmd}'")
        
        print("\n3. Testing vision capture and analysis...")
        print("📸 Capturing image from camera...")
        
        result = vision_plugin.process_command("what do you see")
        
        if result['success']:
            print("✅ Vision analysis successful!")
            print(f"\n📝 JARVIS Observation:")
            print("-" * 30)
            print(result['response'])
            print("-" * 30)
            
            # Log the observation
            print("\n📋 Logging observation to Syllabus_Progress.md...")
            if vision_plugin.log_observation(result['response'], result.get('image_path')):
                print("✅ Observation logged successfully")
            else:
                print("❌ Failed to log observation")
        else:
            print(f"❌ Vision analysis failed: {result['error']}")
        
        print("\n4. Cleanup...")
        vision_plugin.cleanup()
        print("✅ Cleanup completed")
        
        print("\n🎉 Vision Eye Upgrade Demo Complete!")
        print("\nYou can now use these commands with JARVIS:")
        for cmd in test_commands:
            print(f"  • '{cmd}'")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_vision_system()
