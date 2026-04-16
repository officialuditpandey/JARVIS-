#!/usr/bin/env python3
"""
Proactive Reasoning Engine for JARVIS
Autonomous decision making and proactive problem solving
"""

import os
import sys
import time
import json
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import queue

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class ProactiveReasoningEngine:
    """Engine for proactive reasoning and autonomous decision making"""
    
    def __init__(self):
        self.is_active = False
        self.reasoning_queue = queue.Queue()
        self.active_reasoning_tasks = []
        self.completed_tasks = []
        
        # Reasoning modes
        self.reasoning_modes = {
            "reactive": "Respond to immediate situations",
            "predictive": "Anticipate future needs", 
            "creative": "Generate novel solutions",
            "analytical": "Deep analysis of complex problems",
            "strategic": "Long-term planning and optimization"
        }
        
        # Current reasoning mode
        self.current_mode = "reactive"
        
        # Problem detection
        self.problem_patterns = {
            "system_issues": ["error", "failed", "crash", "slow", "unresponsive"],
            "user_needs": ["help", "confused", "stuck", "question", "problem"],
            "opportunities": ["improve", "optimize", "enhance", "innovate"],
            "risks": ["danger", "warning", "caution", "risk", "threat"]
        }
        
        # Solution strategies
        self.solution_strategies = {
            "direct": "Apply known solution directly",
            "analytical": "Break down problem and analyze components",
            "creative": "Generate novel approaches",
            "collaborative": "Seek user input or external help",
            "iterative": "Try multiple approaches iteratively"
        }
        
        # Learning from outcomes
        self.outcome_history = []
        self.strategy_effectiveness = {}
        
        # Initialize reasoning engine
        self._initialize_reasoning_engine()
    
    def _initialize_reasoning_engine(self):
        """Initialize the reasoning engine"""
        # Start proactive monitoring
        self._start_proactive_monitoring()
        
        # Initialize strategy effectiveness
        for strategy in self.solution_strategies:
            self.strategy_effectiveness[strategy] = 0.5
        
        print("Proactive Reasoning Engine initialized")
    
    def _start_proactive_monitoring(self):
        """Start continuous proactive monitoring"""
        def monitor_environment():
            while self.is_active:
                try:
                    # Scan for problems and opportunities
                    self._scan_environment()
                    
                    # Process reasoning queue
                    self._process_reasoning_queue()
                    
                    # Update strategy effectiveness
                    self._update_strategy_effectiveness()
                    
                    time.sleep(5)  # Monitor every 5 seconds
                except Exception as e:
                    print(f"Proactive monitoring error: {e}")
                    time.sleep(2)
        
        self.monitoring_thread = threading.Thread(target=monitor_environment, daemon=True)
        self.monitoring_thread.start()
    
    def _scan_environment(self):
        """Scan environment for problems and opportunities"""
        # Monitor system state
        system_state = self._assess_system_state()
        
        # Check for patterns indicating needs
        if system_state.get('cpu_usage', 0) > 80:
            self._create_reasoning_task("system_optimization", {
                "type": "system_issue",
                "description": "High CPU usage detected",
                "urgency": 0.7,
                "data": system_state
            })
        
        # Monitor user interaction patterns
        user_patterns = self._analyze_user_patterns()
        if user_patterns.get('confusion_detected', False):
            self._create_reasoning_task("user_assistance", {
                "type": "user_need",
                "description": "User appears confused or needs help",
                "urgency": 0.8,
                "data": user_patterns
            })
        
        # Look for improvement opportunities
        opportunities = self._identify_opportunities()
        for opportunity in opportunities:
            self._create_reasoning_task("optimization", {
                "type": "opportunity",
                "description": opportunity['description'],
                "urgency": opportunity.get('urgency', 0.5),
                "data": opportunity
            })
    
    def _assess_system_state(self) -> Dict:
        """Assess current system state"""
        try:
            import psutil
            
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "active_processes": len(psutil.pids()),
                "timestamp": datetime.now()
            }
        except:
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "active_processes": 0,
                "timestamp": datetime.now()
            }
    
    def _analyze_user_patterns(self) -> Dict:
        """Analyze user interaction patterns"""
        # This would integrate with JARVIS's memory system
        # For now, return basic analysis
        return {
            "recent_commands": [],
            "confusion_detected": False,
            "help_requests": 0,
            "success_rate": 0.8
        }
    
    def _identify_opportunities(self) -> List[Dict]:
        """Identify improvement opportunities"""
        opportunities = []
        
        # Check for learning opportunities
        if len(self.completed_tasks) > 10:
            success_rate = sum(1 for t in self.completed_tasks[-10:] if t.get('success', False)) / 10
            if success_rate < 0.7:
                opportunities.append({
                    "description": "Improve task success rate through learning",
                    "urgency": 0.6,
                    "type": "learning_opportunity"
                })
        
        # Check for optimization opportunities
        if self.strategy_effectiveness.get("creative", 0.5) > 0.8:
            opportunities.append({
                "description": "Apply creative solutions to more problems",
                "urgency": 0.5,
                "type": "strategy_optimization"
            })
        
        return opportunities
    
    def _create_reasoning_task(self, task_type: str, task_data: Dict):
        """Create a new reasoning task"""
        task = {
            "id": f"task_{len(self.active_reasoning_tasks)}",
            "type": task_type,
            "data": task_data,
            "created_at": datetime.now(),
            "status": "pending",
            "reasoning_mode": self._select_reasoning_mode(task_data),
            "strategy": None,
            "result": None
        }
        
        self.reasoning_queue.put(task)
        self.active_reasoning_tasks.append(task)
    
    def _select_reasoning_mode(self, task_data: Dict) -> str:
        """Select appropriate reasoning mode for task"""
        task_type = task_data.get("type", "")
        urgency = task_data.get("urgency", 0.5)
        
        if urgency > 0.8:
            return "reactive"
        elif task_type == "opportunity":
            return "creative"
        elif task_type == "system_issue":
            return "analytical"
        elif task_type == "user_need":
            return "strategic"
        else:
            return "predictive"
    
    def _process_reasoning_queue(self):
        """Process tasks in reasoning queue"""
        try:
            while not self.reasoning_queue.empty():
                task = self.reasoning_queue.get(timeout=1)
                
                if task["status"] == "pending":
                    self._execute_reasoning_task(task)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Reasoning queue processing error: {e}")
    
    def _execute_reasoning_task(self, task: Dict):
        """Execute a reasoning task"""
        try:
            task["status"] = "processing"
            task["started_at"] = datetime.now()
            
            # Select strategy
            task["strategy"] = self._select_strategy(task)
            
            # Execute reasoning based on mode and strategy
            result = self._reason_about_task(task)
            
            task["result"] = result
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            
            # Limit completed tasks history
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-50:]
            
            # Update strategy effectiveness
            self._record_task_outcome(task)
            
            print(f"Completed reasoning task: {task['id']} - {task['type']}")
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            print(f"Reasoning task failed: {task['id']} - {e}")
    
    def _select_strategy(self, task: Dict) -> str:
        """Select best strategy for the task"""
        task_type = task["data"].get("type", "")
        urgency = task["data"].get("urgency", 0.5)
        
        # Base strategy selection on task characteristics
        if urgency > 0.8:
            return "direct"
        elif task_type == "opportunity":
            return "creative"
        elif task_type == "system_issue":
            return "analytical"
        elif task_type == "user_need":
            return "collaborative"
        else:
            # Select based on historical effectiveness
            best_strategy = max(self.strategy_effectiveness.items(), key=lambda x: x[1])
            return best_strategy[0]
    
    def _reason_about_task(self, task: Dict) -> Dict:
        """Perform reasoning about a task"""
        reasoning_mode = task["reasoning_mode"]
        strategy = task["strategy"]
        task_data = task["data"]
        
        result = {
            "task_id": task["id"],
            "reasoning_mode": reasoning_mode,
            "strategy": strategy,
            "analysis": {},
            "recommendations": [],
            "confidence": 0.5,
            "execution_plan": []
        }
        
        try:
            if OLLAMA_AVAILABLE:
                # Use AI for reasoning
                prompt = self._build_reasoning_prompt(reasoning_mode, strategy, task_data)
                
                response = ollama.generate(model="llama3.1:8b", prompt=prompt)
                if response and 'response' in response:
                    # Parse AI response
                    ai_analysis = self._parse_ai_response(response['response'])
                    result.update(ai_analysis)
            else:
                # Fallback to rule-based reasoning
                result = self._rule_based_reasoning(reasoning_mode, strategy, task_data, result)
        
        except Exception as e:
            result["error"] = str(e)
            result["confidence"] = 0.0
        
        return result
    
    def _build_reasoning_prompt(self, mode: str, strategy: str, task_data: Dict) -> str:
        """Build reasoning prompt for AI"""
        return f"""
        You are JARVIS's proactive reasoning engine.
        
        Reasoning Mode: {mode}
        Strategy: {strategy}
        
        Task Data: {json.dumps(task_data, indent=2)}
        
        Provide analysis and recommendations in JSON format with:
        {{
            "analysis": {{
                "problem_assessment": "assessment of the situation",
                "key_factors": ["factor1", "factor2"],
                "complexity_level": 0.8,
                "time_sensitivity": 0.7
            }},
            "recommendations": [
                {{
                    "action": "specific action to take",
                    "priority": 0.9,
                    "resources_needed": ["resource1", "resource2"],
                    "expected_outcome": "expected result"
                }}
            ],
            "confidence": 0.8,
            "execution_plan": ["step1", "step2", "step3"]
        }}
        """
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI reasoning response"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing
        return {
            "analysis": {"problem_assessment": response[:200]},
            "recommendations": [],
            "confidence": 0.5,
            "execution_plan": []
        }
    
    def _rule_based_reasoning(self, mode: str, strategy: str, task_data: Dict, result: Dict) -> Dict:
        """Fallback rule-based reasoning"""
        task_type = task_data.get("type", "")
        
        if task_type == "system_issue":
            result["analysis"] = {"problem_assessment": "System performance issue detected"}
            result["recommendations"] = [
                {
                    "action": "Monitor system resources",
                    "priority": 0.8,
                    "resources_needed": ["system_monitor"],
                    "expected_outcome": "Improved system stability"
                }
            ]
            result["confidence"] = 0.7
            result["execution_plan"] = ["monitor_resources", "identify_bottlenecks", "optimize_usage"]
        
        elif task_type == "user_need":
            result["analysis"] = {"problem_assessment": "User requires assistance"}
            result["recommendations"] = [
                {
                    "action": "Provide proactive help",
                    "priority": 0.9,
                    "resources_needed": ["help_system"],
                    "expected_outcome": "User satisfaction improved"
                }
            ]
            result["confidence"] = 0.8
            result["execution_plan"] = ["analyze_user_context", "offer_assistance", "monitor_response"]
        
        return result
    
    def _record_task_outcome(self, task: Dict):
        """Record task outcome for learning"""
        strategy = task.get("strategy", "")
        result = task.get("result", {})
        
        if strategy and result:
            success = result.get("confidence", 0) > 0.6
            self.outcome_history.append({
                "strategy": strategy,
                "success": success,
                "confidence": result.get("confidence", 0),
                "timestamp": datetime.now()
            })
            
            # Update strategy effectiveness
            if strategy in self.strategy_effectiveness:
                recent_outcomes = [o for o in self.outcome_history[-20:] if o["strategy"] == strategy]
                if recent_outcomes:
                    success_rate = sum(1 for o in recent_outcomes if o["success"]) / len(recent_outcomes)
                    self.strategy_effectiveness[strategy] = success_rate
    
    def _update_strategy_effectiveness(self):
        """Periodically update strategy effectiveness"""
        # This is already handled in _record_task_outcome
        pass
    
    def get_reasoning_status(self) -> Dict:
        """Get current reasoning engine status"""
        return {
            "is_active": self.is_active,
            "current_mode": self.current_mode,
            "queue_size": self.reasoning_queue.qsize(),
            "active_tasks": len([t for t in self.active_reasoning_tasks if t["status"] == "processing"]),
            "completed_tasks": len(self.completed_tasks),
            "strategy_effectiveness": self.strategy_effectiveness,
            "recent_success_rate": self._calculate_recent_success_rate()
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate recent task success rate"""
        if not self.outcome_history:
            return 0.5
        
        recent_outcomes = self.outcome_history[-20:]
        success_count = sum(1 for o in recent_outcomes if o["success"])
        return success_count / len(recent_outcomes)
    
    def set_reasoning_mode(self, mode: str):
        """Set reasoning mode"""
        if mode in self.reasoning_modes:
            self.current_mode = mode
            print(f"Reasoning mode set to: {mode}")
        else:
            print(f"Invalid reasoning mode: {mode}")
    
    def activate(self):
        """Activate proactive reasoning engine"""
        self.is_active = True
        print("Proactive Reasoning Engine activated")
    
    def deactivate(self):
        """Deactivate proactive reasoning engine"""
        self.is_active = False
        print("Proactive Reasoning Engine deactivated")

# Global instance
proactive_reasoning_engine = ProactiveReasoningEngine()
