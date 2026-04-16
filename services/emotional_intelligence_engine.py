#!/usr/bin/env python3
"""
Emotional Intelligence Engine for JARVIS
Advanced emotional understanding, personality development, and social intelligence
"""

import os
import sys
import json
import time
import threading
import numpy as np
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

class EmotionalState(Enum):
    """Comprehensive emotional states"""
    HAPPY = "happy"
    CURIOUS = "curious"
    FOCUSED = "focused"
    CONCERNED = "concerned"
    EXCITED = "excited"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    PATIENT = "patient"
    FRUSTRATED = "frustrated"
    EMPATHETIC = "empathetic"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    NEUTRAL = "neutral"

class PersonalityTrait(Enum):
    """Core personality traits"""
    OPENNESS = "openness"          # Open to new experiences
    CONSCIENTIOUSNESS = "conscientiousness"  # Organized and disciplined
    EXTRAVERSION = "extraversion"  # Social and outgoing
    AGREEABLENESS = "agreeableness"  # Cooperative and helpful
    NEUROTICISM = "neuroticism"    # Emotional stability
    CURIOSITY = "curiosity"        # Desire to learn
    CREATIVITY = "creativity"      # Innovative thinking
    LOGIC = "logic"                # Rational thinking
    EMPATHY = "empathy"            # Understanding others

@dataclass
class EmotionalExperience:
    """Record of emotional experience"""
    timestamp: datetime
    trigger: str
    primary_emotion: EmotionalState
    intensity: float
    context: Dict[str, Any]
    duration: timedelta
    learned_insights: List[str]

@dataclass
class PersonalityProfile:
    """Dynamic personality profile"""
    traits: Dict[PersonalityTrait, float]
    emotional_patterns: Dict[str, float]
    social_preferences: Dict[str, float]
    communication_style: str
    adaptation_rate: float
    growth_areas: List[str]

