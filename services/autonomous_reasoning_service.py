#!/usr/bin/env python3
"""
Autonomous Reasoning Service for JARVIS - Feature 12
Real Intelligence with system state reflection and personality adaptation
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import psutil
import subprocess

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class AutonomousReasoningService:
    """Autonomous Reasoning service with system state reflection and personality adaptation"""
    
    def __init__(self):
        self.is_active = False
        self.system_state = {}
        self.user_context = {}
        self.personality_mode = "default"
        self.reasoning_history = []
        
        # System monitoring
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.update_interval = 30  # Update system state every 30 seconds
        
        # Personality modes
        self.personality_modes = {
            "studying": {
                "style": "concise",
                "helpfulness": "high",
                "formality": "moderate",
                "response_length": "short",
                "keywords": ["study", "homework", "assignment", "exam", "learn", "research"]
            },
            "working": {
                "style": "professional",
                "helpfulness": "high",
                "formality": "high",
                "response_length": "medium",
                "keywords": ["work", "project", "meeting", "deadline", "office", "business"]
            },
            "casual": {
                "style": "friendly",
                "helpfulness": "moderate",
                "formality": "low",
                "response_length": "medium",
                "keywords": ["relax", "break", "game", "entertainment", "fun", "chat"]
            },
            "focused": {
                "style": "direct",
                "helpfulness": "high",
                "formality": "moderate",
                "response_length": "very_short",
                "keywords": ["focus", "concentrate", "deep work", "important", "urgent"]
            },
            "default": {
                "style": "balanced",
                "helpfulness": "high",
                "formality": "moderate",
                "response_length": "medium",
                "keywords": []
            }
        }
        
        # Self-correction patterns
        self.error_patterns = {
            "command_failure": ["failed", "error", "unable", "cannot", "exception"],
            "uncertainty": ["maybe", "perhaps", "probably", "might", "unclear"],
            "repetition": ["again", "repeat", "same", "duplicate"],
            "confusion": ["confused", "unclear", "don't understand", "not sure"]
        }
        
        # Initialize
        self._initialize_reasoning()
        
        print("Autonomous Reasoning Service initialized")
    
    def _initialize_reasoning(self):
        """Initialize reasoning system"""
        try:
            # Update initial system state
            self._update_system_state()
            
            # Detect initial user context
            self._detect_user_context()
            
            # Start monitoring thread
            self._start_monitoring()
            
        except Exception as e:
            print(f"Reasoning initialization failed: {e}")
    
    def _update_system_state(self):
        """Update current system state"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Temperature (simplified - would use proper monitoring in production)
            cpu_temp = self._estimate_cpu_temperature()
            
            # Time of day
            current_time = datetime.now()
            time_of_day = self._classify_time_of_day(current_time)
            
            # Active applications
            active_apps = self._get_active_applications()
            
            # System load
            system_load = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'cpu_temp': cpu_temp,
                'timestamp': current_time.isoformat(),
                'time_of_day': time_of_day,
                'active_applications': active_apps,
                'system_uptime': psutil.boot_time()
            }
            
            self.system_state = system_load
            
        except Exception as e:
            print(f"System state update failed: {e}")
    
    def _estimate_cpu_temperature(self) -> float:
        """Estimate CPU temperature (simplified)"""
        try:
            # This would use proper temperature monitoring in production
            # For now, estimate based on CPU load
            cpu_load = psutil.cpu_percent()
            
            if cpu_load > 80:
                return 70.0 + (cpu_load - 80) * 0.5  # High load = high temp
            elif cpu_load > 50:
                return 50.0 + (cpu_load - 50) * 0.67  # Medium load = medium temp
            else:
                return 35.0 + cpu_load * 0.3  # Low load = low temp
                
        except:
            return 45.0  # Default temperature
    
    def _classify_time_of_day(self, current_time: datetime) -> str:
        """Classify time of day"""
        hour = current_time.hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _get_active_applications(self) -> List[Dict[str, Any]]:
        """Get list of active applications"""
        try:
            if not WIN32_AVAILABLE:
                return []
            
            active_apps = []
            
            def enum_windows_callback(hwnd, apps):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            
                            app_info = {
                                'title': title,
                                'pid': pid,
                                'name': process.name(),
                                'cpu_percent': process.cpu_percent(),
                                'memory_percent': process.memory_percent()
                            }
                            apps.append(app_info)
                        except:
                            pass
                return True
            
            win32gui.EnumWindows(enum_windows_callback, active_apps)
            
            # Sort by CPU usage
            active_apps.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return active_apps[:10]  # Return top 10
            
        except Exception as e:
            print(f"Active applications detection failed: {e}")
            return []
    
    def _detect_user_context(self):
        """Detect user context based on system state"""
        try:
            context = {
                'activity': 'unknown',
                'environment': 'unknown',
                'focus_level': 'medium',
                'detected_at': datetime.now().isoformat()
            }
            
            # Analyze active applications
            active_apps = self.system_state.get('active_applications', [])
            app_names = [app['name'].lower() for app in active_apps]
            
            # Detect study context
            study_apps = ['notepad.exe', 'word.exe', 'excel.exe', 'powerpnt.exe', 'acrobat.exe', 'chrome.exe', 'firefox.exe']
            if any(study_app in app_names for study_app in study_apps):
                context['activity'] = 'studying'
                context['focus_level'] = 'high'
            
            # Detect work context
            work_apps = ['outlook.exe', 'teams.exe', 'slack.exe', 'zoom.exe', 'excel.exe', 'powerpnt.exe']
            if any(work_app in app_names for work_app in work_apps):
                context['activity'] = 'working'
                context['focus_level'] = 'high'
            
            # Detect casual context
            casual_apps = ['spotify.exe', 'netflix.exe', 'steam.exe', 'discord.exe', 'chrome.exe']
            if any(casual_app in app_names for casual_app in casual_apps):
                context['activity'] = 'casual'
                context['focus_level'] = 'low'
            
            # Detect environment based on time
            time_of_day = self.system_state.get('time_of_day', 'unknown')
            if time_of_day in ['morning', 'afternoon']:
                context['environment'] = 'productive'
            elif time_of_day in ['evening', 'night']:
                context['environment'] = 'relaxed'
            
            # Adjust based on CPU temperature
            cpu_temp = self.system_state.get('cpu_temp', 45.0)
            if cpu_temp > 65:
                context['system_stress'] = 'high'
            elif cpu_temp > 50:
                context['system_stress'] = 'medium'
            else:
                context['system_stress'] = 'low'
            
            self.user_context = context
            
        except Exception as e:
            print(f"User context detection failed: {e}")
    
    def _start_monitoring(self):
        """Start system monitoring thread"""
        try:
            self.is_active = True
            self.stop_event.clear()
            
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            print("System monitoring started")
            
        except Exception as e:
            print(f"Failed to start monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_active and not self.stop_event.is_set():
            try:
                # Update system state
                self._update_system_state()
                
                # Detect user context
                self._detect_user_context()
                
                # Adapt personality based on context
                self._adapt_personality()
                
                # Wait for next update
                self.stop_event.wait(self.update_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def _adapt_personality(self):
        """Adapt personality based on user context"""
        try:
            activity = self.user_context.get('activity', 'unknown')
            
            # Map activity to personality mode
            if activity == 'studying':
                self.personality_mode = 'studying'
            elif activity == 'working':
                self.personality_mode = 'working'
            elif activity == 'casual':
                self.personality_mode = 'casual'
            else:
                # Check system stress
                stress = self.user_context.get('system_stress', 'medium')
                if stress == 'high':
                    self.personality_mode = 'focused'
                else:
                    self.personality_mode = 'default'
            
        except Exception as e:
            print(f"Personality adaptation failed: {e}")
    
    def reflect_on_system_state(self, query: str) -> Dict[str, Any]:
        """Reflect on system state before responding"""
        try:
            reflection = {
                'query': query,
                'system_state': self.system_state.copy(),
                'user_context': self.user_context.copy(),
                'personality_mode': self.personality_mode,
                'reflections': [],
                'adaptations': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate reflections based on system state
            reflections = []
            
            # Time-based reflections
            time_of_day = self.system_state.get('time_of_day', 'unknown')
            if time_of_day == 'morning':
                reflections.append("It's morning - you might be starting your day. I should be energizing and helpful.")
            elif time_of_day == 'afternoon':
                reflections.append("It's afternoon - peak productivity time. I should be efficient and focused.")
            elif time_of_day == 'evening':
                reflections.append("It's evening - time to wind down. I should be more relaxed.")
            elif time_of_day == 'night':
                reflections.append("It's night - you might be working late. I should be concise and not overwhelming.")
            
            # CPU temperature reflections
            cpu_temp = self.system_state.get('cpu_temp', 45.0)
            if cpu_temp > 65:
                reflections.append(f"System temperature is high ({cpu_temp:.1f}°C). I should keep responses brief to reduce processing load.")
            elif cpu_temp > 50:
                reflections.append(f"System is moderately warm ({cpu_temp:.1f}°C). I should be efficient.")
            
            # Activity-based reflections
            activity = self.user_context.get('activity', 'unknown')
            if activity == 'studying':
                reflections.append("You're studying. I should be concise, helpful, and not interrupt your focus.")
            elif activity == 'working':
                reflections.append("You're working. I should be professional and efficient.")
            elif activity == 'casual':
                reflections.append("You're in a casual mode. I can be more conversational.")
            
            # Memory usage reflections
            memory_percent = self.system_state.get('memory_percent', 50)
            if memory_percent > 80:
                reflections.append(f"Memory usage is high ({memory_percent:.1f}%). I should be mindful of system resources.")
            
            reflection['reflections'] = reflections
            
            # Generate adaptations
            adaptations = []
            personality = self.personality_modes.get(self.personality_mode, self.personality_modes['default'])
            
            adaptations.append(f"Personality mode: {self.personality_mode}")
            adaptations.append(f"Response style: {personality['style']}")
            adaptations.append(f"Response length: {personality['response_length']}")
            adaptations.append(f"Helpfulness level: {personality['helpfulness']}")
            
            reflection['adaptations'] = adaptations
            
            # Store in history
            self.reasoning_history.append(reflection)
            if len(self.reasoning_history) > 100:
                self.reasoning_history = self.reasoning_history[-100:]
            
            return reflection
            
        except Exception as e:
            return {
                'error': f'System reflection failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def adapt_response(self, original_response: str, query: str) -> str:
        """Adapt response based on system state and personality"""
        try:
            # Get reflection
            reflection = self.reflect_on_system_state(query)
            
            if 'error' in reflection:
                return original_response
            
            personality = self.personality_modes.get(reflection['personality_mode'], self.personality_modes['default'])
            
            adapted_response = original_response
            
            # Apply personality adaptations
            if personality['style'] == 'concise':
                adapted_response = self._make_concise(adapted_response)
            elif personality['style'] == 'professional':
                adapted_response = self._make_professional(adapted_response)
            elif personality['style'] == 'friendly':
                adapted_response = self._make_friendly(adapted_response)
            elif personality['style'] == 'direct':
                adapted_response = self._make_direct(adapted_response)
            
            # Apply length constraints
            if personality['response_length'] == 'short':
                adapted_response = self._shorten_response(adapted_response, 100)
            elif personality['response_length'] == 'very_short':
                adapted_response = self._shorten_response(adapted_response, 50)
            
            return adapted_response
            
        except Exception as e:
            print(f"Response adaptation failed: {e}")
            return original_response
    
    def _make_concise(self, response: str) -> str:
        """Make response more concise"""
        sentences = response.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Keep only the most important sentences
        if len(sentences) > 2:
            sentences = sentences[:2]
        
        return '. '.join(sentences) + '.'
    
    def _make_professional(self, response: str) -> str:
        """Make response more professional"""
        # Replace informal language
        replacements = {
            "hey": "Hello",
            "hi": "Hello",
            "thanks": "Thank you",
            "cool": "excellent",
            "awesome": "excellent",
            "gonna": "going to",
            "wanna": "want to",
            "yeah": "yes"
        }
        
        for informal, formal in replacements.items():
            response = response.replace(informal, formal)
        
        return response
    
    def _make_friendly(self, response: str) -> str:
        """Make response more friendly"""
        # Add friendly elements
        if not response.startswith(('Hey', 'Hi', 'Hello')):
            response = "Hey! " + response
        
        return response
    
    def _make_direct(self, response: str) -> str:
        """Make response more direct"""
        # Remove filler words
        filler_words = ["actually", "basically", "essentially", "in fact", "really"]
        for filler in filler_words:
            response = response.replace(filler + " ", "")
        
        return response
    
    def _shorten_response(self, response: str, max_length: int) -> str:
        """Shorten response to maximum length"""
        if len(response) <= max_length:
            return response
        
        # Truncate at sentence boundary
        truncated = response[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def detect_and_correct_errors(self, query: str, response: str, error: Exception = None) -> Dict[str, Any]:
        """Detect errors and provide self-correction"""
        try:
            correction = {
                'query': query,
                'original_response': response,
                'error': str(error) if error else None,
                'corrections': [],
                'explanation': '',
                'corrected_response': response,
                'timestamp': datetime.now().isoformat()
            }
            
            # Detect error patterns
            if error:
                correction['corrections'].append(f"Error detected: {type(error).__name__}: {str(error)}")
                correction['explanation'] = f"I encountered a {type(error).__name__} error. "
                
                # Provide specific explanations
                if "ConnectionError" in str(error):
                    correction['explanation'] += "This appears to be a network connectivity issue. Please check your internet connection."
                elif "PermissionError" in str(error):
                    correction['explanation'] += "This is a permission issue. The system may need administrator privileges."
                elif "FileNotFoundError" in str(error):
                    correction['explanation'] += "A required file was not found. The file may have been moved or deleted."
                elif "TimeoutError" in str(error):
                    correction['explanation'] += "The operation timed out. This might be due to high system load or network issues."
                else:
                    correction['explanation'] += "This is an unexpected error. Please try again or contact support."
                
                # Generate corrected response
                correction['corrected_response'] = f"I apologize, but I encountered an error: {correction['explanation']}"
            
            # Detect uncertainty in response
            response_lower = response.lower()
            for pattern in self.error_patterns['uncertainty']:
                if pattern in response_lower:
                    correction['corrections'].append(f"Uncertainty detected: '{pattern}'")
                    correction['explanation'] += "I'm not completely certain about this response. "
                    break
            
            # Detect repetition
            words = response.lower().split()
            if len(words) > 10:
                word_count = {}
                for word in words:
                    word_count[word] = word_count.get(word, 0) + 1
                
                for word, count in word_count.items():
                    if count > 3 and word not in ['the', 'a', 'an', 'and', 'or', 'but']:
                        correction['corrections'].append(f"Repetition detected: '{word}' repeated {count} times")
                        correction['explanation'] += "I notice I'm repeating myself. Let me be more concise. "
                        break
            
            # Store correction in history
            self.reasoning_history.append(correction)
            if len(self.reasoning_history) > 100:
                self.reasoning_history = self.reasoning_history[-100:]
            
            return correction
            
        except Exception as e:
            return {
                'error': f'Error correction failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_reasoning_status(self) -> Dict[str, Any]:
        """Get reasoning service status"""
        return {
            'is_active': self.is_active,
            'personality_mode': self.personality_mode,
            'system_state': self.system_state,
            'user_context': self.user_context,
            'reasoning_history_count': len(self.reasoning_history),
            'last_updated': datetime.now().isoformat()
        }
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2)
            
            print("Autonomous reasoning monitoring stopped")
            
        except Exception as e:
            print(f"Failed to stop monitoring: {e}")

    def get_status(self):
        return {
            'is_active': self.is_active,
            'personality_mode': self.personality_mode
        }
