#!/usr/bin/env python3
"""
JARVIS Weather Plugin
Modular weather service that can be dynamically loaded
"""

import sys
import os
import requests
from typing import Dict, Any
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class WeatherPlugin:
    """Weather plugin for JARVIS"""
    
    def __init__(self):
        self.name = "weather"
        self.version = "1.0.0"
        self.description = "Provides weather information for any city"
        self.dependencies = ["requests"]
    
    def get_weather(self, city: str = "auto:ip") -> Dict[str, Any]:
        """Get weather information for specified city"""
        try:
            response = requests.get(f"https://wttr.in/{city}?format=3")
            if response.status_code == 200:
                weather_data = response.text.strip()
                return {
                    'success': True,
                    'data': weather_data,
                    'city': city,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"Unable to fetch weather for {city}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Weather service error: {e}"
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'methods': ['get_weather']
        }
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    print(f"Weather plugin: Missing dependency {dep}")
                    return False
            
            print(f"Weather plugin initialized successfully")
            return True
        except Exception as e:
            print(f"Weather plugin initialization failed: {e}")
            return False