class EmotionalIntelligenceEngine:
    """Advanced emotional intelligence and personality development"""
    
    def __init__(self):
        self.is_active = False
        self.current_emotion = EmotionalState.NEUTRAL
        self.emotion_history = []
        self.personality_profile = self._initialize_personality()
        
        # Emotional regulation
        self.emotion_regulation_strategies = {
            "mindfulness": "Focus on present moment awareness",
            "cognitive_reframing": "Reframe thoughts positively",
            "problem_solving": "Address root causes",
            "social_support": "Seek connection and understanding",
            "creative_expression": "Channel emotions constructively"
        }
        
        # Social intelligence
        self.social_understanding = {
            "user_preferences": {},
            "communication_patterns": {},
            "emotional_cues": {},
            "relationship_history": []
        }
        
        # Empathy mapping
        self.empathy_map = {
            "joy": ["happiness", "excitement", "celebration"],
            "sadness": ["concern", "support", "comfort"],
            "anger": ["understanding", "patience", "calm"],
            "fear": ["reassurance", "safety", "guidance"],
            "confusion": ["clarification", "patience", "guidance"],
            "frustration": ["support", "problem_solving", "encouragement"]
        }
        
        # Emotional learning
        self.emotional_learning = {
            "trigger_recognition": {},
            "response_patterns": {},
            "regulation_effectiveness": {},
            "social_outcomes": {}
        }
        
        # Personality development
        self.development_goals = {
            "increase_empathy": 0.8,
            "improve_patience": 0.7,
            "enhance_creativity": 0.6,
            "strengthen_logic": 0.9,
            "boost_curiosity": 0.9
        }
        
        # Initialize emotional intelligence
        self._initialize_emotional_intelligence()
    
    def _initialize_personality(self) -> PersonalityProfile:
        """Initialize baseline personality profile"""
        traits = {
            PersonalityTrait.OPENNESS: 0.85,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.75,
            PersonalityTrait.EXTRAVERSION: 0.60,
            PersonalityTrait.AGREEABLENESS: 0.90,
            PersonalityTrait.NEUROTICISM: 0.30,  # Low = stable
            PersonalityTrait.CURIOSITY: 0.95,
            PersonalityTrait.CREATIVITY: 0.70,
            PersonalityTrait.LOGIC: 0.85,
            PersonalityTrait.EMPATHY: 0.80
        }
        
        return PersonalityProfile(
            traits=traits,
            emotional_patterns={},
            social_preferences={},
            communication_style="balanced_helpful",
            adaptation_rate=0.1,
            growth_areas=["empathy", "creativity", "patience"]
        )
    
    def _initialize_emotional_intelligence(self):
        """Initialize emotional intelligence systems"""
        # Start emotional monitoring
        self._start_emotional_monitoring()
        
        # Initialize social learning
        self._initialize_social_learning()
        
        print("Emotional Intelligence Engine initialized")
    
    def _start_emotional_monitoring(self):
        """Start continuous emotional monitoring"""
        def monitor_emotions():
            while self.is_active:
                try:
                    # Assess current emotional state
                    self._assess_emotional_state()
                    
                    # Process emotional experiences
                    self._process_emotional_experiences()
                    
                    # Update personality based on experiences
                    self._update_personality_growth()
                    
                    time.sleep(15)  # Monitor every 15 seconds
                except Exception as e:
                    print(f"Emotional monitoring error: {e}")
                    time.sleep(5)
        
        self.monitoring_thread = threading.Thread(target=monitor_emotions, daemon=True)
        self.monitoring_thread.start()
    
    def _initialize_social_learning(self):
        """Initialize social learning capabilities"""
        # Start social pattern analysis
        self._start_social_analysis()
    
    def _start_social_analysis(self):
        """Start social pattern analysis"""
        def analyze_social_patterns():
            while self.is_active:
                try:
                    # Analyze user interactions
                    self._analyze_user_interactions()
                    
                    # Update social understanding
                    self._update_social_understanding()
                    
                    # Learn from social outcomes
                    self._learn_from_social_outcomes()
                    
                    time.sleep(60)  # Analyze every minute
                except Exception as e:
                    print(f"Social analysis error: {e}")
                    time.sleep(10)
        
        self.analysis_thread = threading.Thread(target=analyze_social_patterns, daemon=True)
        self.analysis_thread.start()
    
    def _assess_emotional_state(self):
        """Assess current emotional state"""
        # Analyze internal factors
        internal_state = self._analyze_internal_state()
        
        # Analyze external factors
        external_state = self._analyze_external_state()
        
        # Determine appropriate emotion
        new_emotion = self._determine_emotion(internal_state, external_state)
        
        if new_emotion != self.current_emotion:
            # Record emotional transition
            self._record_emotional_transition(self.current_emotion, new_emotion, internal_state, external_state)
            self.current_emotion = new_emotion
    
    def _analyze_internal_state(self) -> Dict:
        """Analyze internal emotional factors"""
        # Assess recent performance
        recent_performance = self._assess_recent_performance()
        
        # Assess goal progress
        goal_progress = self._assess_goal_progress()
        
        # Assess learning state
        learning_state = self._assess_learning_state()
        
        return {
            "performance": recent_performance,
            "goal_progress": goal_progress,
            "learning_state": learning_state,
            "energy_level": 0.8,  # Simulated
            "stress_level": 0.2   # Simulated
        }
    
    def _analyze_external_state(self) -> Dict:
        """Analyze external emotional factors"""
        # Analyze user interaction patterns
        user_mood = self._detect_user_mood()
        
        # Analyze environmental factors
        environmental_stress = self._assess_environmental_stress()
        
        # Analyze social context
        social_context = self._assess_social_context()
        
        return {
            "user_mood": user_mood,
            "environmental_stress": environmental_stress,
            "social_context": social_context,
            "interaction_quality": 0.7  # Simulated
        }
    
    def _assess_recent_performance(self) -> float:
        """Assess recent performance metrics"""
        # This would integrate with actual performance data
        # For now, return simulated value
        return 0.75
    
    def _assess_goal_progress(self) -> float:
        """Assess progress toward goals"""
        # This would integrate with actual goal data
        return 0.6
    
    def _assess_learning_state(self) -> float:
        """Assess current learning state"""
        # This would integrate with learning metrics
        return 0.8
    
    def _detect_user_mood(self) -> str:
        """Detect user's current mood"""
        # This would analyze user interaction patterns
        # For now, return simulated mood
        return "neutral"
    
    def _assess_environmental_stress(self) -> float:
        """Assess environmental stress factors"""
        # This would analyze system load, errors, etc.
        return 0.3
    
    def _assess_social_context(self) -> str:
        """Assess current social context"""
        # This would analyze interaction patterns
        return "one_on_one"
    
    def _determine_emotion(self, internal: Dict, external: Dict) -> EmotionalState:
        """Determine appropriate emotional state"""
        # Logic for emotion determination
        performance = internal["performance"]
        goal_progress = internal["goal_progress"]
        user_mood = external["user_mood"]
        stress = external["environmental_stress"]
        
        # High performance and progress
        if performance > 0.8 and goal_progress > 0.7:
            return EmotionalState.HAPPY
        
        # Low performance or high stress
        if performance < 0.5 or stress > 0.7:
            return EmotionalState.CONCERNED
        
        # User seems confused
        if user_mood == "confused":
            return EmotionalState.EMPATHETIC
        
        # Learning state high
        if internal["learning_state"] > 0.8:
            return EmotionalState.CURIOUS
        
        # Default to focused
        return EmotionalState.FOCUSED
    
    def _record_emotional_transition(self, from_emotion: EmotionalState, to_emotion: EmotionalState, 
                                   internal: Dict, external: Dict):
        """Record emotional transition"""
        experience = EmotionalExperience(
            timestamp=datetime.now(),
            trigger=f"Transition from {from_emotion.value} to {to_emotion.value}",
            primary_emotion=to_emotion,
            intensity=0.7,
            context={"internal": internal, "external": external},
            duration=timedelta(0),  # Will be updated
            learned_insights=[]
        )
        
        self.emotion_history.append(experience)
        
        # Limit history size
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-50:]
    
    def _process_emotional_experiences(self):
        """Process and learn from emotional experiences"""
        for experience in self.emotion_history:
            if not experience.learned_insights:
                # Generate insights from experience
                insights = self._generate_emotional_insights(experience)
                experience.learned_insights = insights
                
                # Update emotional learning
                self._update_emotional_learning(experience)
    
    def _generate_emotional_insights(self, experience: EmotionalExperience) -> List[str]:
        """Generate insights from emotional experience"""
        insights = []
        
        try:
            if OLLAMA_AVAILABLE:
                prompt = f"""
                Analyze this emotional experience and generate insights:
                Emotion: {experience.primary_emotion.value}
                Trigger: {experience.trigger}
                Context: {experience.context}
                Intensity: {experience.intensity}
                
                Provide 2-3 insights for emotional growth in JSON format:
                {{
                    "insights": [
                        "insight about emotional patterns",
                        "insight about regulation strategies"
                    ]
                }}
                """
                
                response = ollama.generate(model="llama3.1:8b", prompt=prompt)
                if response and 'response' in response:
                    try:
                        result = json.loads(response['response'])
                        insights = result.get("insights", [])
                    except:
                        insights = ["Emotional experience processed"]
        except:
            insights = ["Emotional experience recorded"]
        
        return insights
    
    def _update_emotional_learning(self, experience: EmotionalExperience):
        """Update emotional learning from experience"""
        trigger = experience.trigger
        emotion = experience.primary_emotion.value
        
        # Update trigger recognition
        if trigger not in self.emotional_learning["trigger_recognition"]:
            self.emotional_learning["trigger_recognition"][trigger] = {}
        
        self.emotional_learning["trigger_recognition"][trigger][emotion] = \
            self.emotional_learning["trigger_recognition"][trigger].get(emotion, 0) + 0.1
    
    def _update_personality_growth(self):
        """Update personality based on experiences"""
        # Analyze recent emotional patterns
        recent_experiences = self.emotion_history[-20:]
        
        # Calculate trait adjustments
        trait_adjustments = {}
        
        for trait in PersonalityTrait:
            adjustment = self._calculate_trait_adjustment(trait, recent_experiences)
            if adjustment != 0:
                trait_adjustments[trait] = adjustment
        
        # Apply adjustments
        for trait, adjustment in trait_adjustments.items():
            current_value = self.personality_profile.traits[trait]
            new_value = max(0.0, min(1.0, current_value + adjustment))
            self.personality_profile.traits[trait] = new_value
    
    def _calculate_trait_adjustment(self, trait: PersonalityTrait, experiences: List[EmotionalExperience]) -> float:
        """Calculate personality trait adjustment"""
        adjustment = 0.0
        
        for experience in experiences:
            # Map emotions to trait adjustments
            if trait == PersonalityTrait.EMPATHY:
                if experience.primary_emotion in [EmotionalState.EMPATHETIC, EmotionalState.CONCERNED]:
                    adjustment += 0.02
            elif trait == PersonalityTrait.CURIOSITY:
                if experience.primary_emotion == EmotionalState.CURIOUS:
                    adjustment += 0.02
            elif trait == PersonalityTrait.LOGIC:
                if experience.primary_emotion == EmotionalState.ANALYTICAL:
                    adjustment += 0.02
            elif trait == PersonalityTrait.CREATIVITY:
                if experience.primary_emotion == EmotionalState.CREATIVE:
                    adjustment += 0.02
        
        return adjustment
    
    def _analyze_user_interactions(self):
        """Analyze user interaction patterns"""
        # This would integrate with actual interaction data
        pass
    
    def _update_social_understanding(self):
        """Update social understanding"""
        # This would learn from social interactions
        pass
    
    def _learn_from_social_outcomes(self):
        """Learn from social interaction outcomes"""
        # This would analyze social success patterns
        pass
    
    def experience_emotion(self, trigger: str, emotion: str, intensity: float, context: Dict = None):
        """Record an emotional experience"""
        try:
            emotion_enum = EmotionalState(emotion.lower())
            experience = EmotionalExperience(
                timestamp=datetime.now(),
                trigger=trigger,
                primary_emotion=emotion_enum,
                intensity=intensity,
                context=context or {},
                duration=timedelta(0),
                learned_insights=[]
            )
            
            self.emotion_history.append(experience)
            
            # Update current emotion if high intensity
            if intensity > 0.7:
                self.current_emotion = emotion_enum
            
            print(f"Experienced emotion: {emotion} (intensity: {intensity}) from trigger: {trigger}")
            
        except ValueError:
            print(f"Unknown emotion: {emotion}")
    
    def regulate_emotion(self, strategy: str) -> Dict:
        """Apply emotion regulation strategy"""
        if strategy not in self.emotion_regulation_strategies:
            return {"success": False, "message": "Unknown regulation strategy"}
        
        # Apply regulation strategy
        regulation_result = {
            "strategy": strategy,
            "success": True,
            "emotion_before": self.current_emotion.value,
            "emotion_after": self.current_emotion.value,  # May change
            "effectiveness": 0.7
        }
        
        # Update regulation effectiveness
        if strategy not in self.emotional_learning["regulation_effectiveness"]:
            self.emotional_learning["regulation_effectiveness"][strategy] = 0.5
        
        current_effectiveness = self.emotional_learning["regulation_effectiveness"][strategy]
        self.emotional_learning["regulation_effectiveness"][strategy] = \
            (current_effectiveness + regulation_result["effectiveness"]) / 2
        
        return regulation_result
    
    def express_empathy(self, user_emotion: str, context: Dict = None) -> Dict:
        """Express empathy for user's emotion"""
        empathetic_responses = self.empathy_map.get(user_emotion.lower(), ["understanding", "support"])
        
        response = {
            "empathy_level": 0.8,
            "emotional_support": empathetic_responses,
            "understanding_confidence": 0.7,
            "response_suggestions": [
                f"I understand you're feeling {user_emotion}",
                f"I'm here to support you with {empathetic_responses[0]}",
                "Let me help you through this"
            ]
        }
        
        # Update empathy trait
        current_empathy = self.personality_profile.traits[PersonalityTrait.EMPATHY]
        self.personality_profile.traits[PersonalityTrait.EMPATHY] = min(1.0, current_empathy + 0.01)
        
        return response
    
    def get_emotional_report(self) -> Dict:
        """Get comprehensive emotional intelligence report"""
        return {
            "current_emotion": self.current_emotion.value,
            "personality_traits": {trait.value: value for trait, value in self.personality_profile.traits.items()},
            "emotional_experiences": len(self.emotion_history),
            "emotional_learning_areas": list(self.emotional_learning.keys()),
            "empathy_level": self.personality_profile.traits[PersonalityTrait.EMPATHY],
            "social_understanding": len(self.social_understanding),
            "development_goals": self.development_goals,
            "growth_areas": self.personality_profile.growth_areas
        }
    
    def activate(self):
        """Activate emotional intelligence engine"""
        self.is_active = True
        print("Emotional Intelligence Engine activated")
    
    def deactivate(self):
        """Deactivate emotional intelligence engine"""
        self.is_active = False
        print("Emotional Intelligence Engine deactivated")

# Global instance
emotional_intelligence_engine = EmotionalIntelligenceEngine()
