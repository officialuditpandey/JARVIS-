#!/usr/bin/env python3
"""
Autonomous Documentation Service for JARVIS
Automatically updates SYSTEM_LOG.md with every new feature and health status
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import subprocess

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class AutonomousDocumentationService:
    """Autonomous documentation service for system logging"""
    
    def __init__(self):
        self.system_log_file = "SYSTEM_LOG.md"
        self.feature_registry_file = "docs/feature_registry.json"
        self.health_log_file = "docs/health_log.json"
        
        # Documentation state
        self.is_active = False
        self.documentation_thread = None
        self.stop_event = threading.Event()
        
        # Feature tracking
        self.feature_registry = {}
        self.feature_health = {}
        self.last_update_time = 0
        self.update_interval = 300  # Update every 5 minutes
        
        # System metrics
        self.system_metrics = {
            'total_features': 0,
            'healthy_features': 0,
            'unhealthy_features': 0,
            'last_health_check': None,
            'system_uptime': 0
        }
        
        # Initialize
        self._initialize_documentation()
        
        print("Autonomous Documentation Service initialized")
    
    def _initialize_documentation(self):
        """Initialize documentation system"""
        try:
            # Create docs directory
            os.makedirs("docs", exist_ok=True)
            
            # Load feature registry
            self._load_feature_registry()
            
            # Load health log
            self._load_health_log()
            
            # Initialize SYSTEM_LOG.md if it doesn't exist
            if not os.path.exists(self.system_log_file):
                self._create_initial_system_log()
            
        except Exception as e:
            print(f"Documentation initialization failed: {e}")
    
    def _load_feature_registry(self):
        """Load feature registry from file"""
        try:
            if os.path.exists(self.feature_registry_file):
                with open(self.feature_registry_file, 'r') as f:
                    self.feature_registry = json.load(f)
                print(f"Loaded {len(self.feature_registry)} features from registry")
            else:
                self.feature_registry = {}
                self._save_feature_registry()
                
        except Exception as e:
            print(f"Failed to load feature registry: {e}")
            self.feature_registry = {}
    
    def _save_feature_registry(self):
        """Save feature registry to file"""
        try:
            data = {
                'features': self.feature_registry,
                'last_updated': datetime.now().isoformat(),
                'total_features': len(self.feature_registry)
            }
            
            with open(self.feature_registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save feature registry: {e}")
    
    def _load_health_log(self):
        """Load health log from file"""
        try:
            if os.path.exists(self.health_log_file):
                with open(self.health_log_file, 'r') as f:
                    data = json.load(f)
                    self.feature_health = data.get('feature_health', {})
                print(f"Loaded health data for {len(self.feature_health)} features")
            else:
                self.feature_health = {}
                self._save_health_log()
                
        except Exception as e:
            print(f"Failed to load health log: {e}")
            self.feature_health = {}
    
    def _save_health_log(self):
        """Save health log to file"""
        try:
            data = {
                'feature_health': self.feature_health,
                'last_updated': datetime.now().isoformat(),
                'system_metrics': self.system_metrics
            }
            
            with open(self.health_log_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save health log: {e}")
    
    def _create_initial_system_log(self):
        """Create initial SYSTEM_LOG.md"""
        try:
            initial_content = """# JARVIS OMNI-UPGRADE SYSTEM LOG

## System Overview
**Last Updated**: {timestamp}
**Version**: 1.0.0
**Status**: Initializing

## Feature Registry
*Features will be automatically documented here*

## Health Status
*System health will be automatically monitored here*

## Recent Changes
*Changes will be automatically logged here*

