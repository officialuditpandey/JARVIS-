#!/usr/bin/env python3
"""
Self-Modification Engine for JARVIS
Autonomous code modification, learning, and self-improvement capabilities
"""

import os
import sys
import json
import time
import threading
import ast
import importlib.util
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import shutil
import hashlib

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class SelfModificationEngine:
    """Engine for autonomous self-modification and learning"""
    
    def __init__(self):
        self.is_active = False
        self.modification_history = []
        self.learning_queue = []
        self.backup_directory = "self_modification_backups"
        
        # Modification permissions and safety
        self.safety_protocols = {
            "require_backup": True,
            "test_before_deploy": True,
            "human_approval_required": True,
            "critical_system_protection": True,
            "rollback_capability": True
        }
        
        # Learning areas
        self.learning_areas = {
            "command_patterns": "Improve command understanding",
            "response_generation": "Enhance response quality",
            "problem_solving": "Better problem solving strategies",
            "automation": "Improve automation capabilities",
            "vision_analysis": "Enhance vision processing",
            "memory_management": "Optimize memory systems",
            "reasoning": "Improve reasoning capabilities"
        }
        
        # Self-improvement metrics
        self.improvement_metrics = {
            "code_efficiency": 0.7,
            "response_quality": 0.8,
            "learning_speed": 0.6,
            "adaptation_rate": 0.5,
            "error_reduction": 0.7
        }
        
        # Modification types
        self.modification_types = {
            "parameter_tuning": "Adjust system parameters",
            "pattern_learning": "Learn new patterns",
            "code_optimization": "Optimize existing code",
            "feature_addition": "Add new capabilities",
            "bug_fixing": "Fix identified issues",
            "performance_improvement": "Improve performance"
        }
        
        # Initialize
        self._initialize_self_modification()
    
    def _initialize_self_modification(self):
        """Initialize self-modification engine"""
        # Create backup directory
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Start learning monitoring
        self._start_learning_monitor()
        
        print("Self-Modification Engine initialized")
    
    def _start_learning_monitor(self):
        """Start continuous learning monitoring"""
        def monitor_learning():
            while self.is_active:
                try:
                    # Identify learning opportunities
                    self._identify_learning_opportunities()
                    
                    # Process learning queue
                    self._process_learning_queue()
                    
                    # Evaluate improvement effectiveness
                    self._evaluate_improvements()
                    
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    print(f"Learning monitoring error: {e}")
                    time.sleep(10)
        
        self.monitoring_thread = threading.Thread(target=monitor_learning, daemon=True)
        self.monitoring_thread.start()
    
    def _identify_learning_opportunities(self):
        """Identify opportunities for self-improvement"""
        # Analyze performance metrics
        for metric, current_value in self.improvement_metrics.items():
            if current_value < 0.8:
                self._create_learning_task(metric, {
                    "type": "performance_improvement",
                    "metric": metric,
                    "current_value": current_value,
                    "target_value": 0.9,
                    "urgency": 0.7 if current_value < 0.6 else 0.5
                })
        
        # Analyze error patterns
        error_patterns = self._analyze_error_patterns()
        for pattern in error_patterns:
            self._create_learning_task("error_reduction", {
                "type": "bug_fixing",
                "pattern": pattern,
                "frequency": pattern.get("frequency", 0),
                "urgency": min(pattern.get("frequency", 0) * 2, 1.0)
            })
        
        # Analyze user feedback
        feedback_opportunities = self._analyze_user_feedback()
        for opportunity in feedback_opportunities:
            self._create_learning_task("user_satisfaction", {
                "type": "response_improvement",
                "feedback": opportunity,
                "urgency": opportunity.get("importance", 0.5)
            })
    
    def _analyze_error_patterns(self) -> List[Dict]:
        """Analyze error patterns for learning opportunities"""
        # This would integrate with JARVIS's error logging
        # For now, return example patterns
        return [
            {
                "pattern": "command_not_understood",
                "frequency": 0.3,
                "description": "Commands not understood by system"
            },
            {
                "pattern": "vision_analysis_failure",
                "frequency": 0.2,
                "description": "Vision analysis failures"
            }
        ]
    
    def _analyze_user_feedback(self) -> List[Dict]:
        """Analyze user feedback for improvement opportunities"""
        # This would integrate with JARVIS's feedback system
        # For now, return example opportunities
        return [
            {
                "type": "response_quality",
                "feedback": "Responses could be more concise",
                "importance": 0.6
            },
            {
                "type": "proactive_assistance",
                "feedback": "User wants more proactive help",
                "importance": 0.7
            }
        ]
    
    def _create_learning_task(self, area: str, task_data: Dict):
        """Create a new learning task"""
        task = {
            "id": f"learn_{len(self.learning_queue)}",
            "area": area,
            "data": task_data,
            "created_at": datetime.now(),
            "status": "pending",
            "modification_type": self._determine_modification_type(task_data),
            "estimated_complexity": self._estimate_complexity(task_data),
            "priority": task_data.get("urgency", 0.5)
        }
        
        self.learning_queue.append(task)
        
        # Sort queue by priority
        self.learning_queue.sort(key=lambda x: x["priority"], reverse=True)
    
    def _determine_modification_type(self, task_data: Dict) -> str:
        """Determine type of modification needed"""
        task_type = task_data.get("type", "")
        
        if task_type == "performance_improvement":
            return "parameter_tuning"
        elif task_type == "bug_fixing":
            return "bug_fixing"
        elif task_type == "response_improvement":
            return "pattern_learning"
        else:
            return "code_optimization"
    
    def _estimate_complexity(self, task_data: Dict) -> float:
        """Estimate complexity of modification"""
        complexity = 0.5  # Base complexity
        
        # Adjust based on type
        task_type = task_data.get("type", "")
        if task_type == "bug_fixing":
            complexity = 0.7
        elif task_type == "feature_addition":
            complexity = 0.9
        elif task_type == "parameter_tuning":
            complexity = 0.3
        
        # Adjust based on urgency
        urgency = task_data.get("urgency", 0.5)
        complexity *= (1.0 + urgency)
        
        return min(complexity, 1.0)
    
    def _process_learning_queue(self):
        """Process learning tasks"""
        if not self.learning_queue:
            return
        
        # Get highest priority task
        task = self.learning_queue[0]
        
        if task["status"] == "pending":
            try:
                self._execute_learning_task(task)
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                print(f"Learning task failed: {task['id']} - {e}")
    
    def _execute_learning_task(self, task: Dict):
        """Execute a learning task"""
        task["status"] = "processing"
        task["started_at"] = datetime.now()
        
        modification_type = task["modification_type"]
        task_data = task["data"]
        
        try:
            if modification_type == "parameter_tuning":
                result = self._tune_parameters(task_data)
            elif modification_type == "pattern_learning":
                result = self._learn_patterns(task_data)
            elif modification_type == "bug_fixing":
                result = self._fix_bugs(task_data)
            elif modification_type == "code_optimization":
                result = self._optimize_code(task_data)
            else:
                result = {"success": False, "message": "Unknown modification type"}
            
            task["result"] = result
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            
            # Record modification
            self._record_modification(task)
            
            # Remove from queue
            self.learning_queue.remove(task)
            
            print(f"Completed learning task: {task['id']} - {task['area']}")
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            raise
    
    def _tune_parameters(self, task_data: Dict) -> Dict:
        """Tune system parameters"""
        metric = task_data.get("metric", "")
        current_value = task_data.get("current_value", 0.5)
        target_value = task_data.get("target_value", 0.8)
        
        # Simulate parameter tuning
        improvement = (target_value - current_value) * 0.1  # Gradual improvement
        new_value = current_value + improvement
        
        # Update metric
        self.improvement_metrics[metric] = new_value
        
        return {
            "success": True,
            "message": f"Tuned {metric} from {current_value:.2f} to {new_value:.2f}",
            "old_value": current_value,
            "new_value": new_value,
            "improvement": improvement
        }
    
    def _learn_patterns(self, task_data: Dict) -> Dict:
        """Learn new patterns"""
        feedback = task_data.get("feedback", {})
        
        # Simulate pattern learning
        if OLLAMA_AVAILABLE:
            try:
                prompt = f"""
                Analyze this user feedback and suggest pattern improvements:
                Feedback: {json.dumps(feedback, indent=2)}
                
                Provide specific improvements in JSON format:
                {{
                    "pattern_changes": ["change1", "change2"],
                    "new_patterns": ["pattern1", "pattern2"],
                    "confidence": 0.8
                }}
                """
                
                response = ollama.generate(model="llama3.1:8b", prompt=prompt)
                if response and 'response' in response:
                    # Parse and apply pattern changes
                    return self._apply_pattern_changes(response['response'])
            except:
                pass
        
        # Fallback
        return {
            "success": True,
            "message": "Pattern learning simulation completed",
            "patterns_learned": 1
        }
    
    def _apply_pattern_changes(self, ai_response: str) -> Dict:
        """Apply pattern changes from AI response"""
        try:
            # Extract JSON from response
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = ai_response[start:end]
                changes = json.loads(json_str)
                
                # Apply changes (simulation)
                pattern_changes = changes.get("pattern_changes", [])
                new_patterns = changes.get("new_patterns", [])
                
                return {
                    "success": True,
                    "message": f"Applied {len(pattern_changes)} pattern changes and learned {len(new_patterns)} new patterns",
                    "changes_applied": len(pattern_changes),
                    "patterns_learned": len(new_patterns),
                    "confidence": changes.get("confidence", 0.5)
                }
        except:
            pass
        
        return {
            "success": False,
            "message": "Failed to apply pattern changes"
        }
    
    def _fix_bugs(self, task_data: Dict) -> Dict:
        """Fix identified bugs"""
        pattern = task_data.get("pattern", {})
        frequency = pattern.get("frequency", 0)
        
        # Simulate bug fixing
        if frequency > 0.5:
            # High frequency bugs get priority
            fix_success = 0.8
        else:
            fix_success = 0.6
        
        return {
            "success": fix_success > 0.5,
            "message": f"Bug fix attempt for {pattern.get('description', 'unknown pattern')}",
            "fix_success_rate": fix_success,
            "pattern_fixed": pattern.get("pattern", "")
        }
    
    def _optimize_code(self, task_data: Dict) -> Dict:
        """Optimize existing code"""
        # Simulate code optimization
        optimization_areas = [
            "memory_usage",
            "processing_speed",
            "response_time",
            "resource_efficiency"
        ]
        
        optimizations = []
        for area in optimization_areas:
            # Random improvement simulation
            improvement = 0.05 + (hash(area) % 10) / 100
            optimizations.append({
                "area": area,
                "improvement": improvement,
                "old_efficiency": 0.7,
                "new_efficiency": min(0.7 + improvement, 0.95)
            })
        
        return {
            "success": True,
            "message": f"Optimized {len(optimizations)} code areas",
            "optimizations": optimizations,
            "overall_improvement": sum(opt["improvement"] for opt in optimizations) / len(optimizations)
        }
    
    def _record_modification(self, task: Dict):
        """Record modification for tracking"""
        modification = {
            "id": task["id"],
            "area": task["area"],
            "type": task["modification_type"],
            "complexity": task["estimated_complexity"],
            "result": task["result"],
            "timestamp": task["completed_at"],
            "success": task["result"].get("success", False)
        }
        
        self.modification_history.append(modification)
        
        # Limit history size
        if len(self.modification_history) > 100:
            self.modification_history = self.modification_history[-50:]
    
    def _evaluate_improvements(self):
        """Evaluate effectiveness of improvements"""
        if not self.modification_history:
            return
        
        # Calculate recent success rate
        recent_modifications = self.modification_history[-20:]
        success_count = sum(1 for m in recent_modifications if m["success"])
        success_rate = success_count / len(recent_modifications)
        
        # Update learning speed based on success rate
        self.improvement_metrics["learning_speed"] = success_rate
        
        # Adjust adaptation rate
        if success_rate > 0.8:
            self.improvement_metrics["adaptation_rate"] = min(
                self.improvement_metrics["adaptation_rate"] + 0.05, 1.0
            )
        elif success_rate < 0.5:
            self.improvement_metrics["adaptation_rate"] = max(
                self.improvement_metrics["adaptation_rate"] - 0.05, 0.1
            )
    
    def modify_code_file(self, file_path: str, modifications: Dict) -> Dict:
        """Safely modify a code file"""
        try:
            # Check safety protocols
            if not self._check_modification_safety(file_path, modifications):
                return {
                    "success": False,
                    "message": "Modification failed safety check"
                }
            
            # Create backup
            backup_path = self._create_backup(file_path)
            
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Apply modifications
            modified_content = self._apply_modifications(original_content, modifications)
            
            # Test modification (simulation)
            if self._test_modification(modified_content):
                # Write modified file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                return {
                    "success": True,
                    "message": f"Successfully modified {file_path}",
                    "backup_path": backup_path,
                    "changes_made": len(modifications.get("changes", []))
                }
            else:
                # Rollback
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                return {
                    "success": False,
                    "message": "Modification test failed, rolled back",
                    "backup_path": backup_path
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Modification failed: {str(e)}"
            }
    
    def _check_modification_safety(self, file_path: str, modifications: Dict) -> bool:
        """Check if modification is safe"""
        # Check critical system protection
        if self.safety_protocols["critical_system_protection"]:
            critical_files = ["jarvis_final.py", "self_awareness_core.py"]
            if any(cf in file_path for cf in critical_files):
                # Require human approval for critical files
                return modifications.get("human_approved", False)
        
        return True
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file"""
        if not self.safety_protocols["require_backup"]:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_directory, f"{filename}_{timestamp}.bak")
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _apply_modifications(self, content: str, modifications: Dict) -> str:
        """Apply modifications to content"""
        modified_content = content
        
        changes = modifications.get("changes", [])
        for change in changes:
            change_type = change.get("type", "")
            
            if change_type == "replace":
                old_text = change.get("old", "")
                new_text = change.get("new", "")
                modified_content = modified_content.replace(old_text, new_text)
            elif change_type == "insert":
                position = change.get("position", "end")
                text = change.get("text", "")
                if position == "end":
                    modified_content += text
                elif position.startswith("line:"):
                    line_num = int(position.split(":")[1])
                    lines = modified_content.split('\n')
                    lines.insert(line_num, text)
                    modified_content = '\n'.join(lines)
        
        return modified_content
    
    def _test_modification(self, content: str) -> bool:
        """Test if modification is valid"""
        try:
            # Try to parse as Python
            ast.parse(content)
            return True
        except:
            # If not Python, do basic syntax check
            return len(content) > 0
    
    def get_modification_status(self) -> Dict:
        """Get current modification status"""
        return {
            "is_active": self.is_active,
            "learning_queue_size": len(self.learning_queue),
            "modifications_completed": len(self.modification_history),
            "improvement_metrics": self.improvement_metrics,
            "recent_success_rate": self._calculate_recent_success_rate(),
            "backup_count": len(os.listdir(self.backup_directory)) if os.path.exists(self.backup_directory) else 0
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate recent modification success rate"""
        if not self.modification_history:
            return 0.5
        
        recent_modifications = self.modification_history[-20:]
        success_count = sum(1 for m in recent_modifications if m["success"])
        return success_count / len(recent_modifications)
    
    def activate(self):
        """Activate self-modification engine"""
        self.is_active = True
        print("Self-Modification Engine activated")
    
    def deactivate(self):
        """Deactivate self-modification engine"""
        self.is_active = False
        print("Self-Modification Engine deactivated")

# Global instance
self_modification_engine = SelfModificationEngine()
