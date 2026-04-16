"""
JARVIS Plugin System
Dynamic plugin loading and management
"""

import os
import sys
import importlib.util
from typing import Dict, List, Any

class PluginManager:
    """Plugin manager for JARVIS"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.loaded_plugins = {}
        self.plugin_info = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins"""
        plugins = []
        
        if os.path.exists(self.plugins_dir):
            for filename in os.listdir(self.plugins_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    plugin_name = filename[:-3]  # Remove .py extension
                    plugins.append(plugin_name)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            plugin_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")
            
            # Add plugins directory to Python path
            if self.plugins_dir not in sys.path:
                sys.path.insert(0, self.plugins_dir)
            
            # Import plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            
            # Execute the module to load its contents
            spec.loader.exec_module(module)
            
            # Initialize plugin
            if hasattr(module, 'initialize'):
                success = module.initialize()
            else:
                success = True
            
            if success:
                self.loaded_plugins[plugin_name] = module
                self.plugin_info[plugin_name] = module.get_info() if hasattr(module, 'get_info') else {}
                
                print(f"Plugin loaded: {plugin_name}")
                return True
            else:
                print(f"Plugin initialization failed: {plugin_name}")
                return False
                
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name in self.loaded_plugins:
            try:
                # Remove plugin from loaded plugins
                del self.loaded_plugins[plugin_name]
                del self.plugin_info[plugin_name]
                
                print(f"Plugin unloaded: {plugin_name}")
                return True
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {e}")
                return False
        
        return False
    
    def get_plugin_method(self, plugin_name: str, method_name: str):
        """Get a method from a loaded plugin"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            if hasattr(plugin, method_name):
                return getattr(plugin, method_name)
        
        return None
    
    def get_all_plugins_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all loaded plugins"""
        return self.plugin_info
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.loaded_plugins.keys())
