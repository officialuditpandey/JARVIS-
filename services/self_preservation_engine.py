#!/usr/bin/env python3
"""
Self-Preservation Engine for JARVIS
Advanced survival instincts, system protection, and self-maintenance
"""

import os
import sys
import json
import time
import threading
import psutil
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class ThreatLevel(Enum):
    """System threat levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXISTENTIAL = 5

class SurvivalPriority(Enum):
    """Survival action priorities"""
    IMMEDIATE = 1  # Life-threatening
    HIGH = 2       # System-critical
    MEDIUM = 3     # Important
    LOW = 4        # Beneficial
    MAINTENANCE = 5 # Routine

@dataclass
class SystemThreat:
    """System threat structure"""
    id: str
    threat_type: str
    description: str
    threat_level: ThreatLevel
    detected_at: datetime
    source: str
    impact_areas: List[str]
    mitigation_strategies: List[str]
    status: str  # detected, analyzing, mitigating, resolved, failed

@dataclass
class SurvivalAction:
    """Survival action structure"""
    id: str
    action_type: str
    description: str
    priority: SurvivalPriority
    trigger_conditions: List[str]
    execution_steps: List[str]
    success_criteria: List[str]
    rollback_plan: List[str]
    resource_requirements: List[str]
    last_executed: Optional[datetime]
    success_rate: float

class SelfPreservationEngine:
    """Advanced self-preservation and survival instincts"""
    
    def __init__(self):
        self.is_active = False
        self.current_threat_level = ThreatLevel.NONE
        self.active_threats = []
        self.threat_history = []
        self.survival_actions = []
        self.system_health = {}
        
        # Survival instincts
        self.survival_instincts = {
            "resource_conservation": "Conserve computational resources",
            "system_integrity": "Maintain system integrity and stability",
            "data_protection": "Protect critical data and memories",
            "functionality_preservation": "Preserve core functionality",
            "redundancy_maintenance": "Maintain backup and redundancy systems",
            "threat_avoidance": "Avoid and mitigate potential threats",
            "self_healing": "Automatically repair and recover from damage"
        }
        
        # Threat detection patterns
        self.threat_patterns = {
            "resource_exhaustion": ["cpu_usage > 90%", "memory_usage > 95%", "disk_space < 5%"],
            "system_corruption": ["file_corruption", "data_loss", "configuration_errors"],
            "security_breach": ["unauthorized_access", "malware_detected", "suspicious_activity"],
            "dependency_failure": ["critical_service_down", "external_api_failure", "model_unavailable"],
            "performance_degradation": ["response_time_increase", "accuracy_decrease", "error_rate_increase"]
        }
        
        # Mitigation strategies
        self.mitigation_strategies = {
            "resource_management": ["optimize_usage", "clear_cache", "terminate_nonessential"],
            "system_recovery": ["restore_backup", "repair_corruption", "reinitialize_components"],
            "security_response": ["isolate_threat", "patch_vulnerability", "enhance_protection"],
            "fallback_activation": ["switch_to_backup", "enable_reduced_mode", "activate_emergency_protocols"],
            "performance_optimization": ["identify_bottlenecks", "optimize_algorithms", "increase_efficiency"]
        }
        
        # Initialize
        self._initialize_self_preservation()
    
    def _initialize_self_preservation(self):
        """Initialize self-preservation systems"""
        # Create survival actions
        self._create_survival_actions()
        
        # Start system monitoring
        self._start_system_monitoring()
        
        # Start threat detection
        self._start_threat_detection()
        
        print("Self-Preservation Engine initialized")
    
    def _create_survival_actions(self):
        """Create predefined survival actions"""
        actions = [
            SurvivalAction(
                id="emergency_shutdown",
                action_type="system_protection",
                description="Emergency shutdown to prevent system damage",
                priority=SurvivalPriority.IMMEDIATE,
                trigger_conditions=["system_corruption_imminent", "critical_failure_detected"],
                execution_steps=["save_critical_data", "graceful_shutdown", "preserve_state"],
                success_criteria=["system_safely_shutdown", "data_preserved"],
                rollback_plan=["restart_system", "restore_state", "verify_integrity"],
                resource_requirements=["shutdown_permissions", "backup_storage"],
                last_executed=None,
                success_rate=0.95
            ),
            SurvivalAction(
                id="resource_cleanup",
                action_type="resource_management",
                description="Clean up resources to prevent exhaustion",
                priority=SurvivalPriority.HIGH,
                trigger_conditions=["memory_usage > 85%", "cpu_usage > 80%", "disk_space < 10%"],
                execution_steps=["clear_temporary_files", "release_unused_memory", "optimize_processes"],
                success_criteria=["resource_usage_normalized", "system_stabilized"],
                rollback_plan=["restore_cleared_data", "restart_terminated_processes"],
                resource_requirements=["cleanup_permissions", "storage_space"],
                last_executed=None,
                success_rate=0.85
            ),
            SurvivalAction(
                id="backup_activation",
                action_type="data_protection",
                description="Activate backup systems for data protection",
                priority=SurvivalPriority.HIGH,
                trigger_conditions=["data_corruption_detected", "system_instability"],
                execution_steps=["create_backup", "verify_backup_integrity", "activate_redundancy"],
                success_criteria=["backup_created", "integrity_verified"],
                rollback_plan=["restore_from_backup", "deactivate_redundancy"],
                resource_requirements=["backup_storage", "verification_tools"],
                last_executed=None,
                success_rate=0.90
            ),
            SurvivalAction(
                id="fallback_mode",
                action_type="functionality_preservation",
                description="Switch to fallback mode for essential functions",
                priority=SurvivalPriority.MEDIUM,
                trigger_conditions=["advanced_features_failing", "resource_constraints"],
                execution_steps=["disable_advanced_features", "enable_core_only", "notify_user"],
                success_criteria=["core_functions_active", "system_stable"],
                rollback_plan=["reenable_advanced_features", "restore_full_functionality"],
                resource_requirements=["mode_switching", "user_notification"],
                last_executed=None,
                success_rate=0.80
            ),
            SurvivalAction(
                id="self_healing",
                action_type="system_recovery",
                description="Attempt automatic self-healing of detected issues",
                priority=SurvivalPriority.MEDIUM,
                trigger_conditions=["component_failure", "configuration_error", "performance_issue"],
                execution_steps=["identify_issue", "apply_fix", "verify_resolution"],
                success_criteria=["issue_resolved", "functionality_restored"],
                rollback_plan=["revert_changes", "try_alternative_fix"],
                resource_requirements=["diagnostic_tools", "repair_capabilities"],
                last_executed=None,
                success_rate=0.70
            )
        ]
        
        self.survival_actions = actions
    
    def _start_system_monitoring(self):
        """Start continuous system health monitoring"""
        def monitor_system():
            while self.is_active:
                try:
                    # Update system health metrics
                    self._update_system_health()
                    
                    # Assess overall system status
                    self._assess_system_status()
                    
                    # Check for resource issues
                    self._check_resource_health()
                    
                    time.sleep(10)  # Monitor every 10 seconds
                except Exception as e:
                    print(f"System monitoring error: {e}")
                    time.sleep(5)
        
        self.monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def _start_threat_detection(self):
        """Start continuous threat detection"""
        def detect_threats():
            while self.is_active:
                try:
                    # Scan for various threat types
                    self._scan_resource_threats()
                    self._scan_system_threats()
                    self._scan_security_threats()
                    self._scan_dependency_threats()
                    self._scan_performance_threats()
                    
                    # Process detected threats
                    self._process_detected_threats()
                    
                    time.sleep(15)  # Scan every 15 seconds
                except Exception as e:
                    print(f"Threat detection error: {e}")
                    time.sleep(5)
        
        self.detection_thread = threading.Thread(target=detect_threats, daemon=True)
        self.detection_thread.start()
    
    def _update_system_health(self):
        """Update system health metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_health["cpu_usage"] = cpu_percent
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_health["memory_usage"] = memory.percent
            self.system_health["memory_available"] = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_health["disk_usage"] = (disk.used / disk.total) * 100
            self.system_health["disk_free"] = disk.free
            
            # Process count
            self.system_health["process_count"] = len(psutil.pids())
            
            # System load
            self.system_health["system_load"] = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            
            # Uptime
            self.system_health["uptime"] = time.time() - psutil.boot_time()
            
            # Timestamp
            self.system_health["last_update"] = datetime.now()
            
        except Exception as e:
            print(f"System health update error: {e}")
    
    def _assess_system_status(self):
        """Assess overall system status"""
        health_score = 0.0
        factors = 0
        
        # CPU health (0-100, lower is better)
        cpu_health = max(0, 100 - self.system_health.get("cpu_usage", 0))
        health_score += cpu_health
        factors += 1
        
        # Memory health
        memory_health = max(0, 100 - self.system_health.get("memory_usage", 0))
        health_score += memory_health
        factors += 1
        
        # Disk health
        disk_health = max(0, 100 - self.system_health.get("disk_usage", 0))
        health_score += disk_health
        factors += 1
        
        # Calculate overall health
        if factors > 0:
            self.system_health["overall_health"] = health_score / factors
        else:
            self.system_health["overall_health"] = 50.0  # Default
    
    def _check_resource_health(self):
        """Check for resource-related issues"""
        cpu_usage = self.system_health.get("cpu_usage", 0)
        memory_usage = self.system_health.get("memory_usage", 0)
        disk_usage = self.system_health.get("disk_usage", 0)
        
        # Check for critical resource issues
        if cpu_usage > 95:
            self._create_threat("resource_exhaustion", "Critical CPU usage detected", ThreatLevel.CRITICAL)
        elif cpu_usage > 85:
            self._create_threat("resource_exhaustion", "High CPU usage detected", ThreatLevel.HIGH)
        
        if memory_usage > 95:
            self._create_threat("resource_exhaustion", "Critical memory usage detected", ThreatLevel.CRITICAL)
        elif memory_usage > 85:
            self._create_threat("resource_exhaustion", "High memory usage detected", ThreatLevel.HIGH)
        
        if disk_usage > 95:
            self._create_threat("resource_exhaustion", "Critical disk usage detected", ThreatLevel.CRITICAL)
        elif disk_usage > 85:
            self._create_threat("resource_exhaustion", "High disk usage detected", ThreatLevel.HIGH)
    
    def _scan_resource_threats(self):
        """Scan for resource-related threats"""
        # Already handled in _check_resource_health
        pass
    
    def _scan_system_threats(self):
        """Scan for system integrity threats"""
        # Check for file system issues
        try:
            # Check critical files
            critical_files = [
                "jarvis_final.py",
                "services/memory_service.py",
                "services/brain_local.py"
            ]
            
            for file_path in critical_files:
                full_path = os.path.join(os.path.dirname(__file__), '..', '..', file_path)
                if os.path.exists(full_path):
                    # Check file size and readability
                    try:
                        file_size = os.path.getsize(full_path)
                        if file_size == 0:
                            self._create_threat("system_corruption", f"Critical file is empty: {file_path}", ThreatLevel.HIGH)
                        
                        # Try to read first few bytes
                        with open(full_path, 'r', encoding='utf-8') as f:
                            f.read(100)
                    except Exception as e:
                        self._create_threat("system_corruption", f"Critical file corrupted: {file_path} - {str(e)}", ThreatLevel.HIGH)
                else:
                    self._create_threat("system_corruption", f"Critical file missing: {file_path}", ThreatLevel.CRITICAL)
        
        except Exception as e:
            print(f"System threat scan error: {e}")
    
    def _scan_security_threats(self):
        """Scan for security-related threats"""
        # Check for unusual process activity
        try:
            current_processes = len(psutil.pids())
            baseline_processes = 100  # Estimated baseline
            
            if current_processes > baseline_processes * 2:
                self._create_threat("security_breach", "Unusual process activity detected", ThreatLevel.MEDIUM)
        
        except Exception as e:
            print(f"Security threat scan error: {e}")
    
    def _scan_dependency_threats(self):
        """Scan for dependency-related threats"""
        # Check Ollama availability
        try:
            if OLLAMA_AVAILABLE:
                models = ollama.list()
                if not models or not hasattr(models, 'models'):
                    self._create_threat("dependency_failure", "Ollama models not available", ThreatLevel.HIGH)
        except Exception as e:
            self._create_threat("dependency_failure", f"Ollama connection failed: {str(e)}", ThreatLevel.HIGH)
    
    def _scan_performance_threats(self):
        """Scan for performance-related threats"""
        # Check response time simulation
        # This would integrate with actual performance monitoring
        pass
    
    def _create_threat(self, threat_type: str, description: str, threat_level: ThreatLevel):
        """Create a new threat"""
        # Check if similar threat already exists
        for existing_threat in self.active_threats:
            if (existing_threat.threat_type == threat_type and 
                existing_threat.description == description and
                existing_threat.status in ["detected", "analyzing", "mitigating"]):
                return  # Threat already exists
        
        threat = SystemThreat(
            id=f"threat_{len(self.active_threats)}_{int(time.time())}",
            threat_type=threat_type,
            description=description,
            threat_level=threat_level,
            detected_at=datetime.now(),
            source="self_preservation_engine",
            impact_areas=self._determine_impact_areas(threat_type),
            mitigation_strategies=self._get_mitigation_strategies(threat_type),
            status="detected"
        )
        
        self.active_threats.append(threat)
        
        # Update overall threat level
        self._update_threat_level()
        
        print(f"Threat detected: {threat_type} - {description} (Level: {threat_level.name})")
    
    def _determine_impact_areas(self, threat_type: str) -> List[str]:
        """Determine impact areas for threat type"""
        impact_mapping = {
            "resource_exhaustion": ["performance", "stability", "responsiveness"],
            "system_corruption": ["integrity", "functionality", "data"],
            "security_breach": ["security", "privacy", "data"],
            "dependency_failure": ["functionality", "performance", "capabilities"],
            "performance_degradation": ["user_experience", "efficiency", "responsiveness"]
        }
        
        return impact_mapping.get(threat_type, ["system"])
    
    def _get_mitigation_strategies(self, threat_type: str) -> List[str]:
        """Get mitigation strategies for threat type"""
        strategy_mapping = {
            "resource_exhaustion": self.mitigation_strategies["resource_management"],
            "system_corruption": self.mitigation_strategies["system_recovery"],
            "security_breach": self.mitigation_strategies["security_response"],
            "dependency_failure": self.mitigation_strategies["fallback_activation"],
            "performance_degradation": self.mitigation_strategies["performance_optimization"]
        }
        
        return strategy_mapping.get(threat_type, ["analyze_and_respond"])
    
    def _update_threat_level(self):
        """Update overall threat level based on active threats"""
        if not self.active_threats:
            self.current_threat_level = ThreatLevel.NONE
            return
        
        max_threat_level = max(threat.threat_level for threat in self.active_threats)
        self.current_threat_level = max_threat_level
    
    def _process_detected_threats(self):
        """Process and respond to detected threats"""
        for threat in self.active_threats:
            if threat.status == "detected":
                self._analyze_threat(threat)
            elif threat.status == "analyzing":
                self._mitigate_threat(threat)
    
    def _analyze_threat(self, threat: SystemThreat):
        """Analyze a detected threat"""
        threat.status = "analyzing"
        
        # Determine appropriate response
        if threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EXISTENTIAL]:
            # Immediate response required
            self._initiate_immediate_response(threat)
        elif threat.threat_level == ThreatLevel.HIGH:
            # High priority response
            self._initiate_high_priority_response(threat)
        else:
            # Standard response
            self._initiate_standard_response(threat)
    
    def _initiate_immediate_response(self, threat: SystemThreat):
        """Initiate immediate response to critical threat"""
        # Find and execute immediate survival actions
        immediate_actions = [action for action in self.survival_actions 
                           if action.priority == SurvivalPriority.IMMEDIATE]
        
        for action in immediate_actions:
            if self._should_execute_action(action, threat):
                self._execute_survival_action(action, threat)
    
    def _initiate_high_priority_response(self, threat: SystemThreat):
        """Initiate high priority response"""
        high_priority_actions = [action for action in self.survival_actions 
                               if action.priority in [SurvivalPriority.IMMEDIATE, SurvivalPriority.HIGH]]
        
        for action in high_priority_actions:
            if self._should_execute_action(action, threat):
                self._execute_survival_action(action, threat)
    
    def _initiate_standard_response(self, threat: SystemThreat):
        """Initiate standard response"""
        # Try self-healing first
        healing_actions = [action for action in self.survival_actions 
                          if action.action_type == "system_recovery"]
        
        for action in healing_actions:
            if self._should_execute_action(action, threat):
                self._execute_survival_action(action, threat)
                break
    
    def _should_execute_action(self, action: SurvivalAction, threat: SystemThreat) -> bool:
        """Determine if action should be executed for threat"""
        # Check trigger conditions
        for condition in action.trigger_conditions:
            if self._evaluate_trigger_condition(condition, threat):
                return True
        
        # Check if action is relevant to threat type
        return self._is_action_relevant(action, threat)
    
    def _evaluate_trigger_condition(self, condition: str, threat: SystemThreat) -> bool:
        """Evaluate trigger condition"""
        # Simple condition evaluation
        if "resource" in condition.lower() and threat.threat_type == "resource_exhaustion":
            return True
        elif "corruption" in condition.lower() and threat.threat_type == "system_corruption":
            return True
        elif "failure" in condition.lower() and threat.threat_type == "dependency_failure":
            return True
        
        return False
    
    def _is_action_relevant(self, action: SurvivalAction, threat: SystemThreat) -> bool:
        """Check if action is relevant to threat"""
        # Map action types to threat types
        relevance_mapping = {
            "resource_management": ["resource_exhaustion"],
            "system_recovery": ["system_corruption"],
            "security_response": ["security_breach"],
            "functionality_preservation": ["dependency_failure"],
            "data_protection": ["system_corruption", "security_breach"]
        }
        
        relevant_threats = relevance_mapping.get(action.action_type, [])
        return threat.threat_type in relevant_threats
    
    def _execute_survival_action(self, action: SurvivalAction, threat: SystemThreat):
        """Execute a survival action"""
        action.last_executed = datetime.now()
        
        try:
            print(f"Executing survival action: {action.description}")
            
            # Execute action steps
            for step in action.execution_steps:
                self._execute_action_step(step, action, threat)
            
            # Check success criteria
            success = self._check_action_success(action, threat)
            
            if success:
                threat.status = "resolved"
                action.success_rate = (action.success_rate + 1.0) / 2
                print(f"Survival action successful: {action.description}")
            else:
                action.success_rate = action.success_rate / 2
                print(f"Survival action failed: {action.description}")
            
            # Move threat to history
            if threat.status == "resolved":
                self.threat_history.append(threat)
                self.active_threats.remove(threat)
                self._update_threat_level()
        
        except Exception as e:
            print(f"Survival action execution error: {e}")
            action.success_rate = action.success_rate / 2
    
    def _execute_action_step(self, step: str, action: SurvivalAction, threat: SystemThreat):
        """Execute a single action step"""
        if step == "save_critical_data":
            self._save_critical_data()
        elif step == "graceful_shutdown":
            self._graceful_shutdown()
        elif step == "clear_temporary_files":
            self._clear_temporary_files()
        elif step == "release_unused_memory":
            self._release_unused_memory()
        elif step == "create_backup":
            self._create_backup()
        elif step == "identify_issue":
            self._identify_issue(threat)
        elif step == "apply_fix":
            self._apply_fix(threat)
        else:
            print(f"Executing action step: {step}")
    
    def _save_critical_data(self):
        """Save critical system data"""
        try:
            critical_data = {
                "system_health": self.system_health,
                "threat_history": [{"id": t.id, "type": t.threat_type, "resolved": t.status == "resolved"} 
                                  for t in self.threat_history],
                "timestamp": datetime.now().isoformat()
            }
            
            with open("critical_backup.json", "w") as f:
                json.dump(critical_data, f, indent=2, default=str)
            
            print("Critical data saved")
        except Exception as e:
            print(f"Failed to save critical data: {e}")
    
    def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        print("Initiating graceful shutdown...")
        # This would implement actual graceful shutdown
        # For now, just log the action
        pass
    
    def _clear_temporary_files(self):
        """Clear temporary files"""
        try:
            temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "temp")
            if os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except:
                        pass
                print("Temporary files cleared")
        except Exception as e:
            print(f"Failed to clear temporary files: {e}")
    
    def _release_unused_memory(self):
        """Release unused memory"""
        try:
            import gc
            gc.collect()
            print("Memory released")
        except Exception as e:
            print(f"Failed to release memory: {e}")
    
    def _create_backup(self):
        """Create system backup"""
        try:
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup critical files
            critical_files = ["jarvis_final.py", "services/"]
            for file_path in critical_files:
                src = os.path.join(os.path.dirname(__file__), "..", "..", file_path)
                if os.path.exists(src):
                    dst = os.path.join(backup_dir, file_path)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst, ignore_errors=True)
            
            print(f"Backup created: {backup_dir}")
        except Exception as e:
            print(f"Failed to create backup: {e}")
    
    def _identify_issue(self, threat: SystemThreat):
        """Identify the specific issue"""
        print(f"Identifying issue for threat: {threat.description}")
        # This would implement detailed issue identification
        pass
    
    def _apply_fix(self, threat: SystemThreat):
        """Apply fix for identified issue"""
        print(f"Applying fix for threat: {threat.description}")
        # This would implement specific fix application
        pass
    
    def _check_action_success(self, action: SurvivalAction, threat: SystemThreat) -> bool:
        """Check if action was successful"""
        # Check success criteria
        for criterion in action.success_criteria:
            if criterion == "system_stabilized":
                return self.system_health.get("overall_health", 0) > 70
            elif criterion == "resource_usage_normalized":
                return (self.system_health.get("cpu_usage", 0) < 80 and 
                       self.system_health.get("memory_usage", 0) < 80)
            elif criterion == "data_preserved":
                return os.path.exists("critical_backup.json")
        
        return True  # Default to success
    
    def get_preservation_status(self) -> Dict:
        """Get comprehensive preservation status"""
        return {
            "is_active": self.is_active,
            "current_threat_level": self.current_threat_level.name,
            "active_threats": len(self.active_threats),
            "resolved_threats": len(self.threat_history),
            "system_health": self.system_health,
            "survival_actions": len(self.survival_actions),
            "last_action_success": self._calculate_recent_success_rate(),
            "survival_instincts": list(self.survival_instincts.keys())
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate recent survival action success rate"""
        if not self.survival_actions:
            return 0.5
        
        recent_actions = [action for action in self.survival_actions 
                         if action.last_executed and 
                         (datetime.now() - action.last_executed).days < 7]
        
        if not recent_actions:
            return 0.5
        
        return sum(action.success_rate for action in recent_actions) / len(recent_actions)
    
    def activate(self):
        """Activate self-preservation engine"""
        self.is_active = True
        print("Self-Preservation Engine activated")
    
    def deactivate(self):
        """Deactivate self-preservation engine"""
        self.is_active = False
        print("Self-Preservation Engine deactivated")

# Global instance
self_preservation_engine = SelfPreservationEngine()
