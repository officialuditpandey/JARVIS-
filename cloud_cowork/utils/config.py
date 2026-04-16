"""Configuration for Cloud Cowork HUD"""

import os
from typing import Dict, Any

class Config:
    """Configuration management for Cloud Cowork HUD"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            "hud": {
                "theme": "dark",
                "position": "bottom-center",
                "opacity": 0.9,
                "auto_hide": False,
                "animation_speed": "normal"
            },
            "ai": {
                "model": "hybrid",
                "max_history": 50,
                "auto_speak": True
            },
            "vision": {
                "model": "moondream",
                "resolution": "720p",
                "fps": 30
            },
            "automation": {
                "auto_scan": False,
                "notifications": True,
                "quick_actions": ["whatsapp", "volume", "brightness"]
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    import json
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return self.merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            self.save_config(default_config)
            return default_config
    
    def merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge default config with loaded config"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent
        for key in keys[:-1]:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return
        
        # Set the value
        config[keys[-1]] = value
        self.save_config(config)
