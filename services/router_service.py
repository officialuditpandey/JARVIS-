#!/usr/bin/env python3
"""
Hybrid Router Service for JARVIS
Intelligently routes voice commands to Ollama or Gemini based on content
"""

import os
import re
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {'hybrid_router': {'enabled': True}}

class FastPrivateRouter:
    """Fast + Private router with Gemini default and Moondream privacy handling"""
    
    def __init__(self):
        self.active_brain = "gemini"  # Default brain
        self.privacy_mode = False
        self.routing_stats = {
            'gemini_count': 0,
            'moondream_count': 0,
            'total_commands': 0
        }
        
        # Privacy-sensitive tasks that MUST use Moondream (local processing)
        self.privacy_tasks = {
            # Camera-related tasks
            'camera', 'webcam', 'what do you see', 'look at', 'show me', 'what can you see',
            'what\'s in my hand', 'what is in my hand', 'in my hand', 'holding',
            'what am i holding', 'identify object', 'detect person', 'face detection',
            'presence', 'who is there', 'is anyone there', 'security', 'monitor',
            
            # Visual solver commands
            'solve this', 'look at this', 'jarvis solve this', 'jarvis look at this',
            
            # System monitoring commands
            'system status', 'check storage', 'storage status', 'disk usage',
            
            # System actions (privacy-sensitive)
            'open', 'close', 'start', 'stop', 'run', 'launch', 'execute',
            'volume', 'mute', 'unmute', 'lock', 'unlock', 'shutdown', 'restart',
            
            # Screen-related tasks
            'screen', 'what\'s on my screen', 'what is on my screen', 'screenshot',
            'ui error', 'interface', 'window', 'dialog', 'popup', 'error message',
            'what\'s wrong', 'fix this', 'help with', 'can\'t click', 'button not working',
            
            # Local file system tasks
            'local file', 'my file', 'this file', 'folder', 'directory', 'local',
            'on my computer', 'my desktop', 'my documents', 'private', 'personal'
        }
        
        # General tasks that can use Gemini (cloud processing)
        self.general_tasks = {
            'explain', 'help me understand', 'what is', 'how to', 'why does',
            'coding', 'programming', 'debug', 'algorithm', 'code review',
            'research', 'search online', 'internet', 'web', 'information',
            'write', 'create', 'generate', 'summarize', 'translate',
            'math', 'calculate', 'analyze', 'compare', 'recommend'
        }
        
        print("Fast + Private Router initialized")
        print(f"Default Brain: Gemini 3 Flash (High Quality)")
        print(f"Privacy Brain: Moondream via Ollama (Local Processing)")
        print(f"Privacy tasks: {len(self.privacy_tasks)} keywords")
        print(f"General tasks: {len(self.general_tasks)} keywords")
    
    def analyze_command(self, query: str) -> Tuple[str, str]:
        """
        Analyze command and determine routing for Fast + Private architecture
        Returns: (routing_decision, reasoning)
        """
        query_lower = query.lower().strip()
        
        # Check for privacy-sensitive tasks (MUST route to Moondream)
        for privacy in self.privacy_tasks:
            if privacy in query_lower:
                self.active_brain = "moondream"
                self.privacy_mode = True
                reasoning = f"Privacy-sensitive task detected: '{privacy}' -> Moondream (Local Processing)"
                return "moondream", reasoning
        
        # Check for general tasks (can route to Gemini)
        for general in self.general_tasks:
            if general in query_lower:
                self.active_brain = "gemini"
                self.privacy_mode = False
                reasoning = f"General task detected: '{general}' -> Gemini (Cloud Processing)"
                return "gemini", reasoning
        
        # Default: route to Gemini for all other queries
        self.active_brain = "gemini"
        self.privacy_mode = False
        reasoning = "Default routing -> Gemini 3 Flash (High Quality)"
        return "gemini", reasoning
    
    def route_command(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route command to appropriate brain
        Returns: routing result with decision and metadata
        """
        routing_decision, reasoning = self.analyze_command(query)
        
        # Update statistics
        self.routing_stats['total_commands'] += 1
        if routing_decision == "moondream":
            self.routing_stats['moondream_count'] += 1
        else:  # gemini
            self.routing_stats['gemini_count'] += 1
        
        result = {
            'query': query,
            'routing_decision': routing_decision,
            'active_brain': self.active_brain,
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        print(f"Router: {routing_decision.upper()} - {reasoning}")
        return result
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total = self.routing_stats['total_commands']
        if total > 0:
            gemini_percent = (self.routing_stats['gemini_count'] / total) * 100
            moondream_percent = (self.routing_stats['moondream_count'] / total) * 100
        else:
            gemini_percent = moondream_percent = 0
        
        return {
            'active_brain': self.active_brain,
            'privacy_mode': self.privacy_mode,
            'total_commands': total,
            'gemini_count': self.routing_stats['gemini_count'],
            'moondream_count': self.routing_stats['moondream_count'],
            'gemini_percentage': round(gemini_percent, 1),
            'moondream_percentage': round(moondream_percent, 1),
            'last_updated': datetime.now().isoformat()
        }
    
    def set_active_brain(self, brain: str) -> bool:
        """Manually set active brain"""
        if brain in ['gemini', 'moondream']:
            self.active_brain = brain
            self.privacy_mode = (brain == 'moondream')
            print(f"Router: Active brain manually set to {brain.upper()}")
            return True
        return False
    
    def reset_stats(self):
        """Reset routing statistics"""
        self.routing_stats = {
            'gemini_count': 0,
            'moondream_count': 0,
            'total_commands': 0
        }
        self.privacy_mode = False
        print("Router: Statistics reset")
    
    def is_privacy_mode(self) -> bool:
        """Check if currently in privacy mode"""
        return self.privacy_mode
    
    def get_status(self) -> Dict[str, Any]:
        """Get router status"""
        return {
            'status': 'active',
            'active_brain': self.active_brain,
            'privacy_mode': self.privacy_mode,
            'routing_stats': self.get_routing_stats(),
            'privacy_tasks_count': len(self.privacy_tasks),
            'general_tasks_count': len(self.general_tasks),
            'config': {
                'enabled': CONFIG.get('hybrid_router', {}).get('enabled', True),
                'default_brain': 'gemini',
                'privacy_brain': 'moondream',
                'architecture': 'fast-private'
            }
        }

# Test function
def test_router():
    """Test Fast + Private router functionality"""
    router = FastPrivateRouter()
    
    test_commands = [
        "what do you see?",           # Privacy -> Moondream
        "what's in my hand?",        # Privacy -> Moondream
        "what's on my screen?",      # Privacy -> Moondream
        "explain quantum physics",   # General -> Gemini
        "help me code this",         # General -> Gemini
        "who is there?",             # Privacy -> Moondream
        "research this topic",       # General -> Gemini
        "fix this ui error",         # Privacy -> Moondream
        "how to debug python",       # General -> Gemini
        "camera monitoring",         # Privacy -> Moondream
    ]
    
    print("=== Fast + Private Router Test ===")
    for cmd in test_commands:
        result = router.route_command(cmd)
        print(f"Command: {cmd}")
        print(f"Route: {result['routing_decision'].upper()}")
        print(f"Privacy Mode: {router.is_privacy_mode()}")
        print(f"Reason: {result['reasoning']}")
        print()
    
    print("=== Routing Statistics ===")
    stats = router.get_routing_stats()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_router()