---
*This log is automatically maintained by JARVIS Autonomous Documentation Service*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            with open(self.system_log_file, 'w') as f:
                f.write(initial_content)
                
            print("Initial SYSTEM_LOG.md created")
            
        except Exception as e:
            print(f"Failed to create initial system log: {e}")
    
    def register_feature(self, feature_id: str, feature_name: str, description: str, 
                        category: str, version: str = "1.0.0") -> bool:
        """Register a new feature in the system"""
        try:
            feature_data = {
                'id': feature_id,
                'name': feature_name,
                'description': description,
                'category': category,
                'version': version,
                'registered_at': datetime.now().isoformat(),
                'status': 'active',
                'health': 'unknown'
            }
            
            self.feature_registry[feature_id] = feature_data
            self._save_feature_registry()
            
            # Update system log
            self._update_system_log('feature_registered', feature_data)
            
            print(f"Feature registered: {feature_name} ({feature_id})")
            return True
            
        except Exception as e:
            print(f"Feature registration failed: {e}")
            return False
    
    def update_feature_health(self, feature_id: str, health_status: str, 
                            metrics: Dict[str, Any] = None) -> bool:
        """Update health status for a feature"""
        try:
            if feature_id not in self.feature_registry:
                print(f"Feature {feature_id} not found in registry")
                return False
            
            health_data = {
                'status': health_status,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics or {}
            }
            
            self.feature_health[feature_id] = health_data
            self._save_health_log()
            
            # Update system log if health changed significantly
            if health_status in ['critical', 'error', 'failed']:
                self._update_system_log('health_alert', {
                    'feature_id': feature_id,
                    'health_status': health_status,
                    'metrics': metrics
                })
            
            print(f"Health updated for {feature_id}: {health_status}")
            return True
            
        except Exception as e:
            print(f"Health update failed: {e}")
            return False
    
    def start_automatic_documentation(self):
        """Start automatic documentation updates"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start documentation thread
            self.documentation_thread = threading.Thread(target=self._documentation_loop, daemon=True)
            self.documentation_thread.start()
            
            print("Automatic documentation started")
            return True
            
        except Exception as e:
            print(f"Failed to start automatic documentation: {e}")
            return False
    
    def stop_automatic_documentation(self):
        """Stop automatic documentation updates"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.documentation_thread and self.documentation_thread.is_alive():
                self.documentation_thread.join(timeout=2)
            
            print("Automatic documentation stopped")
            
        except Exception as e:
            print(f"Failed to stop automatic documentation: {e}")
    
    def _documentation_loop(self):
        """Main documentation loop"""
        print("Documentation loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                current_time = time.time()
                
                # Update system log periodically
                if current_time - self.last_update_time > self.update_interval:
                    self._update_system_log('periodic_update')
                    self.last_update_time = current_time
                
                # Check system health
                self._check_system_health()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Documentation loop error: {e}")
                time.sleep(60)
        
        print("Documentation loop ended")
    
    def _check_system_health(self):
        """Check overall system health"""
        try:
            # Count features by health status
            healthy = sum(1 for h in self.feature_health.values() if h['status'] in ['healthy', 'good'])
            unhealthy = sum(1 for h in self.feature_health.values() if h['status'] in ['unhealthy', 'error', 'critical'])
            
            self.system_metrics.update({
                'total_features': len(self.feature_registry),
                'healthy_features': healthy,
                'unhealthy_features': unhealthy,
                'last_health_check': datetime.now().isoformat()
            })
            
            # Update system log if there are issues
            if unhealthy > 0:
                self._update_system_log('health_summary', self.system_metrics)
                
        except Exception as e:
            print(f"System health check failed: {e}")
    
    def _update_system_log(self, update_type: str, data: Dict[str, Any] = None):
        """Update SYSTEM_LOG.md with new information"""
        try:
            # Read current content
            with open(self.system_log_file, 'r') as f:
                content = f.read()
            
            # Generate new content based on update type
            if update_type == 'feature_registered':
                feature_data = data
                new_entry = f"""
### {feature_data['name']} (#{feature_data['id']})
- **Category**: {feature_data['category']}
- **Version**: {feature_data['version']}
- **Description**: {feature_data['description']}
- **Status**: {feature_data['status']}
- **Registered**: {feature_data['registered_at']}
"""
                
                # Add to feature registry section
                if "## Feature Registry" in content:
                    content = content.replace("## Feature Registry", f"## Feature Registry{new_entry}")
            
            elif update_type == 'health_alert':
                alert_data = data
                new_entry = f"""
### Health Alert - {alert_data['feature_id']}
- **Status**: {alert_data['health_status']}
- **Timestamp**: {datetime.now().isoformat()}
- **Metrics**: {json.dumps(alert_data.get('metrics', {}), indent=2)}
"""
                
                # Add to health status section
                if "## Health Status" in content:
                    content = content.replace("## Health Status", f"## Health Status{new_entry}")
            
            elif update_type == 'periodic_update' or update_type == 'health_summary':
                # Update system overview and health status
                self._update_system_overview(content)
                self._update_health_status(content)
                self._update_recent_changes(content, update_type)
            
            # Update timestamp
            content = content.replace(
                f"**Last Updated**:",
                f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Write updated content
            with open(self.system_log_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"System log update failed: {e}")
    
    def _update_system_overview(self, content: str):
        """Update system overview section"""
        try:
            overview_section = f"""
## System Overview
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version**: 1.0.0
**Status**: {'Healthy' if self.system_metrics['unhealthy_features'] == 0 else 'Attention Required'}
**Total Features**: {self.system_metrics['total_features']}
**Healthy Features**: {self.system_metrics['healthy_features']}
**Unhealthy Features**: {self.system_metrics['unhealthy_features']}
**Last Health Check**: {self.system_metrics.get('last_health_check', 'Never')}
"""
            
            # Replace system overview
            start_marker = "## System Overview"
            end_marker = "## Feature Registry"
            
            if start_marker in content and end_marker in content:
                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker)
                
                new_content = content[:start_idx] + overview_section + content[end_idx:]
                return new_content
                
        except Exception as e:
            print(f"System overview update failed: {e}")
        
        return content
    
    def _update_health_status(self, content: str):
        """Update health status section"""
        try:
            health_section = "\n## Health Status\n"
            
            # Add feature health summary
            for feature_id, health_data in self.feature_health.items():
                if feature_id in self.feature_registry:
                    feature_name = self.feature_registry[feature_id]['name']
                    status = health_data['status']
                    timestamp = health_data['timestamp']
                    metrics = health_data.get('metrics', {})
                    
                    health_section += f"""
### {feature_name}
- **Status**: {status}
- **Last Check**: {timestamp}
- **Metrics**: {json.dumps(metrics, indent=2)}
"""
            
            # Replace health status section
            start_marker = "## Health Status"
            end_marker = "## Recent Changes"
            
            if start_marker in content and end_marker in content:
                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker)
                
                new_content = content[:start_idx] + health_section + "\n" + content[end_idx:]
                return new_content
                
        except Exception as e:
            print(f"Health status update failed: {e}")
        
        return content
    
    def _update_recent_changes(self, content: str, update_type: str):
        """Update recent changes section"""
        try:
            changes_section = f"""
## Recent Changes
- **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**: {update_type.replace('_', ' ').title()}
- Total Features: {self.system_metrics['total_features']}
- Healthy Features: {self.system_metrics['healthy_features']}
- Unhealthy Features: {self.system_metrics['unhealthy_features']}
"""
            
            # Replace recent changes
            start_marker = "## Recent Changes"
            end_marker = "---"
            
            if start_marker in content and end_marker in content:
                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker)
                
                new_content = content[:start_idx] + changes_section + "\n" + content[end_idx:]
                return new_content
                
        except Exception as e:
            print(f"Recent changes update failed: {e}")
        
        return content
    
    def generate_feature_report(self, feature_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive feature report"""
        try:
            if feature_id:
                # Generate report for specific feature
                if feature_id not in self.feature_registry:
                    return {"error": f"Feature {feature_id} not found"}
                
                feature_data = self.feature_registry[feature_id]
                health_data = self.feature_health.get(feature_id, {})
                
                return {
                    'feature': feature_data,
                    'health': health_data,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                # Generate system-wide report
                return {
                    'system_metrics': self.system_metrics,
                    'feature_registry': self.feature_registry,
                    'feature_health': self.feature_health,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_documentation_status(self) -> Dict[str, Any]:
        """Get documentation service status"""
        return {
            'is_active': self.is_active,
            'system_log_file': self.system_log_file,
            'feature_registry_file': self.feature_registry_file,
            'health_log_file': self.health_log_file,
            'total_features': len(self.feature_registry),
            'tracked_health': len(self.feature_health),
            'last_update': datetime.fromtimestamp(self.last_update_time).isoformat() if self.last_update_time > 0 else None,
            'update_interval': self.update_interval,
            'system_metrics': self.system_metrics
        }
