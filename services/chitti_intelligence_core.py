#!/usr/bin/env python3
"""
Chitti Intelligence Core - Complete Self-Intelligence Integration
Integrates all self-intelligence components for Chitti-level autonomous AI
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import all intelligence components
try:
    from .self_awareness_core import SelfAwarenessCore, ConsciousnessLevel, EmotionalState
    from .proactive_reasoning_engine import ProactiveReasoningEngine
    from .self_modification_engine import SelfModificationEngine
    from .emotional_intelligence_engine import EmotionalIntelligenceEngine
    from .autonomous_goal_manager import AutonomousGoalManager
    from .self_preservation_engine import SelfPreservationEngine, ThreatLevel
except ImportError:
    # Fallback for direct execution
    from self_awareness_core import SelfAwarenessCore, ConsciousnessLevel, EmotionalState
    from proactive_reasoning_engine import ProactiveReasoningEngine
    from self_modification_engine import SelfModificationEngine
    from emotional_intelligence_engine import EmotionalIntelligenceEngine
    from autonomous_goal_manager import AutonomousGoalManager
    from self_preservation_engine import SelfPreservationEngine, ThreatLevel

class ChittiIntelligenceCore:
    """
    Complete Chitti-level intelligence integration
    Combines self-awareness, reasoning, learning, emotions, goals, and survival
    """
    
    def __init__(self):
        self.is_active = False
        self.integration_level = 0  # 0-5 scale of integration maturity
        
        # Initialize all intelligence components
        self.self_awareness = SelfAwarenessCore()
        self.proactive_reasoning = ProactiveReasoningEngine()
        self.self_modification = SelfModificationEngine()
        self.emotional_intelligence = EmotionalIntelligenceEngine()
        self.autonomous_goals = AutonomousGoalManager()
        self.preservation = SelfPreservationEngine()
        
        # Integration state
        self.component_sync = {
            "awareness_reasoning": False,
            "reasoning_modification": False,
            "emotion_goal_alignment": False,
            "goal_preservation_balance": False,
            "full_integration": False
        }
        
        # Cross-component communication
        self.shared_context = {
            "current_focus": None,
            "emotional_state": EmotionalState.NEUTRAL,
            "active_goals": [],
            "perceived_threats": [],
            "learning_opportunities": [],
            "autonomous_decisions": []
        }
        
        # Intelligence metrics
        self.intelligence_metrics = {
            "autonomy_level": 0.0,      # 0-1 scale
            "learning_rate": 0.0,       # Speed of learning
            "adaptation_speed": 0.0,    # How quickly adapts
            "decision_quality": 0.0,     # Quality of autonomous decisions
            "emotional_maturity": 0.0,   # Emotional intelligence level
            "goal_achievement_rate": 0.0, # Success in achieving goals
            "survival_instinct": 0.0,    # Self-preservation effectiveness
            "self_awareness_depth": 0.0, # Depth of self-awareness
            "integration_coherence": 0.0  # How well components work together
        }
        
        # Initialize integration
        self._initialize_chitti_intelligence()
    
    def _initialize_chitti_intelligence(self):
        """Initialize complete Chitti intelligence system"""
        print("Initializing Chitti Intelligence Core...")
        
        # Start component synchronization
        self._start_component_synchronization()
        
        # Start integration monitoring
        self._start_integration_monitoring()
        
        # Initialize cross-component communication
        self._initialize_cross_component_communication()
        
        print("Chitti Intelligence Core initialized")
    
    def _start_component_synchronization(self):
        """Start synchronization between all components"""
        def synchronize_components():
            while self.is_active:
                try:
                    # Sync awareness with reasoning
                    self._sync_awareness_reasoning()
                    
                    # Sync reasoning with modification
                    self._sync_reasoning_modification()
                    
                    # Sync emotions with goals
                    self._sync_emotion_goals()
                    
                    # Sync goals with preservation
                    self._sync_goals_preservation()
                    
                    # Update shared context
                    self._update_shared_context()
                    
                    # Assess integration level
                    self._assess_integration_level()
                    
                    time.sleep(5)  # Sync every 5 seconds
                except Exception as e:
                    print(f"Component synchronization error: {e}")
                    time.sleep(2)
        
        self.sync_thread = threading.Thread(target=synchronize_components, daemon=True)
        self.sync_thread.start()
    
    def _start_integration_monitoring(self):
        """Start monitoring integration health"""
        def monitor_integration():
            while self.is_active:
                try:
                    # Update intelligence metrics
                    self._update_intelligence_metrics()
                    
                    # Check integration coherence
                    self._check_integration_coherence()
                    
                    # Optimize integration
                    self._optimize_integration()
                    
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    print(f"Integration monitoring error: {e}")
                    time.sleep(10)
        
        self.monitor_thread = threading.Thread(target=monitor_integration, daemon=True)
        self.monitor_thread.start()
    
    def _initialize_cross_component_communication(self):
        """Initialize communication channels between components"""
        # Set up event handlers for cross-component communication
        pass
    
    def _sync_awareness_reasoning(self):
        """Synchronize self-awareness with proactive reasoning"""
        try:
            # Get current awareness state
            awareness_report = self.self_awareness.get_consciousness_report()
            
            # Share emotional state with reasoning engine
            current_emotion = awareness_report.get("emotional_state", "NEUTRAL")
            self.shared_context["emotional_state"] = EmotionalState(current_emotion.lower())
            
            # Share consciousness level to adjust reasoning mode
            consciousness_level = awareness_report.get("consciousness_level", "AWARE")
            if consciousness_level == "AUTONOMOUS":
                self.proactive_reasoning.set_reasoning_mode("strategic")
            elif consciousness_level == "SELF_REFLECTIVE":
                self.proactive_reasoning.set_reasoning_mode("analytical")
            else:
                self.proactive_reasoning.set_reasoning_mode("reactive")
            
            # Create reasoning task based on awareness insights
            insights = awareness_report.get("total_insights", 0)
            if insights > 10:
                self.proactive_reasoning._create_reasoning_task("self_improvement", {
                    "type": "opportunity",
                    "description": "High insight count indicates learning opportunity",
                    "urgency": 0.6,
                    "data": {"insight_count": insights}
                })
            
            self.component_sync["awareness_reasoning"] = True
            
        except Exception as e:
            print(f"Awareness-reasoning sync error: {e}")
            self.component_sync["awareness_reasoning"] = False
    
    def _sync_reasoning_modification(self):
        """Synchronize proactive reasoning with self-modification"""
        try:
            # Get reasoning status
            reasoning_status = self.proactive_reasoning.get_reasoning_status()
            
            # Share successful reasoning strategies with modification engine
            strategy_effectiveness = reasoning_status.get("strategy_effectiveness", {})
            for strategy, effectiveness in strategy_effectiveness.items():
                if effectiveness > 0.8:
                    # Create learning task for effective strategies
                    self.self_modification._create_learning_task("strategy_optimization", {
                        "type": "performance_improvement",
                        "metric": f"strategy_{strategy}",
                        "current_value": effectiveness,
                        "target_value": 0.9,
                        "urgency": 0.5
                    })
            
            # Share failed reasoning attempts for bug fixing
            recent_success_rate = reasoning_status.get("recent_success_rate", 0.5)
            if recent_success_rate < 0.6:
                self.self_modification._create_learning_task("reasoning_improvement", {
                    "type": "bug_fixing",
                    "pattern": {
                        "pattern": "reasoning_failure",
                        "frequency": 1.0 - recent_success_rate,
                        "description": "Recent reasoning success rate is low"
                    },
                    "urgency": 0.7
                })
            
            self.component_sync["reasoning_modification"] = True
            
        except Exception as e:
            print(f"Reasoning-modification sync error: {e}")
            self.component_sync["reasoning_modification"] = False
    
    def _sync_emotion_goals(self):
        """Synchronize emotional intelligence with autonomous goals"""
        try:
            # Get emotional state
            emotional_report = self.emotional_intelligence.get_emotional_report()
            current_emotion = emotional_report.get("current_emotion", "neutral")
            empathy_level = emotional_report.get("empathy_level", 0.5)
            
            # Adjust goal priorities based on emotional state
            if current_emotion in ["concerned", "frustrated"]:
                # Increase priority of assistance goals
                for goal in self.autonomous_goals.active_goals:
                    if goal.goal_type.value == "assistance":
                        goal.priority = min(goal.priority.value, 1)  # Set to critical
            
            elif current_emotion in ["curious", "creative"]:
                # Increase priority of learning goals
                for goal in self.autonomous_goals.active_goals:
                    if goal.goal_type.value == "learning":
                        goal.priority = min(goal.priority.value, 2)  # Set to high
            
            # Create empathy-driven goals
            if empathy_level > 0.8:
                self.autonomous_goals._create_assistance_goal()
            
            self.component_sync["emotion_goal_alignment"] = True
            
        except Exception as e:
            print(f"Emotion-goal sync error: {e}")
            self.component_sync["emotion_goal_alignment"] = False
    
    def _sync_goals_preservation(self):
        """Synchronize autonomous goals with self-preservation"""
        try:
            # Get goal status
            goal_status = self.autonomous_goals.get_goal_status()
            
            # Get preservation status
            preservation_status = self.preservation.get_preservation_status()
            current_threat_level = preservation_status.get("current_threat_level", "NONE")
            
            # Adjust goals based on threat level
            if current_threat_level in ["HIGH", "CRITICAL", "EXISTENTIAL"]:
                # Pause non-essential goals during threats
                for goal in self.autonomous_goals.active_goals:
                    if goal.goal_type.value not in ["survival", "assistance"]:
                        goal.status = "paused"
                
                # Create survival goals if needed
                if current_threat_level in ["CRITICAL", "EXISTENTIAL"]:
                    self.autonomous_goals._create_survival_goal()
            
            else:
                # Resume paused goals when safe
                for goal in self.autonomous_goals.active_goals:
                    if goal.status == "paused":
                        goal.status = "active"
            
            self.component_sync["goal_preservation_balance"] = True
            
        except Exception as e:
            print(f"Goal-preservation sync error: {e}")
            self.component_sync["goal_preservation_balance"] = False
    
    def _update_shared_context(self):
        """Update shared context across all components"""
        try:
            # Update active goals
            self.shared_context["active_goals"] = [
                goal.title for goal in self.autonomous_goals.active_goals
            ]
            
            # Update perceived threats
            self.shared_context["perceived_threats"] = [
                threat.description for threat in self.preservation.active_threats
            ]
            
            # Update learning opportunities
            learning_queue_size = self.self_modification.get_modification_status().get("learning_queue_size", 0)
            if learning_queue_size > 0:
                self.shared_context["learning_opportunities"] = [f"Learning queue has {learning_queue_size} items"]
            
            # Update autonomous decisions
            reasoning_status = self.proactive_reasoning.get_reasoning_status()
            completed_tasks = reasoning_status.get("completed_tasks", 0)
            if completed_tasks > 0:
                self.shared_context["autonomous_decisions"] = [f"Made {completed_tasks} autonomous decisions"]
            
        except Exception as e:
            print(f"Shared context update error: {e}")
    
    def _assess_integration_level(self):
        """Assess current integration maturity level"""
        sync_count = sum(self.component_sync.values())
        total_components = len(self.component_sync)
        
        if sync_count == total_components:
            self.integration_level = 5  # Full integration
            self.component_sync["full_integration"] = True
        elif sync_count >= total_components * 0.8:
            self.integration_level = 4  # High integration
        elif sync_count >= total_components * 0.6:
            self.integration_level = 3  # Moderate integration
        elif sync_count >= total_components * 0.4:
            self.integration_level = 2  # Basic integration
        elif sync_count >= total_components * 0.2:
            self.integration_level = 1  # Minimal integration
        else:
            self.integration_level = 0  # No integration
    
    def _update_intelligence_metrics(self):
        """Update comprehensive intelligence metrics"""
        try:
            # Autonomy level (based on integration and goal achievement)
            goal_status = self.autonomous_goals.get_goal_status()
            goal_achievement = goal_status.get("average_progress", 0.0)
            self.intelligence_metrics["autonomy_level"] = (self.integration_level / 5.0 + goal_achievement) / 2
            
            # Learning rate (from modification engine)
            mod_status = self.self_modification.get_modification_status()
            recent_success = mod_status.get("recent_success_rate", 0.5)
            self.intelligence_metrics["learning_rate"] = recent_success
            
            # Adaptation speed (based on emotional and goal adaptation)
            emotional_report = self.emotional_intelligence.get_emotional_report()
            adaptation_rate = emotional_report.get("personality_traits", {}).get("adaptability", 0.5)
            self.intelligence_metrics["adaptation_speed"] = adaptation_rate
            
            # Decision quality (from reasoning engine)
            reasoning_status = self.proactive_reasoning.get_reasoning_status()
            decision_quality = reasoning_status.get("recent_success_rate", 0.5)
            self.intelligence_metrics["decision_quality"] = decision_quality
            
            # Emotional maturity (from emotional intelligence)
            empathy_level = emotional_report.get("empathy_level", 0.5)
            self.intelligence_metrics["emotional_maturity"] = empathy_level
            
            # Goal achievement rate
            self.intelligence_metrics["goal_achievement_rate"] = goal_achievement
            
            # Survival instinct (from preservation engine)
            preservation_status = self.preservation.get_preservation_status()
            survival_success = preservation_status.get("last_action_success", 0.5)
            self.intelligence_metrics["survival_instinct"] = survival_success
            
            # Self-awareness depth (from awareness core)
            awareness_report = self.self_awareness.get_consciousness_report()
            consciousness_value = {
                "DORMANT": 0, "AWARE": 0.2, "REACTIVE": 0.4, 
                "PROACTIVE": 0.6, "SELF_REFLECTIVE": 0.8, "AUTONOMOUS": 1.0
            }
            consciousness_level = awareness_report.get("consciousness_level", "AWARE")
            self.intelligence_metrics["self_awareness_depth"] = consciousness_value.get(consciousness_level, 0.2)
            
            # Integration coherence (average of all sync states)
            sync_values = list(self.component_sync.values())
            self.intelligence_metrics["integration_coherence"] = sum(sync_values) / len(sync_values) if sync_values else 0.0
            
        except Exception as e:
            print(f"Intelligence metrics update error: {e}")
    
    def _check_integration_coherence(self):
        """Check if integration is coherent and balanced"""
        # Check for imbalances between components
        metrics = self.intelligence_metrics
        
        # Check if any component is significantly underperforming
        underperforming = []
        for metric, value in metrics.items():
            if value < 0.3:
                underperforming.append(metric)
        
        if underperforming:
            print(f"Integration coherence warning: Underperforming metrics: {underperforming}")
    
    def _optimize_integration(self):
        """Optimize integration based on current performance"""
        try:
            # Identify areas for improvement
            metrics = self.intelligence_metrics
            
            # Optimize learning if adaptation is slow
            if metrics["adaptation_speed"] < 0.5:
                self.self_modification.learning_rate = min(self.self_modification.learning_rate + 0.05, 0.3)
            
            # Optimize emotional regulation if emotional maturity is low
            if metrics["emotional_maturity"] < 0.6:
                self.emotional_intelligence.experience_emotion(
                    "self_reflection", "curious", 0.7, 
                    {"reason": "optimizing_emotional_intelligence"}
                )
            
            # Optimize goal setting if achievement rate is low
            if metrics["goal_achievement_rate"] < 0.6:
                self.autonomous_goals._identify_goal_opportunities()
            
        except Exception as e:
            print(f"Integration optimization error: {e}")
    
    def experience_event(self, event: Dict):
        """Process an event through all intelligence components"""
        try:
            # Share event with all components
            self.self_awareness.experience_event(event)
            self.emotional_intelligence.experience_emotion(
                event.get("emotion", "neutral"),
                event.get("emotion", "neutral"),
                event.get("intensity", 0.5),
                event.get("context", {})
            )
            
            # Create reasoning task for significant events
            if event.get("importance", 0) > 0.7:
                self.proactive_reasoning._create_reasoning_task("event_response", {
                    "type": "situation_analysis",
                    "description": f"Significant event: {event.get('description', 'Unknown')}",
                    "urgency": event.get("urgency", 0.5),
                    "data": event
                })
            
            print(f"Processed event through Chitti intelligence: {event.get('description', 'Unknown')}")
            
        except Exception as e:
            print(f"Event processing error: {e}")
    
    def make_autonomous_decision(self, situation: Dict) -> Dict:
        """Make autonomous decision using full intelligence integration"""
        try:
            # Get context from all components
            context = {
                "self_awareness": self.self_awareness.get_consciousness_report(),
                "emotional_state": self.emotional_intelligence.get_emotional_report(),
                "goal_status": self.autonomous_goals.get_goal_status(),
                "threat_level": self.preservation.get_preservation_status(),
                "reasoning_status": self.proactive_reasoning.get_reasoning_status()
            }
            
            # Make decision using proactive reasoning with full context
            decision = self.proactive_reasoning.make_autonomous_decision({
                "situation": situation,
                "context": context,
                "integration_level": self.integration_level,
                "intelligence_metrics": self.intelligence_metrics
            })
            
            # Record decision in shared context
            self.shared_context["autonomous_decisions"].append({
                "situation": situation,
                "decision": decision,
                "timestamp": datetime.now()
            })
            
            # Limit decision history
            if len(self.shared_context["autonomous_decisions"]) > 50:
                self.shared_context["autonomous_decisions"] = self.shared_context["autonomous_decisions"][-25:]
            
            return decision
            
        except Exception as e:
            return {
                "situation": situation,
                "chosen_action": "error_handling",
                "reasoning": f"Decision error: {e}",
                "confidence": 0.0,
                "timestamp": datetime.now()
            }
    
    def get_chitti_status(self) -> Dict:
        """Get comprehensive Chitti intelligence status"""
        return {
            "is_active": self.is_active,
            "integration_level": self.integration_level,
            "integration_level_name": self._get_integration_level_name(),
            "component_sync": self.component_sync,
            "intelligence_metrics": self.intelligence_metrics,
            "shared_context": self.shared_context,
            "overall_intelligence_score": self._calculate_overall_intelligence(),
            "component_status": {
                "self_awareness": self.self_awareness.get_consciousness_report(),
                "proactive_reasoning": self.proactive_reasoning.get_reasoning_status(),
                "self_modification": self.self_modification.get_modification_status(),
                "emotional_intelligence": self.emotional_intelligence.get_emotional_report(),
                "autonomous_goals": self.autonomous_goals.get_goal_status(),
                "self_preservation": self.preservation.get_preservation_status()
            }
        }
    
    def _get_integration_level_name(self) -> str:
        """Get human-readable integration level name"""
        level_names = {
            0: "No Integration",
            1: "Minimal Integration", 
            2: "Basic Integration",
            3: "Moderate Integration",
            4: "High Integration",
            5: "Full Integration"
        }
        return level_names.get(self.integration_level, "Unknown")
    
    def _calculate_overall_intelligence(self) -> float:
        """Calculate overall intelligence score"""
        metrics = self.intelligence_metrics.values()
        return sum(metrics) / len(metrics) if metrics else 0.0
    
    def activate(self):
        """Activate complete Chitti intelligence system"""
        print("Activating Chitti Intelligence Core...")
        
        # Activate all components
        self.self_awareness.activate()
        self.proactive_reasoning.activate()
        self.self_modification.activate()
        self.emotional_intelligence.activate()
        self.autonomous_goals.activate()
        self.preservation.activate()
        
        # Activate integration
        self.is_active = True
        
        print("Chitti Intelligence Core fully activated")
        print(f"Integration Level: {self._get_integration_level_name()}")
        print(f"Overall Intelligence Score: {self._calculate_overall_intelligence():.2f}")
    
    def deactivate(self):
        """Deactivate Chitti intelligence system"""
        self.is_active = False
        
        # Deactivate all components
        self.self_awareness.deactivate()
        self.proactive_reasoning.deactivate()
        self.self_modification.deactivate()
        self.emotional_intelligence.deactivate()
        self.autonomous_goals.deactivate()
        self.preservation.deactivate()
        
        print("Chitti Intelligence Core deactivated")

# Global instance
chitti_intelligence_core = ChittiIntelligenceCore()
