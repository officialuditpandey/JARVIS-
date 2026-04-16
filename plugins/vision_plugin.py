#!/usr/bin/env python3
"""
JARVIS Vision Plugin
Modular vision service that can be dynamically loaded
"""

import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class VisionPlugin:
    """Vision plugin for JARVIS - handles "what do you see?" commands"""
    
    def __init__(self):
        self.name = "vision"
        self.version = "1.0.0"
        self.description = "Provides camera capture and visual analysis capabilities"
        self.dependencies = ["cv2", "PIL", "ollama"]
        self.vision_service = None
        
        # Command patterns this plugin handles
        self.command_patterns = [
            "what do you see",
            "what can you see",
            "what do you observe",
            "look around",
            "scan the room",
            "describe what you see",
            "vision analysis",
            "camera view"
        ]
    
    def initialize(self) -> bool:
        """Initialize plugin and vision service"""
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    print(f"Vision plugin: Missing dependency {dep}")
                    return False
            
            # Import and initialize vision service
            from services.vision_service import VisionService
            self.vision_service = VisionService()
            
            # Test vision service initialization
            if not hasattr(self.vision_service, 'capture_and_analyze'):
                print("Vision plugin: VisionService missing required methods")
                return False
            
            print(f"Vision plugin initialized successfully")
            return True
            
        except Exception as e:
            print(f"Vision plugin initialization failed: {e}")
            return False
    
    def handles_command(self, query: str) -> bool:
        """Check if this plugin should handle the given command"""
        query_lower = query.lower().strip()
        return any(pattern in query_lower for pattern in self.command_patterns)
    
    def process_command(self, query: str) -> Dict[str, Any]:
        """Process vision command and return result"""
        try:
            if not self.vision_service:
                return {
                    'success': False,
                    'error': 'Vision service not initialized'
                }
            
            print("JARVIS Vision: Capturing and analyzing scene...")
            
            # Capture and analyze the scene
            result = self.vision_service.capture_and_analyze(
                prompt="You are JARVIS's eyes. Analyze the attached image and describe exactly what is in the physical room. Ignore previous stress test logs and any text context. Focus only on what you can see in this image - objects, people, furniture, and the physical environment."
            )
            
            if result['success']:
                return {
                    'success': True,
                    'response': result['analysis'],
                    'image_path': result.get('image_path'),
                    'timestamp': result.get('timestamp')
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Vision command processing failed: {e}'
            }
    
    def log_observation(self, observation: str, image_path: str = None) -> bool:
        """Log visual observation to Syllabus_Progress.md"""
        try:
            log_file = "Syllabus_Progress.md"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
## Visual Observation - {timestamp}

**Command:** "JARVIS, what do you see?"

**Observation:** {observation}

**Image Saved:** {image_path or 'temp_eye.jpg'}

---
"""
            
            # Append to log file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            print(f"Visual observation logged to {log_file}")
            return True
            
        except Exception as e:
            print(f"Failed to log observation: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'methods': ['process_command', 'handles_command', 'log_observation'],
            'command_patterns': self.command_patterns,
            'vision_service_available': self.vision_service is not None
        }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.vision_service and hasattr(self.vision_service, 'cleanup'):
                self.vision_service.cleanup()
        except Exception as e:
            print(f"Vision plugin cleanup failed: {e}")
