"""Database Manager for Cloud Cowork HUD"""

import json
import os
from typing import List, Dict, Any

class DatabaseManager:
    """Database manager for persistent storage"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def save_data(self, filename: str, data: Any):
        """Save data to file"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    def load_data(self, filename: str, default: Any = None) -> Any:
        """Load data from file"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return default
    
    def save_command_history(self, commands: List[Dict]):
        """Save command history"""
        self.save_data('command_history.json', commands)
    
    def load_command_history(self) -> List[Dict]:
        """Load command history"""
        return self.load_data('command_history.json', [])
    
    def save_notifications(self, notifications: List[Dict]):
        """Save notifications"""
        self.save_data('notifications.json', notifications)
    
    def load_notifications(self) -> List[Dict]:
        """Load notifications"""
        return self.load_data('notifications.json', [])
    
    def save_settings(self, settings: Dict):
        """Save user settings"""
        self.save_data('settings.json', settings)
    
    def load_settings(self) -> Dict:
        """Load user settings"""
        return self.load_data('settings.json', {})
