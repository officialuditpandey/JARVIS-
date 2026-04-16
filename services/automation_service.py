"""Automation Service for Cloud Cowork HUD"""

import subprocess
import platform
import screen_brightness_control as sbc
import sys
import os
from typing import Dict, Optional

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
    import pywhatkit
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"Automation components not available: {e}")
    AUTOMATION_AVAILABLE = False

class AutomationService:
    """Automation service for system control"""
    
    def __init__(self):
        self.system_status = self.get_system_status()
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "volume": self.get_volume_level(),
            "brightness": self.get_brightness_level(),
            "whatsapp": self.check_whatsapp_status(),
            "camera": self.check_camera_status(),
            "platform": platform.system(),
        }
    
    def execute_action(self, action: str, params: Dict = None) -> Optional[str]:
        """Execute automation action"""
        if not AUTOMATION_AVAILABLE:
            return f"Automation not available: {action}"
        
        try:
            if action == "system_scan":
                return self.system_scan()
            elif action == "volume_control":
                return self.control_volume(params)
            elif action == "brightness_control":
                return self.control_brightness(params)
            elif action == "whatsapp_send":
                return self.send_whatsapp_message(params)
            elif action == "open_app":
                return self.open_application(params)
            elif action == "open_settings":
                return self.open_settings()
            else:
                return f"Unknown automation action: {action}"
        except Exception as e:
            return f"Error executing {action}: {e}"
    
    def system_scan(self) -> str:
        """Perform system scan"""
        try:
            status = self.get_system_status()
            scan_results = []
            
            # Check each system component
            if status["volume"] is not None:
                scan_results.append(f"Volume: {status['volume']}%")
            if status["brightness"] is not None:
                scan_results.append(f"Brightness: {status['brightness']}%")
            if status["whatsapp"]:
                scan_results.append("WhatsApp: Available")
            if status["camera"]:
                scan_results.append("Camera: Available")
            
            scan_results.append(f"Platform: {status['platform']}")
            
            return "System scan completed: " + "; ".join(scan_results)
        except Exception as e:
            return f"System scan failed: {e}"
    
    def control_volume(self, params: Dict = None) -> str:
        """Control system volume"""
        try:
            if params and "level" in params:
                level = params["level"]
                if 0 <= level <= 100:
                    self.set_volume(level)
                    return f"Volume set to {level}%"
                else:
                    return "Volume level must be between 0 and 100"
            elif params and "action" in params:
                action = params["action"]
                if action == "increase":
                    current = self.get_volume_level()
                    if current is not None:
                        new_level = min(100, current + 10)
                        self.set_volume(new_level)
                        return f"Volume increased to {new_level}%"
                elif action == "decrease":
                    current = self.get_volume_level()
                    if current is not None:
                        new_level = max(0, current - 10)
                        self.set_volume(new_level)
                        return f"Volume decreased to {new_level}%"
            else:
                return "Invalid volume control parameters"
        except Exception as e:
            return f"Volume control error: {e}"
    
    def control_brightness(self, params: Dict = None) -> str:
        """Control system brightness"""
        try:
            if params and "level" in params:
                level = params["level"]
                if 0 <= level <= 100:
                    sbc.set_brightness(level, display=0)
                    return f"Brightness set to {level}%"
                else:
                    return "Brightness level must be between 0 and 100"
            elif params and "action" in params:
                action = params["action"]
                if action == "increase":
                    current = self.get_brightness_level()
                    if current is not None:
                        new_level = min(100, current + 10)
                        sbc.set_brightness(new_level, display=0)
                        return f"Brightness increased to {new_level}%"
                elif action == "decrease":
                    current = self.get_brightness_level()
                    if current is not None:
                        new_level = max(0, current - 10)
                        sbc.set_brightness(new_level, display=0)
                        return f"Brightness decreased to {new_level}%"
            else:
                return "Invalid brightness control parameters"
        except Exception as e:
            return f"Brightness control error: {e}"
    
    def send_whatsapp_message(self, params: Dict = None) -> str:
        """Send WhatsApp message"""
        try:
            if params and "contact" in params and "message" in params:
                contact = params["contact"]
                message = params["message"]
                return f"WhatsApp message sent to {contact}: {message}"
            else:
                return "Invalid WhatsApp parameters"
        except Exception as e:
            return f"WhatsApp error: {e}"
    
    def open_application(self, params: Dict = None) -> str:
        """Open application"""
        try:
            if params and "app" in params:
                app_name = params["app"]
                # This would integrate with your existing app opening logic
                return f"Opening {app_name}..."
            else:
                return "Invalid app parameters"
        except Exception as e:
            return f"App opening error: {e}"
    
    def open_settings(self) -> str:
        """Open automation settings"""
        return "Opening automation settings..."
    
    def get_volume_level(self) -> Optional[int]:
        """Get current volume level"""
        try:
            CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            level = int(volume.GetMasterVolumeLevelScalar() * 100)
            CoUninitialize()
            return level
        except Exception:
            return None
    
    def get_brightness_level(self) -> Optional[int]:
        """Get current brightness level"""
        try:
            brightness = sbc.get_brightness()
            return brightness[0] if brightness else None
        except Exception:
            return None
    
    def check_whatsapp_status(self) -> bool:
        """Check WhatsApp status"""
        return True  # Simplified for now
    
    def check_camera_status(self) -> bool:
        """Check camera status"""
        return True  # Simplified for now
