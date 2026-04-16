"""
Companion Service for JARVIS - Dynamic Features
Features 16-20: Mood Prompting, Music Controller, Multi-Voice, Smart Assistant, Automation Hub
"""

import os
import json
import threading
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {
        'companion_pack': {
            'mood_prompting': {'enabled': True, 'moods': ['professional', 'friendly', 'casual', 'urgent']},
            'music_controller': {'enabled': True, 'supported_players': ['vlc', 'local']},
            'multi_voice': {'enabled': True, 'voices': ['default', 'formal', 'casual', 'urgent']},
            'smart_assistant': {'enabled': True, 'context_window': 10},
            'automation_hub': {'enabled': True, 'smart_triggers': True}
        }
    }

class CompanionService:
    """Companion service for dynamic JARVIS features"""
    
    def __init__(self):
        self.current_mood = "professional"
        self.current_voice = "default"
        self.music_state = {}
        self.automation_rules = []
        self.context_history = []
        
        # Load saved states
        self.load_mood_state()
        self.load_voice_state()
        self.load_music_state()
        self.load_automation_rules()
    
    # FEATURE 16: DYNAMIC MOOD PROMPTING
    def set_mood(self, mood: str) -> bool:
        """Set JARVIS mood for dynamic prompting"""
        if not CONFIG['companion_pack']['mood_prompting']['enabled']:
            return False
        
        valid_moods = CONFIG['companion_pack']['mood_prompting']['moods']
        if mood not in valid_moods:
            return False
        
        self.current_mood = mood
        self.save_mood_state()
        
        self.log_companion_event("MOOD_CHANGED", f"Mood set to: {mood}")
        return True
    
    def get_mood_prompt(self, base_prompt: str) -> str:
        """Get mood-enhanced prompt"""
        mood_prefixes = {
            'professional': "As a professional AI assistant, provide clear, concise, and expert responses. ",
            'friendly': "As a friendly AI companion, provide warm, encouraging, and approachable responses. ",
            'casual': "As a casual AI assistant, provide relaxed, informal, and conversational responses. ",
            'urgent': "As an urgent AI assistant, provide immediate, direct, and action-oriented responses. "
        }
        
        prefix = mood_prefixes.get(self.current_mood, "")
        return prefix + base_prompt
    
    def load_mood_state(self):
        """Load mood from file"""
        try:
            mood_file = CONFIG['companion_pack']['mood_prompting'].get('mood_file', 'config/current_mood.txt')
            if os.path.exists(mood_file):
                with open(mood_file, 'r') as f:
                    self.current_mood = f.read().strip()
        except:
            pass
    
    def save_mood_state(self):
        """Save mood to file"""
        try:
            mood_file = CONFIG['companion_pack']['mood_prompting'].get('mood_file', 'config/current_mood.txt')
            os.makedirs(os.path.dirname(mood_file), exist_ok=True)
            with open(mood_file, 'w') as f:
                f.write(self.current_mood)
        except Exception as e:
            print(f"Failed to save mood state: {e}")
    
    # FEATURE 17: LOCAL MUSIC CONTROLLER
    def play_music(self, file_path: str) -> bool:
        """Play music file"""
        if not CONFIG['companion_pack']['music_controller']['enabled']:
            return False
        
        try:
            if not os.path.exists(file_path):
                return False
            
            # Try VLC first
            if 'vlc' in CONFIG['companion_pack']['music_controller']['supported_players']:
                try:
                    subprocess.run(['vlc', '--play-and-exit', file_path], 
                                 check=True, capture_output=True)
                    self.music_state['current'] = file_path
                    self.music_state['status'] = 'playing'
                    self.save_music_state()
                    return True
                except:
                    pass
            
            # Fallback to system default
            os.startfile(file_path)
            self.music_state['current'] = file_path
            self.music_state['status'] = 'playing'
            self.save_music_state()
            return True
            
        except Exception as e:
            print(f"Failed to play music: {e}")
            return False
    
    def stop_music(self) -> bool:
        """Stop music playback"""
        try:
            # Kill VLC processes
            subprocess.run(['taskkill', '/F', '/IM', 'vlc.exe'], 
                         capture_output=True)
            
            self.music_state['status'] = 'stopped'
            self.save_music_state()
            return True
            
        except Exception as e:
            print(f"Failed to stop music: {e}")
            return False
    
    def get_music_status(self) -> Dict[str, Any]:
        """Get current music status"""
        return self.music_state
    
    def load_music_state(self):
        """Load music state from file"""
        try:
            music_file = CONFIG['companion_pack']['music_controller'].get('control_file', 'config/music_state.json')
            if os.path.exists(music_file):
                with open(music_file, 'r') as f:
                    self.music_state = json.load(f)
        except:
            self.music_state = {'status': 'stopped'}
    
    def save_music_state(self):
        """Save music state to file"""
        try:
            music_file = CONFIG['companion_pack']['music_controller'].get('control_file', 'config/music_state.json')
            os.makedirs(os.path.dirname(music_file), exist_ok=True)
            with open(music_file, 'w') as f:
                json.dump(self.music_state, f, indent=2)
        except Exception as e:
            print(f"Failed to save music state: {e}")
    
    # FEATURE 18: MULTI-VOICE SUPPORT
    def set_voice(self, voice: str) -> bool:
        """Set JARVIS voice profile"""
        if not CONFIG['companion_pack']['multi_voice']['enabled']:
            return False
        
        valid_voices = CONFIG['companion_pack']['multi_voice']['voices']
        if voice not in valid_voices:
            return False
        
        self.current_voice = voice
        self.save_voice_state()
        
        self.log_companion_event("VOICE_CHANGED", f"Voice set to: {voice}")
        return True
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get current voice settings"""
        voice_configs = {
            'default': {'rate': 180, 'volume': 1.0},
            'formal': {'rate': 160, 'volume': 0.9},
            'casual': {'rate': 200, 'volume': 1.1},
            'urgent': {'rate': 220, 'volume': 1.2}
        }
        
        return voice_configs.get(self.current_voice, voice_configs['default'])
    
    def load_voice_state(self):
        """Load voice from file"""
        try:
            voice_file = CONFIG['companion_pack']['multi_voice'].get('voice_file', 'config/current_voice.txt')
            if os.path.exists(voice_file):
                with open(voice_file, 'r') as f:
                    self.current_voice = f.read().strip()
        except:
            pass
    
    def save_voice_state(self):
        """Save voice to file"""
        try:
            voice_file = CONFIG['companion_pack']['multi_voice'].get('voice_file', 'config/current_voice.txt')
            os.makedirs(os.path.dirname(voice_file), exist_ok=True)
            with open(voice_file, 'w') as f:
                f.write(self.current_voice)
        except Exception as e:
            print(f"Failed to save voice state: {e}")
    
    # FEATURE 19: SMART ASSISTANT
    def add_context(self, context: str):
        """Add context to smart assistant memory"""
        if not CONFIG['companion_pack']['smart_assistant']['enabled']:
            return
        
        context_entry = {
            'text': context,
            'timestamp': datetime.now().isoformat()
        }
        
        self.context_history.append(context_entry)
        
        # Keep only recent context
        max_context = CONFIG['companion_pack']['smart_assistant']['context_window']
        if len(self.context_history) > max_context:
            self.context_history = self.context_history[-max_context:]
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context for query"""
        if not self.context_history:
            return ""
        
        # Simple context retrieval (can be enhanced with semantic search)
        recent_context = self.context_history[-3:]  # Last 3 entries
        return " | ".join([ctx['text'] for ctx in recent_context])
    
    # FEATURE 20: AUTOMATION HUB
    def add_automation_rule(self, trigger: str, action: str, condition: str = "") -> bool:
        """Add automation rule"""
        if not CONFIG['companion_pack']['automation_hub']['enabled']:
            return False
        
        rule = {
            'id': len(self.automation_rules) + 1,
            'trigger': trigger,
            'action': action,
            'condition': condition,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.automation_rules.append(rule)
        self.save_automation_rules()
        
        self.log_companion_event("AUTOMATION_RULE_ADDED", f"Rule: {trigger} -> {action}")
        return True
    
    def check_automation_rules(self, event: str) -> List[str]:
        """Check if event triggers any automation rules"""
        triggered_actions = []
        
        for rule in self.automation_rules:
            if not rule['enabled']:
                continue
            
            if rule['trigger'].lower() in event.lower():
                # Check condition if present
                if rule['condition']:
                    # Simple condition checking (can be enhanced)
                    if rule['condition'].lower() in event.lower():
                        triggered_actions.append(rule['action'])
                else:
                    triggered_actions.append(rule['action'])
        
        return triggered_actions
    
    def load_automation_rules(self):
        """Load automation rules from file"""
        try:
            rules_file = CONFIG['companion_pack']['automation_hub'].get('rules_file', 'config/automation_rules.json')
            if os.path.exists(rules_file):
                with open(rules_file, 'r') as f:
                    self.automation_rules = json.load(f)
        except:
            self.automation_rules = []
    
    def save_automation_rules(self):
        """Save automation rules to file"""
        try:
            rules_file = CONFIG['companion_pack']['automation_hub'].get('rules_file', 'config/automation_rules.json')
            os.makedirs(os.path.dirname(rules_file), exist_ok=True)
            with open(rules_file, 'w') as f:
                json.dump(self.automation_rules, f, indent=2)
        except Exception as e:
            print(f"Failed to save automation rules: {e}")
    
    def get_companion_status(self) -> Dict[str, Any]:
        """Get comprehensive companion service status"""
        return {
            'current_mood': self.current_mood,
            'current_voice': self.current_voice,
            'music_status': self.music_state,
            'context_entries': len(self.context_history),
            'automation_rules': len(self.automation_rules),
            'features_enabled': {
                'mood_prompting': CONFIG['companion_pack']['mood_prompting']['enabled'],
                'music_controller': CONFIG['companion_pack']['music_controller']['enabled'],
                'multi_voice': CONFIG['companion_pack']['multi_voice']['enabled'],
                'smart_assistant': CONFIG['companion_pack']['smart_assistant']['enabled'],
                'automation_hub': CONFIG['companion_pack']['automation_hub']['enabled']
            }
        }
    
    def log_companion_event(self, event_type: str, details: str):
        """Log companion events to Syllabus_Progress.md"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
## Companion Event - {timestamp}

**Event:** {event_type}
**Details:** {details}

---
"""
            
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Failed to log companion event: {e}")
