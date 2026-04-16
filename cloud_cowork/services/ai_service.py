"""AI Service for Cloud Cowork HUD"""

import asyncio
import sys
import os
from typing import Tuple, Optional, List, Dict

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from core.ai_engine import get_hybrid_response
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Legacy AI backend not available: {e}")
    AI_AVAILABLE = False

try:
    from .brain import HybridRouter
    HYBRID_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"Hybrid Router not available: {e}")
    HYBRID_ROUTER_AVAILABLE = False

class AIService:
    """AI Service for processing commands with HybridRouter"""
    
    def __init__(self):
        self.is_processing = False
        self.command_history = []
        self.context_history = []
        
        # Initialize HybridRouter if available
        if HYBRID_ROUTER_AVAILABLE:
            try:
                self.hybrid_router = HybridRouter()
                self.use_hybrid = True
                print("Hybrid Router initialized successfully")
            except Exception as e:
                print(f"Hybrid Router initialization failed: {e}")
                self.hybrid_router = None
                self.use_hybrid = False
        else:
            self.hybrid_router = None
            self.use_hybrid = False
    
    async def process_command(self, command: str, context: List[str] = None) -> Tuple[str, str]:
        """Process AI command with intelligent routing"""
        if self.is_processing:
            return "JARVIS is currently processing another request...", "Processing"
        
        self.is_processing = True
        
        try:
            # Use HybridRouter if available
            if self.use_hybrid and self.hybrid_router:
                response, source = await self.hybrid_router.route_command(command, context or self.context_history)
                result = f"[{source.upper()}] {response}"
            elif AI_AVAILABLE:
                # Fallback to legacy system
                response, source = get_hybrid_response(command, context or self.context_history)
                result = f"[{source.upper()}] {response}"
            else:
                result = "AI service is currently unavailable"
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
                "personal": self.hybrid_router.is_personal_command(command) if self.hybrid_router else False
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
    
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def get_routing_stats(self) -> Dict:
        """Get routing statistics from HybridRouter"""
        if self.use_hybrid and self.hybrid_router:
            return self.hybrid_router.get_routing_stats()
        return {"total": 0, "personal": 0, "general": 0, "hybrid_available": False}
    
    def get_ai_status(self) -> Dict:
        """Get AI service status"""
        status = {
            "processing": self.is_processing,
            "hybrid_router": self.use_hybrid,
            "legacy_available": AI_AVAILABLE,
            "total_commands": len(self.command_history)
        }
        
        if self.use_hybrid and self.hybrid_router:
            status.update(self.hybrid_router.get_status())
        
        return status
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return (self.use_hybrid and self.hybrid_router.is_available()) or AI_AVAILABLE
    
    def set_context(self, context: List[str]):
        """Set conversation context"""
        self.context_history = context[-10:]  # Keep only last 10
    
    def add_to_context(self, message: str):
        """Add message to context"""
        self.context_history.append(message)
        if len(self.context_history) > 10:
            self.context_history.pop(0)
