from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class AgentStatus(Enum):
    ONLINE = "online"
    BUSY = "busy"
    THINKING = "thinking"
    SLEEPING = "sleeping"
    ERROR = "error"

class AgentState:
    """Represents the current state of the JARVIS agent."""
    
    def __init__(self):
        self.status = AgentStatus.ONLINE
        self.thinking = "Ready"
        self.doing = "Idle"
        self.current_task_id: Optional[str] = None
        self.last_activity = datetime.now()
        self.system_stats: Dict[str, Any] = {}
        self.error_message: Optional[str] = None
    
    def update_status(self, status: AgentStatus, thinking: str = "", doing: str = ""):
        """Update agent status."""
        self.status = status
        if thinking:
            self.thinking = thinking
        if doing:
            self.doing = doing
        self.last_activity = datetime.now()
    
    def set_current_task(self, task_id: str):
        """Set the currently executing task."""
        self.current_task_id = task_id
        self.update_status(AgentStatus.BUSY, f"Executing task {task_id}", "Processing...")
    
    def clear_current_task(self):
        """Clear the current task."""
        self.current_task_id = None
        self.update_status(AgentStatus.ONLINE, "Ready", "Idle")
    
    def set_error(self, error_message: str):
        """Set error state."""
        self.error_message = error_message
        self.update_status(AgentStatus.ERROR, "Error occurred", f"Error: {error_message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "status": self.status.value,
            "thinking": self.thinking,
            "doing": self.doing,
            "current_task_id": self.current_task_id,
            "last_activity": self.last_activity.isoformat(),
            "system_stats": self.system_stats,
            "error_message": self.error_message,
        }
