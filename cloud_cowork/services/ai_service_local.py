"""
Local AI Service for Cloud Cowork HUD
Uses only local Ollama models (no external APIs)
"""

import asyncio
import sys
import os
from typing import Tuple, Optional, List, Dict

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from .brain_local import LocalBrain
    LOCAL_BRAIN_AVAILABLE = True
except ImportError as e:
    print(f"Local brain not available: {e}")
    LOCAL_BRAIN_AVAILABLE = False

try:
    from .vision_local import LocalVision
    LOCAL_VISION_AVAILABLE = True
except ImportError as e:
    print(f"Local vision not available: {e}")
    LOCAL_VISION_AVAILABLE = False

try:
    from .voice_local import LocalVoice
    LOCAL_VOICE_AVAILABLE = True
except ImportError as e:
    print(f"Local voice not available: {e}")
    LOCAL_VOICE_AVAILABLE = False

class LocalAIService:
    """Local AI Service using only Ollama models"""
    
    def __init__(self, model_name: str = "llama3.1:8b", vision_model: str = "moondream"):
        self.is_processing = False
        self.command_history = []
        self.context_history = []
        
        # Initialize local brain
        if LOCAL_BRAIN_AVAILABLE:
            try:
                self.brain = LocalBrain(model_name, vision_model)
                self.use_brain = True
                print("Local brain initialized successfully")
            except Exception as e:
                print(f"Local brain initialization failed: {e}")
                self.brain = None
                self.use_brain = False
        else:
            self.brain = None
            self.use_brain = False
        
        # Initialize local vision
        if LOCAL_VISION_AVAILABLE:
            try:
                self.vision = LocalVision(vision_model)
                print("Local vision initialized successfully")
            except Exception as e:
                print(f"Local vision initialization failed: {e}")
                self.vision = None
        else:
            self.vision = None
        
        # Initialize local voice
        if LOCAL_VOICE_AVAILABLE:
            try:
                self.voice = LocalVoice()
                print("Local voice initialized successfully")
            except Exception as e:
                print(f"Local voice initialization failed: {e}")
                self.voice = None
        else:
            self.voice = None
    
    async def process_command(self, command: str, context: List[str] = None) -> Tuple[str, str]:
        """Process command using local AI"""
        if self.is_processing:
            return "JARVIS is currently processing another request...", "Processing"
        
        self.is_processing = True
        
        try:
            if self.use_brain and self.brain:
                # Use local brain
                response, source = await self.brain.process_command(command, context or self.context_history)
                
                # Speak response if voice is available
                if self.voice and response:
                    self.voice.speak(response)
                
                result = f"[{source.upper()}] {response}"
            else:
                result = "Local AI service is currently unavailable"
                source = "None"
            
            # Update context history
            self.context_history.append(command)
            if len(self.context_history) > 10:
                self.context_history.pop(0)
            
            # Add to command history
            self.command_history.append({
                "command": command,
                "response": result,
                "source": source,
                "timestamp": str(asyncio.get_event_loop().time()),
                "local": True
            })
            
            # Keep only last 50 commands
            if len(self.command_history) > 50:
                self.command_history = self.command_history[-50:]
            
            return result, source
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            return error_msg, "Error"
        finally:
            self.is_processing = False
    
    def process_voice_command(self, timeout: int = 5) -> Optional[Tuple[str, str]]:
        """Process voice command"""
        if not self.voice:
            return None
        
        try:
            # Listen for voice input
            text = self.voice.start_listening(timeout)
            if text and text.strip():
                # Process the recognized text
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response, source = loop.run_until_complete(self.process_command(text))
                finally:
                    loop.close()
                
                return text, response
            return None
        except Exception as e:
            print(f"Voice command error: {e}")
            return None
    
    def analyze_vision(self, prompt: str = "Analyze this image.") -> Optional[str]:
        """Analyze vision using local Moondream"""
        if not self.vision:
            return "Vision service not available"
        
        try:
            # Try to capture screen first
            screenshot = self.vision.capture_screen()
            if screenshot:
                analysis = self.vision.analyze_image(screenshot, prompt)
                
                # Speak analysis if voice is available
                if self.voice and analysis:
                    self.voice.speak(analysis)
                
                return analysis
            else:
                return "Screen capture failed"
        except Exception as e:
            return f"Vision analysis error: {e}"
    
    def start_camera_analysis(self, prompt: str = "Analyze this camera frame.") -> Optional[str]:
        """Start camera and analyze frame"""
        if not self.vision:
            return "Vision service not available"
        
        try:
            if self.vision.start_camera_feed():
                analysis = self.vision.analyze_camera_frame(prompt)
                
                # Speak analysis if voice is available
                if self.voice and analysis:
                    self.voice.speak(analysis)
                
                return analysis
            else:
                return "Camera not available"
        except Exception as e:
            return f"Camera analysis error: {e}"
    
    def stop_camera(self):
        """Stop camera feed"""
        if self.vision:
            self.vision.stop_camera_feed()
    
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def get_tasks(self) -> List[Dict]:
        """Get current tasks from brain"""
        if self.brain:
            return self.brain.get_tasks()
        return []
    
    def add_task(self, description: str, priority: str = "medium") -> bool:
        """Add task to brain"""
        if self.brain:
            try:
                self.brain.add_task(description, priority)
                return True
            except:
                return False
        return False
    
    def complete_task(self, task_id: int) -> bool:
        """Complete task"""
        if self.brain:
            return self.brain.complete_task(task_id)
        return False
    
    def get_statistics(self) -> Dict:
        """Get service statistics"""
        stats = {
            "processing": self.is_processing,
            "total_commands": len(self.command_history),
            "brain_available": self.use_brain and self.brain.is_available() if self.brain else False,
            "vision_available": self.vision.is_available() if self.vision else False,
            "voice_available": self.voice.is_available() if self.voice else False
        }
        
        if self.brain:
            stats.update(self.brain.get_statistics())
        
        if self.vision:
            stats["vision_status"] = self.vision.get_status()
        
        if self.voice:
            stats["voice_status"] = self.voice.get_status()
        
        return stats
    
    def is_available(self) -> bool:
        """Check if any local service is available"""
        return (self.use_brain and self.brain.is_available()) if self.brain else False
    
    def get_status(self) -> Dict:
        """Get comprehensive service status"""
        status = {
            "processing": self.is_processing,
            "use_brain": self.use_brain,
            "total_commands": len(self.command_history)
        }
        
        if self.brain:
            status.update(self.brain.get_status())
        
        return status
    
    def set_context(self, context: List[str]):
        """Set conversation context"""
        self.context_history = context[-10:]  # Keep only last 10
    
    def add_to_context(self, message: str):
        """Add message to context"""
        self.context_history.append(message)
        if len(self.context_history) > 10:
            self.context_history.pop(0)
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """Speak text using local TTS"""
        if self.voice:
            return self.voice.speak(text, blocking)
        return False
    
    def start_listening(self, timeout: int = 5) -> Optional[str]:
        """Start voice listening"""
        if self.voice:
            return self.voice.start_listening(timeout)
        return None
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.voice:
            self.voice.stop_speaking()
    
    def get_microphones(self) -> List[str]:
        """Get available microphones"""
        if self.voice:
            return self.voice.get_microphones()
        return []
    
    def calibrate_microphone(self, duration: int = 3) -> bool:
        """Calibrate microphone"""
        if self.voice:
            return self.voice.calibrate_microphone(duration)
        return False
