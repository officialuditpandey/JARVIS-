#!/usr/bin/env python3
"""
JARVIS WhatsApp Plugin
Modular WhatsApp service that can be dynamically loaded
"""

import sys
import os
import re
import platform
from typing import Dict, Any
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class WhatsAppPlugin:
    """WhatsApp plugin for JARVIS"""
    
    def __init__(self):
        self.name = "whatsapp"
        self.version = "1.0.0"
        self.description = "Provides WhatsApp messaging capabilities"
        self.dependencies = ["pywhatkit", "pyperclip"]
    
    def send_message(self, contact: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message to contact"""
        try:
            # Clean phone number
            clean_phone = re.sub(r"[^\d+]", "", contact)
            if not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            
            # Use pywhatkit to send message
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(clean_phone, message)
            
            return {
                'success': True,
                'contact': contact,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"WhatsApp plugin error: {e}"
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'methods': ['send_message']
        }
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    print(f"WhatsApp plugin: Missing dependency {dep}")
                    return False
            
            print(f"WhatsApp plugin initialized successfully")
            return True
        except Exception as e:
            print(f"WhatsApp plugin initialization failed: {e}")
            return False
