"""
Hybrid Brain Service for Cloud Cowork HUD
Routes commands between Personal (Ollama) and General (Gemini) AI models
"""

import os
import sys
import asyncio
import re
from typing import Tuple, Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"Gemini not available: {e}")
    GEMINI_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Ollama not available: {e}")
    OLLAMA_AVAILABLE = False

class HybridRouter:
    """Hybrid AI Router that intelligently routes commands between Personal and General AI"""
    
    def __init__(self, gemini_key: str = None, local_model: str = "llama3.1:8b"):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.local_model = local_model
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
            except Exception as e:
                print(f"Gemini initialization failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
        
        # Initialize Ollama if available
        if OLLAMA_AVAILABLE:
            try:
                # Test if local model is available
                models = ollama.list()
                available_models = [model.model.split(':')[0] for model in models.models]
                self.ollama_available = self.local_model.split(':')[0] in available_models
                
                if not self.ollama_available:
                    print(f"Local model {local_model} not found in Ollama")
                    # Try to find an alternative model
                    for model in available_models:
                        if 'llama' in model.lower() or 'mistral' in model.lower():
                            self.local_model = model
                            self.ollama_available = True
                            print(f"Using alternative model: {model}")
                            break
            except Exception as e:
                print(f"Ollama initialization failed: {e}")
                self.ollama_available = False
        else:
            self.ollama_available = False
        
        # Personal content detection patterns
        self.personal_keywords = [
            'syllabus', 'study', 'course', 'assignment', 'homework', 'exam', 'test',
            'my', 'private', 'personal', 'confidential', 'secret', 'notes',
            'file', 'document', 'project', 'work', 'task', 'deadline',
            'schedule', 'calendar', 'meeting', 'class', 'lecture', 'tutorial'
        ]
        
        self.personal_file_patterns = [
            r'\.(txt|doc|pdf|docx|ppt|pptx|xls|xlsx)$',
            r'(notes|documents|files|downloads|desktop|documents)',
            r'(c:\\|/home/|/users/|~/)',
            r'(assignment|project|homework|syllabus)'
        ]
        
        # Command history for context
        self.command_history = []
        self.max_history = 50
    
    def is_personal_command(self, command: str) -> bool:
        """Determine if a command is Personal (local) or General (cloud)"""
        command_lower = command.lower()
        
        # Check for personal keywords
        for keyword in self.personal_keywords:
            if keyword in command_lower:
                return True
        
        # Check for personal file patterns
        for pattern in self.personal_file_patterns:
            if re.search(pattern, command_lower):
                return True
        
        # Check for questions about personal data
        personal_questions = [
            'what do i have', 'what are my', 'show me my', 'find my',
            'what did i', 'where is my', 'help me with my'
        ]
        
        for question in personal_questions:
            if question in command_lower:
                return True
        
        # Check for local system commands
        local_system_commands = [
            'open file', 'create file', 'save file', 'delete file',
            'search file', 'find file', 'list files', 'directory',
            'folder', 'path', 'location'
        ]
        
        for sys_cmd in local_system_commands:
            if sys_cmd in command_lower:
                return True
        
        return False
    
    async def route_command(self, command: str, context: List[str] = None) -> Tuple[str, str]:
        """
        Route command to appropriate AI model
        Returns: (response, source)
        """
        # Add to command history
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'personal': self.is_personal_command(command)
        })
        
        # Keep history manageable
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Determine routing
        is_personal = self.is_personal_command(command)
        
        if is_personal and self.ollama_available:
            # Route to local Ollama for personal content
            response = await self._route_to_ollama(command, context)
            source = "Local"
        elif not is_personal and self.gemini_available:
            # Route to Gemini for general queries (FatihMakes speed)
            response = await self._route_to_gemini(command, context)
            source = "Gemini"
        elif self.ollama_available:
            # Fallback to Ollama
            response = await self._route_to_ollama(command, context)
            source = "Local"
        else:
            # No AI available
            response = "AI services are currently unavailable"
            source = "None"
        
        return response, source
    
    async def _route_to_gemini(self, command: str, context: List[str] = None) -> str:
        """Route command to Gemini API for general queries"""
        try:
            # Build context-aware prompt
            prompt = self._build_prompt(command, context, "general")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.gemini_model.generate_content(prompt)
            )
            
            return response.text
        except Exception as e:
            return f"Gemini error: {e}"
    
    async def _route_to_ollama(self, command: str, context: List[str] = None) -> str:
        """Route command to Ollama for personal queries"""
        try:
            # Build context-aware prompt
            prompt = self._build_prompt(command, context, "personal")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ollama.generate(self.local_model, prompt)
            )
            
            if isinstance(response, dict):
                return response.get("response", str(response))
            return str(response)
        except Exception as e:
            return f"Ollama error: {e}"
    
    def _build_prompt(self, command: str, context: List[str], mode: str) -> str:
        """Build context-aware prompt based on routing mode"""
        if mode == "personal":
            # Personal mode - focus on local/private content
            prompt = f"""You are JARVIS, a personal AI assistant. You have access to the user's local files and personal information.

Context: {chr(10).join(context[-5:]) if context else 'No previous context'}

User Command: {command}

Instructions:
- This is a PERSONAL command related to the user's private files, studies, or local content
- Provide helpful, personalized responses
- You have access to local files and can help with personal tasks
- Be conversational but maintain privacy and security
- If you need to access files, explain what you're looking for
- Focus on personal productivity, study help, or local system assistance

Response:"""
        else:
            # General mode - use Gemini for speed and general knowledge
            prompt = f"""You are JARVIS, a knowledgeable AI assistant. This is a GENERAL query that doesn't involve personal files or private information.

Context: {chr(10).join(context[-3:]) if context else 'No previous context'}

User Command: {command}

Instructions:
- This is a GENERAL command for broad knowledge and assistance
- Provide accurate, helpful responses using your general knowledge
- Be conversational and engaging
- Focus on the user's immediate question or request
- You can access general web knowledge and information

Response:"""
        
        return prompt
    
    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        if not self.command_history:
            return {"total": 0, "personal": 0, "general": 0}
        
        total = len(self.command_history)
        personal = sum(1 for cmd in self.command_history if cmd.get('personal', False))
        general = total - personal
        
        return {
            "total": total,
            "personal": personal,
            "general": general,
            "personal_percentage": round((personal / total) * 100, 1) if total > 0 else 0,
            "gemini_available": self.gemini_available,
            "ollama_available": self.ollama_available,
            "local_model": self.local_model
        }
    
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.gemini_available or self.ollama_available
    
    def get_status(self) -> Dict:
        """Get current router status"""
        return {
            "gemini_available": self.gemini_available,
            "ollama_available": self.ollama_available,
            "local_model": self.local_model,
            "total_commands": len(self.command_history),
            "last_command": self.command_history[-1] if self.command_history else None
        }
