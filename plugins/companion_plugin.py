#!/usr/bin/env python3
"""
Companion Plugin for JARVIS - Dynamic Features
"""

import sys
import os
from typing import Dict, Any

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from services.companion_service import CompanionService
    COMPANION_AVAILABLE = True
except ImportError:
    COMPANION_AVAILABLE = False

class CompanionPlugin:
    """Companion plugin for dynamic JARVIS features"""
    
    def __init__(self):
        self.name = "companion"
        self.version = "1.0.0"
        self.description = "Dynamic mood, voice, and automation features"
        self.companion_service = None
        
        self.command_patterns = [
            "set mood",
            "change mood",
            "set voice",
            "change voice",
            "play music",
            "stop music",
            "add automation",
            "companion status"
        ]
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            if not COMPANION_AVAILABLE:
                return False
            
            self.companion_service = CompanionService()
            return True
        except Exception as e:
            print(f"Companion plugin initialization failed: {e}")
            return False
    
    def handles_command(self, query: str) -> bool:
        """Check if plugin handles command"""
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.command_patterns)
    
    def process_command(self, query: str) -> Dict[str, Any]:
        """Process companion command"""
        try:
            query_lower = query.lower()
            
            # Mood commands
            if "set mood" in query_lower or "change mood" in query_lower:
                mood = query_lower.replace("set mood", "").replace("change mood", "").strip()
                valid_moods = ['professional', 'friendly', 'casual', 'urgent']
                
                if mood in valid_moods:
                    if self.companion_service.set_mood(mood):
                        return {
                            'success': True,
                            'response': f"Mood set to {mood}. I'll respond with a {mood} tone."
                        }
                    else:
                        return {'success': False, 'error': 'Failed to set mood'}
                else:
                    return {
                        'success': False, 
                        'error': f'Invalid mood. Choose from: {", ".join(valid_moods)}'
                    }
            
            # Voice commands
            elif "set voice" in query_lower or "change voice" in query_lower:
                voice = query_lower.replace("set voice", "").replace("change voice", "").strip()
                valid_voices = ['default', 'formal', 'casual', 'urgent']
                
                if voice in valid_voices:
                    if self.companion_service.set_voice(voice):
                        return {
                            'success': True,
                            'response': f"Voice set to {voice}."
                        }
                    else:
                        return {'success': False, 'error': 'Failed to set voice'}
                else:
                    return {
                        'success': False,
                        'error': f'Invalid voice. Choose from: {", ".join(valid_voices)}'
                    }
            
            # Music commands
            elif "play music" in query_lower:
                # For now, just acknowledge (can be enhanced with file selection)
                return {
                    'success': True,
                    'response': "Music playback feature ready. Please specify music file path."
                }
            
            elif "stop music" in query_lower:
                if self.companion_service.stop_music():
                    return {
                        'success': True,
                        'response': "Music stopped."
                    }
                else:
                    return {'success': False, 'error': 'No music playing'}
            
            # Automation commands
            elif "add automation" in query_lower:
                # Simple automation (can be enhanced)
                return {
                    'success': True,
                    'response': "Automation hub ready. Rules can be configured via settings."
                }
            
            # Status
            elif "companion status" in query_lower:
                status = self.companion_service.get_companion_status()
                return {
                    'success': True,
                    'response': f"Current mood: {status['current_mood']}. "
                                f"Voice: {status['current_voice']}. "
                                f"Automation rules: {status['automation_rules']}."
                }
            
            else:
                return {'success': False, 'error': 'Unknown companion command'}
                
        except Exception as e:
            return {'success': False, 'error': f'Companion command failed: {e}'}
