#!/usr/bin/env python3
"""
Vision System Status Monitor
Tracks and logs vision system performance for debugging
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VisionSystemMonitor:
    """Monitor and log vision system status"""
    
    def __init__(self):
        self.log_file = os.path.join(os.path.dirname(__file__), os.getenv("VISION_LOGS_FILE", "vision_system_logs.json"))
        self.status_history = []
        self.load_history()
    
    def load_history(self):
        """Load existing history"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.status_history = data.get('history', [])
        except:
            self.status_history = []
    
    def log_attempt(self, method: str, success: bool, error: str = None, response_time: float = None):
        """Log a vision system attempt"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'success': success,
            'error': error,
            'response_time': response_time
        }
        
        self.status_history.append(entry)
        
        # Keep only last 100 entries
        if len(self.status_history) > 100:
            self.status_history = self.status_history[-100:]
        
        # Save to file
        try:
            with open(self.log_file, 'w') as f:
                json.dump({'history': self.status_history}, f, indent=2)
        except Exception as e:
            print(f"Failed to save vision log: {e}")
    
    def get_success_rate(self, method: str = None, last_n: int = 10) -> float:
        """Get success rate for a method or overall"""
        recent = self.status_history[-last_n:]
        if method:
            recent = [e for e in recent if e['method'] == method]
        
        if not recent:
            return 0.0
        
        success_count = sum(1 for e in recent if e['success'])
        return (success_count / len(recent)) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system performance summary"""
        if not self.status_history:
            return {"status": "No data available"}
        
        recent = self.status_history[-20:]  # Last 20 attempts
        
        return {
            'total_attempts': len(self.status_history),
            'recent_attempts': len(recent),
            'overall_success_rate': self.get_success_rate(),
            'recent_success_rate': self.get_success_rate(last_n=20),
            'method_performance': {
                'VisionService': self.get_success_rate('VisionService', last_n=10),
                'Screenshot': self.get_success_rate('Screenshot', last_n=10),
                'BasicCapture': self.get_success_rate('BasicCapture', last_n=10)
            },
            'last_error': next((e['error'] for e in recent if not e['success']), None),
            'last_success': next((e['timestamp'] for e in recent if e['success']), None)
        }

# Global monitor instance
vision_monitor = VisionSystemMonitor()

def log_vision_attempt(method: str, success: bool, error: str = None, response_time: float = None):
    """Convenience function to log vision attempts"""
    vision_monitor.log_attempt(method, success, error, response_time)

def get_vision_status() -> Dict[str, Any]:
    """Get current vision system status"""
    return vision_monitor.get_summary()
