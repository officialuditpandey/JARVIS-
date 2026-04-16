#!/usr/bin/env python3
"""
JARVIS Security Plugin - The Guardian Upgrade
Provides security mode control and alert management
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import cv2

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from services.security_service import SecurityService
    from services.voice_service import speak
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"Security components not available: {e}")
    SECURITY_AVAILABLE = False

class SecurityPlugin:
    """Security plugin for JARVIS - handles Security Mode commands"""
    
    def __init__(self):
        self.name = "security"
        self.version = "1.0.0"
        self.description = "Provides security monitoring and alert capabilities"
        self.dependencies = ["cv2", "numpy", "threading"]
        self.security_service = None
        self.is_active = False
        
        # Command patterns this plugin handles
        self.command_patterns = [
            "engage security mode",
            "engage security",
            "start security mode",
            "start security",
            "activate security",
            "security mode on",
            "turn on security",
            "enable security",
            "disarm security",
            "stop security mode",
            "stop security",
            "deactivate security",
            "security mode off",
            "turn off security",
            "disable security",
            "security status"
        ]
    
    def initialize(self) -> bool:
        """Initialize plugin and security service"""
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    print(f"Security plugin: Missing dependency {dep}")
                    return False
            
            # Initialize security service
            self.security_service = SecurityService()
            
            # Test security service initialization
            if not hasattr(self.security_service, 'start_monitoring'):
                print("Security plugin: SecurityService missing required methods")
                return False
            
            print(f"Security plugin initialized successfully")
            return True
            
        except Exception as e:
            print(f"Security plugin initialization failed: {e}")
            return False
    
    def handles_command(self, query: str) -> bool:
        """Check if this plugin should handle the given command"""
        query_lower = query.lower().strip()
        return any(pattern in query_lower for pattern in self.command_patterns)
    
    def security_alert_callback(self, frame, image_path: str):
        """Callback for security alerts"""
        try:
            # Speak alert message
            speak("Sir, an unknown person has entered the room.")
            
            # Log additional details
            print(f"SECURITY ALERT: Person detected - Image saved to {image_path}")
            
        except Exception as e:
            print(f"Security alert callback error: {e}")
    
    def process_command(self, query: str) -> Dict[str, Any]:
        """Process security command and return result"""
        try:
            if not self.security_service:
                return {
                    'success': False,
                    'error': 'Security service not initialized'
                }
            
            query_lower = query.lower().strip()
            
            # Handle engage security commands
            if any(pattern in query_lower for pattern in [
                "engage security mode", "engage security", "start security mode", 
                "start security", "activate security", "security mode on",
                "turn on security", "enable security"
            ]):
                return self.engage_security()
            
            # Handle disarm security commands
            elif any(pattern in query_lower for pattern in [
                "disarm security", "stop security mode", "stop security",
                "deactivate security", "security mode off", "turn off security",
                "disable security"
            ]):
                return self.disarm_security()
            
            # Handle status command
            elif "security status" in query_lower:
                return self.get_security_status()
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown security command: {query}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Security command processing failed: {e}'
            }
    
    def engage_security(self) -> Dict[str, Any]:
        """Engage security mode"""
        try:
            if self.is_active:
                return {
                    'success': True,
                    'response': 'Security mode is already active, sir.',
                    'status': 'already_active'
                }
            
            print("JARVIS Security: Engaging Security Mode...")
            
            # Start monitoring with alert callback
            if self.security_service.start_monitoring(self.security_alert_callback):
                self.is_active = True
                
                # Log engagement
                self.log_security_event("SECURITY_ENGAGED", "", "Security mode activated by user command")
                
                return {
                    'success': True,
                    'response': 'Security mode engaged, sir. I am now monitoring the room for any unauthorized personnel.',
                    'status': 'engaged'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to engage security mode. Camera may be unavailable.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to engage security mode: {e}'
            }
    
    def disarm_security(self) -> Dict[str, Any]:
        """Disarm security mode"""
        try:
            if not self.is_active:
                return {
                    'success': True,
                    'response': 'Security mode is not currently active, sir.',
                    'status': 'not_active'
                }
            
            print("JARVIS Security: Disarming Security Mode...")
            
            # Stop monitoring
            if self.security_service.stop_monitoring():
                self.is_active = False
                
                # Log disengagement
                self.log_security_event("SECURITY_DISENGAGED", "", "Security mode deactivated by user command")
                
                return {
                    'success': True,
                    'response': 'Security mode disengaged, sir. Monitoring has been stopped.',
                    'status': 'disengaged'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to properly disarm security mode.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to disarm security mode: {e}'
            }
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            if not self.security_service:
                return {
                    'success': False,
                    'error': 'Security service not available'
                }
            
            status = self.security_service.get_status()
            
            status_text = f"Security mode is {'active' if self.is_active else 'inactive'}. "
            status_text += f"Camera is {'connected' if status['camera_active'] else 'disconnected'}. "
            status_text += f"Baseline is {'captured' if status['baseline_captured'] else 'not captured'}."
            
            return {
                'success': True,
                'response': status_text,
                'details': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get security status: {e}'
            }
    
    def log_security_event(self, event_type: str, image_path: str = "", details: str = ""):
        """Log security event to Syllabus_Progress.md"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
## Security Command - {timestamp}

**Command:** {event_type}
**Image:** {image_path}
**Details:** {details}

---
"""
            
            # Append to log file
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            print(f"Security command logged to Syllabus_Progress.md")
        except Exception as e:
            print(f"Failed to log security command: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'methods': ['process_command', 'handles_command', 'engage_security', 'disarm_security'],
            'command_patterns': self.command_patterns,
            'security_service_available': self.security_service is not None,
            'is_active': self.is_active
        }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.is_active and self.security_service:
                self.security_service.stop_monitoring()
                self.is_active = False
        except Exception as e:
            print(f"Security plugin cleanup failed: {e}")
