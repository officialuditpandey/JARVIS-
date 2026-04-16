#!/usr/bin/env python3
"""
JARVIS Integrations Manager
Manages all external service integrations for enhanced JARVIS
"""

import os
import sys
import json
import time
import threading
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import webbrowser

# Add JARVIS backend path
sys.path.insert(0, '.')

class JarvisIntegrationsManager:
    """Manages all JARVIS external integrations"""
    
    def __init__(self):
        self.is_active = False
        self.integrations = {}
        self.api_keys = {}
        self.integration_db = "jarvis_integrations.db"
        
        # Initialize integration configurations
        self._init_integration_configs()
        
        # Load existing integrations
        self._load_integrations()
        
        # Start integration monitoring
        self._start_integration_monitoring()
    
    def _init_integration_configs(self):
        """Initialize all integration configurations - NO NEW APIs REQUIRED"""
        self.integrations = {
            # SOFTWARE INTEGRATIONS - NO API REQUIRED
            "browser_extension": {
                "name": "Browser Extension",
                "type": "software",
                "status": "inactive",
                "features": ["web_analysis", "auto_summarize", "content_extraction"],
                "api_required": False,
                "setup_method": "browser_extension"
            },
            "code_editor": {
                "name": "Code Editor",
                "type": "software",
                "status": "inactive",
                "features": ["smart_assistance", "code_completion", "project_management"],
                "api_required": False,
                "setup_method": "plugin"
            },
            "local_file_manager": {
                "name": "Local File Manager",
                "type": "software",
                "status": "inactive",
                "features": ["smart_organization", "quick_search", "auto_backup"],
                "api_required": False,
                "setup_method": "local"
            },
            "system_monitor": {
                "name": "System Monitor",
                "type": "software",
                "status": "inactive",
                "features": ["performance_tracking", "resource_optimization", "health_alerts"],
                "api_required": False,
                "setup_method": "local"
            },
            
            # LOCAL PRODUCTIVITY TOOLS - NO API REQUIRED
            "local_notes": {
                "name": "Local Note Manager",
                "type": "productivity",
                "status": "inactive",
                "features": ["organization", "search", "categorization"],
                "api_required": False,
                "setup_method": "local"
            },
            "local_tasks": {
                "name": "Local Task Manager",
                "type": "productivity",
                "status": "inactive",
                "features": ["task_tracking", "reminders", "prioritization"],
                "api_required": False,
                "setup_method": "local"
            },
            "document_scanner": {
                "name": "Document Scanner",
                "type": "productivity",
                "status": "inactive",
                "features": ["OCR", "text_extraction", "document_organization"],
                "api_required": False,
                "setup_method": "local",
                "dependencies": ["pytesseract"]
            },
            
            # LOCAL ENTERTAINMENT - NO API REQUIRED
            "local_music": {
                "name": "Local Music Player",
                "type": "entertainment",
                "status": "inactive",
                "features": ["playback_control", "playlist_management", "library_organization"],
                "api_required": False,
                "setup_method": "local"
            },
            "local_videos": {
                "name": "Local Video Player",
                "type": "entertainment",
                "status": "inactive",
                "features": ["playback_control", "library_management", "recommendations"],
                "api_required": False,
                "setup_method": "local"
            },
            "local_games": {
                "name": "Local Game Library",
                "type": "entertainment",
                "status": "inactive",
                "features": ["library_management", "launch_shortcuts", "time_tracking"],
                "api_required": False,
                "setup_method": "local"
            },
            
            # OFFLINE CAPABILITIES - NO API REQUIRED
            "offline_ai": {
                "name": "Offline AI (Ollama)",
                "type": "ai_service",
                "status": "active",  # Already using Ollama
                "features": ["local_reasoning", "analysis", "chat"],
                "api_required": False,
                "setup_method": "local",
                "dependencies": ["ollama"]
            },
            "offline_vision": {
                "name": "Offline Vision (Moondream)",
                "type": "ai_service",
                "status": "active",  # Already using Moondream
                "features": ["object_detection", "scene_analysis", "text_recognition"],
                "api_required": False,
                "setup_method": "local",
                "dependencies": ["ollama", "moondream"]
            },
            "offline_speech": {
                "name": "Offline Speech Recognition",
                "type": "ai_service",
                "status": "inactive",
                "features": ["speech_to_text", "voice_commands", "transcription"],
                "api_required": False,
                "setup_method": "local",
                "dependencies": ["vosk", "whisper_local"]
            }
        }
    
    def _load_integrations(self):
        """Load existing integration statuses"""
        try:
            with sqlite3.connect(self.integration_db) as conn:
                cursor = conn.cursor()
                
                # Create integrations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS integrations (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        status TEXT,
                        config TEXT,
                        last_sync TIMESTAMP,
                        usage_count INTEGER
                    )
                ''')
                
                # Load existing integrations
                cursor.execute("SELECT id, status, config FROM integrations")
                for row in cursor.fetchall():
                    if row[0] in self.integrations:
                        self.integrations[row[0]]["status"] = row[1]
                        if row[2]:
                            config = json.loads(row[2])
                            self.integrations[row[0]].update(config)
                
                conn.commit()
                print(f"Loaded {len([i for i in self.integrations.values() if i['status'] == 'active'])} active integrations")
                
        except Exception as e:
            print(f"Failed to load integrations: {e}")
    
    def _start_integration_monitoring(self):
        """Start monitoring all active integrations"""
        def monitor():
            while self.is_active:
                try:
                    self._sync_active_integrations()
                    time.sleep(300)  # Sync every 5 minutes
                except Exception as e:
                    print(f"Integration monitoring error: {e}")
                    time.sleep(60)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def _sync_active_integrations(self):
        """Sync data from active integrations"""
        for integration_id, integration in self.integrations.items():
            if integration["status"] == "active":
                try:
                    self._sync_integration(integration_id, integration)
                except Exception as e:
                    print(f"Sync error for {integration['name']}: {e}")
    
    def _sync_integration(self, integration_id: str, integration: Dict):
        """Sync specific integration"""
        integration_type = integration["type"]
        
        if integration_type == "online":
            self._sync_online_service(integration_id, integration)
        elif integration_type == "productivity":
            self._sync_productivity_tool(integration_id, integration)
        elif integration_type == "entertainment":
            self._sync_entertainment_service(integration_id, integration)
        elif integration_type == "ai_service":
            self._sync_ai_service(integration_id, integration)
    
    def _sync_online_service(self, integration_id: str, integration: Dict):
        """Sync online service integration"""
        # This would implement actual API calls to sync data
        print(f"Syncing {integration['name']}...")
        # Placeholder for actual sync implementation
    
    def _sync_productivity_tool(self, integration_id: str, integration: Dict):
        """Sync productivity tool integration"""
        print(f"Syncing {integration['name']}...")
        # Placeholder for actual sync implementation
    
    def _sync_entertainment_service(self, integration_id: str, integration: Dict):
        """Sync entertainment service integration"""
        print(f"Syncing {integration['name']}...")
        # Placeholder for actual sync implementation
    
    def _sync_ai_service(self, integration_id: str, integration: Dict):
        """Sync AI service integration"""
        print(f"Syncing {integration['name']}...")
        # Placeholder for actual sync implementation
    
    def activate_integration(self, integration_id: str, config: Dict = None) -> bool:
        """Activate an integration"""
        if integration_id not in self.integrations:
            print(f"Unknown integration: {integration_id}")
            return False
        
        integration = self.integrations[integration_id]
        
        try:
            # Check if API key is required
            if integration.get("api_required", False) and not config:
                print(f"API key required for {integration['name']}")
                return False
            
            # Activate integration
            integration["status"] = "active"
            if config:
                integration.update(config)
            
            # Save to database
            self._save_integration_status(integration_id, integration)
            
            # Perform initial sync
            self._sync_integration(integration_id, integration)
            
            print(f"Activated: {integration['name']}")
            return True
            
        except Exception as e:
            print(f"Failed to activate {integration['name']}: {e}")
            return False
    
    def deactivate_integration(self, integration_id: str) -> bool:
        """Deactivate an integration"""
        if integration_id not in self.integrations:
            return False
        
        integration = self.integrations[integration_id]
        integration["status"] = "inactive"
        
        # Save to database
        self._save_integration_status(integration_id, integration)
        
        print(f"Deactivated: {integration['name']}")
        return True
    
    def _save_integration_status(self, integration_id: str, integration: Dict):
        """Save integration status to database"""
        try:
            with sqlite3.connect(self.integration_db) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO integrations 
                    (id, name, status, config, last_sync, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    integration_id,
                    integration["name"],
                    integration["status"],
                    json.dumps({k: v for k, v in integration.items() if k not in ["name", "status"]}),
                    datetime.now(),
                    integration.get("usage_count", 0)
                ))
                
                conn.commit()
                
        except Exception as e:
            print(f"Failed to save integration status: {e}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        active_count = len([i for i in self.integrations.values() if i["status"] == "active"])
        total_count = len(self.integrations)
        
        return {
            "total_integrations": total_count,
            "active_integrations": active_count,
            "inactive_integrations": total_count - active_count,
            "integration_types": {
                "software": len([i for i in self.integrations.values() if i["type"] == "software"]),
                "online": len([i for i in self.integrations.values() if i["type"] == "online"]),
                "productivity": len([i for i in self.integrations.values() if i["type"] == "productivity"]),
                "entertainment": len([i for i in self.integrations.values() if i["type"] == "entertainment"]),
                "ai_service": len([i for i in self.integrations.values() if i["type"] == "ai_service"])
            },
            "integrations": self.integrations
        }
    
    def setup_browser_extension(self):
        """Setup browser extension integration"""
        print("Setting up Browser Extension Integration...")
        
        # Create browser extension manifest
        manifest = {
            "manifest_version": 3,
            "name": "JARVIS Assistant",
            "version": "1.0",
            "description": "JARVIS AI assistant for web page analysis",
            "permissions": [
                "activeTab",
                "scripting",
                "storage"
            ],
            "host_permissions": [
                "http://localhost:8000"
            ],
            "action": {
                "default_popup": "popup.html",
                "default_icon": "icon.png"
            }
        }
        
        # Save manifest
        os.makedirs("browser_extension", exist_ok=True)
        with open("browser_extension/manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Create popup HTML
        popup_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Assistant</title>
    <style>
        body { width: 300px; padding: 10px; font-family: Arial, sans-serif; }
        button { width: 100%; padding: 8px; margin: 5px 0; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        #result { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>JARVIS Assistant</h3>
    <button onclick="analyzePage()">Analyze Page</button>
    <button onclick="summarizePage()">Summarize Content</button>
    <button onclick="extractText()">Extract Text</button>
    <div id="result"></div>
    
    <script>
        async function analyzePage() {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'analyze', url: window.location.href, content: document.body.innerText })
            });
            const result = await response.json();
            document.getElementById('result').innerHTML = '<strong>Analysis:</strong><br>' + result.analysis;
        }
        
        async function summarizePage() {
            const response = await fetch('http://localhost:8000/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'summarize', url: window.location.href, content: document.body.innerText })
            });
            const result = await response.json();
            document.getElementById('result').innerHTML = '<strong>Summary:</strong><br>' + result.summary;
        }
        
        async function extractText() {
            const response = await fetch('http://localhost:8000/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'extract', url: window.location.href, content: document.body.innerText })
            });
            const result = await response.json();
            document.getElementById('result').innerHTML = '<strong>Extracted Text:</strong><br>' + result.text;
        }
    </script>
</body>
</html>
        '''
        
        with open("browser_extension/popup.html", "w") as f:
            f.write(popup_html)
        
        print("Browser extension created in 'browser_extension' directory")
        print("Load it in Chrome/Edge: chrome://extensions/ -> Load unpacked")
        print("Load it in Firefox: about:debugging -> Load Temporary Add-on")
    
    def setup_local_file_manager(self) -> bool:
        """Setup local file manager - NO API NEEDED"""
        print("Setting up Local File Manager...")
        
        try:
            config = {
                "local_path": os.path.expanduser("~/Documents"),
                "features_enabled": ["smart_organization", "quick_search", "auto_backup"]
            }
            
            return self.activate_integration("local_file_manager", config)
        except Exception as e:
            print(f"Local file manager setup failed: {e}")
            return False
    
    def setup_local_notes(self) -> bool:
        """Setup local note manager - NO API NEEDED"""
        print("Setting up Local Note Manager...")
        
        try:
            config = {
                "notes_path": "local_notes",
                "features_enabled": ["organization", "search", "categorization"]
            }
            
            return self.activate_integration("local_notes", config)
        except Exception as e:
            print(f"Local notes setup failed: {e}")
            return False
    
    def setup_local_tasks(self) -> bool:
        """Setup local task manager - NO API NEEDED"""
        print("Setting up Local Task Manager...")
        
        try:
            config = {
                "tasks_path": "local_tasks",
                "features_enabled": ["task_tracking", "reminders", "prioritization"]
            }
            
            return self.activate_integration("local_tasks", config)
        except Exception as e:
            print(f"Local tasks setup failed: {e}")
            return False
    
    def setup_system_monitor(self) -> bool:
        """Setup system monitor - NO API NEEDED"""
        print("Setting up System Monitor...")
        
        try:
            config = {
                "features_enabled": ["performance_tracking", "resource_optimization", "health_alerts"]
            }
            
            return self.activate_integration("system_monitor", config)
        except Exception as e:
            print(f"System monitor setup failed: {e}")
            return False
    
    def setup_offline_speech(self) -> bool:
        """Setup offline speech recognition - NO API NEEDED"""
        print("Setting up Offline Speech Recognition...")
        print("Note: Requires installing 'vosk' and downloading speech models")
        
        try:
            config = {
                "features_enabled": ["speech_to_text", "voice_commands", "transcription"],
                "model_path": "vosk_models"
            }
            
            return self.activate_integration("offline_speech", config)
        except Exception as e:
            print(f"Offline speech setup failed: {e}")
            return False
    
    def get_integration_recommendations(self) -> List[str]:
        """Get recommendations for integrations to setup"""
        recommendations = []
        
        # Analyze user patterns and suggest integrations
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 17:
            recommendations.append("Setup email integration for work productivity")
            recommendations.append("Configure calendar integration for schedule management")
        
        if current_hour >= 18:
            recommendations.append("Setup entertainment integrations for evening use")
            recommendations.append("Configure music library integration")
        
        # Check for file types and suggest tools
        if os.path.exists(os.path.expanduser("~/Documents")):
            recommendations.append("Setup cloud storage integration for file backup")
        
        return recommendations
    
    def activate(self):
        """Activate integrations manager"""
        self.is_active = True
        print("JARVIS Integrations Manager activated")
    
    def deactivate(self):
        """Deactivate integrations manager"""
        self.is_active = False
        print("JARVIS Integrations Manager deactivated")

# Global instance
jarvis_integrations = JarvisIntegrationsManager()
